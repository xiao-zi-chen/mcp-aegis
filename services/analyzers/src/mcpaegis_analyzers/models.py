from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class Finding:
    finding_key: str
    severity: str
    confidence: str
    category: str
    title: str
    detail: str
    file_path: str
    line: int
    evidence: dict
    remediation: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class ScanReport:
    target_path: str
    finding_count: int
    findings: list[Finding]

    def to_dict(self) -> dict:
        return {
            "targetPath": self.target_path,
            "findingCount": self.finding_count,
            "findings": [finding.to_dict() for finding in self.findings],
        }
