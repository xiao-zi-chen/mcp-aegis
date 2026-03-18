from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml


def load_policy_bundle(policy_path: str, schema_path: str) -> dict:
    policy = yaml.safe_load(Path(policy_path).read_text(encoding="utf-8"))
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    jsonschema.validate(policy, schema)
    return policy
