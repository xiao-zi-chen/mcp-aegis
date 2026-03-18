import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "services" / "scan-orchestrator" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcpaegis_scan_orchestrator.runner import run_sandbox_plan


class RunnerTest(unittest.TestCase):
    def test_blocked_plan_does_not_execute(self) -> None:
        result, event, capabilities = run_sandbox_plan({"allowExecution": False, "engine": "docker", "mode": "planned"}, execute=False)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["executed"])
        self.assertEqual(event["eventType"], "runtime-launch-blocked")
        self.assertIn("binaryAvailable", capabilities)
        self.assertEqual(capabilities["adapter"], "docker")

    def test_dry_run_plan_returns_planned(self) -> None:
        result, event, capabilities = run_sandbox_plan(
            {"allowExecution": True, "engine": "docker", "mode": "planned", "dockerCommand": ["docker", "run"]},
            execute=False,
        )
        self.assertEqual(result["status"], "planned")
        self.assertFalse(result["executed"])
        self.assertEqual(event["eventType"], "runtime-launch-planned")
        self.assertEqual(capabilities["engine"], "docker")
        self.assertEqual(capabilities["adapter"], "docker")

    def test_unsupported_engine_returns_unavailable(self) -> None:
        result, event, capabilities = run_sandbox_plan(
            {"allowExecution": True, "engine": "custom-engine", "mode": "planned", "command": ["python", "--version"]},
            execute=True,
        )
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["executed"])
        self.assertEqual(event["eventType"], "runtime-launch-unavailable")
        self.assertTrue(capabilities["binaryAvailable"])
        self.assertEqual(capabilities["adapter"], "unsupported")
        self.assertFalse(capabilities["executeSupported"])


if __name__ == "__main__":
    unittest.main()
