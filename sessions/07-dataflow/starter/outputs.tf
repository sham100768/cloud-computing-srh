output "worker_service_account" {
  value = google_service_account.dataflow.email
}

output "air_subscription" {
  value = google_pubsub_subscription.dataflow.id
}

output "live_tables" {
  value = [
    "${var.dataset_id}.live_events",
    "${var.dataset_id}.departures_by_port",
    "${var.dataset_id}.live_status",
  ]
}
