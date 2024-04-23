from sqlalchemy import  Column, Integer, String, Float, Boolean, Sequence, TIMESTAMP
from sqlalchemy.types import DECIMAL
from db import Base


# alchemy
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, Sequence('event_id_seq'), primary_key=True)
    event_date = Column(TIMESTAMP)
    metric1 = Column(Integer)
    metric2 = Column(DECIMAL(10,2))
    attribute1 = Column(Integer, nullable=True)
    attribute2 = Column(Integer, nullable=True)
    attribute3 = Column(Integer, nullable=True)
    attribute4 = Column(String, nullable=True) 
    attribute5 = Column(String, nullable=True)
    attribute6 = Column(Boolean, nullable=True)

