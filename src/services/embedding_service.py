"""Embedding service for generating vector embeddings."""

from typing import List, Optional
from abc import ABC, abstractmethod

from src.core.config import settings
from src.core.logging import logger


class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass


class LocalEmbeddingService(BaseEmbeddingService):
    """Local embedding service using sentence-transformers directly."""

    def __init__(self, model_name: str = settings.embedding_model):
        logger.info(f"Initializing local embeddings: {model_name}")
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info(f"Loaded embedding model: {model_name}")

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI embedding service."""

    def __init__(self, api_key: Optional[str] = None):
        logger.info("Initializing OpenAI embeddings")
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = "text-embedding-3-small"

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
        )
        return response.data[0].embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model,
        )
        return [item.embedding for item in response.data]


def get_embedding_service() -> BaseEmbeddingService:
    """Factory function to get appropriate embedding service."""
    if settings.use_local_embeddings:
        return LocalEmbeddingService()
    else:
        return OpenAIEmbeddingService()