"""Component: Process documents - chunk text using RecursiveCharacterTextSplitter."""

from kfp import dsl
from typing import NamedTuple


@dsl.component(
    base_image="python:3.12-slim",
    packages_to_install=["langchain-text-splitters>=0.3.0"],
)
def process_documents(
    input_path: dsl.InputPath("Documents"),
    output_path: dsl.OutputPath("Chunks"),
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> NamedTuple("Outputs", [("chunk_count", int), ("avg_chunk_size", float)]):
    """Process documents into chunks.
    
    Args:
        input_path: Input documents JSON
        output_path: Output chunks JSON
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks
    
    Returns:
        chunk_count: Total number of chunks created
        avg_chunk_size: Average chunk size in characters
    """
    import json
    import hashlib
    from collections import namedtuple
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # Load documents
    with open(input_path, "r") as f:
        documents = json.load(f)
    
    # Initialize splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    all_chunks = []
    total_chars = 0
    
    for doc in documents:
        chunks = splitter.split_text(doc["content"])
        doc_id = hashlib.md5(doc["filename"].encode()).hexdigest()[:12]
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            all_chunks.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "content": chunk,
                "metadata": {
                    "filename": doc["filename"],
                    "chunk_index": i,
                    "type": doc["type"],
                },
            })
            total_chars += len(chunk)
    
    # Save chunks
    with open(output_path, "w") as f:
        json.dump(all_chunks, f, indent=2)
    
    avg_size = total_chars / max(len(all_chunks), 1)
    print(f"✅ Created {len(all_chunks)} chunks (avg size: {avg_size:.0f} chars)")
    
    Outputs = namedtuple("Outputs", ["chunk_count", "avg_chunk_size"])
    return Outputs(chunk_count=len(all_chunks), avg_chunk_size=round(avg_size, 2))