
import duckdb
from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class Event:
    id: int
    event_date: str
    metric1: int
    metric2: float
    attribute1: Optional[int] = None
    attribute2: Optional[int] = None
    attribute3: Optional[int] = None
    attribute4: Optional[str] = None
    attribute5: Optional[str] = None
    attribute6: Optional[bool] = None
    

def delete_table():
    with duckdb.connect("adtech.db") as con:
        con.sql('''DROP TABLE IF EXISTS events''')
    


def create_table():
    with duckdb.connect("adtech.db") as con:
        # Create events table if not exists
        con.sql('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                event_date DATETIME,
                attribute1 INTEGER,
                attribute2 INTEGER,
                attribute3 INTEGER,
                attribute4 TEXT,
                attribute5 TEXT,
                attribute6 BOOLEAN,
                metric1 INTEGER,
                metric2 FLOAT
            )
        ''')
        con.table("events").show()


def insert_dummy_data():
    with open('./data/test_event.json', 'r') as f:
            dummy_data = json.load(f)
    
    with duckdb.connect("adtech.db") as con:
        for event_data in dummy_data:
            con.execute('''
                INSERT INTO events (id, event_date, attribute1, attribute2, attribute3, attribute4, attribute5, attribute6, metric1, metric2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_data['id'], event_data['event_date'], 
                  event_data.get('attribute1'), event_data.get('attribute2'), event_data.get('attribute3'), event_data.get('attribute4'), 
                  event_data.get('attribute5'), event_data.get('attribute6'), event_data.get('metric1'), event_data.get('metric2')))
            
        con.sql('''SELECT * FROM events limit 20''').show()