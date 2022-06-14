resource "google_pubsub_topic" "cloud_function_trigger" {
  name = "forecast-daily-trigger"
}

# resource "google_cloud_scheduler_job" "job" {
#   name        = "forecast-daily-trigger"
#   description = "Scheduled daily to trigger cloud function which getting the data from forecast and uploading to bigquery"
#   schedule    = "*/5 * * * *"

#   pubsub_target {
#     # topic.id is the topic's full resource name.
#     topic_name = google_pubsub_topic.cloud_function_trigger.id
#     data       = base64encode("test")
#   }
# }