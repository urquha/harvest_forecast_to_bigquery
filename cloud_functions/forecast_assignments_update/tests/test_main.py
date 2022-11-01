import forecast
import os
import mock
from main import json_list, load_config, forecast_assignments_to_bigquery_update, expand_rows, get_dates, make_row, get_assignments, check_billable, get_billable_codes
import pandas as pd
from datetime import datetime
from unittest.mock import patch

class mockResponse():
    def __init__(self, request):
        self._json_data()
        self.response_type = request

    def _json_data(self):
        self._json_data = {"json": "data", "stored": "here"}


def test_json_list():
    response = json_list([mockResponse('')])
    assert response ==  [{"json": "data", "stored": "here"}]

@mock.patch.dict(os.environ, {
    'FORECAST_ACCOUNT_ID': "account_id",
    'FORECAST_ACCESS_TOKEN': "auth_token",
    'TABLE_NAME': "assignments_table",
    'DATASET_ID': "dataset_id",
    'TABLE_LOCATION': "table_location"
        }
    )
def test_load_config(mock_config):
    assert load_config() == mock_config

@patch('main.get_projects_data')
@patch('main.write_to_bigquery')
@patch('main.get_assignments_data')
def test_forecast_assignments_to_bigquery_update(mock_get_assignments_data, mock_write_to_bigquery, mock_get_projects_data, mock_assignments_response, mock_projects_data):
    mock_get_assignments_data.return_value = mock_assignments_response
    mock_write_to_bigquery.return_value = {}
    mock_get_projects_data.return_value = mock_projects_data
    response = forecast_assignments_to_bigquery_update({})
    assert response == "Finished"

@patch('main.get_assignments_data')
def test_get_assignments(mock_get_assignments_data, mock_assignments_response, mock_expand_rows_response):
    mock_get_assignments_data.return_value = mock_assignments_response
    response = get_assignments(forecast.Api)
    assert response.values.tolist().sort() ==  mock_expand_rows_response.sort()


def test_expand_rows(mock_assignments_response, mock_expand_rows_response):
    df = pd.DataFrame(mock_assignments_response)
    response = expand_rows(df).sort_values('start_date')
    print(response.values.tolist())
    assert response.values.tolist() == pd.DataFrame(mock_expand_rows_response).values.tolist()

     
def test_get_dates():
    end_date = datetime.strptime('2022-08-01', '%Y-%m-%d')
    start_date = datetime.strptime('2022-07-15', '%Y-%m-%d')
    response = get_dates(start_date, end_date)
    assert response == [datetime(2022, 7, 15, 0, 0), datetime(2022, 7, 18, 0, 0), datetime(2022, 7, 19, 0, 0), datetime(2022, 7, 20, 0, 0), datetime(2022, 7, 21, 0, 0), datetime(2022, 7, 22, 0, 0), datetime(2022, 7, 25, 0, 0), datetime(2022, 7, 26, 0, 0), datetime(2022, 7, 27, 0, 0), datetime(2022, 7, 28, 0, 0), datetime(2022, 7, 29, 0, 0), datetime(2022, 8, 1, 0, 0)]

def test_make_row():
    row = pd.Series({'start_date': "2022-05-05", 'end_date': '2022-05-07'})
    date = datetime.strptime('2022-5-06', '%Y-%m-%d')
    response = make_row(row, date)
    assert response.values.tolist() == ["2022-05-06", '2022-05-06']

def test_check_billable():
    row = pd.Series({"project_id": 100})
    response = check_billable(row, [100])
    assert response

@patch('main.get_projects_data')
def test_get_billable_codes(mock_get_projects_data, mock_projects_data):
    mock_get_projects_data.return_value = mock_projects_data
    resp = get_billable_codes(forecast.Api)
    assert resp == [1]