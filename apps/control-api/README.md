# control-api

Current responsibility:

- expose registry and policy APIs
- serve findings and audit metadata
- provide the operator-facing control plane backend

Suggested stack:

- Go
- Postgres

Current scope:

- health endpoint
- readiness endpoint
- registry snapshot-backed server listing
- policy bundle listing and lookup
- persisted assessment listing and lookup

Run locally:

```powershell
cd apps/control-api
go run .\cmd\control-api
```

Important environment variables:

- `MCP_AEGIS_API_ADDRESS`
- `MCP_AEGIS_SNAPSHOT_PATH`
- `MCP_AEGIS_POLICIES_DIR`
- `MCP_AEGIS_REPORTS_DIR`
