import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app import app
from datetime import datetime


class TestApp(unittest.TestCase):

    def setUp(self):
        # Create FastAPI test client
        self.client = TestClient(app)

    @patch('app.get_db')
    def test_add_event(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

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

        response = self.client.post('/event', json=event_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()

    @patch('app.get_db')
    def test_get_analytics_data_all_params(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        response = self.client.get('/analytics/query?metrics=metric1, metric2&groupBy=attribute1&granularity=daily&filters=attribute1__in_=200,300|attribute2__gte=100&endDate=2023-02-01&startDate=2022-12-12')

        self.assertEqual(response.status_code, 200)

        

    @patch('app.get_db')
    def test_missing_required_params(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.client.get('/analytics/query')

        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertTrue('Request validation error' in data['error'] )

    @patch('app.get_db')
    def test_invalid_granularity(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.client.get('/analytics/query?groupBy=attribute1&metrics=metric1,metric2&granularity=invalid')

        self.assertEqual(response.status_code, 400)

    @patch('app.get_db')
    def test_get_analytics_data_with_filters(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.client.get('/analytics/query?metrics=metric1, metric2&groupBy=attribute1&granularity=daily&filters=attribute1__in_=200,300|attribute2__gte=100')
        data = response.json()

        self.assertEqual(response.status_code, 200)


        expected_data = [
            {
                "groupBy": 198772,
                "date": "2024-03-17:00:00:00",
                "metric1": 198772,
                "metric2": "1.20"
            },
            {
                "groupBy": 100,
                "date": "2024-01-15:00:00:00",
                "metric1": 1,
                "metric2": "2.20"
            },
            {
                "groupBy": 198772,
                "date": "2024-03-16:00:00:00",
                "metric1": 198772,
                "metric2": "1.20"
            }
        ]
        self.assertCountEqual(data, expected_data)

    
    @patch('app.get_db')
    def test_get_analytics_data_with_end_date(self, mock_connect):


        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        response = self.client.get('/analytics/query?metrics=metric1, metric2&groupBy=attribute1&granularity=daily&endDate=2023-02-01')
        expected_data = [
            {
                "groupBy": 9,
                "date": "2023-01-01:00:00:00",
                "metric1": 100,
                "metric2": "150.50"
            },
            {
                "groupBy": 8,
                "date": "2023-01-01:00:00:00",
                "metric1": 245,
                "metric2": "253.70"
            }
        ]

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertCountEqual(data, expected_data)


    
    @patch('app.get_db')
    def test_get_analytics_data_with_start_date(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        expected_data = [
            {
            "groupBy": 100,
            "date": "2024-01-15:00:00:00",
            "metric1": 1,
            "metric2": "2.20"
        },
        {
            "groupBy": 198772,
            "date": "2024-03-17:00:00:00",
            "metric1": 198772,
            "metric2": "1.20"
        },
        {
            "groupBy": 198772,
            "date": "2024-03-16:00:00:00",
            "metric1": 198772,
            "metric2": "1.20"
        }
        ]

        response = self.client.get('/analytics/query?metrics=metric1,metric2&groupBy=attribute1&granularity=daily&startDate=2024-01-12')

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertCountEqual(data, expected_data)


    @patch('app.get_db')
    def test_get_analytics_data_without_metrics(self, mock_connect):

        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection


        response = self.client.get('/analytics/query?groupBy=attribute1&granularity=daily')

        self.assertEqual(response.status_code, 400)

    @patch('app.get_db')
    def test_get_analytics_data_invalid_date_format(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = self.client.get('/analytics/query?metrics=metric1,metric2&groupBy=attribute1&granularity=daily&startDate=invalid_date')

        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
