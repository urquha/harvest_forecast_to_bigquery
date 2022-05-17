import forecast
from dotenv import load_dotenv
import os
import json
import io

from google.cloud import bigquery


def get_assignments_data(api):
    assignments = json_list(api.get_assignments(start_date="2022-04-01T00:00:00.000Z", end_date="2022-05-01T00:00:00.000Z"))
    return [json.dumps(record) for record in assignments]

def get_clients_data(api):
    clients = json_list(api.get_clients())
    return [json.dumps(record) for record in clients]

def get_projects_data(api):
    projects = json_list(api.get_projects())
    return [json.dumps(record) for record in projects]

def json_list(response: list):
    # This function maps a response to a json list
    return list(map(lambda item: item._json_data, response)) 

def forecast_to_bigquery(response):
    load_dotenv()
    api = forecast.Api(
        account_id=os.environ.get("HARVEST_ACCOUNT_ID"), 
        auth_token=os.environ.get("HARVEST_ACCESS_TOKEN")
    )
    tables = {
        'assignments_data': get_assignments_data(api),
        'projects_data': get_clients_data(api), 
        'clients_data': get_projects_data(api)
    }
    dataset_id = 'forecast_001'

    client = bigquery.Client()
    response = {"code": 200, "result": []}
    for table_name, data in tables.items():
        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_name)
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.autodetect = True

        response['result'].append({'table_name': f"{len(data)} rows"})
        
        print("Attempting to load {} rows into {}:{}.".format(len(data), dataset_id, table_name))

        job = client.load_table_from_file(
            io.StringIO('\n'.join(data)), 
            table_ref,
            location="europe-west2", 
            job_config=job_config,
            )
        job.done()
    
    return response

    