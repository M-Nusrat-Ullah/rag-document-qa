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

    # LLM Provider: "ollama", "deepseek", "google", "openai"
    llm_provider: str = "ollama"

    # Ollama Settings (Local)
    ollama_model: str = "qwen2.5:3b"
    ollama_base_url: str = "http://localhost:11434"

    # DeepSeek Settings
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_model: str = "deepseek-chat"

    # OpenAI Settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = "gpt-3.5-turbo"

    # Google Gemini Settings
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_model: str = "gemini-2.0-flash"

    # Embedding Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    use_local_embeddings: bool = True

    # Vector Store Settings
    chroma_persist_directory: str = "./data/chroma_db"
    collection_name: str = "documents"

    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # MLflow Settings
    mlflow_enabled: bool = True
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "rag-document-qa"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()