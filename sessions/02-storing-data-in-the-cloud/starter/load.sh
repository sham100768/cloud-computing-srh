#!/usr/bin/env bash
# Load the raw CSV files from your bucket into BigQuery.
# Run from this folder after `terraform apply`. Safe to run again: --replace reloads each table.
set -euo pipefail

PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"
BUCKET="gs://${PROJECT_ID}-raw"

load() {
  local table="$1" prefix="$2"
  echo "Loading ${table} from ${BUCKET}/${prefix}/"
  bq load --replace --source_format=CSV --skip_leading_rows=1 \
    "freight.${table}" "${BUCKET}/${prefix}/*"
}

load rates_unpartitioned rates
load rates rates
load bookings bookings

if bq show freight.schedules >/dev/null 2>&1; then
  load schedules schedules
else
  echo "Skipping schedules: create the table in main.tf first (the TODO), then run this again."
fi

echo "Done. Row counts:"
bq query --use_legacy_sql=false --format=pretty \
  'SELECT table_id, row_count FROM freight.__TABLES__ ORDER BY table_id'
