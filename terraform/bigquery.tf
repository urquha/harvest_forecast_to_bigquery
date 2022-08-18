resource "google_bigquery_dataset" "forecast" {
  dataset_id                  = "Forecast"
  description                 = "Dataset for forecast tables to be used by datastudio"
  location                    = "EU"

  labels = {
    env = var.env
  }
}


resource "google_bigquery_table" "assignments" {
  dataset_id = google_bigquery_dataset.forecast.dataset_id
  table_id   = "assignments"

  time_partitioning {
    type = "DAY"
  }

  labels = {
    env = var.env
  }

  deletion_protection = false
}

resource "google_bigquery_table" "projects" {
  dataset_id = google_bigquery_dataset.forecast.dataset_id
  table_id   = "projects"

  labels = {
    env = var.env
  }

  deletion_protection = false

}

resource "google_bigquery_table" "clients" {
  dataset_id = google_bigquery_dataset.forecast.dataset_id
  table_id   = "clients"

  labels = {
    env = var.env
  }

  deletion_protection = false
}

resource "google_bigquery_table" "person" {
  dataset_id = google_bigquery_dataset.forecast.dataset_id
  table_id   = "person"

  labels = {
    env = var.env
  }

  deletion_protection = false
}

resource "google_bigquery_dataset" "harvest" {
  dataset_id                  = "Harvest"
  description                 = "Dataset for harvest tables to be used by datastudio"
  location                    = "EU"

  labels = {
    env = var.env
  }
}

resource "google_bigquery_table" "harvest" {
  dataset_id = google_bigquery_dataset.harvest.dataset_id
  table_id   = "timesheets"

  labels = {
    env = var.env
  }

  deletion_protection = false
}