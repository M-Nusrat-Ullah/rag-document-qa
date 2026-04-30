"""Component: Generate embeddings using sentence-transformers."""

from kfp import dsl
from typing import NamedTuple


@dsl.component(
    base_image="python:3.12-slim",
    packages_to_install=[
        "sentence-transformers>=3.4.0",
        "torch>=2.0.0",
    ],
)
def generate_embeddings(
    chunks_path: dsl.InputPath("Chunks"),
    embeddings_path: dsl.OutputPath("Embeddings"),
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> NamedTuple("Outputs", [("embedding_count", int), ("dimension", int)]):
    """Generate embeddings for all chunks.
    
    Args:
        chunks_path: Input chunks JSON
        embeddings_path: Output embeddings JSON
        model_name: Hugging Face model name
    
    Returns:
        embedding_count: Total embeddings generated
        dimension: Embedding vector dimension
    """
    import json
    from collections import namedtuple
    from sentence_transformers import SentenceTransformer
    
    # Load chunks
    with open(chunks_path, "r") as f:
        chunks = json.load(f)
    
    # Load model
    print(f"📥 Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Generate embeddings in batch
    texts = [chunk["content"] for chunk in chunks]
    print(f"🧠 Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Combine chunks with embeddings
    output = []
    for chunk, embedding in zip(chunks, embeddings):
        output.append({
            **chunk,
            "embedding": embedding.tolist(),
        })
    
    # Save
    with open(embeddings_path, "w") as f:
        json.dump(output, f)
    
    dim = embeddings.shape[1] if len(embeddings) > 0 else 0
    print(f"✅ Generated {len(embeddings)} embeddings (dim: {dim})")
    
    Outputs = namedtuple("Outputs", ["embedding_count", "dimension"])
    return Outputs(embedding_count=len(embeddings), dimension=dim)