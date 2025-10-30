"""Rendering - Validated DaC Code → Visual Artifact"""
import subprocess
import os
from pathlib import Path
from config import OUTPUT_DIR, RENDER_FORMAT, GRAPHVIZ_FORMAT
from typing import Tuple


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def render_diagram(dot_code: str, filename: str = "diagram") -> Tuple[str, str]:
    """
    Render graphviz code to a visual artifact (SVG/PNG/PDF).
    
    Args:
        dot_code: Valid graphviz dot code
        filename: Base filename for output (without extension)
        
    Returns:
        Tuple[str, str]: (output_file_path, source_code_file_path)
    """
    output_dir = ensure_output_dir()
    
    # Determine output format
    format_ext = GRAPHVIZ_FORMAT.lower()
    output_file = output_dir / f"{filename}.{format_ext}"
    source_file = output_dir / f"{filename}.dot"
    
    # Save source code
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(dot_code)
    
    try:
        # Use graphviz to render
        result = subprocess.run(
            ['dot', f'-T{format_ext}', '-o', str(output_file)],
            input=dot_code,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown rendering error"
            raise RuntimeError(f"Rendering failed: {error_msg}")
        
        return str(output_file), str(source_file)
        
    except FileNotFoundError:
        raise RuntimeError(
            "Graphviz 'dot' command not found. Please install graphviz:\n"
            "  macOS: brew install graphviz\n"
            "  Ubuntu/Debian: sudo apt-get install graphviz\n"
            "  Windows: Download from https://graphviz.org/download/"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Rendering timed out")


def display_results(output_file: str, source_file: str):
    """
    Display information about the generated diagram files.
    
    Args:
        output_file: Path to the rendered diagram file
        source_file: Path to the source dot file
    """
    print("\n" + "="*60)
    print("DIAGRAM GENERATION COMPLETE")
    print("="*60)
    print(f"\nRendered diagram: {output_file}")
    print(f"Source code: {source_file}")
    print(f"\nYou can view the diagram by opening: {output_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test rendering
    test_code = """digraph Test {
    A [label="Start", shape=box]
    B [label="Process", shape=ellipse]
    C [label="End", shape=box]
    
    A -> B [label="begin"]
    B -> C [label="complete"]
}"""
    
    try:
        output, source = render_diagram(test_code, "test_diagram")
        display_results(output, source)
    except Exception as e:
        print(f"Error: {e}")
