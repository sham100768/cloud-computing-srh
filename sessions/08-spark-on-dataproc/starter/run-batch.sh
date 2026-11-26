#!/usr/bin/env bash
# Submits the Spark job to your Dataproc cluster.
#   ./run-batch.sh --explore    look at the archive
#   ./run-batch.sh              build freight.carrier_reliability_batch
set -euo pipefail
cd "$(dirname "$0")"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

gcloud dataproc jobs submit pyspark spark/reliability_job.py \
  --cluster freight-spark \
  --region europe-west3 \
  --files reliability.sql \
  -- \
  --archive "gs://$PROJECT_ID-raw/events/" \
  --table "$PROJECT_ID.freight.carrier_reliability_batch" \
  "$@"
