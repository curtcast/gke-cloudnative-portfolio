resource "helm_release" "prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  force_update     = true

  # 🌟 FORCE HELM TO WAIT UNTIL THE CLUSTER IS BUILT
  depends_on = [google_container_cluster.autopilot_cluster]

  values = [
    yamlencode({
      # Prevent Helm from touching managed kube-system components
      kubeProxy             = { enabled = false }
      kubeScheduler         = { enabled = false }
      kubeControllerManager = { enabled = false }

      alertmanager = { enabled = false }
      prometheus = {
        prometheusSpec = {
          remoteWrite = [{
            url = "https://grafana.net"
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
