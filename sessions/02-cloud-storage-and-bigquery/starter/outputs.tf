output "dataset" {
  value = "${var.project_id}:${google_bigquery_dataset.freight.dataset_id}"
}

output "console_url" {
  value = "https://console.cloud.google.com/bigquery?project=${var.project_id}"
}
