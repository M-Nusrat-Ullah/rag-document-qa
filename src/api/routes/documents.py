"""Document management endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Optional
import tempfile
import os

from src.api.schemas.document import TextIngest, IngestResponse, DocumentStats
from src.services.rag_pipeline import RAGPipeline
from src.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

# Initialize RAG pipeline (singleton pattern in production)
rag_pipeline = RAGPipeline()


@router.post(
    "/upload",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """Upload and ingest a document (PDF, TXT, DOCX, MD)."""
    
    # Validate file type
    allowed_extensions = {".pdf", ".txt", ".docx", ".md"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Ingest document
        metadata = {
            "filename": file.filename,
            "title": title or file.filename,
            "source": "upload"
        }
        
        result = rag_pipeline.ingest_document(
            file_path=tmp_path,
            metadata=metadata
        )
        
        # Clean up
        os.unlink(tmp_path)
        
        return IngestResponse(
            status="success",
            chunks_created=result["chunks_created"],
            total_documents=result["total_documents"],
            message=f"Successfully ingested {file.filename}"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/ingest-text",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED
)
async def ingest_text(request: TextIngest):
    """Ingest raw text into the RAG system."""
    
    try:
        metadata = {
            "title": request.title or "Direct Text Input",
            "source": "text_input",
            **(request.metadata or {})
        }
        
        result = rag_pipeline.ingest_text(
            text=request.text,
            metadata=metadata
        )
        
        return IngestResponse(
            status="success",
            chunks_created=result["chunks_created"],
            total_documents=result["total_documents"],
            message="Successfully ingested text"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/stats",
    response_model=DocumentStats
)
async def get_document_stats():
    """Get document store statistics."""
    stats = rag_pipeline.get_stats()
    return DocumentStats(**stats["vector_store"])


@router.delete(
    "/clear",
    status_code=status.HTTP_200_OK
)
async def clear_documents():
    """Clear all documents from the vector store."""
    success = rag_pipeline.vector_store.delete_collection()
    
    if success:
        # Reinitialize
        rag_pipeline.vector_store = type(rag_pipeline.vector_store)()
        return {"status": "success", "message": "All documents cleared"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to clear documents"
    )