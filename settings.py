"""
Centralized settings management file.
"""

from pathlib import Path
import os
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv()


class AppSettings(BaseSettings):
    """Main application settings that combines all other settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    app_name: str = Field(default="ai-diagram-generator", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-pro", alias="GEMINI_MODEL")
    code_gen_llm_provider: str = Field(default="gemini", alias="CODE_GEN_LLM_PROVIDER")
    code_gen_llm_model: str = Field(default="gemini-2.5-pro", alias="CODE_GEN_LLM_MODEL")
    code_gen_llm_api_key: str = Field(default="", alias="CODE_GEN_LLM_API_KEY")
    max_retry_attempts: int = Field(default=3, alias="MAX_RETRY_ATTEMPTS")  
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    output_dir: str = Field(default="output", alias="OUTPUT_DIR")
    render_format: str = Field(default="svg", alias="RENDER_FORMAT")
    graphviz_format: str = Field(default="svg", alias="GRAPHVIZ_FORMAT")

    @model_validator(mode="after")
    def set_gemini_api_key_from_google_api_key(self):
        """Support GOOGLE_API_KEY as an alias for GEMINI_API_KEY."""
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GOOGLE_API_KEY", "")
        return self

    @property
    def data_dir(self) -> Path:
        """Get the data directory."""
        return Path(__file__).parent / "data"

    @property
    def prompts_dir(self) -> Path:
        """Get the prompts directory."""
        return Path(__file__).parent / "prompts"

    @property
    def context_extraction_prompt_file_path(self) -> Path:
        """Get the context extraction prompt file path."""
        return self.prompts_dir / "context_extraction.yaml"

    @property
    def code_generation_prompt_file_path(self) -> Path:
        """Get the code generation prompt file path."""
        return self.prompts_dir / "code_generation.yaml"

    @property
    def error_correction_prompt_file_path(self) -> Path:
        """Get the error correction prompt file path."""
        return self.prompts_dir / "error_correction.yaml"


def get_settings() -> AppSettings:
    """Get the settings."""
    return AppSettings()
