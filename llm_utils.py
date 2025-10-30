"""Shared utility functions for LLM initialization across all steps."""
from config import LLM_MODEL, OLLAMA_BASE_URL


def get_llm():
    """
    Initialize and return the Ollama LLM.
    
    This function is shared across all steps to ensure consistent LLM initialization.
    """
    from langchain_community.chat_models import ChatOllama
    return ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1
    )
