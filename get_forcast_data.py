import forecast
from dotenv import load_dotenv
import os
import pytest
from data_response_key_lists import person_data_keys
import json
import sys
import io

from google.cloud import bigquery

load_dotenv()

def get_assignments_data():
    assignments = json_list(api.get_assignments(start_date="2022-04-01T00:00:00.000Z", end_date="2022-05-01T00:00:00.000Z"))
    return [json.dumps(record) for record in assignments]

def get_clients_data():
    clients = json_list(api.get_clients())
    return [json.dumps(record) for record in clients]

def get_projects_data():
    projects = json_list(api.get_projects())
    return [json.dumps(record) for record in projects]

def json_list(response: list):
    # This function maps a response to a json list
    return list(map(lambda item: item._json_data, response)) 

def load_to_bigquery():
    
    table_id = table_names[0]
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True

    job = client.load_table_from_json(
        assignments, 
        table_ref,
        location="europe-west2", 
        job_config=job_config,
        num_retries=0,
        timeout=2)
    print(job.result())

    print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))


if __name__ == "__main__":
    api = forecast.Api(
        account_id=os.environ.get("HARVEST_ACCOUNT_ID"), 
        auth_token=os.environ.get("HARVEST_ACCESS_TOKEN")
    )
    assignments = get_assignments_data()
    # pytest.set_trace()
    clients = '\n'.join(get_clients_data())
    projects = '\n'.join(get_projects_data())
    dataset_id = 'forecast_001'
    table_names = ['assignments_data', 'projects_data', 'clients_data']

    client = bigquery.Client()
    load_to_bigquery()
    