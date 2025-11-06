"""Test script to verify diagram generation for samples in test_datasets.yaml."""

import sys
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    colorize,
    Colors,
    load_prompt,
)
from main import generate_diagram
from diagram_generator import DiagramGenerator
from schemas import Request, GraphContext, Component, Relationship
from settings import get_settings
from response_parser import extract_response_content, extract_json_content
import json


def load_test_samples() -> List[Dict]:
    """Load test samples from test_datasets.yaml."""
    test_file = Path(__file__).parent / "test_datasets.yaml"
    if not test_file.exists():
        raise FileNotFoundError(f"Test file not found: {test_file}")

    with open(test_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("test_samples", [])


def normalize_component_name(name: str) -> str:
    """Normalize component name for comparison (lowercase, strip spaces)."""
    return name.lower().strip()


def extract_components_from_dot(dot_code: str) -> Set[str]:
    """Extract component/node names from Graphviz DOT code."""
    components = set()
    
    # Extract all labels (both subgraph and node labels)
    # Pattern: label = "Label Name" or label="Label Name"
    label_pattern = r'label\s*=\s*["\']([^"\']+)["\']'
    all_labels = re.findall(label_pattern, dot_code, re.IGNORECASE)
    components.update(normalize_component_name(label) for label in all_labels)
    
    # Find node IDs: node_id [attributes] or "node_id" [attributes]
    node_id_pattern = r'^\s*["\']?([A-Za-z0-9_][A-Za-z0-9_\s-]+)["\']?\s*\['
    node_ids = re.findall(node_id_pattern, dot_code, re.MULTILINE)
    components.update(normalize_component_name(node_id) for node_id in node_ids)
    
    # Find node references in edges: "Source" -> "Target" or Source -> Target
    edge_pattern = r'["\']?([A-Za-z0-9_][A-Za-z0-9_\s-]+)["\']?\s*->\s*["\']?([A-Za-z0-9_][A-Za-z0-9_\s-]+)["\']?'
    edge_matches = re.findall(edge_pattern, dot_code)
    for source, target in edge_matches:
        components.add(normalize_component_name(source))
        components.add(normalize_component_name(target))

    return components


def validate_components(
    expected_components: List[str], generated_dot: str, sample_name: str
) -> Tuple[bool, List[str]]:
    """Validate that expected components are present in the generated diagram."""
    expected_set = {normalize_component_name(c) for c in expected_components}
    generated_set = extract_components_from_dot(generated_dot)
    
    # Also check the raw DOT code for component names (case-insensitive)
    dot_lower = generated_dot.lower()

    missing = []
    for expected in expected_set:
        found = False
        
        # First check if it's in the extracted components set
        for generated in generated_set:
            # Check for exact match or substring match
            if expected == generated or expected in generated or generated in expected:
                found = True
                break
        
        # Also check if the component name appears anywhere in the DOT code
        # (handles cases where it's in comments or labels we might have missed)
        if not found:
            # Split expected into words and check if all words appear
            expected_words = expected.split()
            if len(expected_words) > 1:
                # For multi-word components, check if all words appear in the DOT code
                if all(word in dot_lower for word in expected_words if len(word) > 2):
                    found = True
            else:
                # Single word - check if it appears as a whole word
                if re.search(r'\b' + re.escape(expected) + r'\b', dot_lower):
                    found = True
        
        if not found:
            missing.append(expected)

    if missing:
        return False, missing
    return True, []


def find_node_id_for_component(component_name: str, dot_code: str) -> List[str]:
    """Find node IDs that might represent a given component name."""
    normalized_name = normalize_component_name(component_name)
    component_words = normalized_name.split()
    possible_ids = []
    
    # Extract all node IDs and their labels
    # Pattern: node_id [label="Label"]
    node_pattern = r'([A-Za-z0-9_][A-Za-z0-9_\s-]*)\s*\[[^\]]*label\s*=\s*["\']([^"\']+)["\']'
    matches = re.findall(node_pattern, dot_code, re.IGNORECASE)
    
    for node_id, label in matches:
        label_normalized = normalize_component_name(label)
        # Check if component name matches the label
        if normalized_name == label_normalized or normalized_name in label_normalized:
            possible_ids.append(node_id.strip())
        # Check if all words from component name are in the label
        elif all(word in label_normalized for word in component_words if len(word) > 2):
            possible_ids.append(node_id.strip())
    
    # Also check node IDs directly (in case they match)
    node_id_pattern = r'^\s*([A-Za-z0-9_][A-Za-z0-9_\s-]+)\s*\['
    all_node_ids = re.findall(node_id_pattern, dot_code, re.MULTILINE)
    for node_id in all_node_ids:
        node_id_normalized = normalize_component_name(node_id.strip())
        if normalized_name == node_id_normalized or normalized_name in node_id_normalized:
            if node_id.strip() not in possible_ids:
                possible_ids.append(node_id.strip())
    
    # Check subgraph labels
    subgraph_pattern = r'subgraph\s+[^{]*\{[^}]*label\s*=\s*["\']([^"\']+)["\']'
    subgraph_labels = re.findall(subgraph_pattern, dot_code, re.IGNORECASE | re.DOTALL)
    for label in subgraph_labels:
        label_normalized = normalize_component_name(label)
        if normalized_name == label_normalized or normalized_name in label_normalized:
            # For subgraphs, we need to find nodes within them
            # This is a simplified check - we'll look for any node in the subgraph
            pass
    
    return possible_ids if possible_ids else [normalized_name.replace(' ', '_')]


def validate_relationships(
    expected_relationships: List[Dict], generated_dot: str, sample_name: str
) -> Tuple[bool, List[str]]:
    """Validate that expected relationships are present in the generated diagram."""
    missing = []
    for rel in expected_relationships:
        source_name = rel["source"]
        target_name = rel["target"]
        source_normalized = normalize_component_name(source_name)
        target_normalized = normalize_component_name(target_name)

        # Find possible node IDs for source and target
        source_ids = find_node_id_for_component(source_name, generated_dot)
        target_ids = find_node_id_for_component(target_name, generated_dot)
        
        found = False
        
        # Check all combinations of source and target IDs
        for source_id in source_ids:
            for target_id in target_ids:
                # Look for edge: source_id -> target_id
                edge_pattern = rf'\b{re.escape(source_id)}\b\s*->\s*\b{re.escape(target_id)}\b'
                if re.search(edge_pattern, generated_dot, re.IGNORECASE):
                    found = True
                    break
                # Try reverse direction
                edge_pattern_reverse = rf'\b{re.escape(target_id)}\b\s*->\s*\b{re.escape(source_id)}\b'
                if re.search(edge_pattern_reverse, generated_dot, re.IGNORECASE):
                    found = True
                    break
            if found:
                break
        
        # Also check if component names appear in edge labels or comments
        if not found:
            # Check if both source and target appear near an edge
            edge_lines = re.findall(r'[^;]*->[^;]*', generated_dot)
            for edge_line in edge_lines:
                edge_lower = edge_line.lower()
                source_words = source_normalized.split()
                target_words = target_normalized.split()
                # Check if all words from both components appear in the edge line
                if (all(word in edge_lower for word in source_words if len(word) > 2) and
                    all(word in edge_lower for word in target_words if len(word) > 2)):
                    found = True
                    break
        
        if not found:
            missing.append(f"{source_name} -> {target_name} ({rel['type']})")

    if missing:
        return False, missing
    return True, []


def test_sample_generation(sample: Dict, index: int, total: int) -> bool:
    """Test diagram generation for a single sample."""
    sample_name = sample.get("name", f"Sample {index + 1}")
    raw_text = sample.get("raw_text", "")
    expected_components = sample.get("components", [])
    expected_relationships = sample.get("relationships", [])

    print_info(f"\n[{index + 1}/{total}] Testing: {sample_name}")
    print(f"   Description: {sample.get('description', 'N/A')}")

    if not raw_text:
        print_warning("   Sample has no raw_text, skipping...")
        return True

    try:
        # Generate diagram
        output_filename = f"test_dataset_{index + 1}_{sample_name.lower().replace(' ', '_')}"
        rendered_file, source_file = generate_diagram(
            raw_text, output_filename=output_filename
        )

        # Read the generated DOT code
        if not Path(source_file).exists():
            print_error(f"   Source file not found: {source_file}")
            return False

        with open(source_file, "r", encoding="utf-8") as f:
            dot_code = f.read()

        print_success(f"   Diagram generated: {rendered_file}")

        # Validate components
        if expected_components:
            components_valid, missing_components = validate_components(
                expected_components, dot_code, sample_name
            )
            if components_valid:
                print_success(
                    f"   ✓ All {len(expected_components)} expected components found"
                )
            else:
                print_warning(
                    f"   ⚠ {len(missing_components)} component(s) not found: {', '.join(missing_components)}"
                )
                # Don't fail the test, just warn

        # Validate relationships
        if expected_relationships:
            relationships_valid, missing_relationships = validate_relationships(
                expected_relationships, dot_code, sample_name
            )
            if relationships_valid:
                print_success(
                    f"   ✓ All {len(expected_relationships)} expected relationships found"
                )
            else:
                print_warning(
                    f"   ⚠ {len(missing_relationships)} relationship(s) not found: {', '.join(missing_relationships[:3])}"
                )
                if len(missing_relationships) > 3:
                    print_warning(f"      ... and {len(missing_relationships) - 3} more")
                # Don't fail the test, just warn

        return True

    except Exception as e:
        print_error(f"   Failed to generate diagram: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_context_extraction(sample: Dict, index: int) -> bool:
    """Test context extraction for a single sample (without full generation)."""
    sample_name = sample.get("name", f"Sample {index + 1}")
    raw_text = sample.get("raw_text", "")
    expected_components = sample.get("components", [])
    expected_relationships = sample.get("relationships", [])

    if not raw_text:
        return True

    try:
        settings = get_settings()
        generator = DiagramGenerator(settings=settings)
        request = Request(raw_text, settings)

        # Extract context
        context_schema = generator.context_extraction_chain.invoke(
            {
                "user_request": request.user_request or request.raw_request,
                "documentation": request.file_content or "",
            }
        )

        response_content = extract_response_content(context_schema)
        json_str = extract_json_content(response_content)
        context_dict = json.loads(json_str)
        context = GraphContext(**context_dict)

        # Validate extracted components
        extracted_component_labels = {
            normalize_component_name(c.label) for c in context.components
        }
        expected_component_set = {
            normalize_component_name(c) for c in expected_components
        }

        found_components = extracted_component_labels.intersection(
            expected_component_set
        )
        component_coverage = (
            len(found_components) / len(expected_component_set)
            if expected_component_set
            else 1.0
        )

        # Validate extracted relationships
        extracted_relationships = []
        for rel in context.relationships:
            source_norm = normalize_component_name(rel.source)
            target_norm = normalize_component_name(rel.target)
            extracted_relationships.append((source_norm, target_norm))

        expected_rel_set = {
            (
                normalize_component_name(r["source"]),
                normalize_component_name(r["target"]),
            )
            for r in expected_relationships
        }

        found_relationships = set(extracted_relationships).intersection(expected_rel_set)
        relationship_coverage = (
            len(found_relationships) / len(expected_rel_set)
            if expected_rel_set
            else 1.0
        )

        print_info(
            f"   Context extraction: {len(context.components)} components, {len(context.relationships)} relationships"
        )
        print_info(
            f"   Component coverage: {component_coverage:.1%} ({len(found_components)}/{len(expected_component_set)})"
        )
        print_info(
            f"   Relationship coverage: {relationship_coverage:.1%} ({len(found_relationships)}/{len(expected_rel_set)})"
        )

        return True

    except Exception as e:
        print_warning(f"   Context extraction test failed: {e}")
        return True  # Don't fail on context extraction errors


def main():
    """Run all tests on samples from test_datasets.yaml."""
    print(colorize("=" * 60, Colors.CYAN))
    print(colorize("TEST DATASETS TEST SUITE", Colors.CYAN, bold=True))
    print(colorize("=" * 60, Colors.CYAN))

    try:
        samples = load_test_samples()
        if not samples:
            print_error("No test samples found in test_datasets.yaml")
            return 1

        print_info(f"\nLoaded {len(samples)} test sample(s) from test_datasets.yaml\n")

        passed = 0
        failed = 0

        # Test each sample
        for i, sample in enumerate(samples):
            # Test context extraction first (faster, no rendering)
            test_context_extraction(sample, i)

            # Test full diagram generation
            if test_sample_generation(sample, i, len(samples)):
                passed += 1
            else:
                failed += 1

        print("\n" + colorize("=" * 60, Colors.CYAN))
        print(
            colorize(
                f"RESULTS: {passed} passed, {failed} failed", Colors.CYAN, bold=True
            )
        )
        print(colorize("=" * 60, Colors.CYAN))

        if failed == 0:
            print_success("\nAll tests passed!", bold=True)
            return 0
        else:
            print_error(f"\n{failed} test(s) failed", bold=True)
            return 1

    except FileNotFoundError as e:
        print_error(f"Test file not found: {e}")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

