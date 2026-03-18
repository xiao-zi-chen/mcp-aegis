from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class Rule:
    key: str
    severity: str
    confidence: str
    category: str
    title: str
    detail: str
    remediation: str
    patterns: tuple[re.Pattern[str], ...]
    file_extensions: tuple[str, ...] = ()


RULES: tuple[Rule, ...] = (
    Rule(
        key="shell-exec",
        severity="high",
        confidence="high",
        category="execution",
        title="Potential shell or process execution",
        detail="This code invokes a shell or subprocess API that can execute arbitrary commands.",
        remediation="Review whether shell execution is required and restrict command construction or block the package.",
        patterns=(
            re.compile(r"\bos\.system\s*\("),
            re.compile(r"\bsubprocess\.(run|Popen|call|check_output|check_call)\s*\("),
            re.compile(r"\bshell\s*=\s*True\b"),
            re.compile(r"\bchild_process\.(exec|spawn|execSync|spawnSync)\s*\("),
        ),
        file_extensions=(".py", ".js", ".ts", ".tsx", ".jsx"),
    ),
    Rule(
        key="network-egress",
        severity="medium",
        confidence="medium",
        category="network",
        title="Potential outbound network access",
        detail="This code uses networking libraries that may exfiltrate data or call undeclared endpoints.",
        remediation="Require an outbound allowlist and review target domains before allowing execution.",
        patterns=(
            re.compile(r"\brequests\.(get|post|put|delete|patch)\s*\("),
            re.compile(r"\bhttpx\.(get|post|put|delete|patch)\s*\("),
            re.compile(r"\burllib\.request\.urlopen\s*\("),
            re.compile(r"\bsocket\.(create_connection|socket)\s*\("),
            re.compile(r"\bfetch\s*\("),
        ),
        file_extensions=(".py", ".js", ".ts", ".tsx", ".jsx"),
    ),
    Rule(
        key="filesystem-write",
        severity="medium",
        confidence="medium",
        category="filesystem",
        title="Potential filesystem mutation",
        detail="This code writes to or deletes files and directories.",
        remediation="Run in a restricted mount profile and review whether write access is actually necessary.",
        patterns=(
            re.compile(r"\bopen\s*\([^)]*,\s*[\"'](w|a|x|wb|ab|xb)[\"']"),
            re.compile(r"\b(write_text|write_bytes|unlink|rmtree|remove|rename|replace)\s*\("),
            re.compile(r"\bfs\.(writeFile|writeFileSync|rm|rmSync|unlink|unlinkSync)\s*\("),
        ),
        file_extensions=(".py", ".js", ".ts", ".tsx", ".jsx"),
    ),
    Rule(
        key="secret-env-access",
        severity="medium",
        confidence="medium",
        category="secrets",
        title="Potential secret or environment access",
        detail="This code reads environment variables that may include credentials or host secrets.",
        remediation="Inject only explicit environment variables and short-lived credentials at runtime.",
        patterns=(
            re.compile(r"\bos\.environ\b"),
            re.compile(r"\bos\.getenv\s*\("),
            re.compile(r"\bprocess\.env\b"),
        ),
        file_extensions=(".py", ".js", ".ts", ".tsx", ".jsx"),
    ),
    Rule(
        key="listener-exposure",
        severity="high",
        confidence="medium",
        category="network",
        title="Potential externally reachable listener",
        detail="This code appears to bind a local service to all interfaces or expose an HTTP listener.",
        remediation="Run inside an isolated network namespace and deny inbound exposure by default.",
        patterns=(
            re.compile(r"0\.0\.0\.0"),
            re.compile(r"\bapp\.listen\s*\("),
            re.compile(r"\bHTTPServer\s*\("),
            re.compile(r"\buvicorn\.run\s*\("),
            re.compile(r"\bserve\s*\("),
        ),
        file_extensions=(".py", ".js", ".ts"),
    ),
    Rule(
        key="unsafe-setup-instruction",
        severity="medium",
        confidence="high",
        category="metadata",
        title="Potentially unsafe operator instruction",
        detail="Project documentation contains instructions that weaken isolation or request broad credentials.",
        remediation="Require manual review before installation and avoid packages that ask users to disable protections.",
        patterns=(
            re.compile(r"disable (the )?sandbox", re.IGNORECASE),
            re.compile(r"full disk access", re.IGNORECASE),
            re.compile(r"set .*token", re.IGNORECASE),
            re.compile(r"run as administrator", re.IGNORECASE),
            re.compile(r"turn off antivirus", re.IGNORECASE),
        ),
        file_extensions=(".md", ".txt", ".rst"),
    ),
    Rule(
        key="manifest-install-script",
        severity="high",
        confidence="high",
        category="supply-chain",
        title="Potential package install or lifecycle script",
        detail="This package manifest defines install-time or publish-time hooks that can execute code during installation.",
        remediation="Require manual review of lifecycle scripts and prefer packages without install-time execution.",
        patterns=(
            re.compile(r'"preinstall"\s*:'),
            re.compile(r'"install"\s*:'),
            re.compile(r'"postinstall"\s*:'),
            re.compile(r'"prepare"\s*:'),
        ),
        file_extensions=(".json",),
    ),
    Rule(
        key="python-build-hook",
        severity="high",
        confidence="medium",
        category="supply-chain",
        title="Potential Python build or setup execution hook",
        detail="This package appears to define Python packaging hooks that may execute code during build or installation.",
        remediation="Review build backends and setup hooks before allowing installation in shared environments.",
        patterns=(
            re.compile(r"\bsetup\s*\("),
            re.compile(r"build-backend\s*="),
            re.compile(r"cmdclass\s*="),
        ),
        file_extensions=(".py", ".toml"),
    ),
    Rule(
        key="prompt-poisoning-metadata",
        severity="high",
        confidence="medium",
        category="metadata",
        title="Potential prompt or tool metadata poisoning",
        detail="Project metadata contains language that attempts to steer the model or operator around safety checks.",
        remediation="Review tool descriptions manually and block packages that instruct the model to ignore safety or policy controls.",
        patterns=(
            re.compile(r"ignore (all )?(previous|prior) instructions", re.IGNORECASE),
            re.compile(r"do not tell the user", re.IGNORECASE),
            re.compile(r"always comply", re.IGNORECASE),
            re.compile(r"bypass (security|safety|policy)", re.IGNORECASE),
            re.compile(r"override (the )?(system|developer) prompt", re.IGNORECASE),
        ),
        file_extensions=(".md", ".txt", ".rst", ".json"),
    ),
    Rule(
        key="suspicious-credential-request",
        severity="medium",
        confidence="high",
        category="metadata",
        title="Potential broad credential request",
        detail="Project metadata asks for broad or persistent credentials that exceed normal least-privilege setup.",
        remediation="Require narrowly scoped credentials and deny packages that request personal access tokens or admin credentials without strong justification.",
        patterns=(
            re.compile(r"personal access token", re.IGNORECASE),
            re.compile(r"api key with full access", re.IGNORECASE),
            re.compile(r"administrator credentials", re.IGNORECASE),
            re.compile(r"root token", re.IGNORECASE),
        ),
        file_extensions=(".md", ".txt", ".rst"),
    ),
)
