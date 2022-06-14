import forecast
from dotenv import load_dotenv
import os
import json
import io

from google.cloud import bigquery

def get_assignments_data(api: forecast.Api):
    assignments = json_list(api.get_assignments(start_date="2022-04-01T00:00:00.000Z", end_date="2022-05-01T00:00:00.000Z"))
    return [json.dumps(record) for record in assignments]

def get_clients_data(api: forecast.Api):
    clients = json_list(api.get_clients())
    return [json.dumps(record) for record in clients]

def get_projects_data(api: forecast.Api):
    projects = json_list(api.get_projects())
    return [json.dumps(record) for record in projects]

def json_list(response: list) -> list:
    # This function maps a response to a json list    
    return list(map(lambda item: item._json_data, response)) 

def load_config() -> dict:
    import pytest
    pytest.set_trace()
    return {
        'account_id': os.environ.get("FORECAST_ACCOUNT_ID"),
        'auth_token': os.environ.get("FORECAST_ACCESS_TOKEN"),
        'assignments_table': os.environ.get('ASSIGNMENTS_TABLE_NAME'),
        'projects_table': os.environ.get('PROJECTS_TABLE_NAME'),
        'clients_table': os.environ.get('CLIENTS_TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_NAME')
    }

def load_data_to_bigquery(client, dataset_id, table_name, table_data):
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_name)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True

    print("Attempting to load {} rows into {}:{}.".format(len(table_data), dataset_id, table_name))

    job = client.load_table_from_file(
        io.StringIO('\n'.join(table_data)), 
        table_ref,
        location="EU", 
        job_config=job_config,
        )
    job.done()

def forecast_to_bigquery(data: dict, context:dict=None):
    config = load_config()

    api = forecast.Api(
        account_id=config['account_id'], 
        auth_token=config['auth_token']
    )
    tables = {
        config['assignments_table']: get_assignments_data(api),
        config['projects_table']: get_projects_data(api),
        config['clients_table']: get_clients_data(api)
    }
    print(f"Dataset id - {config['dataset_id']}")

    client = bigquery.Client()

    response = {"code": 200, "data": data, "result": []}
    for table_name, table_data in tables.items():
        response['result'].append(load_data_to_bigquery(client, config['dataset_id'], table_name, table_data))
    
    return response

# if __name__ == "__main__":
#     load_dotenv()
#     forecast_to_bigquery({}, {})