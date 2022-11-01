terraform {
  backend "gcs" {
    bucket  = "tpx-cheetah-data-visuals-tf-state-prod"
    prefix  = "terraform/state"
  }
}