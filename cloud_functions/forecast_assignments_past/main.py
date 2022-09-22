import forecast
import os
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import copy
import sys 

from google.cloud import bigquery

def get_assignments_data(api: forecast.Api, start_date: str, end_date: str) -> list:
    assignments = json_list(api.get_assignments(start_date, end_date))
    return [record for record in assignments]

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


def forecast_assignments_to_bigquery_past(data: dict, context:dict=None):

    config = load_config()

    print(f"Dataset id - {config['dataset_id']}")

    # Dates have to be specified for assignments
    start_timestamp = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "Z"
    end_timestamp = (datetime.now() + timedelta(days=0)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "Z"
    

    api = forecast.Api(
        account_id=config['account_id'], 
        auth_token=config['auth_token']
    )

    print(f"Getting assignments data from {start_timestamp} to {end_timestamp}")
    assignments_data_df = expand_rows(pd.DataFrame(get_assignments_data(api, start_timestamp, end_timestamp)).drop(['placeholder_id'], axis=1))
    
    client = bigquery.Client(location=config['location'])
    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job_config.autodetect = True

    job = client.load_table_from_dataframe(
        assignments_data_df, table_ref, job_config=job_config
    )
    job.result()

    print("Loaded {} rows into {}:{}.".format(job.output_rows, config['dataset_id'], config['table_name']))    

def expand_rows(df):
    # When an assignment is entered, it can be put in for a single day or multiple. 
    # For entries spanning across multiple days, this function converts to single day entries and returns the dataframe.
    rows_to_edit = []
    single_assignment_rows = []
    for index, row in df.iterrows():
        if row['start_date'] != row['end_date']:
            rows_to_edit.append(row)
        else:
            single_assignment_rows.append(row)

    for row in rows_to_edit:
        end_date = datetime.strptime(row['end_date'], '%Y-%m-%d')
        start_date = datetime.strptime(row['start_date'], '%Y-%m-%d')
        date = start_date

        while date <= end_date:
            if date.weekday() > 4:
                date = date + timedelta(days=(7 - date.weekday()))
            string_date = datetime.strftime(date, '%Y-%m-%d')
            row['start_date'] = string_date
            row['end_date'] = string_date
            single_assignment_rows.append(copy.copy(row))
            date = date + timedelta(days=1)

    return pd.DataFrame(single_assignment_rows)

if __name__ == "__main__":
    forecast_assignments_to_bigquery_past({}, {})