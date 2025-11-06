import re
import yaml
import shutil
import datetime
import sys
from pathlib import Path
from typing import Optional, Tuple, List


def generate_timestamp_filename() -> str:
    """
    Generate a timestamp-based filename for diagrams.

    Returns:
        str: Filename in format diagram_YYYYMMDD_HHMMSS
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"diagram_{timestamp}"


def parse_file_path(command: str) -> Optional[Path]:
    """
    Parse the file path from the command.
    
    Returns:
        Path if file path found, None otherwise
    """
    match = re.search(r"--filename\s+([^\s]+)", command)
    if match:
        return Path(match.group(1))
    return None


def read_markdown_file(filepath: Path) -> str:
    """
    Reads the contents of a .md file and returns it as a string.
    """
    return read_text_file(filepath)


def read_text_file(filepath: Path) -> str:
    """
    Reads the contents of a plain text file and returns it as a string.
    Works with any plain text file format (.txt, .md, etc.).
    """
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def count_lines(file_path):
    """
    Count the number of lines in a text or markdown file.

    Args:
        file_path (str): Path to the file.

    Returns:
        int: Number of lines in the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        print("Error: File not found.")
        return 0
    except UnicodeDecodeError:
        print("Error: File encoding issue.")
        return 0


def read_file_contents(filepath: Path) -> str:
    """
    Reads the contents of a .md or .txt file and returns it as a string.

    """
    ext = filepath.suffix.lower()
    if ext == ".md":
        return read_markdown_file(filepath)
    elif ext == ".txt":
        return read_text_file(filepath)
    else:
        raise ValueError(
            f"Unsupported file type: {ext}. Only .md and .txt files are supported."
        )


def copy_file(src_path: Path, dest_path: Path) -> None:
    """
    Copy a file from one path to another.
    """
    shutil.copy2(src_path, dest_path)


def load_prompt(filepath: Path) -> dict:
    """
    Load a prompt from a YAML file.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        prompt_data = yaml.safe_load(f)
    return prompt_data


def render_prompt(filepath: Path) -> str:
    """
    Render a prompt from a dictionary.
    """
    prompt_data = load_prompt(filepath)
    return prompt_data["system"] + "\n\n" + prompt_data["human"]


def chunk_text(text: str, chunk_size: int) -> list:
    """
    Chunk text into smaller chunks.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks


def handle_file(filepath: Optional[Path], data_dir: Path) -> Tuple[Optional[str], Optional[Path]]:
    """
    Handle file processing - copy file to data directory and read contents.
    
    Returns:
        tuple: (file_content, filepath) or (None, None) if no file
    """
    if not filepath or not filepath.exists() or not filepath.is_file():
        return None, None
    copy_file(filepath, data_dir / filepath.name)
    lines = count_lines(filepath)
    text = read_text_file(filepath)
    if lines > 100000:
        chunks = chunk_text(text, 100000)
        # Chunk processing needs to be completed
        # For now, just use the first chunk
        text = chunks[0] if chunks else text
    return text, filepath


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


def supports_color() -> bool:
    """Check if the terminal supports color output."""
    # Check if we're in a terminal
    if not sys.stdout.isatty():
        return False
    
    # Check platform
    platform = sys.platform
    # Windows 10+ supports ANSI colors, but older versions don't
    if platform == "win32":
        # Try to enable ANSI support on Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except:
            return False
    
    return True


def colorize(text: str, color: str, bold: bool = False) -> str:
    """
    Colorize text for terminal output.
    
    Args:
        text: Text to colorize
        color: Color code from Colors class
        bold: Whether to make text bold
    
    Returns:
        str: Colorized text (or plain text if colors not supported)
    """
    if not supports_color():
        return text
    
    result = color
    if bold:
        result += Colors.BOLD
    result += text + Colors.RESET
    return result


def print_success(message: str, bold: bool = False):
    """Print a success message in green."""
    print(colorize(f"[OK] {message}", Colors.GREEN, bold))


def print_error(message: str, bold: bool = False):
    """Print an error message in red."""
    print(colorize(f"[ERROR] {message}", Colors.RED, bold))


def print_warning(message: str, bold: bool = False):
    """Print a warning message in yellow."""
    print(colorize(f"[WARNING] {message}", Colors.YELLOW, bold))


def print_info(message: str, bold: bool = False):
    """Print an info message in blue."""
    print(colorize(message, Colors.BLUE, bold))


def print_tip(message: str, bold: bool = False):
    """Print a tip message in cyan."""
    print(colorize(f"Tip: {message}", Colors.CYAN, bold))
