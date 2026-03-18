# registry-sync

Current responsibility:

- sync package and server metadata from upstream MCP sources
- normalize identity across package ecosystems
- trigger scans for new or changed artifacts

Suggested stack:

- Python

Current scope:

- official registry sync
- normalization into a control-api-readable snapshot

Run locally:

```powershell
cd services/registry-sync
$env:PYTHONPATH='src'
python -m mcpaegis_registry_sync.main --page-size 20 --max-pages 1 --output examples/latest.json
```

Important environment variables:

- `MCP_AEGIS_REGISTRY_BASE_URL`
- `MCP_AEGIS_REGISTRY_OUTPUT_PATH`
- `MCP_AEGIS_REGISTRY_PAGE_SIZE`
- `MCP_AEGIS_REGISTRY_MAX_PAGES`
