import pytest

plugins = ["pytest-bigquery-mock"]


@pytest.fixture
def mock_config():
    return {
        "account_id": "account_id",
        "auth_token": "auth_token",
        "table_name": "assignments_table",
        "dataset_id": "dataset_id",
        "location": "table_location",
    }


@pytest.fixture
def mock_assignments_response():
    return [
        {
            "id": 1,
            "start_date": "2022-08-11",
            "end_date": "2022-08-11",
            "allocation": 14400,
            "notes": None,
            "updated_at": "2020-12-02T12:38:58.902Z",
            "updated_by_id": 1,
            "project_id": 1,
            "person_id": 1,
            "placeholder_id": None,
            "repeated_assignment_set_id": 4,
            "active_on_days_off": False,
        },
        {
            "id": 2,
            "start_date": "2022-08-18",
            "end_date": "2022-08-18",
            "allocation": 14400,
            "notes": None,
            "updated_at": "2020-12-02T12:38:58.914Z",
            "updated_by_id": 2,
            "project_id": 2,
            "person_id": 2,
            "placeholder_id": None,
            "repeated_assignment_set_id": 4,
            "active_on_days_off": False,
        },
        {
            "id": 3,
            "start_date": "2022-08-12",
            "end_date": "2022-08-19",
            "allocation": 14400,
            "notes": None,
            "updated_at": "2020-12-02T12:38:58.914Z",
            "updated_by_id": 3,
            "project_id": 3,
            "person_id": 3,
            "placeholder_id": None,
            "repeated_assignment_set_id": 4,
            "active_on_days_off": False,
        },
    ]


@pytest.fixture
def mock_expand_rows_response():
    return [
        [
            1,
            "2022-08-11",
            "2022-08-11",
            14400,
            None,
            "2020-12-02T12:38:58.902Z",
            1,
            1,
            1,
            None,
            4,
            False,
        ],
        [
            3,
            "2022-08-12",
            "2022-08-12",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            3,
            3,
            3,
            None,
            4,
            False,
        ],
        [
            3,
            "2022-08-15",
            "2022-08-15",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            3,
            3,
            3,
            None,
            4,
            False,
        ],
        [
            3,
            "2022-08-16",
            "2022-08-16",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            3,
            3,
            3,
            None,
            4,
            False,
        ],
        [
            3,
            "2022-08-17",
            "2022-08-17",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            3,
            3,
            3,
            None,
            4,
            False,
        ],
        [
            2,
            "2022-08-18",
            "2022-08-18",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            2,
            2,
            2,
            None,
            4,
            False,
        ],
        [
            3,
            "2022-08-18",
            "2022-08-18",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            3,
            3,
            3,
            None,
            4,
            False,
        ],
        [
            3,
            "2022-08-19",
            "2022-08-19",
            14400,
            None,
            "2020-12-02T12:38:58.914Z",
            3,
            3,
            3,
            None,
            4,
            False,
        ],
    ]


@pytest.fixture
def mock_projects_data():
    return [{"id": 1, "color": "orange"}, {"id": 2, "color": "blue"}]
