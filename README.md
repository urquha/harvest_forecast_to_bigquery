# Forecast to Bigquery
A repo for TPXimpact to ingest forecast data in python and load into bigquery.

This repo uses [poetry](https://python-poetry.org/) to manage dependencies.

`poetry install`
`poetry run python main.py`

## Authentication
Make a [personal access token](https://id.getharvest.com/developers) and have the following filled in in your .env file: 

FORECAST_ACCESS_TOKEN=<FORECAST_ACCESS_TOKEN>

FORECAST_ACCOUNT_ID=<FORECAST_ACCOUNT_ID>
