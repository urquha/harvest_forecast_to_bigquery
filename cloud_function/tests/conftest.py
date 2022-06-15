import pytest

plugins = ["pytest-bigquery-mock"]

@pytest.fixture
def mock_config():
    return {
        'account_id': "account_id",
        'auth_token': "auth_token",
        'assignments_table': "assignments_table",
        'projects_table': "projects_table",
        'clients_table': "clients_table",
        'dataset_id': "dataset_id"
    }

@pytest.fixture
def table_names():
    return ['assignments_table', 'projects_table', 'clients_table']