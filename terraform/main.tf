terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Stores your cluster memory layout securely inside your cloud storage bucket
  backend "gcs" {
    bucket = "gcp-serverless-portfolio-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Define your GKE Autopilot Cluster representation
resource "google_container_cluster" "autopilot_cluster" {
  name             = "portfolio-cluster"
  location         = var.region
  enable_autopilot = true

  # Prevents accidental deletion via a routine command run
  deletion_protection = false
}
