"""Diagram Code Generation - Structured JSON → DaC Code"""

import json
from schemas import GraphContext
from langchain_core.runnables import Runnable
from langchain_core.prompts import PromptTemplate
from utils import render_prompt
from settings import AppSettings
from llm_client import LLMClient


class DaCGenerator:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.llm_client = LLMClient(settings=self.settings)
        self.code_gen_llm = self.llm_client.get_code_gen_llm()
        self.code_generation_chain: Runnable = (
            PromptTemplate.from_template(
                render_prompt(self.settings.code_generation_prompt_file_path)
            ) | self.code_gen_llm
        )

    def generate(self, graph_context: GraphContext) -> str:
        """
        Generate Diagram-as-Code (graphviz) from structured graph context.

        Uses the deterministic graph-to-DOT converter for reliable output.

        Args:
            graph_context: Structured GraphContext object

        Returns:
            str: Raw graphviz DOT code as a string
        """
        # Convert GraphIntent to dictionary format expected by generate_dot_file
        graph_dict = {
            "groups": [group.model_dump() for group in graph_context.groups],
            "components": [comp.model_dump() for comp in graph_context.components],
            "relationships": [rel.model_dump() for rel in graph_context.relationships],
        }

        # Generate DOT code using the deterministic converter
        dot_code = self.code_generation_chain.invoke({"graph_context": graph_dict})

        return dot_code


if __name__ == "__main__":
    # Test the code generation
    from schemas import Component, Relationship, Group, GraphContext

    test_context = GraphContext(
        title="Test Architecture",
        groups=[Group(id="vpc_1", label="VPC 1", type="vpc")],
        components=[
            Component(
                id="api_gateway", label="API Gateway", type="api", parent_group="vpc_1"
            ),
            Component(
                id="user_service",
                label="User Service",
                type="service",
                parent_group="vpc_1",
            ),
            Component(id="db", label="Database", type="database"),
        ],
        relationships=[
            Relationship(
                source="api_gateway",
                target="user_service",
                label="routes to",
                type="api_call",
            ),
            Relationship(
                source="user_service", target="db", label="queries", type="data_flow"
            ),
        ],
    )

    code = DaCGenerator(settings=AppSettings()).generate(test_context)
    print(code)
