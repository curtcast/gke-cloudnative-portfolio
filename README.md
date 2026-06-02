# ⚡ Cloud-Native Microservices Architecture on GKE with Terraform IaC

[Deploy Status](https://github.com)

A highly available, decoupled, cloud-native microservices portfolio application hosted entirely on Google Cloud Platform (GCP). This project orchestrates a multi-service architecture on a **Google Kubernetes Engine (GKE) Autopilot** cluster managed via **Terraform Infrastructure as Code (IaC)**, featuring enterprise-grade Layer 7 HTTPS termination using Google-Managed SSL Certificates and automated GitOps pipelines.

🌟 **[Live Project Demo Link](https://pcurtcast.xyz)** 🌟

---

## 🏛️ System Architecture Diagram

```text
[ Client Browser ]
        │
        ├── (HTTPS Request over Port 443)
        ▼
[ Google Cloud HTTP(S) Global Load Balancer ] ◄─── [ Google-Managed SSL Certificate ]
        │                                           (Automated Free Renewals)
        │ (Static Global IP: 8.232.243.217)
        ▼
[ GKE Autopilot Ingress Controller (GCE) ]
        │
        ├── (Path: /) ───────────────> [ portfolio-frontend-service ] (NodePort)
        │                                       └──> [ portfolio-frontend Pods ] (Nginx Alpine)
        │
        ├── (Path: /api) ────────────> [ portfolio-backend-service ] (ClusterIP)
        │                                       └──> [ portfolio-backend Pods ] (Python API)
        │
        └── (Path: /api/counter) ────> [ increment-visitor-counter-service ] (ClusterIP)
                                                └──> [ counter Pods ] (Python Functions)
                                                             │
                                                  (Secret Mounted Volume)
                                                             ▼
                                                    [ GCP Firestore NoSQL ]
```

---

## 🚀 Core Technical Features

* **☸️ Kubernetes Container Orchestration**: Deployed decoupled microservices independently on **GKE Autopilot**, utilizing replica redundancy for high availability and native cloud horizontal pod autoscaling.
* **🔒 Layer 7 Edge Security (HTTPS)**: Replaced raw Layer 4 LoadBalancers with a global **GKE Ingress (GCE controller)** paired with a `ManagedCertificate` resource for automated, free provisioning and rotation of SSL/TLS certificates.
* **📌 Permanent Network Anchoring**: Reserved a dedicated global static external compute IP address (`8.232.243.217`) mapped directly via Ingress annotations to permanently stabilize public DNS registrar A Records.
* **🏗️ Infrastructure as Code (IaC)**: Authored clean, declarative **Terraform blueprints** to provision native cloud networks (VPC) and cluster resources, using a **Google Cloud Storage (GCS)** remote state backend for secure state synchronization and locking.
* **⚡ Dual Containerization**: Engineered an ultra-lightweight frontend service utilizing an **Nginx Alpine Linux** container environment to optimize resource efficiency on port 8080.
* **🛡️ GKE Secret Partitioning**: Hardened cluster security parameters by deploying localized Kubernetes Secrets and securely mounting IAM Service Account credentials onto application filesystems to safely communicate with a **Firestore NoSQL database**.
* **🩺 Self-Healing Resilience**: Enforced cluster-wide **HTTP/TCP Liveness and Readiness probes** to create a fault-tolerant runtime environment alongside aggressive RollingUpdate deployment strategies.
* **🛠️ Cloud Native Backend**: Built an event-driven Python REST API using the **Google Functions Framework** that strictly separates **GET page reads** from **POST database increments** to ensure metric accuracy.
* **🔐 Advanced CI/CD GitOps**: Designed an automated pipeline with **GitHub Actions** that automatically initializes Terraform variables, handles Python backend unit testing, builds immutable Docker images tagged with `github.sha`, and executes rolling cluster upgrades.

---

## 📂 Project Structure

```text
gcp-serverless-portfolio/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Automated multi-service CI/CD & Terraform GitOps pipeline
├── frontend/
│   ├── index.html              # Responsive Tailwind CSS portfolio & session-locked cookie trigger
│   └── Dockerfile              # Production Nginx runtime compilation blueprint (Expose 8080)
├── backend/
│   ├── main.py                 # Core API transaction processing separating GET/POST methods
│   ├── requirements.txt        # Managed Python environment dependencies
│   ├── test_main.py            # Automated backend Python unit testing suite
│   └── Dockerfile              # Cloud native Functions Framework runner orchestration
├── kubernetes/
│   ├── deployments.yaml        # Complete multi-replica GKE deployment & service manifests (NodePort/ClusterIP)
│   ├── ingress.yaml            # GCE L7 Ingress routing paths, static IP, and SSL bindings
│   ├── managed-cert.yaml       # Google-Managed SSL Certificate Custom Resource definition
│   └── frontend-config.yaml    # HTTP-to-HTTPS frontend configuration policies
├── terraform/
│   ├── main.tf                 # Terraform core configuration and GCS remote state storage
│   ├── variables.tf            # Central infrastructure variables schema
│   └── providers.tf            # GKE and Kubernetes authentication provider configurations
├── .dockerignore               # Local filesystem isolation directives
└── README.md                   # System documentation and deployment blueprints
```

---

## 🛠️ Production Ingress & SSL Layout

The ingress architecture terminates TLS traffic at Google's edge networks before passing unencrypted requests down into the container mesh network.

### 1. SSL Provisioning Blueprint (`kubernetes/managed-cert.yaml`)
```yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: portfolio-managed-cert-v2
spec:
  domains:
    - pcurtcast.xyz
    - www.pcurtcast.xyz
```

### 2. Traffic Distribution Matrix (`kubernetes/ingress.yaml`)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: portfolio-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "portfolio-static-ip"
    networking.gke.io/frontend-config: "portfolio-frontend-config"
    networking.gke.io/managed-certificates: "portfolio-managed-cert-v2"
spec:
  ingressClassName: gce
  rules:
  - host: pcurtcast.xyz
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: portfolio-frontend-service
            port:
              number: 80
# ... configuration mirrors identically across www.pcurtcast.xyz ...
```

---

## 🏃‍♂️ Local Development Setup

### Testing the Backend Image Locally
To simulate the GKE cluster execution environment locally on your machine, navigate to the backend layer and build the image:

```bash
cd backend
docker build --no-cache -t local-backend .
docker run -p 8080:8080 local-backend
```
*(Note: A local run will safely throw a database credentials error if GCP application default credentials are not present locally. Run `gcloud auth application-default login` to resolve this).*

### Local Terraform Operations
```bash
cd terraform
terraform init
terraform plan
```
