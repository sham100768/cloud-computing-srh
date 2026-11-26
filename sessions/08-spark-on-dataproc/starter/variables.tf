variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  description = "Region for Dataproc and its bucket; the same as your dataset"
  type        = string
  default     = "europe-west3"
}

variable "dataset_id" {
  description = "The BigQuery dataset from session 2"
  type        = string
  default     = "freight"
}
