#!/usr/bin/env bash
# Launches the pipeline on Dataflow: Kafka and Pub/Sub in, BigQuery and files out.
# Run it from this folder, with the virtual environment active.
set -euo pipefail

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION=europe-west3

# Kafka's address inside the VPC: the node's internal IP and the listener's port.
BOOTSTRAP=$(kubectl -n kafka get kafka freight \
  -o jsonpath='{.status.listeners[?(@.name=="vpc")].bootstrapServers}')
if [ -z "$BOOTSTRAP" ]; then
  echo "Kafka has no vpc listener yet. Run ../kafka/open-kafka-to-vpc.sh first." >&2
  exit 1
fi
echo "Kafka at $BOOTSTRAP"

python pipeline.py \
  --source live \
  --kafka-bootstrap "$BOOTSTRAP" \
  --pubsub-subscription "projects/$PROJECT_ID/subscriptions/air-events-dataflow" \
  --dataset "$PROJECT_ID:freight" \
  --archive "gs://$PROJECT_ID-raw/events/" \
  --runner DataflowRunner \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --job_name freight-live \
  --temp_location "gs://$PROJECT_ID-dataflow/temp" \
  --staging_location "gs://$PROJECT_ID-dataflow/staging" \
  --service_account_email "dataflow-worker@$PROJECT_ID.iam.gserviceaccount.com" \
  --worker_machine_type e2-standard-2 \
  --num_workers 1 \
  --max_num_workers 1 \
  --setup_file ./setup.py \
  "$@"
