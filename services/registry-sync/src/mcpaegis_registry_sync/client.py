from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


class OfficialRegistryClient:
    def __init__(self, base_url: str, timeout_seconds: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def list_servers(self, *, limit: int, cursor: str | None = None) -> dict[str, Any]:
        params = {"limit": str(limit)}
        if cursor:
            params["cursor"] = cursor

        url = f"{self.base_url}/servers?{urlencode(params)}"
        with urlopen(url, timeout=self.timeout_seconds) as response:
            return json.load(response)
