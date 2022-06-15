# Forecast to Bigquery
A repo for TPXimpact to ingest forecast data in python and load into bigquery.

![Screenshot 2022-06-15 at 14 03 26](https://user-images.githubusercontent.com/35800749/173833593-7e4def50-07dc-424b-ada6-b623eb3dcf89.png)

## Authentication
Make a [personal access token](https://id.getharvest.com/developers)


## Deployment
To deploy all the infra run the following command, filling in the environment variables with their respective values:

`TF_VAR_FORECAST_ACCOUNT_ID=<forecast_account_id>\

TF_VAR_FORECAST_ACCESS_TOKEN=<forecast_access_token\

terraform apply`


To destroy all the infra run the following command, filling in the environment variables with their respective values:

`TF_VAR_FORECAST_ACCOUNT_ID=<forecast_account_id>\

TF_VAR_FORECAST_ACCESS_TOKEN=<forecast_access_token\

terraform destroy`


## Testing
Currently the cloud function can be triggered from the testing tab in the gcp console.!
