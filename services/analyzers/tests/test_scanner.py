import unittest
from pathlib import Path

from mcpaegis_analyzers.scanner import scan_path
from mcpaegis_analyzers.scoring import score_findings


FIXTURES = Path(__file__).parent / "fixtures"


class ScannerTest(unittest.TestCase):
    def test_malicious_fixture_produces_findings_and_high_score(self) -> None:
        report = scan_path(str(FIXTURES / "malicious_server.py"))

        self.assertGreaterEqual(report.finding_count, 3)
        keys = {finding.finding_key for finding in report.findings}
        self.assertIn("shell-exec", keys)
        self.assertIn("network-egress", keys)
        self.assertIn("secret-env-access", keys)

        score = score_findings(report.findings)
        self.assertIn(score["decisionClass"], {"review", "restricted", "block"})
        self.assertGreaterEqual(score["score"], 25)

    def test_benign_fixture_stays_clean(self) -> None:
        report = scan_path(str(FIXTURES / "benign_server.py"))
        score = score_findings(report.findings)

        self.assertEqual(report.finding_count, 0)
        self.assertEqual(score["score"], 0)
        self.assertEqual(score["decisionClass"], "trusted")

    def test_poisoned_package_metadata_is_detected(self) -> None:
        report = scan_path(str(FIXTURES / "poisoned_package"))
        keys = {finding.finding_key for finding in report.findings}
        score = score_findings(report.findings)

        self.assertIn("manifest-install-script", keys)
        self.assertIn("python-build-hook", keys)
        self.assertIn("prompt-poisoning-metadata", keys)
        self.assertIn("suspicious-credential-request", keys)
        self.assertGreaterEqual(score["score"], 40)


if __name__ == "__main__":
    unittest.main()
