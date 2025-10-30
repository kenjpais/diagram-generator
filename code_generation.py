"""Diagram Code Generation - Structured JSON → DaC Code"""
from langchain_core.prompts import ChatPromptTemplate
from schemas import DiagramIntent
from llm_utils import get_llm
from prompt_loader import get_system_prompt, get_human_prompt, get_few_shot_example
import json


def generate_diagram_code(intent: DiagramIntent) -> str:
    """
    Generate Diagram-as-Code (graphviz) from structured intent.
    
    Args:
        intent: Structured DiagramIntent object
        
    Returns:
        str: Raw graphviz code as a string
    """
    llm = get_llm()
    
    # Load prompts from YAML
    system_prompt = get_system_prompt("code_generation.yaml")
    human_prompt = get_human_prompt("code_generation.yaml")
    few_shot_example = get_few_shot_example("code_generation.yaml")
    
    # Convert intent to JSON string
    intent_json = json.dumps(intent.model_dump(), indent=2)
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + few_shot_example),
        ("human", human_prompt)
    ])
    
    # Format and invoke
    formatted_prompt = prompt.format_prompt(intent_json=intent_json)
    response = llm.invoke(formatted_prompt.to_messages())
    
    # Extract content
    if hasattr(response, 'content'):
        content = response.content
    else:
        content = str(response)
    
    # Extract graphviz code from response (remove markdown code blocks if present)
    if "```graphviz" in content:
        code = content.split("```graphviz")[1].split("```")[0].strip()
    elif "```" in content:
        # Try to find any code block
        parts = content.split("```")
        if len(parts) >= 3:
            code = parts[1].strip()
            # Remove language identifier if present
            if "\n" in code:
                lines = code.split("\n")
                if not lines[0].strip().startswith("digraph") and not lines[0].strip().startswith("graph"):
                    code = "\n".join(lines[1:])
        else:
            code = content
    else:
        code = content.strip()
    
    # Remove "Let's think step-by-step:" prefix if present
    if "Let's think step-by-step:" in code:
        code = code.split("Let's think step-by-step:")[-1].strip()
    
    return code


if __name__ == "__main__":
    # Test the code generation
    from schemas import Component, Relationship, DiagramIntent
    
    test_intent = DiagramIntent(
        diagram_type="sequence",
        title="User Login",
        components=[
            Component(id="user", label="User", type="actor"),
            Component(id="auth", label="Auth Service", type="service")
        ],
        relationships=[
            Relationship(source_id="user", target_id="auth", action="login request")
        ]
    )
    
    code = generate_diagram_code(test_intent)
    print(code)
