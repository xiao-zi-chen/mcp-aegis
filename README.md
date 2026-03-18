# MCP Aegis

Open-source security layer for the Model Context Protocol ecosystem.

MCP Aegis aims to make third-party MCP servers safer to discover, evaluate, install, and run. The initial direction is:

- security-aware MCP subregistry
- install-time verification and risk scoring
- policy-based approval and version pinning
- sandboxed execution for local MCP servers
- runtime audit trails for MCP tool usage

## Why This Project

The MCP ecosystem is growing quickly, but trust and runtime isolation are still weak in most real-world setups. MCP Aegis focuses on the missing control plane:

- which MCP servers should be trusted
- which versions are allowed
- what a server can access at runtime
- how teams can audit what happened later

## Current Status

This repository is now in the first implementation phase.

Available now:

- initial system architecture
- first threat model
- first policy specification
- reference policy schema and example bundle
- implementation roadmap
- working `control-api` service
- working `registry-sync` worker
- initial Postgres migration set
- working static analyzers for risky MCP code patterns
- working policy evaluator
- working end-to-end scan orchestrator
- persisted assessment reports queryable via `control-api`
- PostgreSQL import SQL export for scan decisions
- assessment filtering and summary query endpoints
- concrete runtime plan generation and runtime plan API endpoint
- planned sandbox spec generation with dry-run Docker command output
- sandbox runner skeleton with launch result and JSONL audit sink

Planned next:

- Postgres-backed persistence for `control-api`
- richer analyzer coverage and evidence
- CLI installer prototype
- runtime sandbox launcher

## Architecture

See [docs/architecture.md](docs/architecture.md) for the current design, including:

- high-level architecture
- trust boundaries
- install and runtime flows
- deployment topology
- OSS-friendly repository structure

## Core Documents

- [docs/architecture.md](docs/architecture.md)
- [docs/threat-model.md](docs/threat-model.md)
- [docs/policy-spec.md](docs/policy-spec.md)
- [docs/roadmap.md](docs/roadmap.md)
- [packages/policy-spec/schema.json](packages/policy-spec/schema.json)
- [packages/policy-spec/examples/default-policy.yaml](packages/policy-spec/examples/default-policy.yaml)

## Working Components

- [apps/control-api](apps/control-api)
- [services/registry-sync](services/registry-sync)
- [services/analyzers](services/analyzers)
- [services/scan-orchestrator](services/scan-orchestrator)
- [packages/sdk-python](packages/sdk-python)
- [db/migrations/0001_initial.sql](db/migrations/0001_initial.sql)

## Quick Start

Sync a small snapshot from the official MCP Registry:

```powershell
cd services/registry-sync
$env:PYTHONPATH='src'
python -m mcpaegis_registry_sync.main --page-size 20 --max-pages 1 --output examples/latest.json
```

Run the control API:

```powershell
cd apps/control-api
go run .\cmd\control-api
```

Example endpoints:

- `GET /healthz`
- `GET /readyz`
- `GET /api/v1/servers`
- `GET /api/v1/servers/{name}`
- `GET /api/v1/assessments`
- `GET /api/v1/assessments/{serverName}`
- `GET /api/v1/assessment-summary`
- `GET /api/v1/runtime-plans/{serverName}`
- `GET /api/v1/policies`
- `GET /api/v1/policies/{name}`

Run the detection pipeline against a target path:

```powershell
$env:PYTHONPATH='services/analyzers/src;packages/sdk-python/src'
python services/scan-orchestrator/src/mcpaegis_scan_orchestrator/main.py `
  --target services/analyzers/tests/fixtures/malicious_server.py `
  --policy packages/policy-spec/examples/default-policy.yaml `
  --schema packages/policy-spec/schema.json `
  --transport stdio `
  --server-name fixture/malicious-server `
  --container-image python:3.11-slim `
  --audit-output tmp/fixture-malicious-server.audit.jsonl `
  --output services/scan-orchestrator/examples/reports/fixture-malicious-server.json `
  --sql-output tmp/fixture-malicious-server.sql
```

## MVP Direction

The first open-source release should focus on:

1. MCP subregistry with security metadata
2. scan pipeline and explainable risk scoring
3. policy engine for allow, block, and pin decisions
4. Docker-based sandbox for local stdio MCP servers
5. CLI installer for approved MCP configurations

## License

Apache-2.0
