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
    'DATASET_ID': "dataset_id"
        }
    )
def test_load_config(mock_config):
    assert load_config() == mock_config

def test_load_data_to_bigquery(bq_client_mock, mock_config, table_names):
    mock_table_data = {}
    response = load_data_to_bigquery(bq_client_mock, mock_config['dataset_id'], table_names[0], mock_table_data)
    assert response == {table_names[0]: f"{len(mock_table_data)} rows"}