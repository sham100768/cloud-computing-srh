locals {
  labels = {
    course  = "cloud-computing-srh"
    session = "08"
  }
  spark = "serviceAccount:${google_service_account.dataproc.email}"
}

resource "google_project_service" "services" {
  for_each = toset([
    "dataproc.googleapis.com",
    "bigquery.googleapis.com",
    "bigquerystorage.googleapis.com",
  ])
  service            = each.value
  disable_on_destroy = false
}

# Your Spark cluster runs as its own service account: it may read the raw
# archive and write to your dataset, and nothing else.
resource "google_service_account" "dataproc" {
  account_id   = "dataproc-worker"
  display_name = "Dataproc cluster for the reliability job"
}

resource "google_project_iam_member" "dataproc_worker" {
  project = var.project_id
  role    = "roles/dataproc.worker"
  member  = local.spark
}

# Writing to BigQuery runs a job in your project.
resource "google_project_iam_member" "dataproc_bq_jobs" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = local.spark
}

resource "google_bigquery_dataset_iam_member" "dataproc_writes" {
  dataset_id = var.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = local.spark
}

resource "google_storage_bucket_iam_member" "dataproc_reads_archive" {
  bucket = "${var.project_id}-raw"
  role   = "roles/storage.objectViewer"
  member = local.spark
}

# Where Dataproc keeps the cluster's logs and your job's files.
resource "google_storage_bucket" "dataproc" {
  name                        = "${var.project_id}-dataproc"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }

  labels     = local.labels
  depends_on = [google_project_service.services]
}

resource "google_storage_bucket_iam_member" "dataproc_staging" {
  bucket = google_storage_bucket.dataproc.name
  role   = "roles/storage.objectAdmin"
  member = local.spark
}

# The Kappa path writes here: every event replayed from Kafka, through the same
# code as the live job.
resource "google_bigquery_table" "replay_events" {
  dataset_id          = var.dataset_id
  table_id            = "replay_events"
  deletion_protection = false
  description         = "The whole Kafka log, replayed through the Dataflow pipeline"

  time_partitioning {
    type  = "DAY"
    field = "event_time"
  }
  clustering = ["shipment_id"]

  schema = jsonencode([
    { name = "event_id", type = "STRING", mode = "REQUIRED" },
    { name = "shipment_id", type = "STRING", mode = "REQUIRED" },
    { name = "shipper_id", type = "STRING" },
    { name = "mode", type = "STRING" },
    { name = "event_type", type = "STRING", mode = "REQUIRED" },
    { name = "event_time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "location", type = "STRING" },
    { name = "carrier", type = "STRING" },
    { name = "origin", type = "STRING" },
    { name = "destination", type = "STRING" },
    { name = "trade_lane", type = "STRING" },
    { name = "delay_hours", type = "INTEGER" },
  ])

  labels     = local.labels
  depends_on = [google_project_service.services]
}
