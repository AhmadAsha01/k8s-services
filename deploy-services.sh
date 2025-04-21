#!/bin/bash

# Build Docker images for both services
echo "Building Docker images..."
cd ./hash-service
docker build -t hash-service:latest .
cd ..

cd ./length-service
docker build -t length-service:latest .
cd ..

# Load images into Minikube
echo "Loading images into Minikube..."
minikube image load hash-service:latest
minikube image load length-service:latest

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f observability-configmap.yaml

cd ./hash-service
kubectl apply -f hash-deployment.yaml
kubectl apply -f hash-service.yaml
cd ..

cd ./length-service
kubectl apply -f length-deployment.yaml
kubectl apply -f length-service.yaml
cd ..


echo "Services deployment complete!"
echo "Run './install-observability.sh' to install Jaeger and Prometheus"
