from __future__ import annotations

from typing import Any

from .models import NormalizedServer, RegistryMeta, Repository, Transport


def normalize_servers(payload: dict[str, Any]) -> list[NormalizedServer]:
    normalized: list[NormalizedServer] = []
    for item in payload.get("servers", []):
        server = item.get("server", {})
        meta = item.get("_meta", {}).get("io.modelcontextprotocol.registry/official", {})
        repository = server.get("repository", {})
        remotes = server.get("remotes", [])

        normalized.append(
            NormalizedServer(
                id=f"official:{server.get('name', '')}",
                name=server.get("name", ""),
                description=server.get("description", ""),
                version=server.get("version", ""),
                schemaUrl=server.get("$schema", ""),
                websiteUrl=server.get("websiteUrl", ""),
                repository=Repository(
                    url=repository.get("url", ""),
                    source=repository.get("source", ""),
                    id=repository.get("id", ""),
                    subfolder=repository.get("subfolder", ""),
                ),
                transports=[
                    Transport(type=remote.get("type", ""), url=remote.get("url", ""))
                    for remote in remotes
                ],
                registry=RegistryMeta(
                    status=meta.get("status", "unknown"),
                    publishedAt=meta.get("publishedAt", ""),
                    updatedAt=meta.get("updatedAt", ""),
                    statusChangedAt=meta.get("statusChangedAt", ""),
                    isLatest=bool(meta.get("isLatest", False)),
                ),
            )
        )

    normalized.sort(key=lambda server: server.name)
    return normalized
