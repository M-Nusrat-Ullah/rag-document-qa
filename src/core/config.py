"""Application configuration management."""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Info
    app_name: str = "RAG Document Q&A"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # OpenAI Settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = "gpt-3.5-turbo"
    
    # Embedding Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    use_local_embeddings: bool = True  # Set False to use OpenAI embeddings
    
    # Vector Store Settings
    chroma_persist_directory: str = "./data/chroma_db"
    collection_name: str = "documents"
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # MLflow Settings (Phase 2)
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "rag-experiments"
    
    # Redis Settings (Future)
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()