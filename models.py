from pydantic import BaseModel, validator
from typing import List, Optional, Union
from decimal import *
from sqlmodel import  SQLModel ,Field, Session , create_engine, Column, Integer, Sequence


class Event(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_date: str
    metric1: int
    metric2: Decimal
    attribute1: Optional[int] = None
    attribute2: Optional[int] = None
    attribute3: Optional[int] = None
    attribute4: Optional[str] = None 
    attribute5: Optional[str] = None
    attribute6: Optional[bool] = None

    @validator('id')
    def validate_id(cls, value):
        if not value:
            raise ValueError("id field cannot be empty")
        return value

    @validator('event_date')
    def validate_event_date(cls, value):
        if not value:
            raise ValueError("event_date field cannot be empty")
        return value

    

class AnalyticsRequest(SQLModel):
    metrics: str
    granularity: str
    groupBy: str
    filters: Optional[List[str]] = None 
    startDate: Optional[str] = None 
    endDate: Optional[str] = None 

    @validator('metrics')
    def validate_metrics(cls, value):
        if not value:
            raise ValueError("Metrics field cannot be empty")
        return value

    @validator('granularity')
    def validate_granularity(cls, value):
        if value not in ['hourly', 'daily']:
            raise ValueError("Granularity must be either 'hourly' or 'daily'")
        return value

    @validator('groupBy')
    def validate_groupBy(cls, value):
        if not value:
            raise ValueError("groupBy field cannot be empty")
        return value

class AnalyticsResponse(SQLModel):
    groupBy: int
    date: str
    metric1: Optional[int] = None 
    metric2: Optional[Decimal] = None 
