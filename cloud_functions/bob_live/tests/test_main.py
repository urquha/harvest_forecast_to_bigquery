import forecast
import os
import mock
from main import load_config, expand_rows, get_dates, make_row, bob_to_bigquery
import pandas as pd
from datetime import datetime
from unittest.mock import patch

class mockResponse():
    def __init__(self, request):
        self._json_data()
        self.response_type = request

    def _json_data(self):
        self._json_data = {"json": "data", "stored": "here"}

@mock.patch.dict(os.environ, {
    'TABLE_NAME': "assignments_table",
    'DATASET_ID': "dataset_id",
    'TABLE_LOCATION': "table_location",
    "BOB_ACCESS_TOKEN": "bob_token"
        }
    )
def test_load_config(mock_config):
    assert load_config() == mock_config

# @patch('main.get_projects_data')
# @patch('main.write_to_bigquery')
# @patch('main.get_assignments_data')
# def test_forecast_assignments_to_bigquery_update(mock_get_assignments_data, mock_write_to_bigquery, mock_get_projects_data, mock_assignments_response, mock_projects_data):
#     mock_get_assignments_data.return_value = mock_assignments_response
#     mock_write_to_bigquery.return_value = {}
#     mock_get_projects_data.return_value = mock_projects_data
#     response = bob_to_bigquery({})
#     assert response == "Finished"



def test_expand_rows(mock_holidays_response, mock_expand_rows_response):
    df = pd.DataFrame(mock_holidays_response)
    response = expand_rows(df).sort_values('startDate')
    print(response.values.tolist())
    assert response.values.tolist() == mock_expand_rows_response

     
def test_get_dates():
    end_date = datetime.strptime('2022-08-01', '%Y-%m-%d')
    start_date = datetime.strptime('2022-07-15', '%Y-%m-%d')
    response = get_dates(start_date, end_date)
    
    assert response == [datetime(2022, 7, 15, 0, 0), datetime(2022, 7, 18, 0, 0), datetime(2022, 7, 19, 0, 0), datetime(2022, 7, 20, 0, 0), datetime(2022, 7, 21, 0, 0), datetime(2022, 7, 22, 0, 0), datetime(2022, 7, 25, 0, 0), datetime(2022, 7, 26, 0, 0), datetime(2022, 7, 27, 0, 0), datetime(2022, 7, 28, 0, 0), datetime(2022, 7, 29, 0, 0), datetime(2022, 8, 1, 0, 0)]

def test_make_row():
    row = pd.Series({'startDate': "2022-05-05", 'endDate': '2022-05-07'})
    date = datetime.strptime('2022-5-06', '%Y-%m-%d')
    response = make_row(row, date)
    assert response.values.tolist() == ["2022-05-06", '2022-05-06']

