"""Main orchestration script for the AI Diagram Generator."""
import sys
from typing import Optional, Tuple
from datetime import datetime
from intent_extraction import extract_intent
from code_generation import generate_diagram_code
from syntax_validation import validate_graphviz_syntax
from error_correction import correct_diagram_code
from rendering import render_diagram, display_results
from config import MAX_RETRY_ATTEMPTS


def generate_diagram(user_request: str, output_filename: Optional[str] = None, silent: bool = False) -> Tuple[str, str]:
    """
    Execute the complete 5-step diagram generation workflow.
    
    Args:
        user_request: Natural language request from user
        output_filename: Optional filename for output (without extension)
        silent: If True, suppress header output (useful for interactive mode)
        
    Returns:
        tuple: (rendered_file_path, source_file_path)
    """
    if output_filename is None:
        output_filename = generate_timestamp_filename()
    
    if not silent:
        print("="*60)
        print("AI DIAGRAM GENERATOR")
        print("="*60)
        print(f"\nUser Request: {user_request}\n")
    
    # Intent Extraction
    print("Extracting diagram intent from natural language...")
    try:
        intent = extract_intent(user_request)
        print(f"✓ Extracted intent: Graph topology - '{intent.title}'")
        print(f"  Groups: {len(intent.groups)}, Components: {len(intent.components)}, Relationships: {len(intent.relationships)}\n")
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


def print_help():
    """Print help information for interactive mode."""
    print("\n" + "="*60)
    print("HELP - Available Commands")
    print("="*60)
    print("Commands:")
    print("  /help, /h              - Show this help message")
    print("  /exit, /quit, /q       - Exit the application")
    print("  /clear                 - Clear the screen")
    print("\nUsage:")
    print("  Simply type your diagram request and press Enter")
    print("  Example: Draw a sequence diagram for user login")
    print("\n  Filenames are automatically generated with timestamps")
    print("  Format: diagram_YYYYMMDD_HHMMSS")
    print("="*60 + "\n")


def generate_timestamp_filename() -> str:
    """
    Generate a timestamp-based filename for diagrams.
    
    Returns:
        str: Filename in format diagram_YYYYMMDD_HHMMSS
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"diagram_{timestamp}"


def interactive_mode():
    """Run the diagram generator in interactive chat mode."""
    print("\n" + "="*60)
    print("AI DIAGRAM GENERATOR - Interactive Mode")
    print("="*60)
    print("\nType your diagram requests below.")
    print("Type '/help' for available commands or '/exit' to quit.\n")
    
    diagram_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['/exit', '/quit', '/q']:
                print("\n👋 Thanks for using AI Diagram Generator! Goodbye!\n")
                break
            
            if user_input.lower() in ['/help', '/h']:
                print_help()
                continue
            
            if user_input.lower() == '/clear':
                # Clear screen (works on most terminals)
                import os
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
            
            # Use the user input as the request
            request = user_input.strip()
            
            if not request:
                print("⚠️  Please provide a diagram request.\n")
                continue
            
            # Generate timestamp-based filename
            diagram_count += 1
            output_filename = generate_timestamp_filename()
            
            try:
                print("\n" + "─"*60)
                print(f"Processing request #{diagram_count}...")
                print("─"*60 + "\n")
                
                rendered_file, source_file = generate_diagram(
                    request, 
                    output_filename=output_filename,
                    silent=True
                )
                
                print(f"\n✅ Success! Diagram saved to: {rendered_file}")
                print(f"   Source code: {source_file}\n")
                
            except KeyboardInterrupt:
                print("\n⚠️  Generation cancelled by user.\n")
                continue
            except Exception as e:
                print(f"\n❌ Failed to generate diagram: {e}\n")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using AI Diagram Generator! Goodbye!\n")
            break
        except EOFError:
            # Handle Ctrl+D
            print("\n\n👋 Thanks for using AI Diagram Generator! Goodbye!\n")
            break


def main():
    """Main entry point - supports both CLI and interactive modes."""
    # Check if running in interactive mode (no arguments)
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    # Legacy CLI mode (for backward compatibility)
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Interactive mode: python main.py")
        print("  CLI mode: python main.py '<diagram request>' [output_filename]")
        print("\nExamples:")
        print('  python main.py  # Start interactive mode')
        print('  python main.py "Draw a sequence diagram for user login"')
        print('  python main.py "Create a flowchart" my_flowchart')
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
