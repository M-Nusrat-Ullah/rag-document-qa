#!/bin/bash
set -e

echo "🚀 Deploying RAG Document Q&A to Kubernetes..."

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f kubernetes/namespace.yaml

# Create config
echo "⚙️  Creating ConfigMap..."
kubectl apply -f kubernetes/rag-api-configmap.yaml

# Create persistent volumes
echo "💾 Creating persistent volumes..."
kubectl apply -f kubernetes/persistent-volumes.yaml

# Deploy Ollama
echo "🤖 Deploying Ollama..."
kubectl apply -f kubernetes/ollama-deployment.yaml
kubectl apply -f kubernetes/ollama-service.yaml

# Deploy MLflow
echo "📊 Deploying MLflow..."
kubectl apply -f kubernetes/mlflow-deployment.yaml
kubectl apply -f kubernetes/mlflow-service.yaml

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
kubectl wait --for=condition=ready pod -l app=ollama -n rag-app --timeout=120s

# Deploy RAG API
echo "🔧 Deploying RAG API..."
kubectl apply -f kubernetes/rag-api-deployment.yaml
kubectl apply -f kubernetes/rag-api-service.yaml

# Wait for RAG API to be ready
echo "⏳ Waiting for RAG API to be ready..."
kubectl wait --for=condition=ready pod -l app=rag-api -n rag-app --timeout=300s

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access points:"
echo "   RAG API:  http://localhost:30080/docs"
echo "   MLflow:   kubectl port-forward svc/mlflow-service 5000:5000 -n rag-app"
echo "   Ollama:   kubectl port-forward svc/ollama-service 11434:11434 -n rag-app"
echo ""
echo "📋 Check status:"
echo "   kubectl get pods -n rag-app"
echo "   kubectl get svc -n rag-app"