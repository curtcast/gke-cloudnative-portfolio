# ⚡ Cloud-Native Microservices Architecture on GKE with Terraform IaC

![Deploy Status](https://github.com)

A highly available, decoupled, cloud-native microservices portfolio application hosted entirely on Google Cloud Platform (GCP). This project transitions a serverless Cloud Run environment into a fully orchestrated **Google Kubernetes Engine (GKE) Autopilot** cluster managed strictly via **Terraform Infrastructure as Code (IaC)** and automated GitOps pipelines.

🌟 **[Live Project Demo Link](http://YOUR_GKE_EXTERNAL_IP)** 🌟

---

## 🏛️ System Architecture Diagram

```text
[ Client Browser ]
        │
        ├── (HTTP Requests / UI) ───────> [ portfolio-frontend ] 
        │                                 (Docker / Nginx Alpine on GKE - LoadBalancer Service)
        │
        └── (Asynchronous API Fetch) ──> [ portfolio-backend ] & [ increment-visitor-counter ]
                                          (Docker / Python Functions Framework on GKE - ClusterIP)
                                                  │
                                       (IAM Service Account Secret)
                                                  ▼
                                         [ GCP Firestore NoSQL ]
```

---

## 🚀 Core Technical Features

* **☸️ Kubernetes Container Orchestration**: Deployed decoupled microservices independently on **Google Kubernetes Engine (GKE) Autopilot**, utilizing replicas for high availability and automated node scaling.
* **🏗️ Infrastructure as Code (IaC)**: Authored clean, declarative **Terraform blueprints** to provision native cloud networks (VPC) and cluster resources, using a **Google Cloud Storage (GCS)** remote state backend for secure state synchronization and locking.
* **⚡ Dual Containerization**: Engineered an ultra-lightweight frontend service utilizing an **Nginx Alpine Linux** container environment to optimize resource efficiency on port 8080.
* **🛡️ GKE Secret Partitioning**: Hardened cluster security parameters by deploying localized Kubernetes Secrets and securely mounting IAM Service Account credentials onto application filesystems to safely communicate with a **Firestore NoSQL database**.
* **🩺 Self-Healing Resilience**: Enforced cluster-wide **HTTP/TCP Liveness and Readiness probes** to create a fault-tolerant runtime environment alongside aggressive RollingUpdate deployment strategies.
* **🛠️ Cloud Native Backend**: Built an event-driven Python REST API using the **Google Functions Framework** that strictly separates **GET page reads** from **POST database increments** to ensure metric accuracy.
* **🔐 Advanced CI/CD GitOps**: Designed an automated pipeline with **GitHub Actions** that automatically initialises Terraform variables, handles Python backend unit testing, builds immutable Docker images tagged with `github.sha`, and executes rolling cluster upgrades.

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
│   └── deployments.yaml        # Complete multi-replica GKE deployment & service manifests
├── terraform/
│   ├── main.tf                 # Terraform core configuration and GCS remote state storage
│   ├── variables.tf            # Central infrastructure variables schema
│   └── providers.tf            # GKE and Kubernetes authentication provider configurations
├── .dockerignore               # Local filesystem isolation directives
└── README.md                   # System documentation and deployment blueprints
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
