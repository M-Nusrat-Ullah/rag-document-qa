# 🤖 RAG Document Q&A

> Production-ready Retrieval-Augmented Generation (RAG) application for intelligent document question answering.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=flat)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat)
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
- 🐳 **Docker Ready** - Containerized deployment (Phase 2)
- ☸️ **K8s Ready** - Kubernetes manifests (Phase 4)

---

## 🏗️ Architecture

````mermaid
flowchart LR
    Client[🖥️ Client] --> API[⚡ FastAPI]
    API --> DP[📄 Document Processor]
    API --> RAG[🧠 RAG Pipeline]
    DP --> ES[🔢 Embedding Service]
    ES --> VS[(🗄️ ChromaDB)]
    RAG --> VS
    RAG --> ES
    RAG --> LLM[🤖 LLM Service]
    LLM --> Ollama[Ollama - Local]
    LLM --> OpenAI[OpenAI]
    LLM --> Gemini[Google Gemini]
    LLM --> DeepSeek[DeepSeek]


---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **API Framework** | FastAPI |
| **LLM (Local)** | Ollama (Qwen2.5, DeepSeek) |
| **LLM (Cloud)** | OpenAI, Google Gemini, DeepSeek API |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |
| **Vector Store** | ChromaDB |
| **Document Processing** | PyPDF, langchain-text-splitters |
| **Language** | Python 3.12 |

---

```markdown
## 📦 Project Structure

| Path | Description |
|------|-------------|
| `src/api/main.py` | FastAPI application entry point |
| `src/api/routes/health.py` | Health check endpoints |
| `src/api/routes/documents.py` | Document management endpoints |
| `src/api/routes/query.py` | Q&A query endpoints |
| `src/api/schemas/document.py` | Document Pydantic models |
| `src/api/schemas/query.py` | Query Pydantic models |
| `src/core/config.py` | Application configuration |
| `src/core/logging.py` | Logging setup |
| `src/services/document_processor.py` | Document loading & chunking |
| `src/services/embedding_service.py` | Vector embedding generation |
| `src/services/vector_store.py` | ChromaDB operations |
| `src/services/llm_service.py` | Multi-LLM integration |
| `src/services/rag_pipeline.py` | Main RAG orchestration |
| `docker/` | Docker configuration |
| `kubernetes/` | K8s deployment manifests |
| `kubeflow/` | ML pipeline (future) |
| `tests/` | Test suite |


---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) (for local LLM)

### 1. Clone the Repository

```bash
git clone https://github.com/M-Nusrat-Ullah/rag-document-qa.git
cd rag-document-qa


2. Install Ollama & Pull Model
bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull qwen2.5:3b

3. Setup Python Environment
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

pip install -r requirements.txt

4. Configure Environment
bash
cp .env.example .env
# Edit .env with your settings

5. Run the Application
bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

6. Open API Documentation
Navigate to: http://localhost:8000/docs

📖 API Endpoints

Health
Method	Endpoint	Description
GET	/health	Health check
GET	/health/ready	Readiness probe
GET	/health/live	Liveness probe

Documents
Method	Endpoint	Description
POST	/documents/upload	Upload a document (PDF, TXT, MD)
POST	/documents/ingest-text	Ingest raw text
GET	/documents/stats	Get document store statistics
DELETE	/documents/clear	Clear all documents

Query
Method	Endpoint	Description
POST	/query	Ask a question about ingested documents

💡 Usage Examples

Ingest Text
bash
curl -X POST http://localhost:8000/documents/ingest-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python is a programming language created by Guido van Rossum in 1991.",
    "title": "About Python"
  }'

Upload a PDF
bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@document.pdf" \
  -F "title=My Document"

Ask a Question
bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who created Python?",
    "k": 3
  }'

Response
json
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

🔧 Configuration
LLM Providers
Provider	Config	Cost
Ollama (default)	LLM_PROVIDER=ollama	Free (local)
OpenAI	LLM_PROVIDER=openai	Paid API
Google Gemini	LLM_PROVIDER=google	Free tier available
DeepSeek	LLM_PROVIDER=deepseek	Free credits on signup

Environment Variables
Variable	Default	Description
LLM_PROVIDER	ollama	LLM provider to use
OLLAMA_MODEL	qwen2.5:3b	Ollama model name
USE_LOCAL_EMBEDDINGS	true	Use local embeddings
CHUNK_SIZE	1000	Document chunk size
CHUNK_OVERLAP	200	Chunk overlap size


🗺️ Roadmap
 Phase 1: Core RAG Application
 Phase 2: Docker & Docker Compose
 Phase 3: MLflow Experiment Tracking
 Phase 4: Kubernetes Deployment
 Phase 5: Kubeflow ML Pipeline
 Phase 6: Streamlit Frontend UI

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
M. Nusrat Ullah

GitHub: @M-Nusrat-Ullah
LinkedIn: nusrat-ullah-tahmid
Email: nusrat.ullah.tahmid@gmail.com
````
