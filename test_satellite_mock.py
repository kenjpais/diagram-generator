"""Mock test script for Red Hat Satellite architecture - tests code generation without LLM."""
from schemas import GraphIntent, Group, Component, Relationship
from code_generation import generate_diagram_code
from graph_to_dot import generate_dot_file
from syntax_validation import validate_graphviz_syntax
import json

# Create a mock GraphIntent based on Red Hat Satellite architecture
# This simulates what the LLM would extract from the documentation
satellite_intent = GraphIntent(
    title="Red Hat Satellite 6 System Architecture Concept",
    groups=[
        Group(id="external_sources", label="External Content Sources", type="default"),
        Group(id="satellite_env", label="Satellite Server Environment", type="datacenter"),
        Group(id="capsule_env", label="Capsule Server Environment", type="datacenter"),
        Group(id="host_env", label="Managed Hosts", type="host_machine")
    ],
    components=[
        # External sources
        Component(id="redhat_portal", label="Red Hat Customer Portal", type="api", parent_group="external_sources"),
        Component(id="other_sources", label="Other Content Sources", type="api", parent_group="external_sources"),
        
        # Satellite Server
        Component(id="satellite_server", label="Satellite Server", type="server", parent_group="satellite_env"),
        
        # Capsule Servers
        Component(id="capsule_server_1", label="Capsule Server 1", type="server", parent_group="capsule_env"),
        Component(id="capsule_server_2", label="Capsule Server 2", type="server", parent_group="capsule_env"),
        
        # Services on Capsule
        Component(id="puppet_master", label="Puppet Master", type="service", parent_group="capsule_env"),
        Component(id="dns_service", label="DNS Service", type="service", parent_group="capsule_env"),
        Component(id="dhcp_service", label="DHCP Service", type="service", parent_group="capsule_env"),
        Component(id="tftp_service", label="TFTP Service", type="service", parent_group="capsule_env"),
        
        # Managed Hosts
        Component(id="host_1", label="Managed Host 1", type="host", parent_group="host_env"),
        Component(id="host_2", label="Managed Host 2", type="host", parent_group="host_env"),
        Component(id="capsule_base_host", label="Capsule Base Host", type="host", parent_group="capsule_env")
    ],
    relationships=[
        # External to Satellite
        Relationship(source="redhat_portal", target="satellite_server", label="synchronizes content", type="data_flow"),
        Relationship(source="other_sources", target="satellite_server", label="synchronizes content", type="data_flow"),
        
        # Satellite to Capsules
        Relationship(source="satellite_server", target="capsule_server_1", label="manages and mirrors content", type="data_flow"),
        Relationship(source="satellite_server", target="capsule_server_2", label="manages and mirrors content", type="data_flow"),
        
        # Capsule services
        Relationship(source="capsule_server_1", target="puppet_master", label="provides", type="dependency"),
        Relationship(source="capsule_server_1", target="dns_service", label="provides", type="dependency"),
        Relationship(source="capsule_server_1", target="dhcp_service", label="provides", type="dependency"),
        Relationship(source="capsule_server_1", target="tftp_service", label="provides", type="dependency"),
        
        # Capsule to Hosts
        Relationship(source="capsule_server_1", target="host_1", label="provides content and config", type="api_call"),
        Relationship(source="capsule_server_1", target="host_2", label="provides content and config", type="api_call"),
        Relationship(source="capsule_server_2", target="host_1", label="provides content and config", type="api_call"),
        
        # Capsule base host
        Relationship(source="satellite_server", target="capsule_base_host", label="manages", type="dependency"),
        Relationship(source="capsule_server_1", target="capsule_base_host", label="runs on", type="dependency")
    ],
    description="Red Hat Satellite 6 architecture with Satellite Server, Capsule Servers, and managed hosts"
)

def test_graph_generation():
    """Test the graph generation workflow."""
    print("="*60)
    print("Testing Red Hat Satellite Architecture Diagram Generation")
    print("="*60)
    print(f"\nIntent: {satellite_intent.title}")
    print(f"Groups: {len(satellite_intent.groups)}")
    print(f"Components: {len(satellite_intent.components)}")
    print(f"Relationships: {len(satellite_intent.relationships)}\n")
    
    # Step 1: Generate DOT code
    print("Step 1: Generating DOT code...")
    try:
        dot_code = generate_diagram_code(satellite_intent)
        print(f"✓ Generated DOT code ({len(dot_code)} characters)")
        print("\nFirst 500 characters of DOT code:")
        print(dot_code[:500])
        print("...\n")
    except Exception as e:
        print(f"✗ Failed to generate DOT code: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Validate syntax
    print("Step 2: Validating syntax...")
    try:
        is_valid, error_message = validate_graphviz_syntax(dot_code)
        if is_valid:
            print("✓ Syntax validation passed\n")
        else:
            print(f"✗ Syntax validation failed: {error_message}\n")
            return False
    except Exception as e:
        print(f"✗ Validation error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Save to file for inspection
    print("Step 3: Saving DOT code to file...")
    try:
        with open("output/satellite_test.dot", "w") as f:
            f.write(dot_code)
        print("✓ Saved to output/satellite_test.dot\n")
    except Exception as e:
        print(f"✗ Failed to save file: {e}\n")
    
    # Step 4: Print JSON structure
    print("Step 4: Intent structure:")
    print(json.dumps(satellite_intent.model_dump(), indent=2))
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)
    print("\nTo render the diagram, run:")
    print("  dot -Tsvg output/satellite_test.dot -o output/satellite_test.svg")
    print("\nThen open output/satellite_test.svg in a browser.\n")
    
    return True

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    
    success = test_graph_generation()
    exit(0 if success else 1)

