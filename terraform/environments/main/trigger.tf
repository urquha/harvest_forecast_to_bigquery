resource "google_pubsub_topic" "cloud_function_trigger_five_min" {
  name = "harvest-forecast-trigger-5min"
}

resource "google_pubsub_topic" "cloud_function_trigger_daily" {
  name = "harvest-forecast-trigger-daily"
}

resource "google_cloud_scheduler_job" "five_min" {
  name        = "30-min-trigger"
  description = "Scheduled 5 min to trigger cloud function which getting the data from forecast and uploading to bigquery"
  schedule    = "*/30 * * * *"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.cloud_function_trigger_five_min.id
    data       = base64encode("5min")
  }
}

resource "google_cloud_scheduler_job" "daily" {
  name        = "daily-trigger"
  description = "Scheduled daily to trigger cloud function which getting the data from forecast and uploading to bigquery"
  schedule    = "0 5 * * *"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.cloud_function_trigger_daily.id
    data       = base64encode("daily")
  }
}