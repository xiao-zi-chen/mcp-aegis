import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "packages" / "sdk-python" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcpaegis_policy.evaluator import evaluate_policy
from mcpaegis_policy.loader import load_policy_bundle
from mcpaegis_policy.planner import build_runtime_plan


POLICY_PATH = ROOT / "packages" / "policy-spec" / "examples" / "default-policy.yaml"
SCHEMA_PATH = ROOT / "packages" / "policy-spec" / "schema.json"


class PolicyEvaluationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_policy_bundle(str(POLICY_PATH), str(SCHEMA_PATH))

    def test_low_risk_verified_stdio_is_allowed(self) -> None:
        result = evaluate_policy(
            self.bundle,
            {
                "transport": ["stdio"],
                "risk": {"score": 10, "class": "trusted"},
                "ownership": {"verified": True},
                "remote": {"url": ""},
            },
        )

        self.assertEqual(result.decision, "allow")
        self.assertEqual(result.runtime_profile, "trusted")
        self.assertTrue(result.require_digest_pin)

    def test_high_risk_package_is_restricted(self) -> None:
        result = evaluate_policy(
            self.bundle,
            {
                "transport": ["stdio"],
                "risk": {"score": 55, "class": "restricted"},
                "ownership": {"verified": True},
                "remote": {"url": ""},
            },
        )

        self.assertEqual(result.decision, "restricted")
        self.assertEqual(result.runtime_profile, "restricted")
        self.assertEqual(result.remote_access, "deny")

    def test_unverified_remote_is_denied(self) -> None:
        result = evaluate_policy(
            self.bundle,
            {
                "transport": ["streamable-http"],
                "risk": {"score": 5, "class": "trusted"},
                "ownership": {"verified": False},
                "remote": {"url": "https://example.com/mcp"},
            },
        )

        self.assertEqual(result.decision, "deny")

    def test_runtime_plan_is_resolved_from_profile(self) -> None:
        result = evaluate_policy(
            self.bundle,
            {
                "transport": ["stdio"],
                "risk": {"score": 55, "class": "restricted"},
                "ownership": {"verified": True},
                "remote": {"url": ""},
            },
        )

        plan = build_runtime_plan(
            self.bundle,
            result,
            [{"finding_key": "filesystem-write"}, {"finding_key": "shell-exec"}],
            {"name": "fixture/malicious-server", "transport": ["stdio"], "remoteUrl": ""},
        )

        self.assertEqual(plan["profileName"], "restricted")
        self.assertEqual(plan["executionMode"], "sandboxed")
        self.assertIn("/tmp/mcp-aegis", plan["writablePaths"])
        self.assertTrue(plan["hardeningFlags"]["readOnlyRootFs"])


if __name__ == "__main__":
    unittest.main()
