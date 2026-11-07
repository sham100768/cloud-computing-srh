terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }

  # Stretch: store your state in a bucket instead of on disk.
  # Create the bucket first, then uncomment, set the bucket name, and run `terraform init -migrate-state`.
  # backend "gcs" {
  #   bucket = "YOUR-PROJECT-ID-tfstate"
  #   prefix = "session-01"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
