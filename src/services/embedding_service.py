"""Embedding service for generating vector embeddings."""

from typing import List, Optional
from abc import ABC, abstractmethod

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.core.config import settings
from src.core.logging import logger


class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        pass


class LocalEmbeddingService(BaseEmbeddingService):
    """Local embedding service using HuggingFace models."""
    
    def __init__(self, model_name: str = settings.embedding_model):
        logger.info(f"Initializing local embeddings: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.model_name = model_name
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return self.embeddings.embed_documents(texts)


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI embedding service."""
    
    def __init__(self, api_key: Optional[str] = None):
        logger.info("Initializing OpenAI embeddings")
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key or settings.openai_api_key
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return self.embeddings.embed_documents(texts)


def get_embedding_service() -> BaseEmbeddingService:
    """Factory function to get appropriate embedding service."""
    if settings.use_local_embeddings:
        return LocalEmbeddingService()
    else:
        return OpenAIEmbeddingService()