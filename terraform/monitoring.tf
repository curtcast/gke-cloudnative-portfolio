resource "helm_release" "prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts" # 🌟 FIXED REPO URL
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true

  values = [
    yamlencode({
      alertmanager = {
        enabled = false
      }
      
      # 🌟 ADDED YOUR GRAFANA CLOUD METRICS CONNECTION HERE
      prometheus = {
        prometheusSpec = {
          remoteWrite = [
            {
              url = "https://grafana.net"
              basicAuth = {
                username = {
                  name = "grafana-cloud-credentials"
                  key  = "username"
                }
                password = {
                  name = "grafana-cloud-credentials"
                  key  = "password"
                }
              }
            }
          ]
        }
      }
    })
  ]
}

