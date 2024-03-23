import unittest
import json
from unittest.mock import patch, MagicMock
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        # dummy flask client
        self.app = app.test_client()

    @patch('app.duckdb.connect')
    def test_add_event(self, mock_connect):
        # Mock duckdb connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Define sample event data
        event_data = {
            "id": 1,
            "event_date": "2024-01-15T10:00:00",
            "attribute1": 100,
            "attribute2": 200,
            "attribute3": 300,
            "attribute4": "att4",
            "attribute5": "att5",
            "attribute6": True,
            "metric1": 1,
            "metric2": 2.2
        }

        # post to event
        response = self.app.post('/event', json=event_data)

        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['message'], 'Event added successfully')

    @patch('app.duckdb.connect')
    def test_get_analytics_data(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        response = self.app.get('/analytics/query?groupBy=attribute1&filters[attribute2]=200&metrics=metric1,metric2&granularity=hourly&startDate=2024-03-15T00:00:00&endDate=2024-03-15T23:59:59')

        self.assertEqual(response.status_code, 200)

        # Check if the response data contains the expected keys
        data = response.get_json()
        self.assertTrue('results' in data)
        results = data['results']
        self.assertTrue(isinstance(results, list))

       
        for result in results:
            self.assertTrue('group_by' in result)
            self.assertTrue('truncated_event_date' in result)
            self.assertTrue('metrics' in result)
            self.assertTrue('sum_metric1' in result['metrics'])
            self.assertTrue('sum_metric2' in result['metrics'])

    @patch('app.duckdb.connect')
    def test_missing_required_params(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.app.get('/analytics/query')

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'Missing required query parameters: groupBy, metrics, granularity')

    @patch('app.duckdb.connect')
    def test_invalid_granularity(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        
        response = self.app.get('/analytics/query?groupBy=attribute1&filters[attribute2]=200&metrics=metric1,metric2&granularity=invalid')

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'Granularity must be either "hourly" or "daily"')

if __name__ == '__main__':
    unittest.main()
