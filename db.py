
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from db_config import settings

# TODO SSL, Env vars
engine = create_engine(
    settings.duckdb_string, echo=True #, connect_args={'sslmode':'require'}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()




