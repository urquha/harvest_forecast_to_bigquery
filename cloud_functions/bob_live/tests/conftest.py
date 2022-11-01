import pytest
from forecast import Assignment

plugins = ["pytest-bigquery-mock"]

@pytest.fixture
def mock_config():
    return {
        'table_name': "assignments_table",
        'dataset_id': "dataset_id",
        'location': 'table_location',
        'headers': {
            "accept": "application/json",
            "Authorization": "bob_token",
        }
    }

@pytest.fixture
def mock_holidays_response():
    return [
        {'policyTypeDisplayName': 'Holiday', 'endDate': '2022-09-16', 'startPortion': 'all_day', 'endPortion': 'all_day', 'type': 'days', 'startDate': '2022-09-15', 'status': 'approved'},       
        {'policyTypeDisplayName': 'Holiday', 'endDate': '2022-09-16', 'startPortion': 'all_day', 'endPortion': 'morning', 'type': 'days', 'startDate': '2022-09-12', 'status': 'approved'},       
        {'policyTypeDisplayName': 'Holiday', 'endDate': '2022-09-16', 'startPortion': 'morning', 'endPortion': 'morning', 'type': 'days', 'startDate': '2022-09-16', 'status': 'approved'},       
        {'policyTypeDisplayName': 'Holiday', 'endDate': '2022-09-16', 'startPortion': 'afternoon', 'endPortion': 'morning', 'type': 'days', 'startDate': '2022-09-14', 'status': 'approved'},       
        {'policyTypeDisplayName': 'Holiday', 'endDate': '2022-09-16', 'startPortion': 'afternoon', 'endPortion': 'afternoon', 'type': 'days', 'startDate': '2022-09-16', 'status': 'approved'},       
        {'policyTypeDisplayName': 'Holiday', 'endDate': '2022-09-16', 'startPortion': 'afternoon', 'endPortion': 'all_day', 'type': 'days', 'startDate': '2022-09-15', 'status': 'approved'},       
    ]

@pytest.fixture
def mock_expand_rows_response():
    return [
        ['Holiday', '2022-09-12', 'all_day', 'all_day', 'days', '2022-09-12', 'approved'], 
        ['Holiday', '2022-09-13', 'all_day', 'all_day', 'days', '2022-09-13', 'approved'], 
        ['Holiday', '2022-09-14', 'all_day', 'all_day', 'days', '2022-09-14', 'approved'], 
        ['Holiday', '2022-09-14', 'afternoon', 'all_day', 'days', '2022-09-14', 'approved'], 
        ['Holiday', '2022-09-15', 'all_day', 'all_day', 'days', '2022-09-15', 'approved'], 
        ['Holiday', '2022-09-15', 'all_day', 'all_day', 'days', '2022-09-15', 'approved'], 
        ['Holiday', '2022-09-15', 'all_day', 'all_day', 'days', '2022-09-15', 'approved'], 
        ['Holiday', '2022-09-15', 'afternoon', 'all_day', 'days', '2022-09-15', 'approved'], 
        ['Holiday', '2022-09-16', 'morning', 'morning', 'days', '2022-09-16', 'approved'], 
        ['Holiday', '2022-09-16', 'afternoon', 'afternoon', 'days', '2022-09-16', 'approved'], 
        ['Holiday', '2022-09-16', 'all_day', 'all_day', 'days', '2022-09-16', 'approved'], 
        ['Holiday', '2022-09-16', 'all_day', 'morning', 'days', '2022-09-16', 'approved'], 
        ['Holiday', '2022-09-16', 'all_day', 'morning', 'days', '2022-09-16', 'approved'], 
        ['Holiday', '2022-09-16', 'all_day', 'all_day', 'days', '2022-09-16', 'approved']
    ]

@pytest.fixture
def mock_projects_data():
    return [
        {'id': 1, "color": 'orange'},
        {'id': 2, 'color': 'blue'}
    ]