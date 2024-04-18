from fastapi import FastAPI, HTTPException, Query, Request, status, Depends
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


from typing import List
import os
import duckdb
from decimal import *
from datetime import datetime
from models import Event, AnalyticsResponse, AnalyticsRequest
from db import  connect_duckdb, init_table
from  logging import getLogger
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker


logger = getLogger(__name__)

con = connect_duckdb()
# eng  = create_engine(f"duckdb:///adtech.db")
# Base = declarative_base()
# Base.metadata.create_all(eng)
# session = Session(bind=eng)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# # Dependency
# def get_db():
#     db = session()
#     try:
#         yield db
#     finally:
#         db.close()

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

@app.on_event("startup")
def startup(): #con: Session = Depends(get_db)
    # create db tables
    init_table(con)

@app.get("/")
def main_page():
    return {'message': 'Congrats!'}
    

@app.post("/event")
def add_event(event: Event): #con: Session = Depends(get_db)
    
    con.execute('''
        INSERT OR IGNORE INTO events (id, event_date, attribute1, attribute2, attribute3, attribute4, attribute5, attribute6, metric1, metric2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event.id, event.event_date, event.attribute1, event.attribute2, event.attribute3, event.attribute4, event.attribute5, event.attribute6, event.metric1, event.metric2))
    con.commit()
    con.sql('''SELECT * FROM events limit 20''').show()

    return {'message': 'Event added successfully'}



@app.get("/analytics/query", response_model = List[AnalyticsResponse]) # , 
def get_analytics_data( validated_analytics_request: AnalyticsRequest = Depends()):
    # groupBy: str, granularity: str, metrics: str, filters: Optional[List[str]] = None,startDate: Optional[str] = None, endDate: Optional[str] = None ):

    groupBy = validated_analytics_request.groupBy
    granularity = validated_analytics_request.granularity
    metrics = validated_analytics_request.metrics
    filters = validated_analytics_request.filters
    startDate = validated_analytics_request.startDate
    endDate = validated_analytics_request.endDate
    print(validated_analytics_request)

    # query
    query = f'''
        SELECT {groupBy}
    '''
    # select granularity
    if granularity == 'hourly':
        query += f', DATE_TRUNC(\'hour\', event_date) AS truncated_event_date'
    elif granularity == 'daily':
        query += f', DATE_TRUNC(\'day\', event_date) AS truncated_event_date'
    if 'metric1' in metrics:
        query += f', SUM(metric1) AS sum_metric1'
    if 'metric2' in metrics:
        query += f', SUM(metric2) AS sum_metric2'
    query += f'''
        FROM events
    '''
    if filters:
        filter_conditions = ' AND '.join([f'{filter_key} = {filter_value}' for filter_key, filter_value in filters.items()])
        query += f' WHERE {filter_conditions}'
    if startDate:
        
        query += f' AND event_date >= \'{startDate}\''
    if endDate:
        query += f' AND event_date <= \'{endDate}\''
    if granularity == 'hourly':
        query += f' GROUP BY {groupBy}, DATE_TRUNC(\'hour\', event_date)'
    elif granularity == 'daily':
        query += f' GROUP BY {groupBy}, DATE_TRUNC(\'day\', event_date)'

    print(query)
    with duckdb.connect("adtech.db") as con:
        result = con.execute(query).fetchall()

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
        analytics_data.append(AnalyticsResponse(**row_data))
    # 
    return analytics_data

# if __name__ == '__main__':

    # app.run(host=os.environ.get("BACKEND_HOST", "127.0.0.1"), port=5000,debug=True)
    # app.run(host='0.0.0.0')
