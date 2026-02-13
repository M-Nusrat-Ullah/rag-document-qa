"""LLM service for generating responses."""

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from src.core.config import settings
from src.core.logging import logger


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response."""
        pass


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service."""
    
    def __init__(
        self,
        model: str = settings.openai_model,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ):
        logger.info(f"Initializing OpenAI LLM: {model}")
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key or settings.openai_api_key,
            temperature=temperature
        )
        self.model = model
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using OpenAI."""
        
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        logger.info(f"Generating response with {self.model}")
        response = self.llm.invoke(messages)
        
        return response.content


# RAG-specific prompt templates
RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.

Instructions:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say "I don't have enough information to answer this question based on the provided documents."
3. Be concise but comprehensive
4. If relevant, mention which part of the context your answer is based on
5. Do not make up information"""

RAG_USER_PROMPT_TEMPLATE = """Context:
{context}

---

Question: {question}

Please provide a helpful answer based on the context above."""


def get_llm_service() -> BaseLLMService:
    """Factory function to get LLM service."""
    return OpenAILLMService()