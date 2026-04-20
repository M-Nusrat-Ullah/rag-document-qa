"""Document management endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Optional
import tempfile
import os

from src.api.schemas.document import TextIngest, IngestResponse, DocumentStats
from src.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

_pipeline = None


def get_pipeline():
    """Lazy initialization of RAG pipeline."""
    global _pipeline
    if _pipeline is None:
        from src.services.rag_pipeline import RAGPipeline
        _pipeline = RAGPipeline()
    return _pipeline


@router.post("/upload", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
):
    """Upload and ingest a document (PDF, TXT, MD)."""
    allowed_extensions = {".pdf", ".txt", ".md"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported: {file_ext}. Allowed: {allowed_extensions}",
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        metadata = {
            "filename": file.filename,
            "title": title or file.filename,
            "source": "upload",
        }

        pipeline = get_pipeline()
        result = pipeline.ingest_document(file_path=tmp_path, metadata=metadata)
        os.unlink(tmp_path)

        return IngestResponse(
            status="success",
            chunks_created=result["chunks_created"],
            total_documents=result["total_documents"],
            message=f"Successfully ingested {file.filename}",
        )

    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest-text", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_text(request: TextIngest):
    """Ingest raw text into the RAG system."""
    try:
        metadata = {
            "title": request.title or "Direct Text Input",
            "source": "text_input",
            **(request.metadata or {}),
        }

        pipeline = get_pipeline()
        result = pipeline.ingest_text(text=request.text, metadata=metadata)

        return IngestResponse(
            status="success",
            chunks_created=result["chunks_created"],
            total_documents=result["total_documents"],
            message="Successfully ingested text",
        )

    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=DocumentStats)
async def get_document_stats():
    """Get document store statistics."""
    pipeline = get_pipeline()
    stats = pipeline.get_stats()
    return DocumentStats(**stats["vector_store"])


@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_documents():
    """Clear all documents from the vector store."""
    global _pipeline
    pipeline = get_pipeline()
    success = pipeline.vector_store.delete_collection()

    if success:
        _pipeline = None
        return {"status": "success", "message": "All documents cleared"}

    raise HTTPException(status_code=500, detail="Failed to clear documents")