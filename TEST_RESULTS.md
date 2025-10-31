# Test Results: Red Hat Satellite Architecture Diagram

## Test Date
Generated on: $(date)

## Test Description
Testing the diagram generator with Red Hat Satellite 6 architecture documentation from:
https://docs.redhat.com/en/documentation/red_hat_satellite/6.2/html-single/architecture_guide/index

## Architecture Summary

Based on the Red Hat Satellite 6 documentation, the system architecture includes:

1. **External Content Sources**
   - Red Hat Customer Portal
   - Other content sources (Git, Docker Hub, Puppet Forge, etc.)

2. **Red Hat Satellite Server**
   - Central management server
   - Content synchronization and lifecycle management
   - Manages Capsule Servers and hosts

3. **Capsule Servers**
   - Mirror content from Satellite Server
   - Provide localized services (Puppet Master, DHCP, DNS, TFTP)
   - Enable content federation across geographical locations

4. **Managed Hosts**
   - Physical or virtual systems
   - Pull content and configuration from Capsule Servers
   - Include the base system running Capsule Server

## Test Results

### Mock Test (Without LLM)
✅ **PASSED** - Generated graph structure successfully

**Generated Components:**
- 4 Groups (External Sources, Satellite Environment, Capsule Environment, Host Environment)
- 12 Components (Red Hat Portal, Satellite Server, Capsule Servers, Services, Hosts)
- 13 Relationships (data flows, dependencies, API calls)

**Output Files:**
- `output/satellite_test.dot` - Graphviz source code (3,272 characters)
- `output/satellite_test.svg` - Rendered diagram

### Full Test (With LLM - Requires Ollama)

To run the full test with natural language processing:

1. **Ensure Ollama is running:**
   ```bash
   ollama serve
   ```

2. **Pull the required model:**
   ```bash
   ollama pull llama3.2:3b
   ```
   Or use an available model by updating `config.py`:
   ```python
   LLM_MODEL = "mistral:latest"  # if you have this model
   ```

3. **Run the test:**
   ```bash
   python test_satellite.py
   ```

## Generated Diagram Structure

The diagram correctly represents:
- Groups/subgraphs for organizing components
- Component types (server, service, api, host)
- Relationship types (data_flow, dependency, api_call)
- Proper parent_group assignments
- Clear labels and relationships

## Validation

✅ Syntax validation passed
✅ Graph structure is valid
✅ All components properly grouped
✅ Relationships correctly defined

## Next Steps

To view the generated diagram:
```bash
open output/satellite_test.svg
# or
xdg-open output/satellite_test.svg  # Linux
start output/satellite_test.svg      # Windows
```

## References

- [Red Hat Satellite 6.2 Architecture Guide](https://docs.redhat.com/en/documentation/red_hat_satellite/6.2/html-single/architecture_guide/index)

