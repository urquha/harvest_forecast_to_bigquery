import copy
import json
import os
from datetime import datetime, timedelta

import forecast
import httpx
import pandas as pd
from google.cloud import bigquery

BILLABLE_PROJECT_COLOURS = ["orange"]


def get_assignments_data(api: forecast.Api, start_date: str, end_date: str) -> list:
    assignments = json_list(api.get_assignments(start_date, end_date))
    return [record for record in assignments]


def get_clients_data(api: forecast.Api) -> list:
    clients = json_list(api.get_clients())
    return [record for record in clients]


def get_projects_data(api: forecast.Api) -> list:
    projects = json_list(api.get_projects())
    return [record for record in projects]


def get_person_data(api: forecast.Api) -> list:
    people = json_list(api.get_people())
    return [record for record in people]


def json_list(response: list) -> list:
    # This function maps a response to a json list
    return list(map(lambda item: item._json_data, response))


def load_config() -> dict:
    return {
        "account_id": os.environ.get("FORECAST_ACCOUNT_ID"),
        "auth_token": os.environ.get("FORECAST_ACCESS_TOKEN"),
        "table_name": os.environ.get("TABLE_NAME"),
        "dataset_id": os.environ.get("DATASET_ID"),
        "location": os.environ.get("TABLE_LOCATION"),
        "headers": {
            "accept": "application/json",
            "Authorization": os.environ.get("BOB_ACCESS_TOKEN"),
        },
    }


def find_hours(row):
    if row["startPortion"] == "all_day" and row["endPortion"] == "all_day":
        return 8
    return 4


def check_billable(row, billable_projects):
    if row["project_id"] in billable_projects:
        return True
    return False


def get_billable_codes(projects_df: pd.DataFrame) -> list:
    billable_projects = projects_df[projects_df["color"].isin(BILLABLE_PROJECT_COLOURS)]
    return billable_projects["id"].tolist()


# def get_project_client(projects_df: pd.DataFrame, clients_df: pd.DataFrame):


def forecast_assignments_to_bigquery_update(data: dict, context: dict = None):
    config = load_config()
    api = forecast.Api(account_id=config["account_id"], auth_token=config["auth_token"])
    httpx_client = httpx.Client()
    bq_client = bigquery.Client(location=config["location"])

    df = get_assignments(api)
    people_df = pd.DataFrame(get_person_data(api))
    people_df["full_name"] = people_df["first_name"] + " " + people_df["last_name"]
    projects_df = pd.DataFrame(get_projects_data(api))
    clients_df = pd.DataFrame(get_clients_data(api))

    billable_projects = get_billable_codes(projects_df)

    df["billable"] = df.apply(
        lambda row: check_billable(row, billable_projects), axis=1
    )

    holidays_df = get_holidays(config, httpx_client)

    final_df = pd.concat(
        [
            change_assignments_columns(
                df, people_df, projects_df, clients_df
            ).reset_index(drop=True),
            holidays_df.reset_index(drop=True),
        ]
    )

    write_to_bigquery(config, bq_client, final_df)
    return "Finished"


def change_holidays_columns(df):
    df["billable"] = False
    df["entry_type"] = "holiday"
    df["project_id"] = 509809

    return df.drop(
        [
            "policyTypeDisplayName",
            "policyType",
            "startPortion",
            "employeeId",
            "endPortion",
            "status",
        ],
        axis=1,
    ).rename(
        columns={
            "endDate": "end_date",
            "startDate": "start_date",
            "requestId": "id",
            "employeeDisplayName": "name",
        }
    )


def get_holidays(config: dict, client: httpx.Client):
    start_timestamp = (datetime.now() - timedelta(days=56)).strftime("%Y-%m-%d")
    end_timestamp = (datetime.now() + timedelta(days=100)).strftime("%Y-%m-%d")

    url = f"https://api.hibob.com/v1/timeoff/whosout?from={start_timestamp}&to={end_timestamp}&includeHourly=false&includePrivate=false"
    df = expand_holidays_rows(
        pd.DataFrame(
            json.loads(client.get(url, headers=config["headers"]).text)["outs"]
        )
    )

    df["holiday_hours"] = df.apply(lambda row: find_hours(row), axis=1)
    df["holiday_days"] = df["holiday_hours"] / 8
    df["allocation_hours"] = 0
    df["allocation_days"] = 0
    return change_holidays_columns(df)


def expand_holidays_rows(df):
    # When an assignment is entered, it can be put in for a single day or multiple.
    # For entries spanning across multiple days, this function converts to single day entries and returns the dataframe.
    rows_to_edit = df[df["startDate"] != df["endDate"]]
    single_assignment_rows = df[df["startDate"] == df["endDate"]]
    edited_rows = []

    for index, row in rows_to_edit.iterrows():
        # get the times
        end_date = datetime.strptime(row["endDate"], "%Y-%m-%d")
        start_date = datetime.strptime(row["startDate"], "%Y-%m-%d")

        dates = get_dates(start_date, end_date)

        first_row = copy.copy(row)
        if len(dates) > 1:
            first_row["endPortion"] = "all_day"
            middle_rows = copy.copy(row)
            middle_rows["startPortion"] = "all_day"
            middle_rows["endPortion"] = "all_day"
            for date in dates[1:-1]:
                edited_rows.append(make_holiday_row(copy.copy(middle_rows), date))
            last_row = copy.copy(row)
            last_row["startPortion"] = "all_day"
            edited_rows.append(make_holiday_row(copy.copy(last_row), dates[-1]))
        edited_rows.append(make_holiday_row(first_row, dates[0]))

    return pd.concat([single_assignment_rows, pd.DataFrame(edited_rows)])


def get_name(row, df):
    r = df[df["id"] == row["person_id"]]
    if len(r) > 0:
        return r.iloc[0]["full_name"]
    return None


def get_project_name(row, df):
    r = df[df["id"] == row["project_id"]]
    if len(r) > 0:
        return r.iloc[0]["name"]


def get_project_colour(row, df):
    r = df[df["id"] == row["project_id"]]
    if len(r) > 0:
        return r.iloc[0]["color"]


def get_client_name(row, df):
    r = df[df["id"] == row["client_id"]]
    if len(r) > 0:
        return r.iloc[0]["name"]


def change_assignments_columns(
    df: pd.DataFrame,
    people_df: pd.DataFrame,
    projects_df: pd.DataFrame,
    clients_df: pd.DataFrame,
) -> pd.DataFrame:
    df["name"] = df.apply(lambda row: get_name(row, people_df), axis=1)
    df["project"] = df.apply(lambda row: get_project_name(row, projects_df), axis=1)
    df["project_colour"] = df.apply(
        lambda row: get_project_colour(row, projects_df), axis=1
    )
    df["client"] = projects_df.apply(
        lambda row: get_client_name(row, clients_df), axis=1
    )
    df["allocation_hours"] = df["allocation"] / 3600
    df["allocation_days"] = df["allocation_hours"] / 8
    df["holiday_hours"] = 0
    df["holiday_days"] = 0
    df["entry_type"] = "time_forecast"
    return df.drop(
        [
            "notes",
            "updated_at",
            "updated_by_id",
            "person_id",
            "repeated_assignment_set_id",
            "active_on_days_off",
            "allocation",
        ],
        axis=1,
    )


def get_assignments(api: forecast.Api):
    # Dates have to be specified for assignments
    start_timestamp = (datetime.now() - timedelta(days=56)).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3] + "Z"
    end_timestamp = (datetime.now() + timedelta(days=100)).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3] + "Z"

    print(f"Getting assignments data from {start_timestamp} to {end_timestamp}")

    return expand_assignments_rows(
        pd.DataFrame(get_assignments_data(api, start_timestamp, end_timestamp))
    ).drop(["placeholder_id"], axis=1)


def write_to_bigquery(config: dict, client: bigquery.Client, df: pd.DataFrame):
    print(f"Dataset id - {config['dataset_id']}")
    print(f"Table name - {config['table_name']}")

    dataset_ref = client.dataset(config["dataset_id"])
    table_ref = dataset_ref.table(config["table_name"])
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job_config.autodetect = True

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(
        "Loaded {} rows into {}:{}.".format(
            job.output_rows, config["dataset_id"], config["table_name"]
        )
    )


def expand_assignments_rows(df):
    # When an assignment is entered, it can be put in for a single day or multiple.
    # For entries spanning across multiple days, this function converts to single day entries and returns the dataframe.
    rows_to_edit = df[df["start_date"] != df["end_date"]]
    single_assignment_rows = df[df["start_date"] == df["end_date"]]
    edited_rows = []
    for index, row in rows_to_edit.iterrows():
        # get the times
        end_date = datetime.strptime(row["end_date"], "%Y-%m-%d")
        start_date = datetime.strptime(row["start_date"], "%Y-%m-%d")

        dates = get_dates(start_date, end_date)

        for date in dates:
            edited_rows.append(make_assignments_row(copy.copy(row), date))

    return pd.concat([single_assignment_rows, pd.DataFrame(edited_rows)])


def get_dates(start_date: datetime, end_date: datetime) -> list:
    date = copy.copy(start_date)
    dates_list = []
    while date <= end_date:
        if date.weekday() < 5:
            dates_list.append(date)
        date = date + timedelta(days=1)
    return dates_list


def make_holiday_row(row: pd.Series, date: datetime) -> pd.Series:
    string_date = datetime.strftime(date, "%Y-%m-%d")
    row["startDate"] = string_date
    row["endDate"] = string_date
    return row


def make_assignments_row(row: pd.Series, date: datetime) -> pd.Series:
    string_date = datetime.strftime(date, "%Y-%m-%d")
    row["start_date"] = string_date
    row["end_date"] = string_date
    return row


if __name__ == "__main__":
    forecast_assignments_to_bigquery_update({})
