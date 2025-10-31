"""Convert Advanced Architecture Graph Model JSON to Graphviz DOT format."""
from collections import defaultdict
from typing import Dict, Any


def generate_dot_file(graph_json: dict) -> str:
    """
    Converts the Advanced Architecture Graph Model (v2) JSON 
    into a Graphviz DOT string with subgraphs.

    Args:
        graph_json: Dictionary containing groups, components, and relationships
        
    Returns:
        str: Graphviz DOT format code
    """
    
    # --- Style Mappings ---
    COMPONENT_STYLES = {
        "service": "shape=box, style=rounded, fillcolor=\"#D6EAF8\"",
        "database": "shape=cylinder, fillcolor=\"#D1F2EB\"",
        "api": "shape=diamond, fillcolor=\"#FADBD8\"",
        "frontend": "shape=component, fillcolor=\"#FDEDEC\"",
        "router": "shape=Mdiamond, fillcolor=\"#E8DAEF\"",
        "switch": "shape=box, style=rounded, fillcolor=\"#FCF3CF\"",
        "server": "shape=box, style=solid, fillcolor=\"#EDF6E5\"",
        "client": "shape=ellipse, fillcolor=\"#EBDEF0\"",
        "host": "shape=box, style=rounded, fillcolor=\"#D5DBDB\"",
        "vm": "shape=box, style=dashed, fillcolor=\"#D5DBDB\"",
        "hypervisor": "shape=box, style=solid, fillcolor=\"#AEB6BF\"",
        "queue": "shape=box, style=rounded, fillcolor=\"#F8C471\"",
        "default": "shape=box, fillcolor=\"#ECF0F1\""
    }
    
    RELATIONSHIP_STYLES = {
        "api_call": "style=solid, arrowhead=vee, color=\"#2980B9\"",
        "data_flow": "style=dashed, arrowhead=normal, color=\"#1ABC9C\"",
        "dependency": "style=dotted, arrowhead=vee, color=\"#95A5A6\"",
        "network_connection": "style=solid, arrowhead=normal, color=\"#34495E\"",
        "vpn_link": "style=bold, arrowhead=none, color=\"#E74C3C\", label=\"VPN\"",
        "inheritance": "style=dashed, arrowhead=empty, color=\"#9B59B6\"",
        "default": "style=solid, arrowhead=vee, color=\"#2C3E50\""
    }
    
    GROUP_STYLES = {
        "datacenter": ("label=\"{label}\"", "style=dashed", "bgcolor=\"#F4F6F6\""),
        "cloud_region": ("label=\"{label}\"", "style=rounded", "bgcolor=\"#EBF5FB\""),
        "vpc": ("label=\"{label}\"", "style=rounded", "bgcolor=\"#FDF2E9\""),
        "subnet": ("label=\"{label}\"", "style=dotted", "bgcolor=\"#F9E79F\""),
        "on_prem_env": ("label=\"{label}\"", "style=solid", "bgcolor=\"#D5DBDB\""),
        "host_machine": ("label=\"{label}\"", "style=rounded", "bgcolor=\"#E8F8F5\""),
        "default": ("label=\"{label}\"", "style=dotted", "bgcolor=\"#EEEEEE\"")
    }
    # --- End Styles ---
    
    dot_lines = [
        "digraph G {",
        "    # Graph-level attributes",
        "    graph [rankdir=TB, nodesep=1, ranksep=1.5, compound=true];",
        "    node [style=filled];",
        "    edge [fontsize=10];",
        ""
    ]
    
    # --- Group components by parent ---
    components_by_group = defaultdict(list)
    orphan_components = []
    
    for comp in graph_json.get("components", []):
        parent = comp.get("parent_group")
        if parent:
            components_by_group[parent].append(comp)
        else:
            orphan_components.append(comp)
    
    # --- Render Groups (Subgraphs) ---
    dot_lines.append("    # Groups (Subgraphs)")
    for group in graph_json.get("groups", []):
        group_id = group["id"]
        group_label = group["label"]
        group_type = group.get("type", "default")
        style_attrs = GROUP_STYLES.get(group_type, GROUP_STYLES["default"])
        
        dot_lines.append(f'    subgraph "cluster_{group_id}" {{')
        # Format each attribute on separate lines
        for attr_template in style_attrs:
            attr = attr_template.format(label=group_label)
            dot_lines.append(f'        {attr};')
        
        # Render components inside this group
        for comp in components_by_group.get(group_id, []):
            comp_type = comp.get("type", "default")
            comp_style = COMPONENT_STYLES.get(comp_type, COMPONENT_STYLES["default"])
            dot_lines.append(f'        {comp["id"]} [label="{comp["label"]}", {comp_style}];')
        
        dot_lines.append("    }")
    
    # --- Render Orphan Components (nodes not in any group) ---
    if orphan_components:
        dot_lines.append("\n    # Orphan Components")
        for comp in orphan_components:
            comp_type = comp.get("type", "default")
            comp_style = COMPONENT_STYLES.get(comp_type, COMPONENT_STYLES["default"])
            dot_lines.append(f'    {comp["id"]} [label="{comp["label"]}", {comp_style}];')
    
    # --- Render All Relationships (Edges) ---
    dot_lines.append("\n    # Relationships (Edges)")
    for rel in graph_json.get("relationships", []):
        rel_type = rel.get("type", "default")
        style = RELATIONSHIP_STYLES.get(rel_type, RELATIONSHIP_STYLES["default"])
        label = rel.get("label", "")
        dot_lines.append(f'    {rel["source"]} -> {rel["target"]} [label="{label}", {style}];')
    
    dot_lines.append("}")
    return "\n".join(dot_lines)