from __future__ import annotations

from mcpaegis_analyzers.models import Finding
from mcpaegis_policy.evaluator import EvaluationResult


FINDING_ACTIONS = {
    "shell-exec": "Run this MCP server only inside an isolated runtime and require manual review of command execution paths.",
    "network-egress": "Apply an outbound domain allowlist and review every declared remote dependency.",
    "filesystem-write": "Limit writable mounts to a dedicated temp directory and keep the project workspace read-only by default.",
    "secret-env-access": "Inject only explicit, short-lived credentials instead of passing through the host environment.",
    "listener-exposure": "Block inbound exposure and run the server in a private network namespace.",
    "unsafe-setup-instruction": "Require human review before installation and reject any instruction that weakens endpoint protection or sandboxing.",
}


def build_recommendations(findings: list[Finding], decision: EvaluationResult) -> list[str]:
    recommendations: list[str] = []

    for finding in findings:
        action = FINDING_ACTIONS.get(finding.finding_key)
        if action and action not in recommendations:
            recommendations.append(action)

    if decision.decision == "deny":
        recommendations.append("Block installation until the package is reviewed or replaced.")
    elif decision.decision == "restricted":
        recommendations.append(
            f"Allow execution only with the `{decision.runtime_profile}` runtime profile and record audit events."
        )
    elif decision.decision == "review":
        recommendations.append("Require manual approval before installation or upgrade.")

    if decision.require_digest_pin:
        recommendations.append("Pin the exact package digest before allowing this server into shared environments.")

    if decision.remote_access == "deny":
        recommendations.append("Deny remote MCP access unless ownership and target domains are explicitly verified.")

    return recommendations
