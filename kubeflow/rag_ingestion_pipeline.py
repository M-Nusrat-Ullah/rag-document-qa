"""RAG Document Ingestion Pipeline using Kubeflow Pipelines.

This pipeline orchestrates the end-to-end document ingestion workflow:
1. Load documents from source directory
2. Process documents into chunks
3. Generate embeddings using sentence-transformers
4. Store embeddings in ChromaDB
5. Validate the pipeline ran successfully
"""

from kfp import dsl, compiler

from components.load_documents import load_documents
from components.process_documents import process_documents
from components.generate_embeddings import generate_embeddings
from components.store_in_vector_db import store_in_vector_db
from components.validate_pipeline import validate_pipeline


@dsl.pipeline(
    name="rag-document-ingestion-pipeline",
    description="End-to-end RAG document ingestion pipeline",
)
def rag_ingestion_pipeline(
    source_path: str = "/data/documents",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    collection_name: str = "documents",
    persist_directory: str = "/data/chroma_db",
    min_expected_docs: int = 1,
):
    """Run the RAG document ingestion pipeline.
    
    Args:
        source_path: Path to source documents
        chunk_size: Document chunk size
        chunk_overlap: Chunk overlap
        embedding_model: HuggingFace embedding model
        collection_name: ChromaDB collection name
        persist_directory: ChromaDB storage path
        min_expected_docs: Minimum documents expected for validation
    """
    
    # Step 1: Load documents
    load_task = load_documents(source_path=source_path)
    load_task.set_display_name("📂 Load Documents")
    
    # Step 2: Process documents into chunks
    process_task = process_documents(
        input_path=load_task.outputs["output_path"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    process_task.set_display_name("✂️ Chunk Documents")
    
    # Step 3: Generate embeddings
    embed_task = generate_embeddings(
        chunks_path=process_task.outputs["output_path"],
        model_name=embedding_model,
    )
    embed_task.set_display_name("🧠 Generate Embeddings")
    embed_task.set_cpu_limit("2")
    embed_task.set_memory_limit("4Gi")
    
    # Step 4: Store in vector DB
    store_task = store_in_vector_db(
        embeddings_path=embed_task.outputs["embeddings_path"],
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    store_task.set_display_name("💾 Store in ChromaDB")
    
    # Step 5: Validate pipeline
    validate_task = validate_pipeline(
        expected_count=min_expected_docs,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    validate_task.set_display_name("✅ Validate Pipeline")
    validate_task.after(store_task)


if __name__ == "__main__":
    # Compile the pipeline to YAML
    compiler.Compiler().compile(
        pipeline_func=rag_ingestion_pipeline,
        package_path="rag_ingestion_pipeline.yaml",
    )
    print("✅ Pipeline compiled to: rag_ingestion_pipeline.yaml")