output "bucket_name" {
  description = "The bucket Terraform created"
  value       = google_storage_bucket.raw.name
}

output "bucket_url" {
  description = "Open this in the console to see your bucket"
  value       = "https://console.cloud.google.com/storage/browser/${google_storage_bucket.raw.name}"
}
