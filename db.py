
import duckdb

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from db_config import settings

# TODO SSL, Env vars
engine = create_engine(
    settings.duckdb_string, echo=True #, connect_args={'sslmode':'require'}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close() 

# def connect_duckdb(duckdb_file_path = "adtech.db"):
#     # TODO
#     # con  = create_engine(f"duckdb:///{duckdb_file_path}")
#     # eng = create_engine("duckdb:///:memory:")
#     # Base.metadata.create_all(eng)
#     # session = Session(bind=eng)
#     # SQLModel.metadata.create_all(engine)

#     try:
#         con = duckdb.connect(duckdb_file_path)
#     except Exception as e:
#         print(f"DB connection error: {e}")
#     return con

# def init_table(con):
    
#     # Drop tables if they exist
#     create_table(con)
#     insert_dummy_data(con)

# def create_table(con):
#     """
#     Parameter:
#     con : duckdb.connect
#     """
    
#     con.sql('''DROP TABLE IF EXISTS events''')
#     # Create events table if not exists
#     con.sql('''
#         CREATE TABLE IF NOT EXISTS events (
#             id INTEGER PRIMARY KEY,
#             event_date DATETIME,
#             attribute1 INTEGER,
#             attribute2 INTEGER,
#             attribute3 INTEGER,
#             attribute4 TEXT,
#             attribute5 TEXT,
#             attribute6 BOOLEAN,
#             metric1 INTEGER,
#             metric2 DECIMAL(10,2)
#         )
#     ''')
#     con.commit()
#     con.table("events").show()


# def insert_dummy_data(con):
#     """
#     Parameter:
#     con : duckdb.connect
#     """
#     con.execute("INSERT INTO events SELECT * FROM read_json_auto('./data/test_event.json');")
#     con.commit()    
#     con.sql('''SELECT * FROM events limit 20''').show()

