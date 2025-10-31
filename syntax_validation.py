"""Syntax Validation - DaC Code → Error Check"""
from typing import Tuple, Optional

# Try to import pygraphviz, with fallback
try:
    import pygraphviz as pgv
    HAS_PYGRAPHVIZ = True
except ImportError:
    HAS_PYGRAPHVIZ = False
    pgv = None


def validate_graphviz_syntax(dot_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate graphviz syntax using pygraphviz library or fallback validation.
    
    This function ONLY validates syntax - it does NOT generate code.
    Code generation is handled by the LLM in code_generation.py
    
    Args:
        dot_code: Graphviz dot code as string
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
        - If valid: (True, None)
        - If invalid: (False, error_message)
    """
    if HAS_PYGRAPHVIZ:
        try:
            # Attempt to parse the graphviz code
            # If parsing succeeds, the code is valid
            pgv.AGraph(string=dot_code)
            return True, None
        except pgv.agraph.DotError as e:
            # Return the error message from pygraphviz
            error_message = str(e)
            return False, error_message
        except Exception as e:
            # Handle any other unexpected errors
            return False, f"Validation error: {str(e)}"
    else:
        # Fallback to basic validation
        return _validate_graphviz_basic(dot_code)


def _validate_graphviz_basic(dot_code: str) -> Tuple[bool, Optional[str]]:
    """
    Basic graphviz syntax validation without pygraphviz.
    
    Args:
        dot_code: Graphviz dot code as string
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    code = dot_code.strip()
    
    # Check if code starts with digraph or graph
    if not (code.startswith("digraph") or code.startswith("graph")):
        return False, "Diagram must start with 'digraph' or 'graph' keyword"
    
    # Check for balanced braces using stack-based approach
    brace_count = 0
    in_string = False
    escape_next = False
    
    for char in code:
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count < 0:
                    return False, "Closing brace without matching opening brace"
    
    if brace_count != 0:
        return False, f"Unbalanced braces: {brace_count} unclosed opening brace(s)"
    
    # Check for basic structure
    if '{' not in code:
        return False, "Missing opening brace"
    
    if '}' not in code:
        return False, "Missing closing brace"
    
    # Check for basic node/edge syntax
    if '->' not in code and '--' not in code and '[' not in code:
        # Might be valid, but suspicious - let it pass basic check
        pass
    
    # Basic validation passed
    return True, None


if __name__ == "__main__":
    # Test with valid code
    valid_code = """digraph Test {
    A -> B [label="test"]
}"""
    is_valid, error = validate_graphviz_syntax(valid_code)
    print(f"Valid code test: {is_valid}, error: {error}")
    
    # Test with invalid code
    invalid_code = """digraph Test {
    A -> B [label="test"
}"""
    is_valid, error = validate_graphviz_syntax(invalid_code)
    print(f"Invalid code test: {is_valid}, error: {error}")