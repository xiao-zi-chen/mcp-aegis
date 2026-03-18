from __future__ import annotations

from datetime import datetime, timezone
import subprocess
from typing import Any

try:
    from mcpaegis_scan_orchestrator.runtime_adapters import resolve_runner_adapter
except ModuleNotFoundError:
    from runtime_adapters import resolve_runner_adapter

def detect_runtime_capabilities(sandbox_spec: dict[str, Any], timeout_seconds: int | None = 5) -> dict[str, Any]:
    adapter = resolve_runner_adapter(sandbox_spec)
    return adapter.detect_capabilities(timeout_seconds=timeout_seconds)


def run_sandbox_plan(
    sandbox_spec: dict[str, Any],
    *,
    execute: bool,
    timeout_seconds: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    adapter = resolve_runner_adapter(sandbox_spec)
    capabilities = adapter.detect_capabilities(timeout_seconds=5)

    if not sandbox_spec.get("allowExecution", False):
        result = {
            "status": "blocked",
            "executed": False,
            "exitCode": None,
            "stdout": "",
            "stderr": "",
            "reason": "policy denied execution",
            "generatedAt": generated_at,
        }
        return result, _build_launch_event("runtime-launch-blocked", sandbox_spec, result), capabilities

    if not execute:
        result = {
            "status": "planned",
            "executed": False,
            "exitCode": None,
            "stdout": "",
            "stderr": "",
            "reason": "dry-run only",
            "generatedAt": generated_at,
        }
        return result, _build_launch_event("runtime-launch-planned", sandbox_spec, result), capabilities

    if not capabilities.get("executeSupported", False) or not adapter.has_launch_command():
        result = {
            "status": "unavailable",
            "executed": False,
            "exitCode": None,
            "stdout": "",
            "stderr": "",
            "reason": capabilities.get("reason", "runtime unavailable"),
            "generatedAt": generated_at,
        }
        return result, _build_launch_event("runtime-launch-unavailable", sandbox_spec, result), capabilities

    try:
        completed = adapter.execute(timeout_seconds=timeout_seconds)
    except subprocess.TimeoutExpired:
        result = {
            "status": "timed_out",
            "executed": True,
            "exitCode": None,
            "stdout": "",
            "stderr": "",
            "reason": "sandbox execution timed out",
            "generatedAt": generated_at,
        }
        return result, _build_launch_event("runtime-launch-timeout", sandbox_spec, result), capabilities
    except OSError as exc:
        result = {
            "status": "unavailable",
            "executed": False,
            "exitCode": None,
            "stdout": "",
            "stderr": "",
            "reason": str(exc),
            "generatedAt": generated_at,
        }
        return result, _build_launch_event("runtime-launch-unavailable", sandbox_spec, result), capabilities

    result = {
        "status": "succeeded" if completed.returncode == 0 else "failed",
        "executed": True,
        "exitCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "reason": "",
        "generatedAt": generated_at,
    }
    return result, _build_launch_event("runtime-launch-executed", sandbox_spec, result), capabilities


def _build_launch_event(event_type: str, sandbox_spec: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "eventType": event_type,
        "generatedAt": result["generatedAt"],
        "engine": sandbox_spec.get("engine", ""),
        "executionMode": sandbox_spec.get("mode", ""),
        "executed": result["executed"],
        "status": result["status"],
        "exitCode": result["exitCode"],
        "reason": result["reason"],
    }
