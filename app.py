from fastapi import FastAPI, HTTPException, Query, Request, status, Depends
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


from typing import List
import os
import duckdb
from decimal import *
from datetime import datetime
from  logging import getLogger
import json
import crud, schemas, models
from db import get_db, engine

from sqlalchemy.orm import Session
from sqlalchemy import text, func, insert, inspect
from fastapi_sa_orm_filter.main import FilterCore
from fastapi_sa_orm_filter.operators import Operators as ops

logger = getLogger(__name__)

# Filter operations
event_filter = {
    'attribute1': [ops.eq, ops.in_, ops.not_eq],
    'attribute2': [ops.not_eq, ops.gte, ops.lte, ops.in_, ops.eq]
}



app = FastAPI()

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(),"error": "Request validation error"},
    )

@app.exception_handler(ResponseValidationError)
def validation_exception_handler(request: Request, exc: ResponseValidationError):
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(),"error": "Response validation error"},
    )

@app.exception_handler(ValidationError)
def validation_error_exception_handler(request: Request, exc: ValidationError):
    error_message = str(exc)  # Convert ValidationError to string
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": error_message, "error": "Validation error"},
    )



@app.on_event("startup")
def startup():
    #  if there is no table
    insp = inspect(engine)
    if not insp.has_table("events"):
        # init table and dummy data 
        models.Base.metadata.create_all(engine)
        
        dummy_data = open("./data/test_event.json") 
        rows = json.load(dummy_data)
        for row in rows:
            stmt = insert(models.Event).values(**row)
            with engine.begin() as connection:
                cursor = connection.execute(stmt)


@app.get("/")
def main_page():
    return {'message': 'Congrats!'}
    

@app.post("/event")
def create_event(new_event: schemas.Event, db: Session = Depends(get_db)):
    
    event = models.Event(**new_event.dict())

    query = text('''
        INSERT OR IGNORE INTO events (id, event_date, attribute1, attribute2, attribute3, attribute4, attribute5, attribute6, metric1, metric2)
        VALUES (:id, :event_date, :attribute1, :attribute2, :attribute3, :attribute4, :attribute5, :attribute6, :metric1, :metric2)
    ''').bindparams(id=event.id, event_date=event.event_date, attribute1=event.attribute1, attribute2=event.attribute2, attribute3=event.attribute3, 
                    attribute4=event.attribute4, attribute5=event.attribute5, attribute6=event.attribute6, metric1=event.metric1, metric2=event.metric2)
    db.execute(query)
    db.commit()
    # db.refresh(event)

    return new_event



@app.get("/analytics/query", response_model = List[schemas.AnalyticsResponse])
def get_analytics_data( request: schemas.AnalyticsRequest = Depends(), db: Session = Depends(get_db)): 
    """
    Gets aggregated results from DB
    query example: 
    /analytics/query?metrics=metric1,metric2&groupBy=attribute1&granularity=daily&filters=attribute1__in_=200,300|attribute2__gte=100&endDate=2023-02-01&startDate=2022-12-12
    """
    # remove whitespaces
    metrics = [r.strip() for r in request.metrics.split(',')]
    
    granularity = request.granularity.strip()
    group_by = request.groupBy.strip()
    filters = request.filters
    start_date = request.startDate
    end_date = request.endDate
    
    query = db.query(getattr(models.Event, group_by))
    
    if granularity == 'hourly':
        query = query.add_columns(text(f"DATE_TRUNC('hour', event_date)"))
    elif granularity == 'daily':
        query = query.add_columns(text(f"DATE_TRUNC('day', event_date)"))
    if 'metric1' in metrics:
        query = query.add_columns(func.sum(models.Event.metric1).label('sum_metric1'))
    if 'metric2' in metrics:
        query = query.add_columns(func.sum(models.Event.metric2).label('sum_metric2'))
    
    # print(filters)
    if filters:
        filter_inst = FilterCore(models.Event, event_filter)

        # print(filter_inst._get_filter_query(filters))
        filter_query_part = filter_inst.get_filter_query_part(filters)
        query = query.filter(*filter_query_part)

    if start_date:
        query = query.filter(models.Event.event_date >= start_date)
    if end_date:
        query = query.filter(models.Event.event_date <= end_date)

    if granularity == 'hourly':
        query = query.group_by(getattr(models.Event, group_by), text(f"DATE_TRUNC('hour', event_date)"))
    elif granularity == 'daily':
        query = query.group_by(getattr(models.Event, group_by), text(f"DATE_TRUNC('day', event_date)"))

    try:
        
        result = query.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error executing query", error = e)

    # Prepare and return JSON response
    analytics_data = []
    for row in result:
        row_data = {
            'groupBy': row[0],
            'date': datetime.strftime(row[1],'%Y-%m-%d:%H:%M:%S')  
        }
        if 'metric1' in metrics:
            row_data['metric1'] = int(row[2])
        if 'metric2' in metrics:
            row_data['metric2'] = Decimal(round(row[3],2))
        analytics_data.append(schemas.AnalyticsResponse(**row_data))
    # 
    return analytics_data

# if __name__ == '__main__':

    # app.run(host=os.environ.get("BACKEND_HOST", "127.0.0.1"), port=5000,debug=True)
    # app.run(host='0.0.0.0')
