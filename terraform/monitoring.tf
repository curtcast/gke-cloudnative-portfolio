resource "helm_release" "prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  force_update     = true


# Pin the version to prevent inconsistent final plan errors
  version    = "87.5.1"

  # 🌟 FORCE HELM TO WAIT UNTIL THE CLUSTER IS BUILT
  depends_on = [google_container_cluster.autopilot_cluster]

  values = [
    yamlencode({
      # 🌟 ADDED: This completely shuts down and deletes the local Grafana web service
      grafana = {
        enabled = false
      }
      # Prevent Helm from touching managed kube-system components entirely
      kubeProxy             = { enabled = false }
      kubeScheduler         = { enabled = false }
      kubeControllerManager = { enabled = false }
      coreDns               = { enabled = false }
      kubeEtcd              = { enabled = false }
      
      # Disable node-exporter to comply with GKE Autopilot security restrictions
      nodeExporter          = { enabled = false }

      alertmanager = { enabled = false }
      prometheus = {
        prometheusSpec = {
          remoteWrite = [{
            url = "https://prometheus-prod-37-prod-ap-southeast-1.grafana.net/api/prom/push"
            basicAuth = {
              username = { name = "grafana-cloud-credentials", key = "username" }
              password = { name = "grafana-cloud-credentials", key = "password" }
            }
          }]
        }
      }
    })
  ]
}
