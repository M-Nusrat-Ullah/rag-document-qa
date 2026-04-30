# 🔄 Kubeflow Pipeline for RAG Document Ingestion

This directory contains a Kubeflow Pipelines (KFP) v2 definition for automating the RAG document ingestion workflow.

## 📊 Pipeline Architecture

┌─────────────────┐
│ Load Documents │ 📂 Reads PDF/TXT/MD files
└────────┬────────┘
│
▼
┌─────────────────┐
│ Process & Chunk │ ✂️ Splits into chunks (1000 chars, 200 overlap)
└────────┬────────┘
│
▼
┌─────────────────┐
│ Generate Embed. │ 🧠 Creates vectors using sentence-transformers
└────────┬────────┘
│
▼
┌─────────────────┐
│ Store in Chroma │ 💾 Persists to ChromaDB
└────────┬────────┘
│
▼
┌─────────────────┐
│ Validate │ ✅ Verifies success
└─────────────────┘

## 🚀 Components

| Component             | Description                                      | Key Outputs                     |
| --------------------- | ------------------------------------------------ | ------------------------------- |
| `load_documents`      | Loads files from source                          | file_count, total_size_kb       |
| `process_documents`   | Chunks text using RecursiveCharacterTextSplitter | chunk_count, avg_chunk_size     |
| `generate_embeddings` | Creates vector embeddings                        | embedding_count, dimension      |
| `store_in_vector_db`  | Stores in ChromaDB                               | stored_count, collection_size   |
| `validate_pipeline`   | Verifies ingestion success                       | validation_passed, actual_count |

## 🔧 Compile the Pipeline

```bash
cd kubeflow
python compile_pipeline.py
```
