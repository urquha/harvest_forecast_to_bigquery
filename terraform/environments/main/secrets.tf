data "google_secret_manager_secret" "harvest_account_id" {
  secret_id = "HARVEST_ACCOUNT_ID"
  project = var.project
}

data "google_secret_manager_secret" "harvest_access_token" {
  secret_id = "HARVEST_ACCESS_TOKEN"
  project = var.project
}

data "google_secret_manager_secret" "bob_access_token" {
  secret_id = "BOB_ACCESS_TOKEN"
  project = var.project
}

data "google_secret_manager_secret" "forecast_account_id" {
  secret_id = "FORECAST_ACCOUNT_ID"
  project = var.project
}

data "google_secret_manager_secret" "forecast_access_token" {
  secret_id = "FORECAST_ACCESS_TOKEN"
  project = var.project
}