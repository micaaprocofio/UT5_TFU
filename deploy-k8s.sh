#!/bin/bash
set -e

echo "🔍 Verificando cluster de Kubernetes..."
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ Cluster de Kubernetes no está disponible"
    echo ""
    echo "Inicia tu cluster primero:"
    echo "  - Docker Desktop: Habilita Kubernetes en Preferencias"
    echo "  - minikube: minikube start"
    echo "  - kind: kind create cluster"
    exit 1
fi

echo "✅ Cluster disponible"
echo ""

# Detectar si es minikube
IS_MINIKUBE=false
if kubectl config current-context | grep -q "minikube"; then
    IS_MINIKUBE=true
    echo "📦 Detectado: Minikube"
fi

echo "🔨 Construyendo imágenes..."
docker build -t gateway:latest ./gateway
docker build -t products-service:latest ./services/products
docker build -t customers-service:latest ./services/customers
docker build -t orders-service:latest ./services/orders

# Si es minikube, cargar imágenes
if [ "$IS_MINIKUBE" = true ]; then
    echo ""
    echo "📤 Cargando imágenes en minikube..."
    minikube image load gateway:latest
    minikube image load products-service:latest
    minikube image load customers-service:latest
    minikube image load orders-service:latest
    echo "✅ Imágenes cargadas en minikube"
fi

echo ""
echo "🚀 Desplegando en Kubernetes..."
kubectl apply -f k8s/databases.yaml
kubectl apply -f k8s/gateway-deployment.yaml
kubectl apply -f k8s/products-deployment.yaml
kubectl apply -f k8s/customers-deployment.yaml
kubectl apply -f k8s/orders-deployment.yaml
kubectl apply -f k8s/microservices-hpa.yaml

echo ""
echo "⏳ Esperando a que los pods estén listos..."
kubectl wait --for=condition=ready pod -l app=gateway --timeout=60s 2>/dev/null || echo "Gateway aún iniciando..."

echo ""
echo "✅ Desplegado!"
echo ""
kubectl get pods

echo ""
echo "🌐 Acceder a la API:"
if [ "$IS_MINIKUBE" = true ]; then
    echo "   minikube service gateway-service --url"
    echo "   O ejecuta: minikube service gateway-service"
else
    echo "   http://localhost:30080/docs"
fi

echo ""
echo "📋 Comandos útiles:"
echo "   kubectl get svc                      # Ver servicios"
echo "   kubectl logs -l app=gateway -f       # Ver logs del gateway"
echo "   kubectl get hpa                      # Ver autoescalado"
