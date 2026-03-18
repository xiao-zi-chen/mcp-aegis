from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EvaluationResult:
    bundle: str
    bundle_version: int
    decision: str
    runtime_profile: str
    remote_access: str
    require_digest_pin: bool
    matched_rules: list[str]
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "bundleVersion": self.bundle_version,
            "decision": self.decision,
            "runtimeProfile": self.runtime_profile,
            "remoteAccess": self.remote_access,
            "requireDigestPin": self.require_digest_pin,
            "matchedRules": self.matched_rules,
            "reasons": self.reasons,
        }


def evaluate_policy(bundle: dict, context: dict) -> EvaluationResult:
    metadata = bundle["metadata"]
    spec = bundle["spec"]
    defaults = spec["defaults"]

    decision = defaults["installDecision"]
    runtime_profile = defaults["runtimeProfile"]
    remote_access = defaults["remoteAccess"]
    require_digest_pin = False
    matched_rules: list[str] = []
    reasons: list[str] = []

    for rule in spec["rules"]:
        if not _matches(rule["match"], context):
            continue

        matched_rules.append(rule["id"])
        action = rule["action"]
        if "reason" in action:
            reasons.append(action["reason"])
        if "runtimeProfile" in action:
            runtime_profile = action["runtimeProfile"]
        if "remoteAccess" in action:
            remote_access = action["remoteAccess"]
        if "requireDigestPin" in action:
            require_digest_pin = bool(action["requireDigestPin"])
        if "installDecision" in action:
            decision = action["installDecision"]
            if decision == "deny":
                break

    return EvaluationResult(
        bundle=metadata["name"],
        bundle_version=metadata["version"],
        decision=decision,
        runtime_profile=runtime_profile,
        remote_access=remote_access,
        require_digest_pin=require_digest_pin,
        matched_rules=matched_rules,
        reasons=reasons,
    )


def _matches(match: dict, context: dict) -> bool:
    for key, expected in match.items():
        if key == "risk":
            if not _match_risk(expected, context.get("risk", {})):
                return False
        elif key == "transport":
            transports = context.get("transport", [])
            if not _match_list(expected, transports):
                return False
        elif key == "ownership":
            if not _match_mapping(expected, context.get("ownership", {})):
                return False
        elif key == "remote":
            if not _match_remote(expected, context.get("remote", {})):
                return False
        elif key == "server":
            if not _match_mapping(expected, context.get("server", {})):
                return False
        elif key == "source":
            if not _match_mapping(expected, context.get("source", {})):
                return False
        elif key == "labels":
            if not _match_list(expected, context.get("labels", [])):
                return False
        else:
            return False
    return True


def _match_risk(expected: dict, actual: dict) -> bool:
    for key, value in expected.items():
        if key == "score":
            score = actual.get("score")
            if score is None:
                return False
            gte = value.get("gte")
            lte = value.get("lte")
            if gte is not None and score < gte:
                return False
            if lte is not None and score > lte:
                return False
        elif key == "class":
            if not _match_list(value, [actual.get("class", "")]):
                return False
        else:
            return False
    return True


def _match_list(expected: dict, actual: list[str]) -> bool:
    wanted = expected.get("in", [])
    actual_set = set(actual)
    return any(item in actual_set for item in wanted)


def _match_mapping(expected: dict, actual: dict) -> bool:
    for key, value in expected.items():
        if actual.get(key) != value:
            return False
    return True


def _match_remote(expected: dict, actual: dict) -> bool:
    for key, value in expected.items():
        actual_value = actual.get(key, "")
        if value == "*":
            if not actual_value:
                return False
            continue
        if actual_value != value:
            return False
    return True
