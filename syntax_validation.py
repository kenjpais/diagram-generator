"""Syntax Validation - DaC Code → Error Check"""
import pygraphviz as pgv
from typing import Tuple, Optional


def validate_graphviz_syntax(dot_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate graphviz syntax using pygraphviz library.
    
    Args:
        dot_code: Graphviz dot code as string
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
        - If valid: (True, None)
        - If invalid: (False, error_message)
    """
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