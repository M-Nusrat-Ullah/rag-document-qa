"""Component: Load documents from a source directory."""

from kfp import dsl
from typing import NamedTuple


@dsl.component(
    base_image="python:3.12-slim",
    packages_to_install=["pypdf>=5.0.0"],
)
def load_documents(
    source_path: str,
    output_path: dsl.OutputPath("Documents"),
) -> NamedTuple("Outputs", [("file_count", int), ("total_size_kb", float)]):
    """Load documents from source path.
    
    Args:
        source_path: Path to source files (PDF, TXT, MD)
        output_path: Output path for loaded documents JSON
    
    Returns:
        file_count: Number of files loaded
        total_size_kb: Total size in KB
    """
    import json
    import os
    from collections import namedtuple
    from pathlib import Path
    
    documents = []
    total_size = 0
    
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Source path not found: {source_path}")
    
    # Process each file
    for file_path in source.rglob("*"):
        if file_path.suffix.lower() not in [".pdf", ".txt", ".md"]:
            continue
        
        size_kb = file_path.stat().st_size / 1024
        total_size += size_kb
        
        # Read content based on file type
        if file_path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            content = "\n".join(page.extract_text() for page in reader.pages)
        else:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        
        documents.append({
            "filename": file_path.name,
            "filepath": str(file_path),
            "content": content,
            "size_kb": size_kb,
            "type": file_path.suffix.lower()[1:],
        })
    
    # Save documents to output
    with open(output_path, "w") as f:
        json.dump(documents, f, indent=2)
    
    print(f"✅ Loaded {len(documents)} documents ({total_size:.2f} KB)")
    
    Outputs = namedtuple("Outputs", ["file_count", "total_size_kb"])
    return Outputs(file_count=len(documents), total_size_kb=round(total_size, 2))