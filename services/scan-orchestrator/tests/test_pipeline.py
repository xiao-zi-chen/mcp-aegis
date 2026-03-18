import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "services" / "analyzers" / "tests" / "fixtures" / "malicious_server.py"
POLICY = ROOT / "packages" / "policy-spec" / "examples" / "default-policy.yaml"
SCHEMA = ROOT / "packages" / "policy-spec" / "schema.json"
MAIN = ROOT / "services" / "scan-orchestrator" / "src" / "mcpaegis_scan_orchestrator" / "main.py"


class PipelineTest(unittest.TestCase):
    def test_pipeline_detects_and_restricts_malicious_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "report.json"
            env = {
                **os.environ,
                "PYTHONPATH": os.pathsep.join(
                    [
                        str(ROOT / "services" / "analyzers" / "src"),
                        str(ROOT / "packages" / "sdk-python" / "src"),
                    ]
                ),
            }
            subprocess.run(
                [
                    sys.executable,
                    str(MAIN),
                    "--target",
                    str(TARGET),
                    "--policy",
                    str(POLICY),
                    "--schema",
                    str(SCHEMA),
                    "--transport",
                    "stdio",
                    "--output",
                    str(output_path),
                ],
                check=True,
                cwd=ROOT / "services" / "scan-orchestrator",
                env=env,
            )

            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(report["scanReport"]["findingCount"], 3)
            self.assertIn(report["policyDecision"]["decision"], {"review", "restricted", "deny", "allow"})
            self.assertNotEqual(report["policyDecision"]["decision"], "allow")
            self.assertGreaterEqual(len(report["recommendedActions"]), 1)


if __name__ == "__main__":
    unittest.main()
