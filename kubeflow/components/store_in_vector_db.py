"""Component: Store embeddings in ChromaDB."""

from kfp import dsl
from typing import NamedTuple


@dsl.component(
    base_image="python:3.12-slim",
    packages_to_install=["chromadb>=0.6.3"],
)
def store_in_vector_db(
    embeddings_path: dsl.InputPath("Embeddings"),
    collection_name: str = "documents",
    persist_directory: str = "/data/chroma_db",
) -> NamedTuple("Outputs", [("stored_count", int), ("collection_size", int)]):
    """Store embeddings in ChromaDB.
    
    Args:
        embeddings_path: Input embeddings JSON
        collection_name: ChromaDB collection name
        persist_directory: ChromaDB persist directory
    
    Returns:
        stored_count: Embeddings stored in this run
        collection_size: Total collection size after storage
    """
    import json
    from collections import namedtuple
    import chromadb
    
    # Load embeddings
    with open(embeddings_path, "r") as f:
        items = json.load(f)
    
    # Initialize ChromaDB
    print(f"📦 Connecting to ChromaDB at {persist_directory}")
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    
    # Prepare data for batch insert
    ids = [item["chunk_id"] for item in items]
    embeddings = [item["embedding"] for item in items]
    documents = [item["content"] for item in items]
    metadatas = [item["metadata"] for item in items]
    
    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    
    total_count = collection.count()
    print(f"✅ Stored {len(ids)} embeddings (collection total: {total_count})")
    
    Outputs = namedtuple("Outputs", ["stored_count", "collection_size"])
    return Outputs(stored_count=len(ids), collection_size=total_count)