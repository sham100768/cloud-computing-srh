# The curated zone: a BigQuery dataset in the same region as your raw bucket.
resource "google_bigquery_dataset" "freight" {
  dataset_id  = "freight"
  location    = var.region
  description = "Curated freight data loaded from the raw bucket"

  # Lets `terraform destroy` remove the dataset even if it still has tables.
  delete_contents_on_destroy = true

  labels = {
    course  = "cloud-computing-srh"
    session = "02"
  }
}

locals {
  rates_schema = jsonencode([
    { name = "rate_date", type = "DATE", mode = "REQUIRED" },
    { name = "mode", type = "STRING" },
    { name = "contract_type", type = "STRING" },
    { name = "origin", type = "STRING" },
    { name = "destination", type = "STRING" },
    { name = "trade_lane", type = "STRING" },
    { name = "carrier_code", type = "STRING" },
    { name = "carrier_name", type = "STRING" },
    { name = "equipment", type = "STRING" },
    { name = "weight_break", type = "STRING" },
    { name = "rate_usd", type = "NUMERIC" },
    { name = "unit", type = "STRING" },
  ])
}

# The same rates twice: once as one big table, once partitioned and clustered.
# You'll dry-run the same query against both and compare the bytes scanned.
resource "google_bigquery_table" "rates_unpartitioned" {
  dataset_id          = google_bigquery_dataset.freight.dataset_id
  table_id            = "rates_unpartitioned"
  schema              = local.rates_schema
  deletion_protection = false
}

resource "google_bigquery_table" "rates" {
  dataset_id          = google_bigquery_dataset.freight.dataset_id
  table_id            = "rates"
  schema              = local.rates_schema
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "rate_date"
  }

  clustering = ["trade_lane", "carrier_code"]
}

resource "google_bigquery_table" "bookings" {
  dataset_id          = google_bigquery_dataset.freight.dataset_id
  table_id            = "bookings"
  deletion_protection = false

  schema = jsonencode([
    { name = "shipment_id", type = "STRING", mode = "REQUIRED" },
    { name = "booking_date", type = "DATE", mode = "REQUIRED" },
    { name = "shipper_id", type = "STRING" },
    { name = "shipper_name", type = "STRING" },
    { name = "mode", type = "STRING" },
    { name = "origin", type = "STRING" },
    { name = "destination", type = "STRING" },
    { name = "trade_lane", type = "STRING" },
    { name = "carrier_code", type = "STRING" },
    { name = "equipment", type = "STRING" },
    { name = "weight_break", type = "STRING" },
    { name = "quantity", type = "INT64" },
    { name = "unit", type = "STRING" },
    { name = "unit_rate_usd", type = "NUMERIC" },
    { name = "total_cost_usd", type = "NUMERIC" },
    { name = "schedule_id", type = "STRING" },
  ])

  time_partitioning {
    type  = "DAY"
    field = "booking_date"
  }

  clustering = ["trade_lane"]
}

# TODO: you write this one.
# Create a `schedules` table using the columns in event-generator/README.md.
# Hints: planned_departure, planned_arrival, actual_departure and actual_arrival are DATETIME.
# Partition by planned_departure (DAY) and cluster by carrier_code.
#
# resource "google_bigquery_table" "schedules" {
#   ...
# }
