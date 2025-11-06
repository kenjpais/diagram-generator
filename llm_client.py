from settings import AppSettings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
import os

class LLMClient:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.llm = self.get_llm()
        self.code_gen_llm = self.get_code_gen_llm()

    def get_llm(self):
        if self.settings.code_gen_llm_provider == "gemini":
            api_key = self.settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
            if not api_key:
                # Check if ADC might be interfering
                if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                    raise ValueError(
                        "GEMINI_API_KEY is required but not set. "
                        "Application Default Credentials (ADC) detected via GOOGLE_APPLICATION_CREDENTIALS, "
                        "but ADC may not have sufficient scopes for the Generative Language API. "
                        "Please set GEMINI_API_KEY environment variable instead. "
                        "Get an API key from: https://makersuite.google.com/app/apikey"
                    )
                raise ValueError(
                    "GEMINI_API_KEY is required but not set. "
                    "Please set it as an environment variable or in your settings. "
                    "Get an API key from: https://makersuite.google.com/app/apikey"
                )
            return ChatGoogleGenerativeAI(
                model=self.settings.gemini_model, 
                google_api_key=api_key, 
                temperature=0.1
            )
        else:
            return ChatOllama(
                model=self.settings.code_gen_llm_model, 
                base_url=self.settings.ollama_base_url, 
                temperature=0.1
            )

    def get_code_gen_llm(self):
        if self.settings.code_gen_llm_provider == "gemini":
            api_key = self.settings.code_gen_llm_api_key or os.getenv("CODE_GEN_LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
            if not api_key:
                # Check if ADC might be interfering
                if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                    raise ValueError(
                        "API key is required for code generation but not set. "
                        "Application Default Credentials (ADC) detected via GOOGLE_APPLICATION_CREDENTIALS, "
                        "but ADC may not have sufficient scopes for the Generative Language API. "
                        "Please set CODE_GEN_LLM_API_KEY or GEMINI_API_KEY environment variable instead. "
                        "Get an API key from: https://makersuite.google.com/app/apikey"
                    )
                raise ValueError(
                    "API key is required for code generation but not set. "
                    "Please set CODE_GEN_LLM_API_KEY or GEMINI_API_KEY as an environment variable. "
                    "Get an API key from: https://makersuite.google.com/app/apikey"
                )
            return ChatGoogleGenerativeAI(
                model=self.settings.code_gen_llm_model, 
                google_api_key=api_key, 
                temperature=0.1
            )
        else:
            return ChatOllama(
                model=self.settings.code_gen_llm_model, 
                base_url=self.settings.ollama_base_url, 
                temperature=0.1
            )