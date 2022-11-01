import os
import httpx

HOLIDAY_PROJECT_ID = "10050261"
HOLIDAY_TASK_ID = "3707316"

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
            "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID"),
            "Content-Type": "application/json"
        }
    }

def main():
    config = load_config()
    data = '{"user_id":4169516,"project_id":' + HOLIDAY_PROJECT_ID + ',"task_id":' + HOLIDAY_TASK_ID + ',"spent_date":"2022-10-14","hours":1.0}'
    print(data)
    response = httpx.post('https://api.harvestapp.com/v2/time_entries', headers=config['harvest_headers'], data=data)
    import pytest
    pytest.set_trace()
    print(response)
if __name__ == "__main__":
    main()