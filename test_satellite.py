"""Test script for Red Hat Satellite architecture diagram generation."""
from main import generate_diagram
import sys

# Test with Red Hat Satellite architecture description from documentation
request = """Red Hat Satellite Server synchronizes content from Red Hat Customer Portal and other external content sources. 
The Satellite Server manages Capsule Servers which mirror content to facilitate content federation across various geographical locations. 
Host systems pull content and configuration from Capsule Servers in their location. 
Capsule Servers provide localized services such as Puppet Master, DHCP, DNS, and TFTP. 
The base system running a Capsule Server is also a managed host of the Satellite Server."""

try:
    print('Testing with Red Hat Satellite architecture...')
    print('='*60)
    rendered_file, source_file = generate_diagram(request, output_filename='satellite_architecture_test', silent=False)
    print(f'\n✓ Test completed successfully!')
    print(f'  Rendered: {rendered_file}')
    print(f'  Source: {source_file}')
except Exception as e:
    print(f'✗ Test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
