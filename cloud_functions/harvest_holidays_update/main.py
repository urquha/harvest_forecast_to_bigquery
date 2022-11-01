import os
import httpx
import json
from datetime import datetime, timedelta
import pandas as pd
import copy

# COLUMNS_TO_DROP = ['task_assignment_is_active', 'client_id', 'client_name', 'client_currency', 'project_code', 'timer_started_at', 'started_time', 'ended_time', 'cost_rate', 'invoice', 'external_reference', 'user_assignment_budget', 'task_assignment_hourly_rate', 'task_assignment_budget', 'user_assignment_is_active', 'user_assignment_use_default_rates', 'user_assignment_is_project_manager' ]
HOLIDAY_PROJECT_ID = 10050261
HOLIDAY_TASK_ID = 3707316
COLUMN_NAMES = {0: 'Name', 1: 'Date', 2: 'Hours'}
names = ['Olga Wilczynska-Dix', 'Mark West', 'Phil Aiston',
       'Joanna MacDonald', 'Kate Redfern',
       'Jorge De Los Santos Rodriguez', 'Charlotte Turner',
       'Gwenda Evans', 'Cedric Hillion', 'Paul Moloney', 'Zoë Bierman',
       'Lisa Webster', 'Timea Wilson', 'Keith Symonds', 'Ryan Hodges',
       'Matthew Gibbs', 'Neil Clark', 'Matt Brooks', 'Matt Lambert',
       'Chris Williams', 'Caitlin Calhoon', 'Zoë Herman', 'Lou Lai',
       'Arran Bell', 'Yaz El-Amery', 'Dee Owusu', 'Joanne Ralfe',
       'Yinuo Meng', 'Louise Lovejoy', 'James South', 'Orall Cornelius',
       'Alice Lambe', 'Madan Limbu', 'Dan James', 'Richard Burley',
       'Rob Forster', 'Kevin Voong', 'Colin McTaggart', 'Reshma Pancholi',
       'Nicole Ferger', 'Rachael Sutherland', 'Ella Durkin', 'Emma Boden',
       'Cherie Chambers', 'Nilou Darvish', 'Emily Hazlehurst',
       'Jasmine Williamson-Persh', 'Nishma Patel', 'Elys Sargunar',
       'Giulia Favaro', 'Mikey Roche', 'Kimberley Ward', 'Dave Evans',
       'Simon Wakeman', 'Vicky Stewart', 'Chidinma Aroyewun',
       'Roxana Florea', 'Ben Dye', 'Holly Hall Hare-Scott',
       'Frankie Naylor-Knight', 'Liberty Howard', 'Sean Holden',
       'Vyom Pathrolia', 'Luke Holmes', 'Jim Bowes', 'Gem Reeve',
       'Alastair Moore', 'Andrew Dickens', 'Madeleine Williams',
       'Endre Soo', 'Gary Haines', 'Loren Hansi Momodu-Gordon',
       'Mark Keenan', 'Jamie Brown', 'Adi Harari', 'Neil McLeish',
       'Natasha Sagnier', 'Stephanie Harding', 'James Clegg',
       'Julia Murray', 'Gabi Mamon', 'Rohan Sootarsing', 'Nic Borda',
       'Vaughan Johnstone', 'Sian Alcock', 'Josh Davies', 'Lou Barton',
       'Amber Gregory', 'Harry Barnard', 'Katie Pickering',
       'Dominic Krone', 'Martijn van der Heijden', 'Niki Morrigan',
       'Natalie Volichenko', 'Gemma Fountain', 'Lee Mills', 'Imran Kazmi',
       'Jack Holding', 'Mariola Romero', 'Benjamin Dudiak-Fry',
       "Hélène O'Brien", 'Selva Manivasagam', 'Arjun Mahadevan',
       'Rosa Droogers', 'Neal Hendey', 'John Ennew', 'Ian Pearce',
       'Chris Holding', 'Ben Rangasamy', 'Fran Moran', 'Leanne Taylor',
       'Richard Howell', 'Angela Manaj', 'Beth Skinner', 'Chan Pankhania',
       'Magali Bourcy', 'Tony Gledhill', 'Natasha Addison',
       'Alasdair Kenny', 'Dave Iles', 'Emily Vuagniaux', 'Hannah Sibley',
       'Chris Lewis', 'Christopher Lever', 'Ollie Cook', 'Lana Videnova',
       'Carole Ancia', 'Joe Alick Luther', 'Henry Donald Lees',
       'Paul Peet', 'Claire Denning', 'Rowan Blackwood', 'Pete Cooper',
       'Havana Roskrow']
def load_config() -> dict:
    return {
        'table_name': os.environ.get('TABLE_NAME'),
        'dataset_id': os.environ.get('DATASET_ID'),
        'location': os.environ.get('TABLE_LOCATION'),
        'bob_headers': {
            "accept": "application/json",
            "Authorization": os.environ.get("BOB_ACCESS_TOKEN"),
        },
        'harvest_headers': {
            "User-Agent": "Harvest Data Visualisation",
            "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
            "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
        }
    }

def main(data: dict, context:dict=None):
    config = load_config()
    client = httpx.Client()

    start_timestamp = (datetime.now() - timedelta(days=56)).strftime('%Y-%m-%d')
    start_timestamp = datetime.now().strftime('%Y-%m-%d')
    end_timestamp = (datetime.now() + timedelta(days=100)).strftime('%Y-%m-%d')
    
    users_df = pd.DataFrame(json.loads(client.get(url=f"https://api.harvestapp.com/v2/users", headers=config['harvest_headers']).text)['users'])
    
    users_df['Full Name'] = users_df['first_name'] + " " + users_df['last_name']
    users_df = users_df[['first_name', 'last_name', 'Full Name', 'id']]
    
    bob_url = f"https://api.hibob.com/v1/timeoff/whosout?from={start_timestamp}&to={end_timestamp}&includeHourly=false&includePrivate=false"

    bob_holidays_df = expand_rows(pd.DataFrame(json.loads(client.get(bob_url, headers=config['bob_headers']).text)['outs']))
    import pytest
    pytest.set_trace()
    bob_holidays_df['Hours'] = bob_holidays_df.apply(lambda row: find_hours(row), axis=1)
    bob_holidays_df['user_id'] = bob_holidays_df.apply(lambda row: find_user(row, users_df), axis=1)
    
    bob_df = bob_holidays_df[['user_id', 'employeeDisplayName', 'startDate', 'Hours']].rename(columns={'employeeDisplayName': 'Name', 'startDate': 'Date'})
    # bob_df['Source'] = 'Bob'
    
    bob_set = bob_df.to_dict('records')
    # bob_set = [['Andy Urquhart', '2022-10-19', 8],['Andy Urquhart', '2022-10-20', 8],['Andy Urquhart', '2022-10-21', 8]]
    harvest_holidays_df = get_harvest_data(config, client, start_timestamp, end_timestamp)
    harvest_df = harvest_holidays_df[['user_id', 'user_name', 'spent_date', 'hours']].rename(columns={'user_name': 'Name', 'spent_date': 'Date', 'hours': 'Hours'})
    # harvest_df['Source'] = 'Harvest'
    harvest_set = harvest_df.to_dict('records')

    add_to_harvest = [holiday for holiday in bob_set if holiday not in harvest_set]
    # bob_to_harvest = bob_set - harvest_set
    pd.set_option('display.max_columns', None)
    for item in add_to_harvest:

        data = '{"user_id":' + "user_id" + ',"project_id":' + str(HOLIDAY_PROJECT_ID) + ',"task_id":' + str(HOLIDAY_TASK_ID) + ',"spent_date":"2022-10-14","hours":' + item[0] + '}'
        print(data)
    
def get_harvest_data(config: dict, client: httpx.Client, start_timestamp, end_timestamp):
    total_no_pages = json.loads(client.get(url=f"https://api.harvestapp.com/v2/time_entries?page=1&project_id={HOLIDAY_PROJECT_ID}&from={start_timestamp}&to={end_timestamp}&per_page=2000&ref=next", headers=config['harvest_headers']).text)['total_pages']
    
    print(f"Pages: {total_no_pages}")
    times = []

    for page_no in range(1, total_no_pages+1):
        print(f"Getting page {page_no}")
        times.extend(unnest_json(json.loads(client.get(url=f"https://api.harvestapp.com/v2/time_entries?project_id={HOLIDAY_PROJECT_ID}&page={1}&from={start_timestamp}&to={end_timestamp}&per_page=2000&ref=next", headers=config['harvest_headers']).text)['time_entries'])) 
    
    return pd.DataFrame(times)

def unnest_json(times: list) -> list:
    # This function flattens the json response, using key_value as the new key for each value
    for time in times:
        for key in list(time.keys()):
            if type(time[key]) == dict:
                for nested_key in time[key]:
                    time[f"{key}_{nested_key}"] = time[key][nested_key]
                del time[key]
    return times

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

def find_hours(row):
    if row['startPortion'] == "all_day" and row['endPortion'] == "all_day":
        return 8
    return 4

def find_user(row, users_df):
    results = users_df[users_df['Full Name'] == row['employeeDisplayName']]
    if len(results) == 1:
        return results.iloc[0]['id']
    else:
        return 0

if __name__ == "__main__":
    main({})