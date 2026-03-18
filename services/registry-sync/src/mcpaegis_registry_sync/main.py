from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .client import OfficialRegistryClient
from .config import Settings
from .models import to_json_document
from .normalize import normalize_servers
from .writer import write_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync MCP registry metadata into a local snapshot.")
    parser.add_argument("--output", help="Output path for the normalized snapshot JSON.")
    parser.add_argument("--page-size", type=int, help="Number of servers to request per page.")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to fetch.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = Settings.from_env()
    if args.output:
        settings.output_path = args.output
    if args.page_size:
        settings.page_size = args.page_size
    if args.max_pages:
        settings.max_pages = args.max_pages

    client = OfficialRegistryClient(settings.base_url, settings.timeout_seconds)

    cursor: str | None = None
    pages = 0
    all_servers = []

    while pages < settings.max_pages:
        payload = client.list_servers(limit=settings.page_size, cursor=cursor)
        all_servers.extend(normalize_servers(payload))
        cursor = payload.get("metadata", {}).get("nextCursor")
        pages += 1
        if not cursor:
            break

    document = to_json_document(
        generated_at=datetime.now(timezone.utc).isoformat(),
        base_url=settings.base_url,
        servers=all_servers,
    )
    write_snapshot(settings.output_path, document)


if __name__ == "__main__":
    main()
