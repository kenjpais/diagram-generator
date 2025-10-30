"""Main orchestration script for the AI Diagram Generator."""
import sys
from typing import Optional
from intent_extraction import extract_intent
from code_generation import generate_diagram_code
from syntax_validation import validate_graphviz_syntax
from error_correction import correct_diagram_code
from rendering import render_diagram, display_results
from config import MAX_RETRY_ATTEMPTS


def generate_diagram(user_request: str, output_filename: Optional[str] = None) -> tuple:
    """
    Execute the complete 5-step diagram generation workflow.
    
    Args:
        user_request: Natural language request from user
        output_filename: Optional filename for output (without extension)
        
    Returns:
        tuple: (rendered_file_path, source_file_path)
    """
    if output_filename is None:
        output_filename = "generated_diagram"
    
    print("="*60)
    print("AI DIAGRAM GENERATOR")
    print("="*60)
    print(f"\nUser Request: {user_request}\n")
    
    # Intent Extraction
    print("Extracting diagram intent from natural language...")
    try:
        intent = extract_intent(user_request)
        print(f"✓ Extracted intent: {intent.diagram_type} diagram - '{intent.title}'")
        print(f"  Components: {len(intent.components)}, Relationships: {len(intent.relationships)}\n")
    except Exception as e:
        print(f"✗ Error in intent extraction: {e}")
        raise
    
    # Code Generation
    print("Generating diagram code...")
    dot_code = None
    retry_count = 0
    
    while retry_count <= MAX_RETRY_ATTEMPTS:
        try:
            if retry_count == 0:
                dot_code = generate_diagram_code(intent)
            else:
                # This is a retry after correction
                print(f"  Retry attempt {retry_count}/{MAX_RETRY_ATTEMPTS}...")
            
            print(f"✓ Generated diagram code ({len(dot_code)} characters)\n")
            
            # Syntax Validation
            print("Validating syntax...")
            is_valid, error_message = validate_graphviz_syntax(dot_code)
            
            if is_valid:
                print("✓ Syntax validation passed\n")
                break
            else:
                print(f"✗ Syntax validation failed: {error_message}\n")
                
                # Error Correction
                if retry_count < MAX_RETRY_ATTEMPTS:
                    print("Attempting error correction...")
                    try:
                        dot_code = correct_diagram_code(user_request, dot_code, error_message)
                        print(f"✓ Generated corrected code ({len(dot_code)} characters)\n")
                        retry_count += 1
                    except Exception as e:
                        print(f"✗ Error correction failed: {e}")
                        retry_count += 1
                else:
                    raise RuntimeError(
                        f"Failed to generate valid code after {MAX_RETRY_ATTEMPTS} attempts. "
                        f"Last error: {error_message}"
                    )
                    
        except Exception as e:
            if retry_count >= MAX_RETRY_ATTEMPTS:
                raise
            retry_count += 1
            print(f"Error in code generation/correction: {e}. Retrying...\n")
    
    # Rendering
    print("Rendering diagram...")
    try:
        rendered_file, source_file = render_diagram(dot_code, output_filename)
        print("✓ Diagram rendered successfully\n")
        display_results(rendered_file, source_file)
        return rendered_file, source_file
    except Exception as e:
        print(f"✗ Rendering failed: {e}")
        raise


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python main.py '<diagram request>' [output_filename]")
        print("\nExample:")
        print('  python main.py "Draw a sequence diagram for user login and database check"')
        print('  python main.py "Create a flowchart for order processing" my_flowchart')
        sys.exit(1)
    
    user_request = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        rendered_file, source_file = generate_diagram(user_request, output_filename)
        print(f"\n✓ Success! Diagram saved to: {rendered_file}")
    except Exception as e:
        print(f"\n✗ Failed to generate diagram: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
