import unittest
from pathlib import Path

from mcpaegis_policy.evaluator import evaluate_policy
from mcpaegis_policy.loader import load_policy_bundle


ROOT = Path(__file__).resolve().parents[3]
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


if __name__ == "__main__":
    unittest.main()
