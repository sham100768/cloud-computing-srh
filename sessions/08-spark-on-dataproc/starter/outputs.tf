output "spark_service_account" {
  value = google_service_account.dataproc.email
}

output "staging_bucket" {
  value = google_storage_bucket.dataproc.name
}
