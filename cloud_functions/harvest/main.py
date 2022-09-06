import os
import json
import urllib.request
import pandas as pd
from google.cloud import bigquery

COLUMNS_TO_DROP = ['timer_started_at', 'started_time', 'ended_time', 'cost_rate', 'invoice', 'external_reference', 'user_assignment_budget', 'task_assignment_hourly_rate', 'task_assignment_budget']

def load_config() -> dict:
    return {
        'account_id': os.environ.get("HARVEST_ACCOUNT_ID"),
        'table_name': os.environ.get('TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        "authorisation_token": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
        'location': os.environ.get('TABLE_LOCATION')
    }

def harvest_to_bigquery(data: dict, context:dict=None):
    config = load_config()


    url = "https://api.harvestapp.com/v2/time_entries"
    headers = {
        "User-Agent": "Harvest API Example",
        "Authorization": config['authorisation_token'],
        "Harvest-Account-ID": config['account_id']
    }
    request = urllib.request.Request(url=url, headers=headers)
    
    response = urllib.request.urlopen(request, timeout=5)
    responseBody = response.read().decode("utf-8")
    jsonResponse = json.loads(responseBody)

    times = unnest_json(jsonResponse['time_entries'])
    page_no = 2

    while jsonResponse['links'].get('next') != None:
        url = f"https://api.harvestapp.com/v2/time_entries?page={page_no}&per_page=100&ref=next"
        headers = {
            "User-Agent": "Harvest API Example",
            "Authorization": config['authorisation_token'],
            "Harvest-Account-ID": config['account_id']
        }
        request = urllib.request.Request(url=url, headers=headers)
        
        response = urllib.request.urlopen(request, timeout=5)
        responseBody = response.read().decode("utf-8")
        jsonResponse = json.loads(responseBody)
        times += unnest_json(jsonResponse['time_entries'])

        page_no += 1
    
    df_times = pd.DataFrame(times).drop(COLUMNS_TO_DROP, axis=1)
    client = bigquery.Client(location=config['location'])

    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job_config.autodetect = True

    job = client.load_table_from_dataframe(
        df_times, table_ref, job_config=job_config
    )
    job.result()

    print("Loaded {} rows into {}:{}.".format(job.output_rows, config['dataset_id'], config['table_name']))
    

def unnest_json(times: list) -> list:
    # This function flattens the json response, using key_value as the new key for each value
    for time in times:
        for key in list(time.keys()):
            if type(time[key]) == dict:
                for nested_key in time[key]:
                    time[f"{key}_{nested_key}"] = time[key][nested_key]
                del time[key]
    return times

if __name__ == "__main__":
    harvest_to_bigquery({})