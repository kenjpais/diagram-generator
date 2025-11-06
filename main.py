"""Main orchestration script for the AI Diagram Generator."""

from settings import get_settings, AppSettings
from diagram_generator import DiagramGenerator
from schemas import Request
from utils import print_success, print_error, print_warning, print_info, colorize, Colors


def print_help():
    """Print help information for interactive mode."""
    print("\n" + colorize("=" * 60, Colors.CYAN))
    print(colorize("HELP - Available Commands", Colors.CYAN, bold=True))
    print(colorize("=" * 60, Colors.CYAN))
    print("Commands:")
    print("  /help, /h              - Show this help message")
    print("  /exit, /quit, /q       - Exit the application")
    print("  /clear                 - Clear the screen")
    print("\nUsage:")
    print("  Simply type your diagram request and press Enter")
    print("  Example: Draw a sequence diagram for user login")
    print(
        "  Example: Draw a sequence diagram for user login --filename data/user_login.md"
    )
    print(colorize("=" * 60, Colors.CYAN) + "\n")


def setup(settings: AppSettings):
    """Setup the application."""
    settings.data_dir.mkdir(exist_ok=True)


def generate_diagram(user_request: str, output_filename: str = None) -> tuple:
    """
    Generate a diagram from a user request (Python API).
    
    Args:
        user_request: Natural language description of the diagram
        output_filename: Optional custom filename (without extension)
        
    Returns:
        tuple: (rendered_file_path, source_file_path)
    """
    settings = get_settings()
    setup(settings)
    di_gen = DiagramGenerator(settings)
    
    # Create a Request object
    request = Request(user_request, settings)
    
    # Generate the diagram
    rendered_file, source_file = di_gen.generate(request)
    
    return rendered_file, source_file


def main():
    """Main entry point - supports both CLI and interactive modes."""
    print("\n" + colorize("=" * 60, Colors.CYAN))
    print(colorize("AI DIAGRAM GENERATOR", Colors.CYAN, bold=True))
    print(colorize("=" * 60, Colors.CYAN))
    print("\nType your diagram requests below.")
    print("Type '/help' for available commands or '/exit' to quit.\n")

    settings = get_settings()
    setup(settings)
    di_gen = DiagramGenerator(settings)

    while True:
        try:
            # Get user input
            user_input = input("> ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["/exit", "/quit", "/q"]:
                print("\nThanks for using AI Diagram Generator! Goodbye!\n")
                break

            if user_input.lower() in ["/help", "/h"]:
                print_help()
                continue

            if user_input.lower() == "/clear":
                # Clear screen (works on most terminals)
                import os

                os.system("clear" if os.name != "nt" else "cls")
                continue

            # Use the user input as the request
            user_request = user_input.strip()
            if user_request:
                request = Request(user_request, settings)
            else:
                print_warning("Please provide a diagram request.\n")

            try:
                di_gen.generate(request)
            except KeyboardInterrupt:
                print_warning("\nGeneration cancelled by user.\n")
                continue
            except Exception as e:
                print_error(f"\nFailed to generate diagram: {e}\n")
                continue

        except KeyboardInterrupt:
            print("\n\nThanks for using AI Diagram Generator! Goodbye!\n")
            break
        except EOFError:
            # Handle Ctrl+D
            print("\n\nThanks for using AI Diagram Generator! Goodbye!\n")
            break


if __name__ == "__main__":
    main()
