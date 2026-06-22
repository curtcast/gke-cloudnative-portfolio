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

# Automatically provisions a custom Google Cloud Monitoring Dashboard for your portfolio
resource "google_monitoring_dashboard" "gke_dashboard" {
  project        = var.project_id
  dashboard_json = <<EOF
{
  "displayName": "GKE Portfolio Microservices Health",
  "gridLayout": {
    "widgets": [
      {
        "title": "Frontend & Backend Pod CPU Utilization",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"k8s_container\" AND metric.type=\"kubernetes.io/container/cpu/request_utilization\"",
                  "aggregation": {
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              },
              "targetAxis": "Y1"
            }
          ]
        }
      },
      {
        "title": "Container Memory Usage Metrics",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"k8s_container\" AND metric.type=\"kubernetes.io/container/memory/used_bytes\"",
                  "aggregation": {
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              },
              "targetAxis": "Y1"
            }
          ]
        }
      }
    ]
  }
}
EOF
}

resource "helm_release" "kube_prometheus_stack" {
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "monitoring"

  # 🌟 ADD THE REMOTE WRITE ATTRIBUTE BLOCK HERE:
  values = [
    <<-EOT
    prometheus:
      prometheusSpec:
        remoteWrite:
        - url: "https://grafana.net"
          basicAuth:
            username:
              name: grafana-cloud-credentials
              key: username
            password:
              name: grafana-cloud-credentials
              key: password
    EOT
  ]
}
