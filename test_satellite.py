"""Test script for Red Hat Satellite architecture diagram generation."""

from main import generate_diagram
from utils import print_success, print_error, print_info, colorize, Colors
import sys

# Test with Red Hat Satellite architecture description from documentation
request = """Red Hat Satellite Server synchronizes content from Red Hat Customer Portal and other external content sources. 
The Satellite Server manages Capsule Servers which mirror content to facilitate content federation across various geographical locations. 
Host systems pull content and configuration from Capsule Servers in their location. 
Capsule Servers provide localized services such as Puppet Master, DHCP, DNS, and TFTP. 
The base system running a Capsule Server is also a managed host of the Satellite Server."""

try:
    print_info("Testing with Red Hat Satellite architecture...")
    print(colorize("=" * 60, Colors.CYAN))
    rendered_file, source_file = generate_diagram(
        request, output_filename="satellite_architecture_test", silent=False
    )
    print_success(f"\nTest completed successfully!", bold=True)
    print(f"  Rendered: {rendered_file}")
    print(f"  Source: {source_file}")
except Exception as e:
    print_error(f"Test failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
