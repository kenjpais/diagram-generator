"""Shared utility functions for LLM initialization across all steps."""
from config import (
    LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL,
    GEMINI_API_KEY, GEMINI_MODEL,
    CODE_GEN_LLM_PROVIDER
)


def get_llm():
    """
    Initialize and return the LLM based on configuration.
    
    Supports both Ollama and Gemini providers.
    This function is shared across all steps to ensure consistent LLM initialization.
    """
    if LLM_PROVIDER.lower() == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required when using Gemini")
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
    else:
        # Default to Ollama
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1
        )


def get_code_gen_llm():
    """
    Initialize and return the LLM for code generation.
    
    Uses Gemini by default for better code generation quality.
    """
    if CODE_GEN_LLM_PROVIDER.lower() == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required when using Gemini for code generation")
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
    elif CODE_GEN_LLM_PROVIDER.lower() == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1
        )
    else:
        # Fallback to main LLM provider
        return get_llm()
