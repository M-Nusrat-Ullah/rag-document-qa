"""Pydantic schemas for document operations."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class DocumentUpload(BaseModel):
    """Schema for document upload."""
    filename: str
    metadata: Optional[Dict[str, Any]] = None


class TextIngest(BaseModel):
    """Schema for text ingestion."""
    text: str = Field(..., min_length=10, description="Text content to ingest")
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IngestResponse(BaseModel):
    """Response after document ingestion."""
    status: str
    chunks_created: int
    total_documents: int
    message: str


class DocumentStats(BaseModel):
    """Document statistics."""
    collection_name: str
    document_count: int
    persist_directory: str