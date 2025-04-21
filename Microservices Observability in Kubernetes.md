# Microservices Observability in Kubernetes

This project implements a simple two-service application deployed on Kubernetes with monitoring and tracing capabilities. The application consists of a Hash Service and a Length Service, both instrumented with OpenTelemetry for tracing and Prometheus for metrics collection.

## Architecture Overview

- **Hash Service**: Calculates SHA256 hash of input text
- **Length Service**: Calculates length of input text
- **Jaeger**: Distributed tracing system
- **Prometheus**: Metrics collection

## Prerequisites

- Minikube installed and running
- kubectl configured to use Minikube
- Docker installed

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd k8s-services
```

### 2. Build and Deploy Services

Run the deployment script to build Docker images and deploy services to Minikube:

```bash
cd kubernetes
chmod +x deploy-services.sh
./deploy-services.sh
```

This script will:
- Build Docker images for both services
- Load images into Minikube
- Apply Kubernetes manifests (ConfigMaps, Deployments, Services)

### 3. Install Observability Tools

Run the observability installation script to deploy Jaeger and Prometheus:

```bash
chmod +x install-observability.sh
./install-observability.sh
```

This script will:
- Add required Helm repositories
- Install Jaeger using Helm
- Install Prometheus using Helm

### 4. Verify Deployment

Check that all components are running:

```bash
kubectl get all
```

## Accessing the Services

### Expose Services

To access the services from your local machine, use port-forwarding:

```bash
# Expose Hash Service
kubectl port-forward svc/hash-service 8080:8080 &

# Expose Length Service
kubectl port-forward svc/length-service 8081:8081 &

# Expose Jaeger UI
kubectl port-forward svc/jaeger-query 16686:16686 &

# Expose Prometheus UI
kubectl port-forward svc/prometheus-server 9090:80 &
```

### Example Requests

#### Hash Service

```bash
# Calculate hash of "Apple"
curl -X POST http://localhost:8080/hash -d "Apple"
# Expected output: f223faa96f22916294922b171a2696d868fd1f9129302eb41a45b2a2ea2ebbfd
```

#### Length Service

```bash
# Calculate length of "Apple"
curl -X POST http://localhost:8081/length -d "Apple"
# Expected output: 5
```

## Viewing Observability Data

### Traces in Jaeger

1. Open Jaeger UI at http://localhost:16686
2. Select either "hash-service" or "length-service" from the Service dropdown
3. Click "Find Traces" to view traces
4. Click on any trace to see detailed span information

### Metrics in Prometheus

1. Open Prometheus UI at http://localhost:9090
2. Click on "Query"
3. Navigate to the "Graph" tab
4. Enter this example query to view the metric:
   - `sum(hash_request_count_total)` - Number of hash requests

## Implementation Details

### Services

Both services are implemented in Python using Flask and include:
- OpenTelemetry integration for distributed tracing
- Prometheus metrics for monitoring
- Health check endpoints for Kubernetes probes
- Error handling and logging

### Kubernetes Configuration

- Deployments with resource limits and health probes
- Services for network access
- ConfigMaps for configuration

### Observability

- Jaeger for distributed tracing visualization
- Prometheus for metrics collection and monitoring
- OpenTelemetry for instrumentation

## Troubleshooting

If you encounter issues:

1. Check pod status:
   ```bash
   kubectl get pods
   ```

2. Check pod logs:
   ```bash
   kubectl logs <pod-name>
   ```

3. Verify ConfigMap:
   ```bash
   kubectl get configmap observability-config -o yaml
   ```

4. Restart deployments if needed:
   ```bash
   kubectl rollout restart deployment hash-service
   kubectl rollout restart deployment length-service
   ```

## What's Next?

- Grafana.
- CI/CD Pipelines.
- Horizontal Pod Autoscaling based on metrics.