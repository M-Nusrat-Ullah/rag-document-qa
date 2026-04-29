#!/bin/bash
echo "🗑️  Tearing down RAG Document Q&A from Kubernetes..."

kubectl delete -f kubernetes/rag-api-service.yaml --ignore-not-found
kubectl delete -f kubernetes/rag-api-deployment.yaml --ignore-not-found
kubectl delete -f kubernetes/mlflow-service.yaml --ignore-not-found
kubectl delete -f kubernetes/mlflow-deployment.yaml --ignore-not-found
kubectl delete -f kubernetes/ollama-service.yaml --ignore-not-found
kubectl delete -f kubernetes/ollama-deployment.yaml --ignore-not-found
kubectl delete -f kubernetes/persistent-volumes.yaml --ignore-not-found
kubectl delete -f kubernetes/rag-api-configmap.yaml --ignore-not-found
kubectl delete -f kubernetes/namespace.yaml --ignore-not-found

echo "✅ Teardown complete!"