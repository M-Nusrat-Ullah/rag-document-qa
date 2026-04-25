"""Main RAG pipeline orchestrating all services."""

import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.services.document_processor import DocumentProcessor
from src.services.vector_store import VectorStoreService
from src.services.llm_service import (
    get_llm_service,
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE
)
from src.services.experiment_tracker import get_experiment_tracker
from src.core.logging import logger


@dataclass
class RAGResponse:
    """Response from RAG pipeline."""
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    model_used: str


class RAGPipeline:
    """Main RAG pipeline for document Q&A."""

    def __init__(self):
        logger.info("Initializing RAG Pipeline")
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStoreService()
        self.llm_service = get_llm_service()
        self.tracker = get_experiment_tracker()

    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Ingest a document into the RAG system."""
        start_time = time.time()
        logger.info(f"Ingesting document: {file_path}")

        # Process document into chunks
        chunks = self.document_processor.process_document(
            file_path=file_path,
            metadata=metadata
        )

        # Add to vector store
        result = self.vector_store.add_documents(chunks)
        latency = time.time() - start_time

        # Track experiment
        self.tracker.log_ingestion(
            source=file_path,
            title=metadata.get("title", "unknown") if metadata else "unknown",
            chunks_created=len(chunks),
            total_documents=result.get("total_documents", 0),
            latency=latency,
            file_type=metadata.get("source", "upload") if metadata else "upload",
        )

        return {
            "file": file_path,
            "chunks_created": len(chunks),
            **result
        }

    def ingest_text(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Ingest raw text into the RAG system."""
        start_time = time.time()

        # Process text into chunks
        chunks = self.document_processor.process_text(
            text=text,
            metadata=metadata
        )

        # Add to vector store
        result = self.vector_store.add_documents(chunks)
        latency = time.time() - start_time

        # Track experiment
        self.tracker.log_ingestion(
            source="text_input",
            title=metadata.get("title", "Direct Text") if metadata else "Direct Text",
            chunks_created=len(chunks),
            total_documents=result.get("total_documents", 0),
            latency=latency,
            file_type="text",
        )

        return {
            "chunks_created": len(chunks),
            **result
        }

    def query(
        self,
        question: str,
        k: int = 5,
        include_sources: bool = True
    ) -> RAGResponse:
        """Query the RAG system."""
        start_time = time.time()
        logger.info(f"Processing query: {question[:100]}...")

        # Retrieve relevant documents
        search_results = self.vector_store.search(
            query=question,
            k=k
        )

        if not search_results:
            return RAGResponse(
                answer="No relevant documents found to answer your question.",
                sources=[],
                query=question,
                model_used=self.llm_service.model
            )

        # Build context from search results
        context = "\n\n---\n\n".join([
            f"[Source {i+1}]: {result['content']}"
            for i, result in enumerate(search_results)
        ])

        # Generate prompt
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )

        # Generate response
        answer = self.llm_service.generate(
            prompt=user_prompt,
            system_prompt=RAG_SYSTEM_PROMPT
        )

        # Prepare sources
        sources = []
        if include_sources:
            sources = [
                {
                    "content": result["content"][:200] + "...",
                    "metadata": result["metadata"],
                    "relevance_score": round(result["relevance_score"], 3)
                }
                for result in search_results
            ]

        latency = time.time() - start_time

        # Track experiment
        self.tracker.log_query(
            question=question,
            answer=answer,
            sources=sources,
            model_used=self.llm_service.model,
            latency=latency,
            k=k,
        )

        return RAGResponse(
            answer=answer,
            sources=sources,
            query=question,
            model_used=self.llm_service.model
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics."""
        return {
            "vector_store": self.vector_store.get_stats(),
            "llm_model": self.llm_service.model
        }