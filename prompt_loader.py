"""Utility module for loading prompts from YAML files."""
import yaml
from pathlib import Path
from typing import Dict, Any


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> Dict[str, str]:
    """
    Load a prompt from a YAML file.
    
    Args:
        filename: Name of the YAML file (e.g., "intent_extraction.yaml")
        
    Returns:
        Dictionary containing prompt components (system, human, etc.)
    """
    prompt_file = PROMPTS_DIR / filename
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_data = yaml.safe_load(f)
    
    return prompt_data


def get_system_prompt(filename: str) -> str:
    """Get the system prompt from a YAML file."""
    prompt_data = load_prompt(filename)
    return prompt_data.get('system', '')


def get_human_prompt(filename: str) -> str:
    """Get the human/user prompt from a YAML file."""
    prompt_data = load_prompt(filename)
    return prompt_data.get('human', '')


def get_few_shot_example(filename: str) -> str:
    """Get the few-shot example from a YAML file (if present)."""
    prompt_data = load_prompt(filename)
    return prompt_data.get('few_shot_example', '')
