import forecast
import os
from datetime import datetime, timedelta
import pandas as pd
import copy

from google.cloud import bigquery

def get_assignments_data(api: forecast.Api, start_date: str, end_date: str) -> list:
    assignments = json_list(api.get_assignments(start_date, end_date))
    import pytest
    pytest.set_trace()
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

def forecast_assignments_to_bigquery_update(data: dict, context:dict=None):
    config = load_config()
    api = forecast.Api(
        account_id=config['account_id'], 
        auth_token=config['auth_token']
    )
    
    client = bigquery.Client(location=config['location'])
    
    df = get_assignments(api)
    write_to_bigquery(config, client, df)
    return "Finished"

def get_assignments(api: forecast.Api):
    # Dates have to be specified for assignments
    start_timestamp = (datetime.now() - timedelta(days=56)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "Z"
    end_timestamp = (datetime.now() + timedelta(days=100)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "Z"
    
    print(f"Getting assignments data from {start_timestamp} to {end_timestamp}")

    return expand_rows(pd.DataFrame(get_assignments_data(api, start_timestamp, end_timestamp))).drop(['placeholder_id'], axis=1)


def write_to_bigquery(config: dict, client: bigquery.Client, df: pd.DataFrame):
    print(f"Dataset id - {config['dataset_id']}")
    print(f"Table name - {config['table_name']}")

    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )
    job_config.autodetect = True

    job = client.load_table_from_dataframe(
        df, table_ref, job_config=job_config
    )
    job.result()
    print("Loaded {} rows into {}:{}.".format(job.output_rows, config['dataset_id'], config['table_name']))    

def expand_rows(df):
    # When an assignment is entered, it can be put in for a single day or multiple. 
    # For entries spanning across multiple days, this function converts to single day entries and returns the dataframe.
    rows_to_edit = df[df['start_date'] != df['end_date']]
    single_assignment_rows = df[df['start_date'] == df['end_date']]
    edited_rows = []
    for index, row in rows_to_edit.iterrows():        
        # get the times
        end_date = datetime.strptime(row['end_date'], '%Y-%m-%d')
        start_date = datetime.strptime(row['start_date'], '%Y-%m-%d')
        
        dates = get_dates(start_date, end_date)
        
        for date in dates:
            edited_rows.append(make_row(copy.copy(row), date))
    
    return pd.concat([single_assignment_rows, pd.DataFrame(edited_rows)])
    

def get_dates(start_date: datetime, end_date: datetime) -> list:
    date = copy.copy(start_date)
    dates_list = []
    while date <= end_date:
        if date.weekday() < 5:
            dates_list.append(date)
        date = date + timedelta(days=1)
    return dates_list

def make_row(row: pd.Series, date: datetime) -> pd.Series:
    string_date = datetime.strftime(date, '%Y-%m-%d')
    row['start_date'] = string_date
    row['end_date'] = string_date
    return row

if __name__ == "__main__":
    forecast_assignments_to_bigquery_update({})