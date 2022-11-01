resource "google_secret_manager_secret" "forecast_account_id" {
  secret_id = "FORECAST_ACCOUNT_ID"
  project = var.project

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
      replicas {
        location = "europe-west2"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "forecast_account_id" {
  secret = google_secret_manager_secret.forecast_account_id.id
  secret_data = var.FORECAST_ACCOUNT_ID
}

resource "google_secret_manager_secret_iam_binding" "forecast_account_id" {
  project = var.project
  secret_id = google_secret_manager_secret.forecast_account_id.secret_id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

resource "google_secret_manager_secret_iam_binding" "forecast_access_token" {
  project = var.project
  secret_id = google_secret_manager_secret.forecast_access_token.secret_id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

resource "google_secret_manager_secret" "forecast_access_token" {
  secret_id = "FORECAST_ACCESS_TOKEN"
  project = var.project
#   labels = {
#     label = "my-label"
#   }

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
      replicas {
        location = "europe-west2"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "forecast_access_token" {
  secret = google_secret_manager_secret.forecast_access_token.id
  secret_data = var.FORECAST_ACCESS_TOKEN
}

resource "google_secret_manager_secret" "harvest_account_id" {
  secret_id = "HARVEST_ACCOUNT_ID"
  project = var.project

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
      replicas {
        location = "europe-west2"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "harvest_account_id" {
  secret = google_secret_manager_secret.harvest_account_id.id
  secret_data = var.HARVEST_ACCOUNT_ID
}

resource "google_secret_manager_secret_iam_binding" "harvest_account_id" {
  project = var.project
  secret_id = google_secret_manager_secret.harvest_account_id.secret_id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

resource "google_secret_manager_secret_iam_binding" "harvest_access_token" {
  project = var.project
  secret_id = google_secret_manager_secret.harvest_access_token.secret_id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

resource "google_secret_manager_secret" "harvest_access_token" {
  secret_id = "HARVEST_ACCESS_TOKEN"
  project = var.project
#   labels = {
#     label = "my-label"
#   }

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
      replicas {
        location = "europe-west2"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "harvest_access_token" {
  secret = google_secret_manager_secret.harvest_access_token.id
  secret_data = var.HARVEST_ACCESS_TOKEN
}

resource "google_secret_manager_secret_iam_binding" "bob_access_token" {
  project = var.project
  secret_id = google_secret_manager_secret.bob_access_token.secret_id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${var.project}@appspot.gserviceaccount.com"
  ]
}

resource "google_secret_manager_secret" "bob_access_token" {
  secret_id = "BOB_ACCESS_TOKEN"
  project = var.project
#   labels = {
#     label = "my-label"
#   }

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
      replicas {
        location = "europe-west2"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "bob_access_token" {
  secret = google_secret_manager_secret.bob_access_token.id
  secret_data = var.BOB_ACCESS_TOKEN
}

