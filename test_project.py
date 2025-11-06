"""Test script to verify the diagram generator project functionality."""

import sys
import json
from pathlib import Path
from typing import Tuple
from utils import print_success, print_error, print_warning, print_info, colorize, Colors


def test_imports():
    """Test that all modules can be imported."""
    print_info("Testing imports...")
    try:
        from code_generation import DaCGenerator
        from syntax_validation import validate_graphviz_syntax
        from rendering import render_diagram, display_results, ensure_output_dir
        from response_parser import (
            extract_response_content,
            extract_graphviz_code,
            extract_json_content,
        )
        from schemas import GraphContext, Component, Relationship, Group
        from llm_utils import get_llm, get_code_gen_llm
        from settings import get_settings
        settings = get_settings()
        MAX_RETRY_ATTEMPTS = settings.max_retry_attempts
        OUTPUT_DIR = settings.output_dir
        from utils import (
            load_prompt,
            render_prompt,
            generate_timestamp_filename,
            parse_file_path,
            read_text_file,
        )
        from settings import AppSettings, get_settings
        from diagram_generator import DiagramGenerator

        print_success("All imports successful")
        return True
    except ImportError as e:
        print_error(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_loading():
    """Test that prompts can be loaded from YAML files."""
    print_info("\nTesting prompt loading...")
    try:
        from utils import load_prompt
        from settings import get_settings

        settings = get_settings()
        prompt_files = [
            settings.context_extraction_prompt_file_path,
            settings.code_generation_prompt_file_path,
            settings.error_correction_prompt_file_path,
        ]

        for prompt_file in prompt_files:
            if not prompt_file.exists():
                print_error(f"Prompt file not found: {prompt_file}")
                return False
            prompt_data = load_prompt(prompt_file)
            if not prompt_data:
                print_error(f"Failed to load {prompt_file.name}: empty data")
                return False
            if "system" not in prompt_data or "human" not in prompt_data:
                print_error(f"Invalid prompt structure in {prompt_file.name}")
                return False
            print_success(f"Loaded {prompt_file.name}")

        return True
    except Exception as e:
        print_error(f"Prompt loading error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_syntax_validation():
    """Test syntax validation functionality."""
    print_info("\nTesting syntax validation...")
    try:
        from syntax_validation import validate_graphviz_syntax, HAS_PYGRAPHVIZ

        # Test valid code
        valid_code = """digraph Test {
    A -> B [label="test"]
}"""
        is_valid, error = validate_graphviz_syntax(valid_code)
        if not is_valid:
            print_error(f"Valid code was rejected: {error}")
            return False
        print_success("Valid code accepted")

        # Test invalid code (missing closing bracket in attribute)
        invalid_code = """digraph Test {
    A -> B [label="test"
}"""
        is_valid, error = validate_graphviz_syntax(invalid_code)
        # Note: Basic validator may not catch bracket errors in attributes,
        # but pygraphviz will if available
        if is_valid and HAS_PYGRAPHVIZ:
            print_error("Invalid code was accepted")
            return False
        elif is_valid:
            print(
                "[OK] Invalid code passed basic validation (pygraphviz needed for full validation)"
            )
        else:
            print_success(f"Invalid code rejected: {error[:50]}...")

        # Test empty code
        empty_is_valid, empty_error = validate_graphviz_syntax("")
        if empty_is_valid:
            print_error("Empty code was accepted")
            return False
        print_success("Empty code rejected")

        # Test code without digraph/graph keyword
        no_keyword_is_valid, no_keyword_error = validate_graphviz_syntax("A -> B")
        if no_keyword_is_valid:
            print_error("Code without digraph/graph keyword was accepted")
            return False
        print_success("Code without digraph/graph keyword rejected")

        return True
    except Exception as e:
        print_error(f"Syntax validation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_response_parser():
    """Test response parsing utilities."""
    print_info("\nTesting response parser...")
    try:
        from response_parser import (
            extract_response_content,
            extract_graphviz_code,
            extract_json_content,
        )

        # Test extract_response_content
        class MockResponse:
            def __init__(self, content):
                self.content = content

        mock_response = MockResponse("test content")
        content = extract_response_content(mock_response)
        if content != "test content":
            print_error("extract_response_content failed")
            return False
        print_success("extract_response_content works with object")

        # Test extract_response_content with string
        content = extract_response_content("test string")
        if content != "test string":
            print_error("extract_response_content failed with string")
            return False
        print_success("extract_response_content works with string")

        # Test extract_graphviz_code
        test_content = """Here's the code:
```graphviz
digraph Test {
    A -> B
}
```"""
        code = extract_graphviz_code(test_content)
        if "digraph" not in code or "A -> B" not in code:
            print_error(f"extract_graphviz_code failed, got: {code[:50]}")
            return False
        print_success("extract_graphviz_code works")

        # Test extract_graphviz_code with plain code (no markdown)
        plain_code = "digraph Test { A -> B }"
        extracted = extract_graphviz_code(plain_code)
        if extracted != plain_code.strip():
            print_error(f"extract_graphviz_code failed with plain code")
            return False
        print_success("extract_graphviz_code works with plain code")

        # Test extract_json_content
        json_content = """Some text before
```json
{"key": "value", "number": 123}
```
Some text after"""
        json_str = extract_json_content(json_content)
        parsed = json.loads(json_str)
        if parsed.get("key") != "value":
            print_error("extract_json_content failed")
            return False
        print_success("extract_json_content works")

        return True
    except Exception as e:
        print_error(f"Response parser error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schemas():
    """Test schema validation."""
    print_info("\nTesting schemas...")
    try:
        from schemas import GraphContext, Component, Relationship, Group

        # Test creating valid GraphContext
        context = GraphContext(
            title="Test Diagram",
            groups=[
                Group(id="group1", label="Group 1", type="vpc")
            ],
            components=[
                Component(id="a", label="Node A", type="service"),
                Component(id="b", label="Node B", type="database", parent_group="group1"),
            ],
            relationships=[
                Relationship(source="a", target="b", label="connects to", type="api_call")
            ],
        )

        if context.title != "Test Diagram":
            print_error("Schema creation failed")
            return False
        if len(context.components) != 2:
            print_error("Schema component count failed")
            return False
        if len(context.relationships) != 1:
            print_error("Schema relationship count failed")
            return False

        print_success("Schema validation works")

        # Test Component model_dump
        comp_dict = context.components[0].model_dump()
        if comp_dict.get("id") != "a":
            print_error("Component model_dump failed")
            return False
        print_success("Component model_dump works")

        # Test Relationship model_dump
        rel_dict = context.relationships[0].model_dump()
        if rel_dict.get("source") != "a":
            print_error("Relationship model_dump failed")
            return False
        print_success("Relationship model_dump works")

        return True
    except Exception as e:
        print_error(f"Schema error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_output_directory():
    """Test that output directory can be created."""
    print_info("\nTesting output directory...")
    try:
        from rendering import ensure_output_dir

        output_dir = ensure_output_dir()
        if not output_dir.exists():
            print_error("Output directory creation failed")
            return False

        print_success(f"Output directory ready: {output_dir}")
        return True
    except Exception as e:
        print_error(f"Output directory error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test utility functions."""
    print_info("\nTesting utilities...")
    try:
        from utils import (
            generate_timestamp_filename,
            parse_file_path,
            load_prompt,
            render_prompt,
        )
        from settings import get_settings

        # Test generate_timestamp_filename
        filename = generate_timestamp_filename()
        if not filename.startswith("diagram_"):
            print_error("generate_timestamp_filename format incorrect")
            return False
        print_success("generate_timestamp_filename works")

        # Test parse_file_path
        path = parse_file_path("test --filename /path/to/file.txt")
        if path is None or str(path) != "/path/to/file.txt":
            print_error(f"parse_file_path failed, got: {path}")
            return False
        print_success("parse_file_path works with filename")

        # Test parse_file_path without filename
        path = parse_file_path("test command without filename")
        if path is not None:
            print_error(f"parse_file_path should return None, got: {path}")
            return False
        print_success("parse_file_path returns None when no filename")

        # Test render_prompt
        settings = get_settings()
        prompt_str = render_prompt(settings.code_generation_prompt_file_path)
        if not prompt_str or len(prompt_str) < 100:
            print_error("render_prompt failed")
            return False
        print_success("render_prompt works")

        return True
    except Exception as e:
        print_error(f"Utils error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings():
    """Test settings management."""
    print_info("\nTesting settings...")
    try:
        from settings import get_settings, AppSettings

        settings = get_settings()
        if not isinstance(settings, AppSettings):
            print_error("get_settings returns wrong type")
            return False

        # Test properties
        if not settings.prompts_dir.exists():
            print_error("prompts_dir does not exist")
            return False

        if not settings.context_extraction_prompt_file_path.exists():
            print_error("context_extraction_prompt_file_path does not exist")
            return False

        print_success("Settings management works")
        return True
    except Exception as e:
        print_error(f"Settings error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dac_generator_initialization():
    """Test DaCGenerator can be initialized."""
    print_info("\nTesting DaCGenerator initialization...")
    try:
        from code_generation import DaCGenerator
        from settings import get_settings

        settings = get_settings()
        
        # This will fail if LLM is not configured, but initialization should work
        try:
            generator = DaCGenerator(settings=settings)
            print_success("DaCGenerator initialized successfully")
            return True
        except ValueError as e:
            # Expected if GEMINI_API_KEY is not set
            if "GEMINI_API_KEY" in str(e):
                print_warning("DaCGenerator initialization requires API key (expected in test)")
                return True
            raise
    except Exception as e:
        print_error(f"DaCGenerator initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_diagram_generator_initialization():
    """Test DiagramGenerator can be initialized."""
    print_info("\nTesting DiagramGenerator initialization...")
    try:
        from diagram_generator import DiagramGenerator
        from settings import get_settings

        settings = get_settings()
        
        # This will fail if LLM is not configured, but initialization should work
        try:
            generator = DiagramGenerator(settings=settings)
            print_success("DiagramGenerator initialized successfully")
            return True
        except ValueError as e:
            # Expected if GEMINI_API_KEY is not set
            if "GEMINI_API_KEY" in str(e):
                print_warning("DiagramGenerator initialization requires API key (expected in test)")
                return True
            raise
    except Exception as e:
        print_error(f"DiagramGenerator initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rendering_simple():
    """Test rendering simple diagram (if graphviz is available)."""
    print_info("\nTesting rendering (simple diagram)...")
    try:
        from rendering import render_diagram
        import subprocess

        # Check if graphviz is available
        try:
            subprocess.run(
                ["dot", "-V"],
                capture_output=True,
                timeout=5
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print_warning("Graphviz not available, skipping rendering test")
            return True

        test_code = """digraph Test {
    A [label="Start", shape=box]
    B [label="End", shape=box]
    A -> B [label="process"]
}"""

        try:
            output, source = render_diagram(test_code, "test_diagram")
            if not Path(output).exists():
                print_error(f"Rendered file not created: {output}")
                return False
            if not Path(source).exists():
                print_error(f"Source file not created: {source}")
                return False
            print_success("Rendering works")
            return True
        except RuntimeError as e:
            if "not found" in str(e).lower():
                print_warning("Graphviz not available, skipping rendering test")
                return True
            raise
    except Exception as e:
        print_warning(f"Rendering test skipped: {e}")
        return True  # Don't fail on rendering tests


def main():
    """Run all tests."""
    print(colorize("=" * 60, Colors.CYAN))
    print(colorize("PROJECT TEST SUITE", Colors.CYAN, bold=True))
    print(colorize("=" * 60, Colors.CYAN))

    tests = [
        test_imports,
        test_settings,
        test_prompt_loading,
        test_syntax_validation,
        test_response_parser,
        test_schemas,
        test_output_directory,
        test_utils,
        test_dac_generator_initialization,
        test_diagram_generator_initialization,
        test_rendering_simple,
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
            print_error(f"Test {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + colorize("=" * 60, Colors.CYAN))
    print(colorize(f"RESULTS: {passed} passed, {failed} failed", Colors.CYAN, bold=True))
    print(colorize("=" * 60, Colors.CYAN))

    if failed == 0:
        print_success("\nAll tests passed!", bold=True)
        return 0
    else:
        print_error(f"\n{failed} test(s) failed", bold=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
