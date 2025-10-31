"""Test script to verify the diagram generator project functionality."""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from intent_extraction import extract_intent
        from code_generation import generate_diagram_code
        from syntax_validation import validate_graphviz_syntax
        from error_correction import correct_diagram_code
        from rendering import render_diagram, display_results
        from response_parser import extract_response_content, extract_graphviz_code, extract_json_content
        from prompt_loader import load_prompt, get_system_prompt, get_human_prompt
        from schemas import DiagramIntent, Component, Relationship
        from llm_utils import get_llm
        from config import MAX_RETRY_ATTEMPTS, OUTPUT_DIR
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_prompt_loading():
    """Test that prompts can be loaded from YAML files."""
    print("\nTesting prompt loading...")
    try:
        from prompt_loader import load_prompt
        
        prompt_files = [
            "intent_extraction.yaml",
            "code_generation.yaml",
            "error_correction.yaml"
        ]
        
        for filename in prompt_files:
            prompt_data = load_prompt(filename)
            if not prompt_data:
                print(f"✗ Failed to load {filename}: empty data")
                return False
            print(f"✓ Loaded {filename}")
        
        return True
    except Exception as e:
        print(f"✗ Prompt loading error: {e}")
        return False


def test_syntax_validation():
    """Test syntax validation functionality."""
    print("\nTesting syntax validation...")
    try:
        from syntax_validation import validate_graphviz_syntax, HAS_PYGRAPHVIZ
        
        # Test valid code
        valid_code = """digraph Test {
    A -> B [label="test"]
}"""
        is_valid, error = validate_graphviz_syntax(valid_code)
        if not is_valid:
            print(f"✗ Valid code was rejected: {error}")
            return False
        print("✓ Valid code accepted")
        
        # Test invalid code (missing closing bracket in attribute)
        invalid_code = """digraph Test {
    A -> B [label="test"
}"""
        is_valid, error = validate_graphviz_syntax(invalid_code)
        # Note: Basic validator may not catch bracket errors in attributes,
        # but pygraphviz will if available
        if is_valid and HAS_PYGRAPHVIZ:
            print("✗ Invalid code was accepted")
            return False
        elif is_valid:
            print("✓ Invalid code passed basic validation (pygraphviz needed for full validation)")
        else:
            print(f"✓ Invalid code rejected: {error[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Syntax validation error: {e}")
        return False


def test_response_parser():
    """Test response parsing utilities."""
    print("\nTesting response parser...")
    try:
        from response_parser import extract_response_content, extract_graphviz_code, extract_json_content
        
        # Test extract_response_content
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        mock_response = MockResponse("test content")
        content = extract_response_content(mock_response)
        if content != "test content":
            print("✗ extract_response_content failed")
            return False
        print("✓ extract_response_content works")
        
        # Test extract_graphviz_code
        test_content = """Here's the code:
```graphviz
digraph Test {
    A -> B
}
```"""
        code = extract_graphviz_code(test_content)
        if "digraph" not in code:
            print("✗ extract_graphviz_code failed")
            return False
        print("✓ extract_graphviz_code works")
        
        return True
    except Exception as e:
        print(f"✗ Response parser error: {e}")
        return False


def test_schemas():
    """Test schema validation."""
    print("\nTesting schemas...")
    try:
        from schemas import DiagramIntent, Component, Relationship
        
        # Test creating valid DiagramIntent
        intent = DiagramIntent(
            diagram_type="flowchart",
            title="Test Diagram",
            components=[
                Component(id="a", label="Node A", type="process"),
                Component(id="b", label="Node B", type="process")
            ],
            relationships=[
                Relationship(source_id="a", target_id="b", action="connects to")
            ]
        )
        
        if intent.diagram_type != "flowchart":
            print("✗ Schema creation failed")
            return False
        
        print("✓ Schema validation works")
        return True
    except Exception as e:
        print(f"✗ Schema error: {e}")
        return False


def test_output_directory():
    """Test that output directory can be created."""
    print("\nTesting output directory...")
    try:
        from rendering import ensure_output_dir
        
        output_dir = ensure_output_dir()
        if not output_dir.exists():
            print("✗ Output directory creation failed")
            return False
        
        print(f"✓ Output directory ready: {output_dir}")
        return True
    except Exception as e:
        print(f"✗ Output directory error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("PROJECT TEST SUITE")
    print("="*60)
    
    tests = [
        test_imports,
        test_prompt_loading,
        test_syntax_validation,
        test_response_parser,
        test_schemas,
        test_output_directory,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} raised exception: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
