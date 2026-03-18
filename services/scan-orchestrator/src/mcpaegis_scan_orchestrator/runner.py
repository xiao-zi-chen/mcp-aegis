from __future__ import annotations

from datetime import datetime, timezone
import shutil
import subprocess
from typing import Any


def run_sandbox_plan(
    sandbox_spec: dict[str, Any],
    *,
    execute: bool,
    timeout_seconds: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    docker_command = sandbox_spec.get("dockerCommand", [])

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
        return result, _build_launch_event("runtime-launch-blocked", sandbox_spec, result)

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
        return result, _build_launch_event("runtime-launch-planned", sandbox_spec, result)

    if not docker_command or shutil.which(docker_command[0]) is None:
        result = {
            "status": "unavailable",
            "executed": False,
            "exitCode": None,
            "stdout": "",
            "stderr": "",
            "reason": "docker executable not available",
            "generatedAt": generated_at,
        }
        return result, _build_launch_event("runtime-launch-unavailable", sandbox_spec, result)

    completed = subprocess.run(
        docker_command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    result = {
        "status": "succeeded" if completed.returncode == 0 else "failed",
        "executed": True,
        "exitCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "reason": "",
        "generatedAt": generated_at,
    }
    return result, _build_launch_event("runtime-launch-executed", sandbox_spec, result)


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
