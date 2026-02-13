"""Query endpoints for RAG Q&A."""

from fastapi import APIRouter, HTTPException, status

from src.api.schemas.query import QueryRequest, QueryResponse, SourceDocument
from src.services.rag_pipeline import RAGPipeline
from src.core.logging import logger

router = APIRouter(prefix="/query", tags=["Query"])

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK
)
async def query_documents(request: QueryRequest):
    """Ask a question about the ingested documents."""
    
    try:
        # Check if there are documents
        stats = rag_pipeline.get_stats()
        if stats["vector_store"]["document_count"] == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents ingested. Please upload documents first."
            )
        
        # Query RAG pipeline
        response = rag_pipeline.query(
            question=request.question,
            k=request.k,
            include_sources=request.include_sources
        )
        
        return QueryResponse(
            answer=response.answer,
            query=response.query,
            sources=[
                SourceDocument(**source) for source in response.sources
            ],
            model_used=response.model_used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )