#!/usr/bin/env bash
# Gathers what Databricks needs into ~/session-09:
#   events.jsonl.gz                   your whole raw archive, as one file
#   carrier_reliability_batch.csv     yesterday's batch table
#   carrier_reliability_stream.csv    yesterday's replay table
set -euo pipefail
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
OUT=~/session-09
mkdir -p "$OUT"

echo "Joining the raw archive into one file..."
gcloud storage cat "gs://$PROJECT_ID-raw/events/*" | gzip > "$OUT/events.jsonl.gz"

for table in carrier_reliability_batch carrier_reliability_stream; do
  bq query --use_legacy_sql=false --location=europe-west3 --format=csv --max_rows=100000 \
    "SELECT * FROM freight.$table ORDER BY carrier, arrival_date" > "$OUT/$table.csv"
done

ls -lh "$OUT"
echo "Done. Download the three files with: cloudshell download ~/session-09/<file>"
