import os
import json
import pandas as pd
from google.cloud import bigquery
import httpx
import asyncio
import time
from datetime import datetime, timedelta

COLUMNS_TO_DROP = ['timer_started_at', 'started_time', 'ended_time', 'cost_rate', 'invoice', 'external_reference', 'user_assignment_budget', 'task_assignment_hourly_rate', 'task_assignment_budget']

def load_config() -> dict:
    return {
        'table_name': os.environ.get('TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        'location': os.environ.get('TABLE_LOCATION'),
        'headers': {
            "User-Agent": "Harvest Data Visualisation",
            "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
            "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
        }
    }

def harvest_to_bigquery_update(data: dict, context:dict=None):
    config = load_config()
    increment = 20
    start_timestamp = (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d')
    end_timestamp = (datetime.now() + timedelta(days=28)).strftime('%Y-%m-%d')

    total_no_pages = json.loads(httpx.get(url=f"https://api.harvestapp.com/v2/time_entries?page=1&from={start_timestamp}&to={end_timestamp}&per_page=2000&ref=next", headers=config['headers'])._content)['total_pages']

    print(f"Pages: {total_no_pages}")
    
    page_no = increment
    times = []

    while page_no <= total_no_pages + increment:
        urls = list(map(lambda page_no: f"https://api.harvestapp.com/v2/time_entries?page={page_no}&from={start_timestamp}&to={end_timestamp}&per_page=2000&ref=next", range(1 + page_no - increment, page_no + 1)))
        print(f"Getting pages {page_no - increment}-{page_no}", urls[0])
        responses = asyncio.run(get_and_unnest_time_entries(config, urls))
        
        times += [item for page in responses for item in page]
        if page_no < total_no_pages:
            time.sleep(4)
        page_no += increment
    
    df_times = pd.DataFrame(times).drop(COLUMNS_TO_DROP, axis=1)

    client = bigquery.Client(location=config['location'])

    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job_config.autodetect = True

    print("Attempting to load rows into bigquery")

    job = client.load_table_from_dataframe(
        df_times, table_ref, job_config=job_config
    )
    job.result()

    print("Loaded {} rows into {}:{}.".format(job.output_rows, config['dataset_id'], config['table_name']))



async def get_and_unnest_time_entries(config: dict, url_list: list) -> list:
    client = httpx.AsyncClient()
    tasks = (client.get(url, headers=config['headers'], timeout=httpx.Timeout(10.0, read=None)) for url in url_list)
    responses = await asyncio.gather(*tasks)
    await client.aclose()    

    for index, response in enumerate(responses):
        if response.status_code != 200:
            print(index, response)

    responses = [unnest_json(json.loads(response.text).get('time_entries')) for response in responses]
    print(len(responses))
    
    return responses

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
    harvest_to_bigquery_update({})