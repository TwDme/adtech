import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app import app
from datetime import datetime

class TestApp(unittest.TestCase):

    def setUp(self):
        # Create FastAPI test client
        self.client = TestClient(app)

    @patch('app.duckdb.connect')
    def test_add_event(self, mock_connect):
        # Mock duckdb connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Define sample event data
        event_data = {
            "id": 1,
            "event_date": "2024-01-15T10:00:00",
            "attribute1": "100",
            "attribute2": "200",
            "attribute3": "300",
            "attribute4": "att4",
            "attribute5": "att5",
            "attribute6": True,
            "metric1": 1,
            "metric2": 2.2
        }

        # Post to event
        response = self.client.post('/event', json=event_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['message'], 'Event added successfully')

    @patch('app.duckdb.connect')
    def test_get_analytics_data(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        response = self.client.get('/analytics/query?groupBy=attribute1&filters[attribute2]=200&metrics=metric1,metric2&granularity=hourly&startDate=2024-03-15T00:00:00&endDate=2024-03-15T23:59:59')

        self.assertEqual(response.status_code, 200)

        

    @patch('app.duckdb.connect')
    def test_missing_required_params(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.client.get('/analytics/query')

        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'Request validation error')

    @patch('app.duckdb.connect')
    def test_invalid_granularity(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.client.get('/analytics/query?groupBy=attribute1&filters[attribute2]=200&metrics=metric1,metric2&granularity=invalid')

        self.assertEqual(response.status_code, 400)

    @patch('app.duckdb.connect')
    def test_get_analytics_data_with_filters(self, mock_connect):
        # Mock database connection and return sample data
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.execute.return_value.fetchall.return_value = [
            (100, datetime(2024, 1, 15, 10, 0, 0), 100, 200, 300, 'att4', 'att5', True, 1, 2.20),
            # Add more sample data as needed
        ]
        
        # Send request to the API
        response = self.client.get('/analytics/query?groupBy=attribute1&filters[attribute2]=200&metrics=metric1,metric2&granularity=hourly')
        
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        print(response)
        # Check if the response data matches the expected data
        expected_data = [
            {
                "attribute1": 100,
                "event_date": "2024-01-15T10:00:00",
                "metric1": 1,
                "metric2": 2.20
            },
            # Add more expected data as needed
        ]
        # TODO filters are null
        self.assertEqual(response.json(), expected_data)

    
    @patch('app.duckdb.connect')
    def test_get_analytics_data_with_end_date(self, mock_connect):
        # TODO
        # Mock database connection and return sample data
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        response = self.client.get('/analytics/query?metrics=metric1, metric2&groupBy=attribute1&granularity=daily&endDate=2023-02-01')
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
