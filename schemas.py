"""Pydantic schemas for structured data in the diagram generation pipeline."""
from pydantic import BaseModel, Field
from typing import List, Optional


class Group(BaseModel):
    """Represents a group/subgraph (e.g., datacenter, VPC, on-premises environment)."""
    id: str = Field(..., description="Unique identifier for the group")
    label: str = Field(..., description="Human-readable label for the group")
    type: str = Field(
        default="default",
        description="Type of group (e.g., 'datacenter', 'vpc', 'cloud_region', 'on_prem_env', 'host_machine')"
    )


class Component(BaseModel):
    """Represents a component/node in the diagram."""
    id: str = Field(..., description="Unique identifier for the component")
    label: str = Field(..., description="Human-readable label for the component")
    type: str = Field(
        ...,
        description="Type of component (e.g., 'service', 'database', 'api', 'frontend', 'router', 'switch', 'server', 'client', 'host', 'vm', 'hypervisor')"
    )
    parent_group: Optional[str] = Field(
        None,
        description="ID of the parent group this component belongs to (if any)"
    )


class Relationship(BaseModel):
    """Represents a relationship/edge between components."""
    source: str = Field(..., description="ID of the source component")
    target: str = Field(..., description="ID of the target component")
    label: str = Field(..., description="Label describing the relationship")
    type: str = Field(
        default="default",
        description="Type of relationship (e.g., 'api_call', 'data_flow', 'dependency进一步提升', 'network_connection', 'vpn_link', 'inheritance')"
    )


class GraphIntent(BaseModel):
    """Structured representation of a graph topology diagram."""
    title: str = Field(..., description="Title of the graph diagram")
    groups: List[Group] = Field(default_factory=list, description="List of groups/subgraphs")
    components: List[Component] = Field(..., description="List of all components/nodes in the diagram")
    relationships: List[Relationship] = Field(..., description="List of all relationships/edges in the diagram")
    description: Optional[str] = Field(None, description="Optional description or context")