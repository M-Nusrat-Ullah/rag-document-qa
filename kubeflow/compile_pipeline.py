"""Compile the Kubeflow pipeline to YAML for deployment."""

import sys
from pathlib import Path

# Add kubeflow directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from kfp import compiler
from rag_ingestion_pipeline import rag_ingestion_pipeline


def main():
    """Compile the pipeline to YAML."""
    output_path = Path(__file__).parent / "rag_ingestion_pipeline.yaml"
    
    compiler.Compiler().compile(
        pipeline_func=rag_ingestion_pipeline,
        package_path=str(output_path),
    )
    
    print(f"✅ Pipeline compiled successfully!")
    print(f"📄 Output: {output_path}")
    print(f"\n🚀 To deploy:")
    print(f"   1. Upload {output_path.name} to Kubeflow Pipelines UI")
    print(f"   2. Or use: kfp run create -p {output_path}")


if __name__ == "__main__":
    main()