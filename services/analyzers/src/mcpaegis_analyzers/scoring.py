from __future__ import annotations

from collections import Counter

from .models import Finding


SEVERITY_WEIGHTS = {
    "critical": 35,
    "high": 20,
    "medium": 10,
    "low": 4,
}

CONFIDENCE_MULTIPLIERS = {
    "high": 1.0,
    "medium": 0.7,
    "low": 0.4,
}


def score_findings(findings: list[Finding]) -> dict:
    score = 0.0
    severity_counter = Counter()
    category_counter = Counter()

    for finding in findings:
        severity_counter[finding.severity] += 1
        category_counter[finding.category] += 1
        score += SEVERITY_WEIGHTS.get(finding.severity, 0) * CONFIDENCE_MULTIPLIERS.get(
            finding.confidence, 0.4
        )

    capped_score = round(min(score, 100.0), 2)
    decision_class = classify_score(capped_score)

    return {
        "score": capped_score,
        "decisionClass": decision_class,
        "evidenceCount": len(findings),
        "severityCounts": dict(severity_counter),
        "categoryCounts": dict(category_counter),
    }


def classify_score(score: float) -> str:
    if score >= 75:
        return "block"
    if score >= 50:
        return "restricted"
    if score >= 25:
        return "review"
    return "trusted"
