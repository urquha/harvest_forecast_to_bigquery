# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "forecast_to_bigquery" {
    type        = "zip"
    source_dir  = "../cloud_functions/forecast"
    output_path = "/tmp/forecast_to_bigquery.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "forecast_to_bigquery" {
    source       = data.archive_file.forecast_to_bigquery.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "cloud_function-${data.archive_file.forecast_to_bigquery.output_md5}.zip"
    bucket       = google_storage_bucket.function_bucket.name

    # # Dependencies are automatically inferred so these lines can be deleted
    # depends_on   = [
    #     google_storage_bucket.function_bucket,  # declared in `storage.tf`
    #     data.forecast_to_bigquery.source
    # ]
}

# Create the Cloud function triggered by a `Finalize` event on the bucket
resource "google_cloudfunctions_function" "forecast_to_bigquery" {
    name                  = "forecast-to-bigquery"
    runtime               = "python37"  # of course changeable
    available_memory_mb   = 512
    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.forecast_to_bigquery.name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "forecast_to_bigquery"
    
    # event_trigger {
    #     event_type = "google.storage.object.finalize"
    #     resource   = "${var.project}-input"
    # }

    event_trigger {
        event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
        resource   = google_pubsub_topic.cloud_function_trigger.id
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

    # # Dependencies are automatically inferred so these lines can be deleted
    # depends_on = [
    #     google_secret_manager_secret_version.forecast_account_id,
    #     google_secret_manager_secret_version.forecast_access_token
        # google_storage_bucket.function_bucket,  # declared in `storage.tf`
        # google_storage_bucket_object.zip
    # ]
}


# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "harvest_to_bigquery" {
    type        = "zip"
    source_dir  = "../cloud_functions/harvest"
    output_path = "/tmp/harvest_to_bigquery.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "harvest_to_bigquery" {
    source       = data.archive_file.harvest_to_bigquery.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "cloud_function-${data.archive_file.harvest_to_bigquery.output_md5}.zip"
    bucket       = google_storage_bucket.function_bucket.name
}

# Create the Cloud function triggered by a `Finalize` event on the bucket
resource "google_cloudfunctions_function" "harvest_to_bigquery" {
    name                  = "harvest-to-bigquery"
    runtime               = "python37"  # of course changeable

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.harvest_to_bigquery.name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "harvest_to_bigquery"
    
    trigger_http = true

    # event_trigger {
    #     event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    #     resource   = google_pubsub_topic.cloud_function_trigger.id
    # }
    
    environment_variables = {
      "DATASET_ID" = google_bigquery_dataset.harvest.dataset_id
      "TABLE_NAME" = google_bigquery_table.harvest.table_id
      "PROJECTS_TABLE_NAME" = google_bigquery_table.projects.table_id
      "TABLE_LOCATION" = google_bigquery_table.harvest.location
    }

    secret_environment_variables {
        key = "HARVEST_ACCOUNT_ID"
        secret = "HARVEST_ACCOUNT_ID"
        version = "latest" 
    }

    secret_environment_variables {
        key = "HARVEST_ACCESS_TOKEN"
        secret = "HARVEST_ACCESS_TOKEN"
        version = "latest" 
    }
}