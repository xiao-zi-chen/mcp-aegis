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
            sql_output_path = Path(tmp_dir) / "report.sql"
            audit_output_path = Path(tmp_dir) / "audit.jsonl"
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
                    "--server-name",
                    "fixture/malicious-server",
                    "--server-version",
                    "0.0.1",
                    "--audit-output",
                    str(audit_output_path),
                    "--output",
                    str(output_path),
                    "--sql-output",
                    str(sql_output_path),
                ],
                check=True,
                cwd=ROOT / "services" / "scan-orchestrator",
                env=env,
            )

            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(report["scanReport"]["findingCount"], 3)
            self.assertEqual(report["server"]["name"], "fixture/malicious-server")
            self.assertIn(report["policyDecision"]["decision"], {"review", "restricted", "deny", "allow"})
            self.assertNotEqual(report["policyDecision"]["decision"], "allow")
            self.assertGreaterEqual(len(report["recommendedActions"]), 1)
            self.assertEqual(report["runtimePlan"]["executionMode"], "sandboxed")
            self.assertTrue(report["runtimePlan"]["requiresManualApproval"])
            self.assertEqual(report["sandboxSpec"]["engine"], "docker")
            self.assertEqual(report["launchAuditEvent"]["eventType"], "runtime-plan-generated")
            self.assertEqual(report["sandboxSpec"]["dockerCommand"][0], "docker")
            self.assertEqual(report["launchResult"]["status"], "planned")
            self.assertEqual(report["runtimeLaunchEvent"]["eventType"], "runtime-launch-planned")

            sql_payload = sql_output_path.read_text(encoding="utf-8")
            self.assertIn("INSERT INTO policy_evaluations", sql_payload)
            self.assertIn("fixture/malicious-server", sql_payload)

            audit_lines = audit_output_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(audit_lines), 2)


if __name__ == "__main__":
    unittest.main()
