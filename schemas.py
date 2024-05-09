from pydantic import BaseModel, field_validator
from typing import List, Optional
from decimal import *
from datetime import datetime
# from fastapi_filter import FilterDepends, with_prefix
# from fastapi_filter.contrib.sqlalchemy import Filter

class EventBase(BaseModel):  

    id: int
    event_date: str
    metric1: int
    metric2: Decimal
    attribute1: Optional[int] = None
    attribute2: Optional[int] = None
    attribute3: Optional[int] = None
    attribute4: Optional[str] = None 
    attribute5: Optional[str] = None
    attribute6: Optional[bool] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    
    class ConfigDict:
        from_attributes = True


class AnalyticsRequest(BaseModel):
    metrics: str
    granularity: str
    groupBy: str
    filters: Optional[str] = None 
    startDate: Optional[datetime] = None 
    endDate: Optional[datetime] = None 

    @field_validator('metrics')
    def validate_metrics(cls, value):
        if not value:
            raise ValueError("Metrics field cannot be empty")
        elif 'metric1' not in value and 'metric2' not in value:
            raise ValueError("Metrics should have at least 1 of these values: 'metric1' or 'metric2")
        return value

    @field_validator('granularity')
    def validate_granularity(cls, value):
        if value not in ['hourly', 'daily']:
            raise ValueError("Granularity must be either 'hourly' or 'daily'")
        return value

    @field_validator('groupBy')
    def validate_groupBy(cls, value):
        if not value:
            raise ValueError("groupBy field cannot be empty")
        return value
    
    class ConfigDict:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    groupBy: int
    date: str
    metric1: Optional[int] = None 
    metric2: Optional[Decimal] = None 

    class ConfigDict:
        from_attributes = True