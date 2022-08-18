import forecast
import os
import json
import time    
import google.cloud.logging
from google.cloud.logging import DESCENDING
import itertools
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

def load_data_to_bigquery(client: bigquery.Client, dataset_id: str, table_name: str, table_df: dict) -> dict:
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_name)

    job_config = bigquery.LoadJobConfig()
    # job_config.schema = [
    #     bigquery.SchemaField('id','INTEGER'),
    #     bigquery.SchemaField('start_date', 'STRING'),
    #     bigquery.SchemaField('end_date', 'STRING'),
    #     bigquery.SchemaField('allocation','FLOAT'),
    #     # bigquery.SchemaField('notes', 'STRING'),
    #     bigquery.SchemaField('updated_at', 'DATE'),
    #     bigquery.SchemaField('updated_by_id','STRING'),
    #     bigquery.SchemaField('project_id', 'STRING'),
    #     bigquery.SchemaField('person_id', 'FLOAT'),
    #     # bigquery.SchemaField('placeholder_id', 'FLOAT'),
    #     bigquery.SchemaField('repeated_assignment_set_id', 'FLOAT'),
    #     bigquery.SchemaField('active_on_days_off','BOOL'),
    # ]
    job_config.autodetect = True
    # table_df = table_df[:1].drop(['start_date', 'end_date',  'updated_at'])
    print("Attempting to load {} rows into {}:{}.".format(len(table_df), dataset_id, table_name))
    table_df = table_df.drop(['notes', 'placeholder_id'], axis=1)
    
    import pytest
    pytest.set_trace()
    job = client.load_table_from_dataframe(table_df, table_ref, job_config=job_config)
        

    result = job.result()
    print(result)
        
    return {table_name: f"{len(table_df)} rows"}

def get_time_since_last_updated(client: bigquery.Client, config: dict) -> str:
    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    # both of these are in milliseconds
    last_updated = int(client.get_table(table_ref)._properties['lastModifiedTime'])
    epoch_time = int(time.time()) * 1000
    return epoch_time - last_updated

def check_num_rows(client: bigquery.Client, config: dict):
    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    return client.list_rows(table_ref)._total_rows

def check_cloud_function_logs(client: google.cloud.logging.Client):
    time_window = datetime.now(timezone.utc) - timedelta(days=30)
    time_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    filter_str = (f"logName:projects/forecast-datastudio/logs/assignments_function_log AND severity=INFO "
                f'AND timestamp>="{time_window.strftime(time_format)}"')
                
    response = client.list_entries(filter_=filter_str, order_by=DESCENDING)

    try:
        return next(itertools.islice(response, 1)).payload
    except:
        return


def forecast_to_bigquery(data: dict, context:dict=None):
    config = load_config()

    print(f"Dataset id - {config['dataset_id']}")

    # The last updated returns the time the table was created if that was the last thing that happened (just created the table...)
    # We check there is any rows, if not then we load the data, if there is then we check when it last loaded
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
    forecast_to_bigquery({}, {})