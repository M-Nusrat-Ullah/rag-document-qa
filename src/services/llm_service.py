"""LLM service supporting Ollama, DeepSeek, OpenAI, and Google Gemini."""

from typing import Optional
from abc import ABC, abstractmethod

from src.core.config import settings
from src.core.logging import logger


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    model: str

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        pass


class OllamaLLMService(BaseLLMService):
    """Ollama local LLM service - completely FREE!"""

    def __init__(
        self,
        model: str = settings.ollama_model,
        base_url: str = settings.ollama_base_url,
    ):
        logger.info(f"Initializing Ollama LLM: {model}")
        import ollama

        self.client = ollama.Client(host=base_url)
        self.model = model

        # Verify model is available
        try:
            self.client.show(model)
            logger.info(f"Ollama model '{model}' is ready")
        except Exception:
            logger.warning(
                f"Model '{model}' not found. Pulling it now..."
            )
            self.client.pull(model)
            logger.info(f"Model '{model}' pulled successfully")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"Generating response with Ollama {self.model}")
        response = self.client.chat(
            model=self.model,
            messages=messages,
        )
        return response["message"]["content"]


class DeepSeekLLMService(BaseLLMService):
    """DeepSeek Chinese LLM service."""

    def __init__(
        self,
        model: str = settings.deepseek_model,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        logger.info(f"Initializing DeepSeek LLM: {model}")
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key or settings.deepseek_api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = model
        self.temperature = temperature

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"Generating response with DeepSeek {self.model}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service."""

    def __init__(
        self,
        model: str = settings.openai_model,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        logger.info(f"Initializing OpenAI LLM: {model}")
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model
        self.temperature = temperature

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"Generating response with {self.model}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content


class GoogleLLMService(BaseLLMService):
    """Google Gemini LLM service."""

    def __init__(
        self,
        model: str = settings.google_model,
        api_key: Optional[str] = None,
    ):
        logger.info(f"Initializing Google Gemini LLM: {model}")
        from google import genai

        self.client = genai.Client(api_key=api_key or settings.google_api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        full_prompt = ""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        logger.info(f"Generating response with {self.model}")
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
        )
        return response.text


# RAG Prompts
RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.

Instructions:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say "I don't have enough information to answer this question based on the provided documents."
3. Be concise but comprehensive
4. Do not make up information"""

RAG_USER_PROMPT_TEMPLATE = """Context:
{context}

---

Question: {question}

Please provide a helpful answer based on the context above."""


def get_llm_service() -> BaseLLMService:
    """Factory function to get LLM service based on config."""
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        return OllamaLLMService()
    elif provider == "deepseek":
        return DeepSeekLLMService()
    elif provider == "google":
        return GoogleLLMService()
    else:
        return OpenAILLMService()