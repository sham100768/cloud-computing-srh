# Your first bucket: the raw zone of the platform you'll build.
# Bucket names are global across all of Google Cloud, so we prefix it with your project ID.
resource "google_storage_bucket" "raw" {
  name     = "${var.project_id}-raw"
  location = var.region

  # Security defaults: no public access, permissions set on the bucket, not per file.
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  # Lets `terraform destroy` remove the bucket even if it still holds files.
  # Fine for coursework; think twice before doing this in production.
  force_destroy = true

  labels = {
    course  = "cloud-computing-srh"
    session = "01"
  }
}

# TODO (step 4): give your neighbour read-only access to your project.
# Uncomment, then run `terraform plan` and read what it will change before you apply.
#
# resource "google_project_iam_member" "neighbour_viewer" {
#   project = var.project_id
#   role    = "roles/viewer"
#   member  = "user:${var.neighbour_email}"
# }
