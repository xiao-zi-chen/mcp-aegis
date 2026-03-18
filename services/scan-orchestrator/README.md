# scan-orchestrator

Current responsibility:

- run the first end-to-end detection loop
- invoke analyzers on a target path
- score findings into a risk class
- evaluate policy and output an actionable decision report

Suggested stack:

- Python

Current scope:

- local target scan orchestration
- risk score generation
- policy evaluation
- JSON report output
- PostgreSQL import SQL export

Run locally:

```powershell
$env:PYTHONPATH='services/analyzers/src;packages/sdk-python/src'
python services/scan-orchestrator/src/mcpaegis_scan_orchestrator/main.py `
  --target services/analyzers/tests/fixtures/malicious_server.py `
  --policy packages/policy-spec/examples/default-policy.yaml `
  --schema packages/policy-spec/schema.json `
  --transport stdio `
  --server-name fixture/malicious-server `
  --output services/scan-orchestrator/examples/reports/fixture-malicious-server.json `
  --sql-output tmp/fixture-malicious-server.sql
```
