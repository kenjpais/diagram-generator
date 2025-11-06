"""Utility module for parsing LLM responses and extracting code."""

import re
from typing import Optional


def extract_response_content(response) -> str:
    """
    Extract text content from an LLM response object.

    Args:
        response: LLM response object (can have .content attribute or be a string)

    Returns:
        str: Text content from the response
    """
    if hasattr(response, "content"):
        return response.content
    else:
        return str(response)


def extract_code_block(content: str, language: Optional[str] = None) -> str:
    """
    Extract code from a markdown code block in the response.

    Args:
        content: Response content that may contain code blocks
        language: Optional language identifier (e.g., "graphviz", "json")
                  If provided, will prioritize blocks with this language

    Returns:
        str: Extracted code without markdown formatting
    """
    content = content.strip()

    # Try to find code block with specific language first
    if language:
        pattern = f"```{language}.*?```"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            code = matches[0]
            # Remove the language identifier and backticks
            code = code.replace(f"```{language}", "").replace("```", "").strip()
            return code

    # Try any code block
    if "```" in content:
        parts = content.split("```")
        if len(parts) >= 3:
            # Get the first code block
            code = parts[1].strip()

            # Remove language identifier if present
            lines = code.split("\n")
            first_line = lines[0].strip()

            # Check if first line is a language identifier
            if not (
                first_line.startswith("digraph")
                or first_line.startswith("graph")
                or first_line.startswith("{")
                or first_line.startswith("[")
            ):
                # Likely a language identifier, remove it
                code = "\n".join(lines[1:])

            return code.strip()

    # No code block found, return as-is
    return content


def extract_graphviz_code(content: str) -> str:
    """
    Extract graphviz code from LLM response.
    Removes markdown formatting and common prefixes.

    Args:
        content: Raw response content from LLM

    Returns:
        str: Clean graphviz code
    """
    # First try to extract from code block
    code = extract_code_block(content, language="graphviz")

    if not code:
        # Try without language specification
        code = extract_code_block(content)

    # Remove common prefixes that LLMs sometimes add
    prefixes_to_remove = [
        "Let's think step-by-step:",
        "Here's the graphviz code:",
        "Generated code:",
        "Here is the corrected code:",
    ]

    for prefix in prefixes_to_remove:
        if code.startswith(prefix):
            code = code[len(prefix) :].strip()
            # Also handle case where prefix Immediately might be followed by newline
            if code.startswith("\n"):
                code = code[1:].strip()

    return code.strip()


def extract_json_content(content: str) -> str:
    """
    Extract JSON content from LLM response.

    Args:
        content: Raw response content from LLM

    Returns:
        str: Extracted JSON string (empty if not found)
    """
    import json
    
    content = content.strip()
    if not content:
        return ""
    
    # First, try parsing the entire content as JSON (in case LLM returns raw JSON)
    try:
        json.loads(content)
        return content
    except json.JSONDecodeError:
        pass
    
    # Try to extract from JSON code block
    json_str = extract_code_block(content, language="json")
    
    # Validate that it's actually JSON
    if json_str and json_str != content:
        try:
            json.loads(json_str)
            return json_str.strip()
        except json.JSONDecodeError:
            pass  # Continue to try other methods
    
    # Try without language specification
    json_str = extract_code_block(content)
    
    # Validate that it's actually JSON (and different from original content)
    if json_str and json_str != content:
        try:
            json.loads(json_str)
            return json_str.strip()
        except json.JSONDecodeError:
            pass  # Continue to try brace matching
    
    # Try to find JSON object in the content using brace matching
    # Look for the first { that starts a JSON object and match braces
    brace_count = 0
    start_pos = -1
    
    for i, char in enumerate(content):
        if char == '{':
            if brace_count == 0:
                start_pos = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_pos != -1:
                json_obj_match = content[start_pos:i+1]
                try:
                    json.loads(json_obj_match)
                    return json_obj_match.strip()
                except json.JSONDecodeError:
                    # Continue searching for next JSON object
                    start_pos = -1
                    continue
    
    # If no valid JSON found, return empty string
    return ""
