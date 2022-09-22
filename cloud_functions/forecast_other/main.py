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

def get_clients_data(api: forecast.Api) -> list:
    clients = json_list(api.get_clients())
    return [record for record in clients]

def get_projects_data(api: forecast.Api) -> list:
    projects = json_list(api.get_projects())
    return [record for record in projects]

def get_person_data(api: forecast.Api) -> list:
    people = json_list(api.get_people())
    return [record for record in people]

def json_list(response: list) -> list:
    # This function maps a response to a json list    
    return list(map(lambda item: item._json_data, response)) 

def load_config() -> dict:
    return {
        'account_id': os.environ.get("FORECAST_ACCOUNT_ID"),
        'auth_token': os.environ.get("FORECAST_ACCESS_TOKEN"),
        'person_table_name': os.environ.get('PERSON_TABLE_NAME'),
        'projects_table_name': os.environ.get('PROJECTS_TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        'location': os.environ.get('TABLE_LOCATION')
    }

def forecast_other_to_bigquery(data: dict, context:dict=None):
    config = load_config()

    print(f"Dataset id - {config['dataset_id']}")


    api = forecast.Api(
        account_id=config['account_id'], 
        auth_token=config['auth_token']
    )

    projects_data_df = pd.DataFrame(get_projects_data(api))
    person_data_df = pd.DataFrame(get_person_data(api)).drop(['working_days', 'roles'], axis=1)

    client = bigquery.Client(location=config['location'])

    dataset_ref = client.dataset(config['dataset_id'])
    projects_table_ref = dataset_ref.table(config['projects_table_name'])
    person_table_ref = dataset_ref.table(config['person_table_name'])
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job_config.autodetect = True

    projects_job = client.load_table_from_dataframe(projects_data_df, projects_table_ref, job_config=job_config)
    projects_job.result()
    person_job = client.load_table_from_dataframe(person_data_df, person_table_ref, job_config=job_config)
    person_job.result()

    print("Loaded {} rows into {}:{}.".format(projects_job.output_rows, config['dataset_id'], config['projects_table_name']))    
    print("Loaded {} rows into {}:{}.".format(person_job.output_rows, config['dataset_id'], config['person_table_name']))    


if __name__ == "__main__":
    forecast_other_to_bigquery({}, {})