from fastapi import FastAPI, HTTPException, Query, Request, status, Depends
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel


from typing import List,Optional
import os
import duckdb
from decimal import *
from datetime import datetime
# from models import Event#, AnalyticsResponse, AnalyticsRequest
# from db import  connect_duckdb, init_table
from  logging import getLogger
# from sqlalchemy import Column, Integer, Sequence, String, create_engine
import crud, schemas, models
from db import get_db, engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import text, func
# # from pydantic_settings import BaseSettings
# from sqlalchemy.orm import sessionmaker



logger = getLogger(__name__)
models.Base.metadata.create_all(bind=engine)


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
async def validation_error_exception_handler(request: Request, exc: ValidationError):
    error_message = str(exc)  # Convert ValidationError to string
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": error_message, "error": "Validation error"},
    )

# @app.on_event("startup")
# def startup(): #con: Session = Depends(get_db)
    # create db tables
    # init_table()

@app.get("/")
def main_page():
    return {'message': 'Congrats!'}
    

@app.post("/event")
def create_event(new_event: schemas.Event, db: Session = Depends(get_db)):
    event = models.Event(**new_event.dict())
    # db.add(new_event)
    query = text('''
        INSERT OR IGNORE INTO events (id, event_date, attribute1, attribute2, attribute3, attribute4, attribute5, attribute6, metric1, metric2)
        VALUES (:id, :event_date, :attribute1, :attribute2, :attribute3, :attribute4, :attribute5, :attribute6, :metric1, :metric2)
    ''').bindparams(id=event.id, event_date=event.event_date, attribute1=event.attribute1, attribute2=event.attribute2, attribute3=event.attribute3, 
                    attribute4=event.attribute4, attribute5=event.attribute5, attribute6=event.attribute6, metric1=event.metric1, metric2=event.metric2)
    db.execute(query)
    db.commit()
    # db.refresh(event)

    return new_event



@app.get("/analytics/query", response_model = List[schemas.AnalyticsResponse]) # , 
def get_analytics_data( request: schemas.AnalyticsRequest = Depends(), db: Session = Depends(get_db)):

    metrics = request.metrics.split(',')
    granularity = request.granularity
    group_by = request.groupBy
    filters = request.filters
    start_date = request.startDate
    end_date = request.endDate
    
    query = db.query(getattr(models.Event, group_by))
    
    if granularity == 'hourly':
        query = query.add_columns(text(f"DATE_TRUNC(\'hour\', events.event_date)"))
    elif granularity == 'daily':
        query = query.add_columns(text(f"DATE_TRUNC(\'day\', events.event_date)"))
    if 'metric1' in metrics:
        query = query.add_columns(func.sum(models.Event.metric1).label('sum_metric1'))
    if 'metric2' in metrics:
        query = query.add_columns(func.sum(models.Event.metric2).label('sum_metric2'))
    
    # TODO check conditions
    if filters:
        filter_conditions = filters.split(';')
        for filter_condition in filter_conditions:
            filter_key, filter_value = filter_condition.split('=')
            query = query.filter(getattr(models.Event, filter_key) == filter_value)
    if start_date:
        query = query.filter(models.Event.event_date >= start_date)
    if end_date:
        query = query.filter(models.Event.event_date <= end_date)

    query = query.group_by(getattr(models.Event, group_by))
    if granularity == 'hourly':
        query = query.group_by(getattr(models.Event, group_by), text(f"DATE_TRUNC(\'hour\', events.event_date)"))
    elif granularity == 'daily':
        query = query.group_by(getattr(models.Event, group_by), text(f"DATE_TRUNC(\'day\', events.event_date)"))

    try:
        result = query.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error executing query")

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
