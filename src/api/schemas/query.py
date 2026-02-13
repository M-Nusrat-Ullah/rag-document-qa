"""Pydantic schemas for query operations."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """Schema for query request."""
    question: str = Field(..., min_length=3, description="Question to ask")
    k: int = Field(default=5, ge=1, le=20, description="Number of sources to retrieve")
    include_sources: bool = Field(default=True, description="Include source documents")


class SourceDocument(BaseModel):
    """Source document in response."""
    content: str
    metadata: Dict[str, Any]
    relevance_score: float


class QueryResponse(BaseModel):
    """Response to a query."""
    answer: str
    query: str
    sources: List[SourceDocument]
    model_used: str