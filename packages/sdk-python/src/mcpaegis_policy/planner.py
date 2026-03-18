from __future__ import annotations

from typing import Any


def build_runtime_plan(bundle: dict, evaluation_result: Any, findings: list[dict], server: dict) -> dict[str, Any]:
    profiles = bundle["spec"]["profiles"]["sandbox"]
    profile = profiles.get(evaluation_result.runtime_profile, {})

    finding_keys = {finding["finding_key"] for finding in findings}
    execution_mode = "blocked" if evaluation_result.decision == "deny" else "sandboxed"
    requires_manual_approval = evaluation_result.decision in {"review", "restricted"}

    mounts = list(profile.get("mounts", []))
    writable_paths: list[str] = []
    if "filesystem-write" in finding_keys:
        writable_paths.append("/tmp/mcp-aegis")

    network_mode = profile.get("networkMode", "none")
    outbound_allowlist = profile.get("network", {}).get("allow", [])
    if evaluation_result.remote_access == "deny":
        outbound_allowlist = []

    env_allowlist = profile.get("environment", {}).get("allow", [])
    no_host_env_passthrough = "secret-env-access" in finding_keys or not env_allowlist

    hardening_flags = {
        "blockRemoteAccess": evaluation_result.remote_access == "deny",
        "requireDigestPin": evaluation_result.require_digest_pin,
        "readOnlyRootFs": profile.get("readOnlyRootFs", True),
        "noHostEnvPassthrough": no_host_env_passthrough,
        "disableInboundListeners": "listener-exposure" in finding_keys or True,
    }

    rationale = list(evaluation_result.reasons)
    if "shell-exec" in finding_keys:
        rationale.append("Shell execution was detected, so direct host execution should not be allowed.")
    if "network-egress" in finding_keys:
        rationale.append("Outbound networking was detected, so allowlists or full denial should be enforced.")
    if "prompt-poisoning-metadata" in finding_keys:
        rationale.append("Prompt or metadata poisoning patterns were detected, so human review is required.")

    return {
        "profileName": evaluation_result.runtime_profile,
        "executionMode": execution_mode,
        "allowExecution": evaluation_result.decision != "deny",
        "requiresManualApproval": requires_manual_approval,
        "networkMode": network_mode,
        "outboundAllowlist": outbound_allowlist,
        "mounts": mounts,
        "writablePaths": writable_paths,
        "environmentAllowlist": env_allowlist,
        "resources": profile.get("resources", {}),
        "hardeningFlags": hardening_flags,
        "serverContext": {
            "name": server.get("name", ""),
            "transport": server.get("transport", []),
            "remoteUrl": server.get("remoteUrl", ""),
        },
        "rationale": rationale,
    }
