"""Configuration settings for the diagram generator."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration (Ollama only)
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")  # Ollama model name
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Retry Configuration
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
RENDER_FORMAT = os.getenv("RENDER_FORMAT", "svg")  # Options: svg, png, pdf

# Graphviz Configuration
GRAPHVIZ_FORMAT = RENDER_FORMAT
