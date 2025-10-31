"""Error Correction - Error Message → Corrected DaC Code"""
from langchain_core.prompts import ChatPromptTemplate
from llm_utils import get_llm
from prompt_loader import get_system_prompt, get_human_prompt
from response_parser import extract_response_content, extract_graphviz_code


def correct_diagram_code(
    original_request: str,
    flawed_code: str,
    error_message: str
) -> str:
    """
    Analyze and correct syntactically flawed diagram code based on error message.
    
    Args:
        original_request: Original user request for context
        flawed_code: The syntactically incorrect graphviz code
        error_message: Error message from the validator
        
    Returns:
        str: Corrected graphviz code
    """
    llm = get_llm()
    
    # Load prompts from YAML
    system_prompt = get_system_prompt("error_correction.yaml")
    human_prompt = get_human_prompt("error_correction.yaml")
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    # Format and invoke
    formatted_prompt = prompt.format_prompt(
        original_request=original_request,
        flawed_code=flawed_code,
        error_message=error_message
    )
    response = llm.invoke(formatted_prompt.to_messages())
    
    # Extract content and parse graphviz code
    content = extract_response_content(response)
    corrected_code = extract_graphviz_code(content)
    
    return corrected_code


if __name__ == "__main__":
    # Test the correction
    original = "Draw a simple flowchart"
    flawed = """digraph Test {
    A -> B [label="test"
}"""
    error = "Unbalanced braces: 1 opening, 1 closing"
    
    corrected = correct_diagram_code(original, flawed, error)
    print("Corrected code:")
    print(corrected)
