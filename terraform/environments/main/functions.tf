resource "google_project_iam_binding" "job_user" {
  project = var.project
  role       = "roles/bigquery.jobUser"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

resource "google_project_iam_binding" "data_editor" {
  project = var.project
  role       = "roles/bigquery.dataEditor"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "forecast_assignments_to_bigquery_update" {
    type        = "zip"
    source_dir  = "../../../cloud_functions/forecast_assignments_update"
    output_path = "/tmp/forecast_assignments_to_bigquery_update.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "forecast_assignments_to_bigquery_update" {
    source       = data.archive_file.forecast_assignments_to_bigquery_update.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "cloud_function-${data.archive_file.forecast_assignments_to_bigquery_update.output_md5}.zip"
    bucket       = data.google_storage_bucket.function_bucket.name

    # # Dependencies are automatically inferred so these lines can be deleted
    # depends_on   = [
    #     google_storage_bucket.function_bucket,  # declared in `storage.tf`
    #     data.forecast_assignments_to_bigquery.source
    # ]
}

resource "google_cloudfunctions_function" "forecast_assignments_to_bigquery_update" {
    name                  = "forecast-assignments-to-bigquery-update"
    runtime               = "python37"  # of course changeable
    available_memory_mb   = 1024
    timeout               = 540
    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = data.google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.forecast_assignments_to_bigquery_update.name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "forecast_assignments_to_bigquery_update"

    event_trigger {
        event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
        resource   = google_pubsub_topic.cloud_function_trigger_five_min.id
    }
    
    environment_variables = {
      "DATASET_ID" = google_bigquery_dataset.forecast.dataset_id
      "TABLE_NAME" = google_bigquery_table.assignments.table_id
    }

    secret_environment_variables {
        key = "FORECAST_ACCOUNT_ID"
        secret = "FORECAST_ACCOUNT_ID"
        version = "latest" 
    }

    secret_environment_variables {
        key = "FORECAST_ACCESS_TOKEN"
        secret = "FORECAST_ACCESS_TOKEN"
        version = "latest" 
    }

    secret_environment_variables {
        key = "BOB_ACCESS_TOKEN"
        secret = "BOB_ACCESS_TOKEN"
        version = "latest" 
    }
}

# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "forecast_sheets" {
    type        = "zip"
    source_dir  = "../../../cloud_functions/forecast_sheets"
    output_path = "/tmp/forecast_sheets.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "forecast_sheets" {
    source       = data.archive_file.forecast_sheets.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "cloud_function-${data.archive_file.forecast_sheets.output_md5}.zip"
    bucket       = data.google_storage_bucket.function_bucket.name
}

resource "google_cloudfunctions_function" "forecast_sheets" {
    name                  = "utilisation-names-teams-capacity"
    runtime               = "python37"  # of course changeable
    timeout               = 540
    available_memory_mb   = 1024

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = data.google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.forecast_sheets.name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "main"
    
    event_trigger {
        event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
        resource   = google_pubsub_topic.cloud_function_trigger_five_min.id
    }
    
    environment_variables = {
      "DATASET_ID" = google_bigquery_dataset.forecast.dataset_id
      "TABLE_NAME" = google_bigquery_table.person.table_id
      "TABLE_LOCATION" = google_bigquery_table.person.location
    }

    secret_environment_variables {
        key = "FORECAST_ACCOUNT_ID"
        secret = "FORECAST_ACCOUNT_ID"
        version = "latest" 
    }

    secret_environment_variables {
        key = "FORECAST_ACCESS_TOKEN"
        secret = "FORECAST_ACCESS_TOKEN"
        version = "latest" 
    }

}

