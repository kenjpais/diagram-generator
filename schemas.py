"""Pydantic schemas for structured data in the diagram generation pipeline."""

from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
from utils import parse_file_path, handle_file
from settings import AppSettings


class Group(BaseModel):
    """Represents a group/subgraph (e.g., datacenter, VPC, on-premises environment)."""

    id: str = Field(..., description="Unique identifier for the group")
    label: str = Field(..., description="Human-readable label for the group")
    type: str = Field(
        default="default",
        description="Type of group (e.g., 'datacenter', 'vpc', 'cloud_region', 'on_prem_env', 'host_machine')",
    )


class Component(BaseModel):
    """Represents a component/node in the diagram."""

    id: str = Field(..., description="Unique identifier for the component")
    label: str = Field(..., description="Human-readable label for the component")
    type: str = Field(
        ...,
        description="Type of component (e.g., 'service', 'database', 'api', 'frontend', 'router', 'switch', 'server', 'client', 'host', 'vm', 'hypervisor')",
    )
    parent_group: Optional[str] = Field(
        None, description="ID of the parent group this component belongs to (if any)"
    )


class Relationship(BaseModel):
    """Represents a relationship/edge between components."""

    source: str = Field(..., description="ID of the source component")
    target: str = Field(..., description="ID of the target component")
    label: str = Field(..., description="Label describing the relationship")
    type: str = Field(
        default="default",
        description="Type of relationship (e.g., 'api_call', 'data_flow', 'dependency进一步提升', 'network_connection', 'vpn_link', 'inheritance')",
    )


class GraphContext(BaseModel):
    """Structured representation of a graph topology diagram."""

    title: str = Field(..., description="Title of the graph diagram")
    groups: List[Group] = Field(
        ..., description="List of all groups/subgraphs in the diagram"
    )
    components: List[Component] = Field(
        ..., description="List of all components/nodes in the diagram"
    )
    relationships: List[Relationship] = Field(
        ..., description="List of all relationships/edges in the diagram"
    )


class Request:
    """Represents a user request for diagram generation."""
    
    def __init__(self, request: str, settings: AppSettings):
        self.raw_request = request
        self.settings = settings
        self.user_request = None
        self.file_content = None
        self.filepath = None
        self.parse()

    def parse(self):
        self.filepath = parse_file_path(self.raw_request)
        if self.filepath:
            self.user_request = self.raw_request.replace(
                str(self.filepath), f"[{self.filepath.name}]"
            ).strip()
        self.file_content, self.filepath = handle_file(
            self.filepath, self.settings.data_dir
        )

    def __str__(self):
        return f"Request(user_request={self.raw_request}, file_content={self.file_content}, filepath={self.filepath})"
