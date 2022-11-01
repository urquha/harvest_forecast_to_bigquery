import os
import httpx
import json
from datetime import datetime, timedelta
import pandas as pd
import copy

from google.cloud import bigquery

def load_config() -> dict:
    return {
        'table_name': os.environ.get('TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        'location': os.environ.get('TABLE_LOCATION'),
        'headers': {
            "accept": "application/json",
            "Authorization": os.environ.get("BOB_ACCESS_TOKEN"),
        }
    }

def find_hours(row):
    if row['startPortion'] == "all_day" and row['endPortion'] == "all_day":
        return 8
    return 4

def bob_to_bigquery(data: dict, context: dict=None):
    config = load_config()
    client = httpx.Client()

    start_timestamp = (datetime.now() - timedelta(days=56)).strftime('%Y-%m-%d')
    end_timestamp = (datetime.now() + timedelta(days=100)).strftime('%Y-%m-%d')
    
    url = f"https://api.hibob.com/v1/timeoff/whosout?from={start_timestamp}&to={end_timestamp}&includeHourly=false&includePrivate=false"

    holidays_df = expand_rows(pd.DataFrame(json.loads(client.get(url, headers=config['headers']).text)['outs']))
    
    holidays_df['hours'] = holidays_df.apply(lambda row: find_hours(row), axis=1)

    df = change_columns(holidays_df)

    client = bigquery.Client(location=config['location'])
    write_to_bigquery(config, client, df)

def change_columns(df):
    df['billable'] = False
    df['entry_type'] = 'holiday'
    df['project_id'] = 509809
    return df.drop(['policyTypeDisplayName', 'policyType',
       'startPortion', 'employeeId', 'endPortion',
       'type',  'status', 
    ], axis=1).rename(columns={'endDate': 'end_date', 'startDate': 'start_date', 'requestId': 'id'})

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
    rows_to_edit = df[df['startDate'] != df['endDate']]
    single_assignment_rows = df[df['startDate'] == df['endDate']]
    edited_rows = []

    for index, row in rows_to_edit.iterrows():        
        # get the times
        end_date = datetime.strptime(row['endDate'], '%Y-%m-%d')
        start_date = datetime.strptime(row['startDate'], '%Y-%m-%d')
        
        dates = get_dates(start_date, end_date)
        
        first_row = copy.copy(row)
        if len(dates) > 1:
            first_row['endPortion'] = 'all_day'
            middle_rows = copy.copy(row)
            middle_rows['startPortion'] = 'all_day'
            middle_rows['endPortion'] = 'all_day'
            for date in dates[1:-1]:
                edited_rows.append(make_row(copy.copy(middle_rows), date))
            last_row = copy.copy(row)
            last_row['startPortion'] = 'all_day'
            edited_rows.append(make_row(copy.copy(last_row), dates[-1]))
        edited_rows.append(make_row(first_row, dates[0]))
    
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
    row['startDate'] = string_date
    row['endDate'] = string_date
    return row

if __name__ == "__main__":
    bob_to_bigquery({})