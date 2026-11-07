variable "project_id" {
  description = "Your own GCP project ID, e.g. cc-anna-123456"
  type        = string
}

variable "region" {
  description = "Where your resources live. europe-west3 is Frankfurt."
  type        = string
  default     = "europe-west3"
}

variable "neighbour_email" {
  description = "The Google account email of the person next to you"
  type        = string
}
