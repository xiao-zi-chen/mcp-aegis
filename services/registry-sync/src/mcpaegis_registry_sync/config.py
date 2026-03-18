from __future__ import annotations

from dataclasses import dataclass
import os

DEFAULT_BASE_URL = "https://registry.modelcontextprotocol.io/v0.1"
DEFAULT_OUTPUT_PATH = "artifacts/registry-sync/latest.json"
DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_PAGES = 1
DEFAULT_TIMEOUT_SECONDS = 20


@dataclass(slots=True)
class Settings:
    base_url: str = DEFAULT_BASE_URL
    output_path: str = DEFAULT_OUTPUT_PATH
    page_size: int = DEFAULT_PAGE_SIZE
    max_pages: int = DEFAULT_MAX_PAGES
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=os.getenv("MCP_AEGIS_REGISTRY_BASE_URL", DEFAULT_BASE_URL),
            output_path=os.getenv("MCP_AEGIS_REGISTRY_OUTPUT_PATH", DEFAULT_OUTPUT_PATH),
            page_size=int(os.getenv("MCP_AEGIS_REGISTRY_PAGE_SIZE", str(DEFAULT_PAGE_SIZE))),
            max_pages=int(os.getenv("MCP_AEGIS_REGISTRY_MAX_PAGES", str(DEFAULT_MAX_PAGES))),
            timeout_seconds=int(
                os.getenv("MCP_AEGIS_REGISTRY_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
            ),
        )
