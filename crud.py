from sqlalchemy.orm import Session

from models import Event

def post_event(db: Session, event: Event):
    return db.add(event)