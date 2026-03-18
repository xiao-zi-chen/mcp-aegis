from __future__ import annotations

from pathlib import Path

from .models import Finding, ScanReport
from .rules import RULES, Rule


TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".md",
    ".txt",
    ".rst",
    ".sh",
}


def scan_path(target_path: str) -> ScanReport:
    root = Path(target_path)
    if not root.exists():
        raise FileNotFoundError(f"target path does not exist: {target_path}")

    findings: list[Finding] = []
    if root.is_file():
        findings.extend(_scan_file(root, root.parent))
    else:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            findings.extend(_scan_file(path, root))

    return ScanReport(target_path=str(root), finding_count=len(findings), findings=findings)


def _scan_file(path: Path, root: Path) -> list[Finding]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    findings: list[Finding] = []
    relative_path = path.relative_to(root).as_posix() if path != root else path.name

    for rule in RULES:
        if rule.file_extensions and path.suffix.lower() not in rule.file_extensions:
            continue

        finding = _apply_rule(rule, relative_path, content)
        if finding is not None:
            findings.append(finding)

    return findings


def _apply_rule(rule: Rule, relative_path: str, content: str) -> Finding | None:
    for pattern in rule.patterns:
        match = pattern.search(content)
        if not match:
            continue

        line = content[: match.start()].count("\n") + 1
        evidence_line = content.splitlines()[line - 1] if content.splitlines() else ""
        return Finding(
            finding_key=rule.key,
            severity=rule.severity,
            confidence=rule.confidence,
            category=rule.category,
            title=rule.title,
            detail=rule.detail,
            file_path=relative_path,
            line=line,
            evidence={"pattern": pattern.pattern, "matchedLine": evidence_line.strip()},
            remediation=rule.remediation,
        )

    return None
