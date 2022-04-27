import forecast
from dotenv import load_dotenv
import os
import pytest
from data_response_key_lists import person_data_keys

load_dotenv()

def get_forecast_data():
    api = forecast.Api(
        account_id=os.environ.get("HARVEST_ACCOUNT_ID"), 
        auth_token=os.environ.get("HARVEST_ACCESS_TOKEN")
    )
         
    # projects = api.get_projects()
    # projects_json = get_json_data(projects)

    # people = api.get_people()
    # people_json = get_json_data(people)
    
    # clients = api.get_clients()
    # clients_json = get_json_data(clients)

    # milestones = api.get_milestones()
    # milestones_json = get_json_data(milestones)

    assignments = api.get_assignments(start_date="2022-04-06T14:40:50.925Z", end_date="2022-04-25T14:40:50.925Z", person_id=109200)
    assignments_json = get_json_data(assignments)

    return assignments_json



        
def get_json_data(response_list):
    json_return = {}
    for item in [response_list[0]]:
        json_return[item.id] = item._json_data
    return json_return


def print_list(lst: list):
    for item in lst:
        print(item)

if __name__ == "__main__":
    
    # This is the data we want to put into bigquery
    forecast_data = get_forecast_data()