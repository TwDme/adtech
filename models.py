from sqlalchemy import Column, Integer, String, Float, Boolean, Sequence
from db import Base




# alchemy
class Event(Base):
    __tablename__ = 'events'
    # TODO seq id
    user_id_seq = Sequence('event_id_seq')
    id = Column(Integer, user_id_seq, primary_key=True, server_default=user_id_seq.next_value())
    event_date = Column(String)
    metric1 = Column(Integer)
    metric2 = Column(Float)
    attribute1 = Column(Integer, nullable=True)
    attribute2 = Column(Integer, nullable=True)
    attribute3 = Column(Integer, nullable=True)
    attribute4 = Column(String, nullable=True) 
    attribute5 = Column(String, nullable=True)
    attribute6 = Column(Boolean, nullable=True)



