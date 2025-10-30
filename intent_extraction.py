"""Intent Extraction - Natural Language → Structured JSON"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import DiagramIntent
from llm_utils import get_llm
from prompt_loader import get_system_prompt, get_human_prompt
import json


def extract_intent(user_request: str) -> DiagramIntent:
    """
    Extract structured diagram intent from natural language using LLM.
    
    Args:
        user_request: Raw natural language request from user
        
    Returns:
        DiagramIntent: Structured JSON object describing the diagram
    """
    llm = get_llm()
    
    # Load prompts from YAML
    system_prompt = get_system_prompt("intent_extraction.yaml")
    human_prompt = get_human_prompt("intent_extraction.yaml")
    
    # Use Pydantic output parser for structured output
    parser = PydanticOutputParser(pydantic_object=DiagramIntent)
    
    # Create prompt with format instructions
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + "\n\n" + parser.get_format_instructions()),
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
        # Handle different response types
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        # Try to extract JSON from response if it's wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON and create DiagramIntent
        parsed_json = json.loads(content)
        intent = DiagramIntent(**parsed_json)
        return intent
        
    except Exception as e:
        # Fallback: try to parse directly
        try:
            intent = parser.parse(content)
            return intent
        except Exception as parse_error:
            raise ValueError(f"Failed to parse LLM response: {parse_error}. Raw response: {content}")


if __name__ == "__main__":
    # Test the intent extraction
    test_request = "Draw a sequence diagram for user login and database check"
    intent = extract_intent(test_request)
    print(json.dumps(intent.model_dump(), indent=2))