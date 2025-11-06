import json
from rendering import validate_dac, render_diagram, display_results
from utils import generate_timestamp_filename, print_success, print_error, print_warning, print_info
from code_generation import DaCGenerator
from langchain_core.runnables import Runnable
from langchain_core.prompts import PromptTemplate
from utils import render_prompt
from schemas import Request, GraphContext
from response_parser import extract_json_content, extract_response_content, extract_graphviz_code
from settings import AppSettings
from llm_client import LLMClient


class DiagramGenerator:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.max_retry_attempts = settings.max_retry_attempts
        self.dac_generator: DaCGenerator = DaCGenerator(settings=self.settings)
        self.llm_client = LLMClient(settings=self.settings)
        self.llm = self.llm_client.get_llm()
        self.code_gen_llm = self.llm_client.get_code_gen_llm()
        self.context_extraction_chain: Runnable = (
            PromptTemplate.from_template(
                render_prompt(self.settings.context_extraction_prompt_file_path)
            ) | self.llm
        )
        self.code_generation_chain: Runnable = (
            PromptTemplate.from_template(
                render_prompt(self.settings.code_generation_prompt_file_path)
            ) | self.code_gen_llm
        )
        self.error_correction_chain: Runnable = (
            PromptTemplate.from_template(
                render_prompt(self.settings.error_correction_prompt_file_path)
            ) | self.code_gen_llm
        )
    
    def generate(self, request: Request) -> None:
        """
        Generate a diagram from a user request.

        Args:
            user_request: Natural language request from user
        """
        print_info("Extracting context...")
        try:
            context_schema = self.context_extraction_chain.invoke(
                {
                    "user_request": request.user_request or request.raw_request,
                    "documentation": request.file_content or "",
                }
            )
            # Extract JSON from the response (handle markdown code blocks)
            response_content = extract_response_content(context_schema)
            
            # Debug: Print first 500 chars of response if needed
            if not response_content or len(response_content.strip()) == 0:
                raise ValueError("Empty response from LLM")
            
            json_str = extract_json_content(response_content)
            
            if not json_str or len(json_str.strip()) == 0:
                raise ValueError(
                    f"Could not extract JSON from LLM response. "
                    f"Response preview: {response_content[:200]}..."
                )
            
            # Parse JSON string to dict
            try:
                context_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON extracted from response. Error: {e}. "
                    f"Extracted JSON preview: {json_str[:200]}..."
                )
            
            # Ensure title field exists (fallback if LLM doesn't provide it)
            if "title" not in context_dict or not context_dict.get("title"):
                context_dict["title"] = "System Architecture Diagram"
            
            # Convert dict to GraphContext Pydantic model
            context = GraphContext(**context_dict)
            print(
                f"Groups: {len(context.groups)}, Components: {len(context.components)}, Relationships: {len(context.relationships)}\n"
            )
        except Exception as e:
            print_error(f"Error in context extraction: {e}")
            raise

        print_info("Generating diagram code...")
        dot_code = None
        retry_count = 0

        while retry_count <= self.max_retry_attempts:
            try:
                if retry_count == 0:
                    dot_code_response = self.dac_generator.generate(context)
                    # Extract graphviz code from LLM response
                    dot_code = extract_graphviz_code(extract_response_content(dot_code_response))
                else:
                    # This is a retry after correction
                    print_info(f"  Retry attempt {retry_count}/{self.max_retry_attempts}...")
                    # dot_code already set from error correction below

                print_success(f"Generated diagram code ({len(dot_code)} characters)\n")

                print_info("Validating syntax...")
                is_valid, error_message = validate_dac(dot_code)
                if is_valid:
                    print_success("Syntax validation passed\n")
                    break
                else:
                    print_error(f"Syntax validation failed: {error_message}\n")
                    if retry_count < self.max_retry_attempts:
                        print_info("Attempting error correction...")
                        try:
                            corrected_response = self.correct_diagram_code(
                                context_dict, dot_code, error_message
                            )
                            # Extract graphviz code from correction response
                            dot_code = extract_graphviz_code(extract_response_content(corrected_response))
                            print_success(
                                f"Generated corrected code ({len(dot_code)} characters)\n"
                            )
                            retry_count += 1
                        except Exception as e:
                            print_error(f"Error correction failed: {e}")
                            retry_count += 1
                    else:
                        raise RuntimeError(
                            f"Failed to generate valid code after {self.max_retry_attempts} attempts. "
                            f"Last error: {error_message}"
                        )

            except Exception as e:
                if retry_count >= self.max_retry_attempts:
                    raise
                retry_count += 1
                print_warning(f"Error in code generation/correction: {e}. Retrying...\n")

        print_info("Rendering diagram...")
        try:
            output_filename = generate_timestamp_filename()
            rendered_file, source_file = render_diagram(dot_code, output_filename)
            print_success(f"Diagram rendered successfully to {output_filename}\n")
            display_results(rendered_file, source_file)
            return rendered_file, source_file
        except Exception as e:
            print_error(f"Rendering failed: {e}")
            raise

    def correct_diagram_code(
        self, context_schema: dict, flawed_code: str, error_message: str
    ) -> str:
        """
        Analyze and correct syntactically flawed diagram code based on error message.

        Args:
            flawed_code: The syntactically incorrect graphviz code
            error_message: Error message from the validator

        Returns:
            str: Corrected graphviz code
        """
        code = self.error_correction_chain.invoke(
            {
                "graph_context": context_schema,
                "flawed_code": flawed_code,
                "error_message": error_message,
            }
        )
        return code
