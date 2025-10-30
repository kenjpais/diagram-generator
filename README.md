# AI Software Architecture Diagram Generator

An intelligent diagram generator that uses LangChain and CodeLlama (or other LLMs) to convert natural language descriptions into structured software architecture diagrams. The system implements a sophisticated 5-step workflow with automatic error detection and self-correction.

## Features

- **Natural Language Input**: Describe your diagram in plain English
- **Multi-Step Pipeline**: Structured workflow ensures high-quality outputs
- **Automatic Error Correction**: Self-reflecting agent fixes syntax errors automatically
- **Multiple Diagram Types**: Supports sequence diagrams, flowcharts, component diagrams, architecture diagrams, and more
- **Graphviz Rendering**: Generates high-quality SVG/PNG/PDF outputs

## Architecture

The system implements a 5-step sequential workflow:

### STEP 1: Intent Extraction (Natural Language → Structured JSON)
- Extracts structured diagram intent from natural language
- Uses LLM with "meticulous analyst" persona
- Outputs structured JSON with diagram type, components, and relationships

### STEP 2: Diagram Code Generation (Structured JSON → DaC Code)
- Translates structured JSON into graphviz code
- Uses few-shot examples and Chain-of-Thought prompting
- Generates human-readable Diagram-as-Code

### STEP 3: Syntax Validation (DaC Code → Error Check)
- Validates graphviz syntax using deterministic parser
- Detects syntax errors before rendering
- Routes to correction step if errors found

### STEP 4: Reflection and Self-Correction (Error → Corrected Code)
- Analyzes error messages and flawed code
- Generates corrected version maintaining original intent
- Implements retry loop with maximum attempt limit

### STEP 5: Final Output and Rendering (Validated Code → Visual Artifact)
- Renders valid graphviz code to visual format (SVG/PNG/PDF)
- Saves both rendered diagram and source code
- Displays results to user

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Graphviz** (for rendering and validation):
   ```bash
   # macOS
   brew install graphviz
   
   # Ubuntu/Debian
   sudo apt-get install graphviz graphviz-dev
   
   # Windows
   # Download from https://graphviz.org/download/
   ```
   
   Note: `pygraphviz` requires graphviz development headers to be installed.

3. **Ollama** (for local CodeLlama, optional):
   ```bash
   # Install Ollama from https://ollama.ai
   # Then pull a model:
   ollama pull llama3.2:3b
   ```

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd diagram-generator
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file (optional, defaults are provided):
   ```bash
   # LLM Configuration (Ollama only)
   LLM_MODEL=llama3.2:3b
   OLLAMA_BASE_URL=http://localhost:11434
   
   # Retry Configuration
   MAX_RETRY_ATTEMPTS=3
   
   # Output Configuration
   OUTPUT_DIR=output
   RENDER_FORMAT=svg
   ```

## Usage

### Command Line

```bash
python main.py "Draw a sequence diagram for user login and database check"

# With custom output filename
python main.py "Create a flowchart for order processing" my_flowchart
```

### Python API

```python
from main import generate_diagram

rendered_file, source_file = generate_diagram(
    "Draw a sequence diagram for user login and database check",
    output_filename="login_flow"
)
print(f"Diagram saved to: {rendered_file}")
```

### Example Requests

- "Draw a sequence diagram for user login and database check"
- "Create a flowchart for order processing"
- "Generate a component diagram showing a microservices architecture"
- "Draw an architecture diagram with API gateway, services, and database"

## Project Structure

```
diagram-generator/
├── main.py                      # Main orchestration script
├── config.py                    # Configuration settings
├── schemas.py                   # Pydantic schemas for structured data
├── prompt_loader.py             # Utility for loading prompts from YAML
├── llm_utils.py                 # Shared LLM initialization utilities
├── intent_extraction.py         # Intent extraction
├── code_generation.py           # Code generation
├── syntax_validation.py         # Syntax validation (using pygraphviz)
├── error_correction.py          # Error correction
├── rendering.py                 # Rendering
├── prompts/                     # YAML prompt files
│   ├── intent_extraction.yaml
│   ├── code_generation.yaml
│   └── error_correction.yaml
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── output/                      # Generated diagrams (created automatically)
```

## Configuration

### LLM Provider

The system uses **Ollama** for LLM inference:
- No API key required
- Free and runs locally
- Excellent for code generation tasks
- Configure via `LLM_MODEL` and `OLLAMA_BASE_URL` environment variables

### Prompts

Prompts are stored in YAML files in the `prompts/` directory:
- `intent_extraction.yaml` - Intent extraction prompts
- `code_generation.yaml` - Code generation prompts
- `error_correction.yaml` - Error correction prompts

You can customize prompts by editing these YAML files without changing the code.

### Output Formats

Supported rendering formats:
- `svg` (default) - Scalable vector graphics
- `png` - Portable network graphics
- `pdf` - Portable document format

Change via `RENDER_FORMAT` environment variable.

## How It Works

1. **User Request**: Natural language description of desired diagram
2. **Intent Extraction**: LLM extracts structured information (components, relationships, diagram type)
3. **Code Generation**: LLM translates structured data to graphviz code using few-shot examples
4. **Validation**: Syntax checker validates the generated code using pygraphviz
5. **Error Correction** (if needed): LLM analyzes errors and generates corrected code (up to MAX_RETRY_ATTEMPTS)
6. **Rendering**: Valid code is rendered to visual format using graphviz
7. **Output**: Both rendered diagram and source code are saved

## Error Handling

The system implements automatic error correction:
- Syntax errors are detected during validation
- Error messages are passed to the error correction module
- The correction module analyzes root causes and generates corrections
- Process repeats until valid code is generated or max retries reached

## Limitations

- Requires graphviz installation for rendering
- LLM quality affects output quality (better models = better diagrams)
- Complex diagrams may require multiple correction attempts
- Sequence diagrams are rendered as graphviz (not true sequence diagram syntax)

## Troubleshooting

### "Graphviz 'dot' command not found"
- Install graphviz using package manager (see Installation section)

### "Failed to parse LLM response"
- Try a different LLM model
- Ensure LLM provider is correctly configured
- Check network connectivity if using cloud-based LLM

### "Rendering timed out"
- Diagram code may be too complex
- Try simplifying the request
- Check graphviz installation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]

## Acknowledgments

- Built with [LangChain](https://python.langchain.com/)
- Uses [Graphviz](https://graphviz.org/) for diagram rendering
- Supports [CodeLlama](https://ai.meta.com/blog/code-llama-large-language-model-coding/) via Ollama