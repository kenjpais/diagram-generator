# AI Graph Topology Diagram Generator

An intelligent diagram generator that uses LangChain and CodeLlama to convert natural language descriptions into structured graph topology diagrams. The system implements a sophisticated 5-step workflow with automatic error detection and self-correction.

## Features

- **Natural Language Input**: Describe your topology in plain English
- **Graph Diagrams Only**: Specialized for network, system, application, cloud, deployment, and infrastructure topologies
- **Multi-Step Pipeline**: Structured workflow ensures high-quality outputs
- **Automatic Error Correction**: Self-reflecting agent fixes syntax errors automatically
- **Advanced Graph Model**: Supports groups/subgraphs, component types, relationship types, and styling
- **Graphviz Rendering**: Generates high-quality SVG/PNG/PDF outputs

## Architecture

The system implements a 5-step sequential workflow:

### Intent Extraction (Natural Language → Structured JSON)
- Extracts structured graph topology from natural language
- Uses LLM with "expert architect" persona
- Outputs structured JSON with groups, components, relationships, and their types

### Diagram Code Generation (Structured JSON → DaC Code)
- Translates structured JSON into graphviz code using LLM (Gemini by default)
- LLM receives JSON schema and actual data to generate Graphviz code
- Uses advanced prompting with few-shot examples for reliable code generation
- Supports groups/subgraphs for organizing components
- Applies appropriate styling based on component and relationship types
- Generates human-readable Diagram-as-Code with proper formatting

### Syntax Validation (DaC Code → Error Check)
- Validates graphviz syntax using pygraphviz library (with fallback)
- Detects syntax errors before rendering
- Routes to correction step if errors found

### Error Correction (Error → Corrected Code)
- Analyzes error messages and flawed code
- Generates corrected version maintaining original intent
- Implements retry loop with maximum attempt limit

### Rendering (Validated Code → Visual Artifact)
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
   # LLM Configuration
   LLM_PROVIDER=gemini  # or "ollama"
   GEMINI_API_KEY=your_api_key_here  # Required for Gemini
   GEMINI_MODEL=gemini-pro  # Gemini model name
   
   # Code Generation LLM (defaults to Gemini)
   CODE_GEN_LLM_PROVIDER=gemini
   
   # Ollama Configuration (if using Ollama)
   LLM_MODEL=llama3.2:3b
   OLLAMA_BASE_URL=http://localhost:11434
   
   # Retry Configuration
   MAX_RETRY_ATTEMPTS=3
   
   # Output Configuration
   OUTPUT_DIR=output
   RENDER_FORMAT=svg
   ```

## Usage

### Quick Start

1. **Ensure Ollama is running:**
   ```bash
   # Start Ollama service (if not already running)
   ollama serve
   
   # In another terminal, verify your model is available
   ollama list
   ```

2. **Start the interactive diagram generator:**
   ```bash
   python main.py
   ```

3. **Type your diagram request:**
   ```
   You: Draw a network topology with routers, switches, and servers
   ```

4. **Check the output:**
   - The diagram will be saved in the `output/` directory
   - Open the generated `.svg` (or `.png`/`.pdf`) file to view your diagram
   - The source `.dot` file is also saved for reference
   - Continue typing more requests or type `/exit` to quit

### Interactive Mode (Recommended)

The tool runs in interactive chat mode by default. Simply run:

```bash
python main.py
```

You'll see a prompt where you can type diagram requests:

```
============================================================
AI DIAGRAM GENERATOR - Interactive Mode
============================================================

Type your diagram requests below.
Type '/help' for available commands or '/exit' to quit.

You: Draw a network topology with routers, switches, and servers
```

**Available Commands:**
- `/help` or `/h` - Show help message
- `/exit`, `/quit`, or `/q` - Exit the application
- `/clear` - Clear the screen

**Features:**
- Automatic timestamp-based filenames (diagram_YYYYMMDD_HHMMSS)
- Generate multiple diagrams in one session
- Continue conversation-style interaction
- Type `/exit` when done

### Testing the Installation

Before using the tool, you can verify everything is set up correctly:

```bash
# Run the test suite
python test_project.py
```

This will test:
- All imports
- Prompt loading
- Syntax validation
- Response parsing
- Schema validation
- Output directory creation

**Infrastructure Topology:**
```
You: Create infrastructure topology with hypervisors, virtual machines, and storage systems
You: Draw infrastructure diagram showing physical servers, VMs, and network connections
```

**Tips for Best Results:**
- Be specific about the topology type (network, system architecture, application, cloud, deployment, infrastructure)
- Mention groups/boundaries explicitly (e.g., "data center", "VPC", "on-premises environment")
- Describe components with their types (e.g., "API gateway", "database", "router", "server")
- Clearly state relationships between components (e.g., "connects to", "sends requests to", "via VPN")
- Mention when components are inside groups (e.g., "servers in datacenter A")

### Output Files

Each diagram generation produces two files:

1. **Rendered Diagram** (`.svg`, `.png`, or `.pdf`):
   - The visual diagram file
   - Format controlled by `RENDER_FORMAT` environment variable
   - Default: SVG (scalable vector graphics)

2. **Source Code** (`.dot`):
   - The graphviz source code
   - Can be edited manually if needed
   - Can be rendered using graphviz command-line tools directly

**Example Output Files:**
```
output/
├── generated_diagram.svg    # Rendered diagram (open this to view)
└── generated_diagram.dot    # Source code (for reference/editing)
```

## Configuration

### LLM Provider

The system supports **Gemini** (default) and **Ollama** for LLM inference:

**Gemini (Default for Code Generation):**
- Uses Google's Gemini API
- Excellent code generation quality
- Requires API key: Set `GEMINI_API_KEY` environment variable
- Get API key from: https://makersuite.google.com/app/apikey
- Configure model via `GEMINI_MODEL` (default: "gemini-pro")

**Ollama:**
- No API key required
- Free and runs locally
- Configure via `LLM_MODEL` and `OLLAMA_BASE_URL` environment variables

**Configuration:**
- `LLM_PROVIDER`: "gemini" or "ollama" (default: "gemini")
- `CODE_GEN_LLM_PROVIDER`: LLM for code generation (default: "gemini", can use "ollama")

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

## Acknowledgments

- Built with [LangChain](https://python.langchain.com/)
- Uses [Graphviz](https://graphviz.org/) for diagram rendering
- Supports [CodeLlama](https://ai.meta.com/blog/code-llama-large-language-model-coding/) via Ollama
