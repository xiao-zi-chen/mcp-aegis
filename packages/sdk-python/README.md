# sdk-python

Current responsibility:

- load and validate policy bundles
- evaluate policy rules against scan results and server metadata

Run locally:

```powershell
cd packages/sdk-python
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```
