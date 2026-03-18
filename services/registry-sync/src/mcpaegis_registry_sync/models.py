from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class SnapshotSource:
    registry: str
    baseUrl: str


@dataclass(slots=True)
class Repository:
    url: str = ""
    source: str = ""
    id: str = ""
    subfolder: str = ""


@dataclass(slots=True)
class Transport:
    type: str
    url: str = ""


@dataclass(slots=True)
class RegistryMeta:
    status: str
    publishedAt: str = ""
    updatedAt: str = ""
    statusChangedAt: str = ""
    isLatest: bool = False


@dataclass(slots=True)
class NormalizedServer:
    id: str
    name: str
    description: str
    version: str
    schemaUrl: str
    websiteUrl: str
    repository: Repository
    transports: list[Transport]
    registry: RegistryMeta


def to_json_document(generated_at: str, base_url: str, servers: list[NormalizedServer]) -> dict:
    return {
        "generatedAt": generated_at,
        "source": asdict(SnapshotSource(registry="official", baseUrl=base_url)),
        "servers": [asdict(server) for server in servers],
    }
