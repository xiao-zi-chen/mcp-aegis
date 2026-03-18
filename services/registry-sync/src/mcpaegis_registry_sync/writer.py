from __future__ import annotations

import json
from pathlib import Path


def write_snapshot(path: str, document: dict) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=False), encoding="utf-8")
