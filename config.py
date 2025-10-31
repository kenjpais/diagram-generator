"""Configuration settings for the diagram generator."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # Options: "ollama" or "gemini"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")  # Ollama model name (when using Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")  # Gemini model name

# Code Generation LLM Configuration (uses Gemini by default)
CODE_GEN_LLM_PROVIDER = os.getenv("CODE_GEN_LLM_PROVIDER", "gemini")

# Retry Configuration
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
RENDER_FORMAT = os.getenv("RENDER_FORMAT", "svg")  # Options: svg, png, pdf

# Graphviz Configuration
GRAPHVIZ_FORMAT = RENDER_FORMAT