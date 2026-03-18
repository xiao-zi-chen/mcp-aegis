import unittest

from mcpaegis_scan_orchestrator.runner import run_sandbox_plan


class RunnerTest(unittest.TestCase):
    def test_blocked_plan_does_not_execute(self) -> None:
        result, event = run_sandbox_plan({"allowExecution": False, "engine": "docker", "mode": "planned"}, execute=False)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["executed"])
        self.assertEqual(event["eventType"], "runtime-launch-blocked")

    def test_dry_run_plan_returns_planned(self) -> None:
        result, event = run_sandbox_plan(
            {"allowExecution": True, "engine": "docker", "mode": "planned", "dockerCommand": ["docker", "run"]},
            execute=False,
        )
        self.assertEqual(result["status"], "planned")
        self.assertFalse(result["executed"])
        self.assertEqual(event["eventType"], "runtime-launch-planned")

    def test_execute_without_docker_returns_unavailable(self) -> None:
        result, event = run_sandbox_plan(
            {"allowExecution": True, "engine": "missing-runner", "mode": "planned", "dockerCommand": ["definitely-not-a-real-binary", "run"]},
            execute=True,
        )
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["executed"])
        self.assertEqual(event["eventType"], "runtime-launch-unavailable")


if __name__ == "__main__":
    unittest.main()
