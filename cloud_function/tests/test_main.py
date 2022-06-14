import os
import mock
from main import json_list, load_config, load_data_to_bigquery

class mockResponse():
    def __init__(self, request):
        self._json_data()
        self.response_type = request

    def _json_data(self):
        self._json_data = {"json": "data", "stored": "here"}


def test_get_projects_data():
    mock_forecast_response = [mockResponse("projects"), mockResponse("assignments")]
    result = json_list(mock_forecast_response)
    assert result == [{"json": "data", "stored": "here"}, {"json": "data", "stored": "here"}] 

@mock.patch.dict(os.environ, {
    'FORECAST_ACCOUNT_ID': "account_id",
    'FORECAST_ACCESS_TOKEN': "auth_token",
    'ASSIGNMENTS_TABLE_NAME': "assignments_table",
    'PROJECTS_TABLE_NAME': "projects_table",
    'CLIENTS_TABLE_NAME': "clients_table",
    'DATASET_NAME': "dataset_name"
        }
    )
def test_load_config():
    assert load_config() == {
        'account_id': "account_id",
        'auth_token': "auth_token",
        'assignments_table': "assignments_table",
        'projects_table': "projects_table",
        'clients_table': "clients_table",
        'dataset_id': "dataset_name"
    }

# def test_load_data_to_bigquery():
