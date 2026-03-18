import unittest

from mcpaegis_registry_sync.normalize import normalize_servers


class NormalizeServersTest(unittest.TestCase):
    def test_normalize_servers_sorts_and_maps_fields(self) -> None:
        payload = {
            "servers": [
                {
                    "server": {
                        "$schema": "https://example/schema.json",
                        "name": "zeta/server",
                        "description": "Zeta",
                        "version": "2.0.0",
                        "websiteUrl": "https://example.com/zeta",
                        "repository": {
                            "url": "https://github.com/example/zeta",
                            "source": "github",
                            "id": "123",
                            "subfolder": "pkg",
                        },
                        "remotes": [{"type": "streamable-http", "url": "https://example.com/mcp"}],
                    },
                    "_meta": {
                        "io.modelcontextprotocol.registry/official": {
                            "status": "active",
                            "publishedAt": "2026-01-01T00:00:00Z",
                            "updatedAt": "2026-01-02T00:00:00Z",
                            "statusChangedAt": "2026-01-03T00:00:00Z",
                            "isLatest": True,
                        }
                    },
                },
                {
                    "server": {
                        "$schema": "https://example/schema.json",
                        "name": "alpha/server",
                        "description": "Alpha",
                        "version": "1.0.0",
                        "remotes": [],
                    },
                    "_meta": {"io.modelcontextprotocol.registry/official": {"status": "active"}},
                },
            ]
        }

        normalized = normalize_servers(payload)

        self.assertEqual([server.name for server in normalized], ["alpha/server", "zeta/server"])
        self.assertEqual(normalized[1].repository.url, "https://github.com/example/zeta")
        self.assertEqual(normalized[1].transports[0].url, "https://example.com/mcp")
        self.assertTrue(normalized[1].registry.isLatest)


if __name__ == "__main__":
    unittest.main()
