"""Pydantic schemas for structured data in the diagram generation pipeline."""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Component(BaseModel):
    """Represents a component/node in the diagram."""
    id: str = Field(..., description="Unique identifier for the component")
    label: str = Field(..., description="Human-readable label for the component")
    type: str = Field(..., description="Type of component (e.g., 'actor', 'service', 'database', 'component')")


class Relationship(BaseModel):
    """Represents a relationship/edge in the diagram."""
    source_id: str = Field(..., description="ID of the source component")
    target_id: str = Field(..., description="ID of the target component")
    action: str = Field(..., description="Description of the action or relationship")


class DiagramIntent(BaseModel):
    """Structured representation of the diagram intent."""
    diagram_type: Literal["sequence", "flowchart", "component", "architecture", "graph", "state"] = Field(
        ..., description="Type of diagram to generate"
    )
    title: str = Field(..., description="Title of the diagram")
    components: List[Component] = Field(..., description="List of all components/nodes in the diagram")
    relationships: List[Relationship] = Field(..., description="List of all relationships/edges in the diagram")
    description: Optional[str] = Field(None, description="Additional description or context")
