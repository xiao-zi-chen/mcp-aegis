# analyzers

Current responsibility:

- hold static analyzer modules for MCP packages and server code
- emit structured findings instead of plain text
- provide risk scoring inputs for policy evaluation

Current scope:

- subprocess and shell execution detector
- filesystem mutation heuristic
- outbound network heuristic
- secret and environment access heuristic
- listener exposure heuristic
- suspicious metadata detector

Run locally:

```powershell
cd services/analyzers
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```
