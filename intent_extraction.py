"""Intent Extraction - Natural Language → Structured JSON"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import GraphIntent
from llm_utils import get_llm
from prompt_loader import get_system_prompt, get_human_prompt
from response_parser import extract_response_content, extract_json_content
import json


def extract_intent(user_request: str) -> GraphIntent:
    """
    Extract structured diagram intent from natural language using LLM.
    
    Args:
        user_request: Raw natural language request from user
        
    Returns:
        GraphIntent: Structured JSON object describing the graph topology
    """
    llm = get_llm()
    
    # Load prompts from YAML
    system_prompt = get_system_prompt("intent_extraction.yaml")
    human_prompt = get_human_prompt("intent_extraction.yaml")
    
    # Use Pydantic output parser for structured output
    parser = PydanticOutputParser(pydantic_object=GraphIntent)
    
    # Create prompt - format instructions already in YAML prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    # Format the prompt
    formatted_prompt = prompt.format_prompt(
        user_request=user_request
    )
    
    # Get LLM response
    response = llm.invoke(formatted_prompt.to_messages())
    
    # Parse response
    try:
        # Extract JSON content from response
        raw_content = extract_response_content(response)
        json_content = extract_json_content(raw_content)
        
        # Parse JSON and create GraphIntent
        parsed_json = json.loads(json_content)
        intent = GraphIntent(**parsed_json)
        return intent
        
    except json.JSONDecodeError as e:
        # Fallback: try to parse using Pydantic parser directly
        try:
            raw_content = extract_response_content(response)
            intent = parser.parse(raw_content)
            return intent
        except Exception as parse_error:
            raise ValueError(
                f"Failed to parse LLM response: {parse_error}. "
                f"JSON decode error: {e}. Raw response: {raw_content[:500]}"
            )
    except Exception as e:
        raw_content = extract_response_content(response)
        raise ValueError(f"Failed to process LLM response: {e}. Raw response: {raw_content[:500]}")


if __name__ == "__main__":
    # Test the intent extraction
    test_request = "Draw a network topology with routers, switches, and servers"
    intent = extract_intent(test_request)
    print(json.dumps(intent.model_dump(), indent=2))