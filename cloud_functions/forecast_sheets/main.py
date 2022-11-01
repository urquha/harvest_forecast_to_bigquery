from re import T
import forecast
import os
import pandas as pd
from google.cloud import bigquery

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
        'table_name': os.environ.get('TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        'location': os.environ.get('TABLE_LOCATION')
    }

def main(data: dict, context: dict=None):
    config = load_config()

    utilisation_roles_url = "https://docs.google.com/spreadsheets/d/1BiWTWY44F3QeRI4zge8JLu3c0mAQsUTcLVBVfpMBJrM/export?format=csv&usp=sharing"
    utilisation_roles = pd.read_csv(utilisation_roles_url)

    primary_roles_url = "https://docs.google.com/spreadsheets/d/1JZAS2RNo1q1URyzer9TINCfr5VKxD7egtoh167l3C0c/export?format=csv&usp=sharing"
    primary_roles = pd.read_csv(primary_roles_url)['Roles'].to_list()
    
    utilisation_data = get_utilisation_data()
    
    api = forecast.Api(
        account_id=config['account_id'], 
        auth_token=config['auth_token']
    )
    bq_client = bigquery.Client(location=config['location'])


    person_data = pd.DataFrame(get_person_data(api))
    person_data['Name'] = person_data['first_name'] + " " + person_data['last_name']
    person_data['primary_role'] = person_data.apply(lambda row:[(i) for i in row['roles'] if i in primary_roles] , axis=1)

    utilisation_roles['primary_role'] = utilisation_roles.apply(lambda row: get_roles(row, person_data), axis=1)

    utilisation_roles['capacity_1_week_hours'] = utilisation_roles.apply(lambda row: get_capacity(row, person_data), axis=1)
    utilisation_roles = utilisation_roles[utilisation_roles['capacity_1_week_hours'] != "Name probably not in forecast"]
    utilisation_roles['capacity_4_week_hours'] = utilisation_roles['capacity_1_week_hours'] * 4
    
    utilisation_roles['capacity_1_week_days'] = utilisation_roles['capacity_1_week_hours'] / 8
    utilisation_roles['capacity_4_week_days'] = utilisation_roles['capacity_4_week_hours'] / 8
    
    pd.set_option('display.max_rows', 10)
   
    write_to_bigquery(config, bq_client, utilisation_roles)
    
def get_roles(row: pd.Series, df):
    try:
        return df[df['Name']==row['Name']]['primary_role'].values[0][0]
    except:
        return "No Primary role"

def get_capacity(row: pd.Series, df: pd.DataFrame):
    try:
        return df[df['Name']==row['Name']]['weekly_capacity'].values[0] / 3600
    except:
        return "Name probably not in forecast"

def get_utilisation_data():
    utilisation_data_url = "https://docs.google.com/spreadsheets/d/1t_SaecjIY-Mj-s1k_X42K62dw32ekfdp-w6Wb2RnSYk/export?format=csv&usp=sharing&gid=452455101"
    utilisation_data = pd.read_csv(utilisation_data_url)
    filtered_utilisation_data = utilisation_data[utilisation_data['First name'].notnull()]
    
    filtered_utilisation_data.loc[:, 'Name'] = filtered_utilisation_data.loc[:, 'First name'] + " " + filtered_utilisation_data.loc[:, 'Surname']
    try:
        filtered_utilisation_data = filtered_utilisation_data.rename(columns={" Avail hrs ": "Avail hrs"})
    except Exception() as e:
        print(e)
    
    return filtered_utilisation_data[['Name', 'Team', 'Sept %', 'Sept hrs', 'Holiday','Sick', 'Non working day', 'Other', 'Avail hrs']]

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


if __name__ == "__main__":
    main({})