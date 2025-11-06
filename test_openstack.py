"""Test script for OpenStack architecture diagram generation."""

from main import generate_diagram
from utils import print_success, print_error, print_tip, colorize, Colors
import sys

# OpenStack architecture description based on Red Hat documentation
# Reference: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux_openstack_platform/7/html/architecture_guide/components

request = """Red Hat Enterprise Linux OpenStack Platform is a collection of interacting services that control compute, storage, and networking resources.

Core OpenStack Services:
- Dashboard (horizon): Web browser-based dashboard for managing OpenStack services
- Identity (keystone): Centralized authentication and authorization service managing users, projects, and roles
- OpenStack Networking (neutron): Provides connectivity between interfaces of OpenStack services
- Compute (nova): Manages virtual machine instances and resources
- Block Storage (cinder): Provides block storage volumes to instances
- Object Storage (swift): Provides object storage service
- Image (glance): Manages virtual machine images
- Orchestration (heat): Provides orchestration service for cloud applications
- Telemetry (ceilometer): Collects metering and monitoring data

Third-party Components:
- MariaDB database: Used by all OpenStack components except Telemetry
- MongoDB database: Used by Telemetry service for storing collected data
- RabbitMQ: Message broker for OpenStack transactions, queuing, and distribution
- Memcached/Redis: External caching used by Object Storage, Dashboard, and Identity services

The Dashboard connects to Identity service for authentication. Identity service provides authentication to all other OpenStack services including Compute, Networking, Block Storage, Object Storage, Image, Orchestration, and Telemetry. Compute service manages virtual machines and connects to Block Storage for volumes and Image service for VM images. Networking service provides network connectivity to Compute instances. Object Storage uses Memcached for caching authenticated clients."""

try:
    print(colorize("=" * 60, Colors.CYAN))
    print(colorize("Generating OpenStack Architecture Diagram", Colors.CYAN, bold=True))
    print(colorize("=" * 60, Colors.CYAN))
    print("\nUsing Red Hat Enterprise Linux OpenStack Platform documentation")
    print(
        "Reference: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux_openstack_platform/7/html/architecture_guide/components\n"
    )

    rendered_file, source_file = generate_diagram(
        request, output_filename="openstack_architecture", silent=False
    )

    print_success(f"\nSuccess! Diagram generated successfully!", bold=True)
    print(f"   Rendered diagram: {rendered_file}")
    print(f"   Source code: {source_file}")
    print_tip(f"Open {rendered_file} to view the diagram\n")

except Exception as e:
    print_error(f"\nFailed to generate diagram: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
