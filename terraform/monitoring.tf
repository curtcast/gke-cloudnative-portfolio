resource "helm_release" "prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  force_update = true

# Prevent Helm from touching managed kube-system components
  set {
    name  = "kubeProxy.enabled"
    value = "false"
  }

  set {
    name  = "kubeScheduler.enabled"
    value = "false"
  }

  set {
    name  = "kubeControllerManager.enabled"
    value = "false"
  }


  # 🌟 FORCE HELM TO WAIT UNTIL THE CLUSTER IS BUILT
  depends_on = [google_container_cluster.autopilot_cluster]

  values = [
    yamlencode({
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
