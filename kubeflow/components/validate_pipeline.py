"""Component: Validate the pipeline ran successfully."""

from kfp import dsl
from typing import NamedTuple


@dsl.component(
    base_image="python:3.12-slim",
    packages_to_install=["chromadb>=0.6.3"],
)
def validate_pipeline(
    expected_count: int,
    collection_name: str = "documents",
    persist_directory: str = "/data/chroma_db",
) -> NamedTuple("Outputs", [("validation_passed", bool), ("actual_count", int)]):
    """Validate that the pipeline succeeded.
    
    Args:
        expected_count: Expected minimum number of documents
        collection_name: ChromaDB collection name
        persist_directory: ChromaDB persist directory
    
    Returns:
        validation_passed: Whether validation passed
        actual_count: Actual document count
    """
    from collections import namedtuple
    import chromadb
    
    print(f"🔍 Validating ChromaDB collection: {collection_name}")
    client = chromadb.PersistentClient(path=persist_directory)
    
    try:
        collection = client.get_collection(name=collection_name)
        actual_count = collection.count()
    except Exception as e:
        print(f"❌ Collection not found: {e}")
        Outputs = namedtuple("Outputs", ["validation_passed", "actual_count"])
        return Outputs(validation_passed=False, actual_count=0)
    
    passed = actual_count >= expected_count
    
    if passed:
        print(f"✅ Validation passed: {actual_count} >= {expected_count}")
    else:
        print(f"❌ Validation failed: {actual_count} < {expected_count}")
    
    Outputs = namedtuple("Outputs", ["validation_passed", "actual_count"])
    return Outputs(validation_passed=passed, actual_count=actual_count)