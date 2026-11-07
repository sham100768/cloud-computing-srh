variable "project_id" {
  description = "Your own GCP project ID"
  type        = string
}

variable "region" {
  description = "Must match your raw bucket's region so BigQuery can load from it"
  type        = string
  default     = "europe-west3"
}
