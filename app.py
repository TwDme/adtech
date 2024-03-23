from flask import Flask, request
import os
import duckdb
from datetime import datetime
from db import Event, delete_table, create_table, insert_dummy_data


app = Flask(__name__)

@app.route("/")
def main_page():
    return '<h1>Check</h1>'
    

@app.route('/event', methods=['POST'])
def add_event():
    # Check if the request contains JSON data
    if not request.json:
        return {'error': 'Request must be in JSON format'}, 400
    
    # Get the request
    event_data = request.json
    
    # Create an Event from request
    event = Event(**event_data)
    
    # Insert to DB
    with duckdb.connect("adtech.db") as con:
    
        con.execute('''
            INSERT OR IGNORE INTO events (id, event_date, attribute1, attribute2, attribute3, attribute4, attribute5, attribute6, metric1, metric2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event.id, event.event_date, event.attribute1, event.attribute2, event.attribute3, event.attribute4, event.attribute5, event.attribute6, event.metric1, event.metric2))
        
        con.sql('''SELECT * FROM events limit 20''').show()

    return {'message': 'Event added successfully'}, 200


@app.route('/analytics/query', methods=['GET'])
def get_analytics_data():
    
    group_by = request.args.get('groupBy') 
    filters = request.args.getlist('filters')
    metrics = request.args.get('metrics')
    granularity = request.args.get('granularity')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    # Check required parameters 
    required_params = ['groupBy', 'metrics', 'granularity']
    missing_params = [param for param in required_params if not request.args.get(param)]
    if missing_params:
        return {'error': f'Missing required query parameters: {", ".join(missing_params)}'}, 400

    # check granularity
    if granularity not in ['hourly', 'daily']:
        return {'error': 'Granularity must be either "hourly" or "daily"'}, 400


    # query
    query = f'''
        SELECT {group_by}
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
    if start_date:
        query += f' AND event_date >= \'{start_date}\''
    if end_date:
        query += f' AND event_date <= \'{end_date}\''
    if granularity == 'hourly':
        query += f' GROUP BY {group_by}, DATE_TRUNC(\'hour\', event_date)'
    elif granularity == 'daily':
        query += f' GROUP BY {group_by}, DATE_TRUNC(\'day\', event_date)'

    print(query)
    with duckdb.connect("adtech.db") as con:
        result = con.execute(query).fetchall()

    # Prepare and return JSON response
    analytics_data = []
    for row in result:
        row_data = {
            group_by: row[0],
            'date': datetime.strftime(row[1],'%d-%m-%Y:%H')  
        }
        if 'metric1' in metrics:
            row_data['sum_metric1'] = row[2]
        if 'metric2' in metrics:
            row_data['sum_metric2'] = round(row[3],1)
        analytics_data.append(row_data)

    return {'results': analytics_data}, 200

if __name__ == '__main__':
    delete_table()
    create_table()
    insert_dummy_data()
    # app.run(host=os.environ.get("BACKEND_HOST", "127.0.0.1"), port=5000,debug=True)
    app.run(host='0.0.0.0')
