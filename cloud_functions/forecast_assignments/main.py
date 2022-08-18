import forecast
import os
import json
from google.cloud.logging import DESCENDING
from datetime import datetime, timedelta, timezone
import pandas as pd

from google.cloud import bigquery

def get_assignments_data(api: forecast.Api, start_date: str, end_date: str) -> list:
    assignments = json_list(api.get_assignments(start_date, end_date))
    return [record for record in assignments]

def get_clients_data(api: forecast.Api) -> list:
    clients = json_list(api.get_clients())
    return [json.dumps(record) for record in clients]

def get_projects_data(api: forecast.Api) -> list:
    projects = json_list(api.get_projects())
    return [json.dumps(record) for record in projects]

def json_list(response: list) -> list:
    # This function maps a response to a json list    
    return list(map(lambda item: item._json_data, response)) 

def load_config() -> dict:
    return {
        'account_id': os.environ.get("FORECAST_ACCOUNT_ID"),
        'auth_token': os.environ.get("FORECAST_ACCESS_TOKEN"),
        'table_name': os.environ.get('TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        'location': os.environ.get('TABLE_LOCATION')
    }


def forecast_assignments_to_bigquery(data: dict, context:dict=None):
    config = load_config()

    print(f"Dataset id - {config['dataset_id']}")

    # Dates have to be specified for assignments
    start_timestamp = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "Z"
    end_timestamp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "Z"
    

    api = forecast.Api(
        account_id=config['account_id'], 
        auth_token=config['auth_token']
    )

    print(f"Getting assignments data from {start_timestamp} to {end_timestamp}")
    assignments_data_df = pd.DataFrame(get_assignments_data(api, start_timestamp, end_timestamp)).drop(['placeholder_id'], axis=1)

    client = bigquery.Client(location=config['location'])

    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    job_config = bigquery.LoadJobConfig()

    job_config.autodetect = True

    job = client.load_table_from_dataframe(
        assignments_data_df, table_ref, job_config=job_config
    )
    job.result()

    print("Loaded {} rows into {}:{}.".format(job.output_rows, config['dataset_id'], config['table_name']))    


if __name__ == "__main__":
    forecast_assignments_to_bigquery({}, {})