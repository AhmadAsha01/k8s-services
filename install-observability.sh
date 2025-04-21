#!/bin/bash

# Install Helm if not already installed
if ! command -v helm &> /dev/null; then
    echo "Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

echo "helm version is: $(helm version)"
sleep 3

# Add Helm repositories
echo "Adding Helm repositories..."
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Jaeger
echo "Installing Jaeger..."
helm upgrade --install jaeger jaegertracing/jaeger --values jaeger.yaml

# Install Prometheus
echo "Installing Prometheus..."
helm install prometheus prometheus-community/prometheus -f prometheus-values.yaml

echo "Observability tools installation complete!"
