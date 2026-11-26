locals {
  labels = {
    course  = "cloud-computing-srh"
    session = "07"
  }
  worker = "serviceAccount:${google_service_account.dataflow.email}"
}

resource "google_project_service" "services" {
  for_each = toset([
    "dataflow.googleapis.com",
    "compute.googleapis.com",
    "bigquery.googleapis.com",
    "pubsub.googleapis.com",
  ])
  service            = each.value
  disable_on_destroy = false
}

# ------------------------------------------------------------- the workers

# Dataflow's workers run as their own service account, with only what the
# pipeline needs, not as the Compute Engine default account.
resource "google_service_account" "dataflow" {
  account_id   = "dataflow-worker"
  display_name = "Dataflow workers for the freight pipeline"
}

resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = local.worker
}

# Somewhere for Dataflow to stage your code and keep temporary files.
# Anything older than 7 days is deleted.
resource "google_storage_bucket" "dataflow" {
  name                        = "${var.project_id}-dataflow"
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

resource "google_storage_bucket_iam_member" "dataflow_temp" {
  bucket = google_storage_bucket.dataflow.name
  role   = "roles/storage.objectAdmin"
  member = local.worker
}

# The pipeline archives every event in your raw bucket from session 1.
resource "google_storage_bucket_iam_member" "dataflow_archive" {
  bucket = "${var.project_id}-raw"
  role   = "roles/storage.objectAdmin"
  member = local.worker
}

# ------------------------------------------------------------- air events

# Its own subscription on session 6's topic, so the pipeline gets every air
# event without taking them away from your debug subscription.
data "google_pubsub_topic" "air_events" {
  name = "air-events"
}

resource "google_pubsub_subscription" "dataflow" {
  name                 = "air-events-dataflow"
  topic                = data.google_pubsub_topic.air_events.id
  ack_deadline_seconds = 60

  expiration_policy {
    ttl = ""
  }

  labels = local.labels
}

resource "google_pubsub_subscription_iam_member" "dataflow_reads" {
  subscription = google_pubsub_subscription.dataflow.name
  role         = "roles/pubsub.subscriber"
  member       = local.worker
}

# Reading from a subscription also means looking it up.
resource "google_pubsub_subscription_iam_member" "dataflow_views" {
  subscription = google_pubsub_subscription.dataflow.name
  role         = "roles/pubsub.viewer"
  member       = local.worker
}

# ------------------------------------------------------------ live tables

resource "google_bigquery_table" "live_events" {
  dataset_id          = var.dataset_id
  table_id            = "live_events"
  deletion_protection = false
  description         = "Every ocean and air event, deduplicated, written by the Dataflow pipeline"

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

resource "google_bigquery_table" "departures_by_port" {
  dataset_id          = var.dataset_id
  table_id            = "departures_by_port"
  deletion_protection = false
  description         = "Departures per port per 5-minute window of event time"

  time_partitioning {
    type  = "DAY"
    field = "window_start"
  }

  schema = jsonencode([
    { name = "window_start", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "window_end", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "port", type = "STRING", mode = "REQUIRED" },
    { name = "departures", type = "INTEGER", mode = "REQUIRED" },
  ])

  labels     = local.labels
  depends_on = [google_project_service.services]
}

# The ops view: where every shipment is now. A view runs its query each time
# you read it, so it's always as fresh as live_events.
resource "google_bigquery_table" "live_status" {
  dataset_id          = var.dataset_id
  table_id            = "live_status"
  deletion_protection = false
  description         = "The latest event for every shipment"

  view {
    use_legacy_sql = false
    query          = <<-SQL
      SELECT * EXCEPT (rn)
      FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY event_time DESC) AS rn
        FROM `${var.project_id}.${var.dataset_id}.live_events`
      )
      WHERE rn = 1
    SQL
  }

  labels     = local.labels
  depends_on = [google_bigquery_table.live_events]
}

resource "google_bigquery_dataset_iam_member" "dataflow_writes" {
  dataset_id = var.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = local.worker
}

# ------------------------------------------------------------- the network

# Dataflow's workers reach Kafka on the GKE node's internal IP, on a NodePort.
# The default network usually allows this already; this rule makes it explicit,
# and only from inside your VPC.
resource "google_compute_firewall" "kafka_nodeport" {
  name          = "allow-kafka-nodeport-from-vpc"
  network       = "default"
  direction     = "INGRESS"
  source_ranges = ["10.128.0.0/9"]

  allow {
    protocol = "tcp"
    ports    = ["30000-32767"]
  }

  depends_on = [google_project_service.services]
}
