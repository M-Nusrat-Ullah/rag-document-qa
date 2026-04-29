# 🤖 RAG Document Q&A

> Production-ready Retrieval-Augmented Generation (RAG) application for intelligent document question answering.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=flat)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📋 Overview

A production-grade RAG system that allows users to upload documents (PDF, TXT, MD), ingest text, and ask natural language questions. The system retrieves relevant context from stored documents and generates accurate answers using LLMs.

### Key Features

- 🔍 **Intelligent Document Q&A** - Ask questions and get answers from your documents
- 📄 **Multi-format Support** - PDF, TXT, and Markdown files
- 🧠 **Local Embeddings** - Uses sentence-transformers (no API costs for embeddings)
- 🤖 **Multi-LLM Support** - Ollama (local), OpenAI, Google Gemini, DeepSeek
- 📊 **Vector Search** - ChromaDB with cosine similarity
- 🚀 **REST API** - FastAPI with auto-generated Swagger documentation
- ❤️ **Health Checks** - Kubernetes-ready liveness and readiness probes
- 🐳 **Dockerized** - Full Docker Compose stack (API + Ollama + auto model pull)
- ☸️ **K8s Ready** - Kubernetes manifests (Phase 4)

---

## 🏗️ Architecture

Client → FastAPI REST API → Document Processor → Embedding Service → ChromaDB (Vector Store)

Client → FastAPI REST API → RAG Pipeline → Vector Search + LLM Service → Response

**Supported LLM Backends:** Ollama (Local) | OpenAI | Google Gemini | DeepSeek

---

## 🛠️ Tech Stack

| Component               | Technology                             |
| ----------------------- | -------------------------------------- |
| **API Framework**       | FastAPI                                |
| **LLM (Local)**         | Ollama (Qwen2.5, DeepSeek)             |
| **LLM (Cloud)**         | OpenAI, Google Gemini, DeepSeek API    |
| **Embeddings**          | sentence-transformers/all-MiniLM-L6-v2 |
| **Vector Store**        | ChromaDB                               |
| **Document Processing** | PyPDF, langchain-text-splitters        |
| **Containerization**    | Docker, Docker Compose                 |
| **Language**            | Python 3.12                            |

---

## 📦 Project Structure

| Path                               | Description                        |
| ---------------------------------- | ---------------------------------- |
| src/api/main.py                    | FastAPI application entry point    |
| src/api/routes/health.py           | Health check endpoints             |
| src/api/routes/documents.py        | Document management endpoints      |
| src/api/routes/query.py            | Q&A query endpoints                |
| src/api/schemas/document.py        | Document Pydantic models           |
| src/api/schemas/query.py           | Query Pydantic models              |
| src/core/config.py                 | Application configuration          |
| src/core/logging.py                | Logging setup                      |
| src/services/document_processor.py | Document loading and chunking      |
| src/services/embedding_service.py  | Vector embedding generation        |
| src/services/vector_store.py       | ChromaDB operations                |
| src/services/llm_service.py        | Multi-LLM integration              |
| src/services/rag_pipeline.py       | Main RAG orchestration             |
| docker/Dockerfile                  | Production container image         |
| docker/Dockerfile.dev              | Development container (hot reload) |
| docker/docker-compose.yml          | Full stack deployment              |
| docker/docker-compose.dev.yml      | Development deployment             |
| kubernetes/                        | K8s deployment manifests           |
| tests/                             | Test suite                         |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

The fastest way to get started — no local Python or Ollama setup needed.

# Clone the repository

    git clone https://github.com/M-Nusrat-Ullah/rag-document-qa.git
    cd rag-document-qa

# Start everything (API + Ollama + auto model pull)

    docker compose -f docker/docker-compose.yml up --build -d

# Watch logs (wait for "Application startup complete")

    docker compose -f docker/docker-compose.yml logs -f

The stack will:

1. Start Ollama server
2. Automatically pull the `qwen2.5:3b` model
3. Start the RAG API

Open **http://localhost:8000/docs** when ready.

### Option 2: Local Development

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) (for local LLM)

### 1. Clone the Repository

    git clone https://github.com/M-Nusrat-Ullah/rag-document-qa.git
    cd rag-document-qa

### 2. Install Ollama and Pull Model

    curl -fsSL https://ollama.com/install.sh | sh
    ollama pull qwen2.5:3b

### 3. Setup Python Environment

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### 4. Configure Environment

    cp .env.example .env

### 5. Run the Application

    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

### 6. Open API Documentation

    Navigate to [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Docker

### Production Stack

# Start all services

    make docker-run

# View logs

    make docker-logs

# Check status

    make docker-status

# Stop all services

    make docker-down

### Development Mode (Hot Reload)

    Uses your host Ollama instance and mounts source code for live reloading:

# Start dev mode

    make docker-dev

# Stop dev mode

    make docker-dev-down

### Docker Services

| Service     | Description                        | Port  |
| ----------- | ---------------------------------- | ----- |
| rag-api     | FastAPI application                | 8000  |
| ollama      | Ollama LLM server                  | 11434 |
| ollama-pull | One-time model puller (auto-exits) | -     |

### Cleanup

# Remove containers, volumes, and images

    make docker-clean


## ☸️ Kubernetes

### Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured
- A Kubernetes cluster (Minikube, Kind, or cloud)
- RAG API Docker image built locally

### Quick Deploy

```bash
# Build the RAG API image first
docker build -t rag-api:latest -f docker/Dockerfile .

# Deploy everything
make k8s-deploy

Manual Deploy

kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/rag-api-configmap.yaml
kubectl apply -f kubernetes/persistent-volumes.yaml
kubectl apply -f kubernetes/ollama-deployment.yaml
kubectl apply -f kubernetes/ollama-service.yaml
kubectl apply -f kubernetes/mlflow-deployment.yaml
kubectl apply -f kubernetes/mlflow-service.yaml
kubectl apply -f kubernetes/rag-api-deployment.yaml
kubectl apply -f kubernetes/rag-api-service.yaml


Access Services

# RAG API (NodePort)
http://localhost:30080/docs

# Port forward MLflow and Ollama
kubectl port-forward svc/mlflow-service 5000:5000 -n rag-app
kubectl port-forward svc/ollama-service 11434:11434 -n rag-app


Useful Commands

# Check status
make k8s-status

# View logs
make k8s-logs-api
make k8s-logs-ollama
make k8s-logs-mlflow

# Teardown
make k8s-teardown
Architecture
Service	Image	Port	Type
rag-api	rag-api:latest	30080	NodePort
ollama	ollama/ollama	11434	ClusterIP
mlflow	python:3.12-slim	5000	ClusterIP


## 📖 API Endpoints

### Health

| Method | Endpoint      | Description     |
| ------ | ------------- | --------------- |
| GET    | /health       | Health check    |
| GET    | /health/ready | Readiness probe |
| GET    | /health/live  | Liveness probe  |

### Documents

| Method | Endpoint               | Description                      |
| ------ | ---------------------- | -------------------------------- |
| POST   | /documents/upload      | Upload a document (PDF, TXT, MD) |
| POST   | /documents/ingest-text | Ingest raw text                  |
| GET    | /documents/stats       | Get document store statistics    |
| DELETE | /documents/clear       | Clear all documents              |

### Query

| Method | Endpoint | Description                             |
| ------ | -------- | --------------------------------------- |
| POST   | /query   | Ask a question about ingested documents |

---

## 💡 Usage Examples

### Ingest Text

    curl -X POST http://localhost:8000/documents/ingest-text \
      -H "Content-Type: application/json" \
      -d '{"text": "Python is a programming language created by Guido van Rossum in 1991.", "title": "About Python"}'

### Upload a PDF

    curl -X POST http://localhost:8000/documents/upload \
      -F "file=@document.pdf" \
      -F "title=My Document"

### Ask a Question

    curl -X POST http://localhost:8000/query \
      -H "Content-Type: application/json" \
      -d '{"question": "Who created Python?", "k": 3}'

### Response

    {
      "answer": "Guido van Rossum created Python.",
      "query": "Who created Python?",
      "sources": [
        {
          "content": "Python is a programming language created by Guido van Rossum...",
          "metadata": {"title": "About Python", "source": "text_input"},
          "relevance_score": 0.799
        }
      ],
      "model_used": "qwen2.5:3b"
    }

---

## 🔧 Configuration

### LLM Providers

| Provider             | Config                | Cost                   |
| -------------------- | --------------------- | ---------------------- |
| **Ollama** (default) | LLM_PROVIDER=ollama   | Free (local)           |
| **OpenAI**           | LLM_PROVIDER=openai   | Paid API               |
| **Google Gemini**    | LLM_PROVIDER=google   | Free tier available    |
| **DeepSeek**         | LLM_PROVIDER=deepseek | Free credits on signup |

### Environment Variables

| Variable             | Default    | Description          |
| -------------------- | ---------- | -------------------- |
| LLM_PROVIDER         | ollama     | LLM provider to use  |
| OLLAMA_MODEL         | qwen2.5:3b | Ollama model name    |
| USE_LOCAL_EMBEDDINGS | true       | Use local embeddings |
| CHUNK_SIZE           | 1000       | Document chunk size  |
| CHUNK_OVERLAP        | 200        | Chunk overlap size   |

---

## 🗺️ Roadmap

- [x] Phase 1: Core RAG Application
- [x] Phase 2: Docker and Docker Compose
- [x] Phase 3: MLflow Experiment Tracking
- [x] Phase 4: Kubernetes Deployment
- [ ] Phase 5: Kubeflow ML Pipeline
- [ ] Phase 6: Streamlit Frontend UI

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**M. Nusrat Ullah**

- GitHub: [@M-Nusrat-Ullah](https://github.com/M-Nusrat-Ullah)
- LinkedIn: [nusrat-ullah-tahmid](https://www.linkedin.com/in/nusrat-ullah-tahmid)
- Email: nusrat.ullah.tahmid@gmail.com
