# Forecast to Bigquery
A repo for TPXimpact to ingest forecast data in python and load into bigquery.

The project is all deployed with terraform from the terraform folder.

The diagram shows:
- External forecast api
- Python code which extracts, transforms and loads the data into big query
- Forecast account id and access token stored in secret manager 
- Trigger for cloud function, cloud scheduler will trigger a pub sub message to trigger the cloud function when specified
- Big query which houses all data
- Data studio which has a connection to bigquery and displays the data

![Screenshot 2022-06-15 at 14 11 05](https://user-images.githubusercontent.com/35800749/173835121-e392b3ce-4d12-42e1-940e-3b982cc1244a.png)

## Authentication
Make a [personal access token](https://id.getharvest.com/developers)


## Deployment
To deploy all the infra run the following command, filling in the environment variables with their respective values:

`TF_VAR_FORECAST_ACCOUNT_ID=<forecast_account_id> TF_VAR_FORECAST_ACCESS_TOKEN=<forecast_access_token terraform apply`


To destroy all the infra run the following command, filling in the environment variables with their respective values:

`TF_VAR_FORECAST_ACCOUNT_ID=<forecast_account_id> TF_VAR_FORECAST_ACCESS_TOKEN=<forecast_access_token terraform destroy`


## Testing
Currently the cloud function can be triggered from the testing tab in the gcp console.

Unit tests can be run by navigating to the cloud functions folder and running:

`pip install -r requirements.txt`

`pytest`
