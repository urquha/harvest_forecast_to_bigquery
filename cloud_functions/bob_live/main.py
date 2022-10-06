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

def bob_to_bigquery(data: dict, context: dict=None):
    config = load_config()
    client = httpx.Client()

    start_timestamp = (datetime.now() - timedelta(days=56)).strftime('%Y-%m-%d')
    end_timestamp = (datetime.now() + timedelta(days=100)).strftime('%Y-%m-%d')
        

    url = f"https://api.hibob.com/v1/timeoff/whosout?from={start_timestamp}&to={end_timestamp}&includeHourly=false&includePrivate=false"

    holidays_df = expand_rows(pd.DataFrame(json.loads(client.get(url, headers=config['headers']).text)['outs']))
    # import pytest
    # pytest.set_trace()
    # holidays_df['hours'] = holidays_df['']

    client = bigquery.Client(location=config['location'])
    dataset_ref = client.dataset(config['dataset_id'])
    table_ref = dataset_ref.table(config['table_name'])
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job_config.autodetect = True

    job = client.load_table_from_dataframe(
        holidays_df, table_ref, job_config=job_config
    )
    job.result()

    print("Loaded {} rows into {}:{}.".format(job.output_rows, config['dataset_id'], config['table_name'])) 

def expand_rows(df):
    # When an assignment is entered, it can be put in for a single day or multiple. 
    # For entries spanning across multiple days, this function converts to single day entries and returns the dataframe.
    
    rows_to_edit = []
    single_assignment_rows = []
    for index, row in df.iterrows():
        if row['startDate'] != row['endDate']:
            rows_to_edit.append(row)
        else:
            single_assignment_rows.append(row)
    
    for row in rows_to_edit:
        end_date = datetime.strptime(row['endDate'], '%Y-%m-%d')
        start_date = datetime.strptime(row['startDate'], '%Y-%m-%d')
        date = start_date
        import pytest
        pytest.set_trace()
        
        while date <= end_date:
            if date.weekday() > 4:
                date = date + timedelta(days=(7 - date.weekday()))
            string_date = datetime.strftime(date, '%Y-%m-%d')
            row['startDate'] = string_date
            row['endDate'] = string_date
            single_assignment_rows.append(copy.copy(row))
            date = date + timedelta(days=1)

    return pd.DataFrame(single_assignment_rows)

if __name__ == "__main__":
    bob_to_bigquery({})