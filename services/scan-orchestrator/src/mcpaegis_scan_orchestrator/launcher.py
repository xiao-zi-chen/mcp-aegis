from __future__ import annotations

from pathlib import Path
from typing import Any


def build_sandbox_spec(
    runtime_plan: dict[str, Any],
    server: dict[str, Any],
    *,
    target_path: str,
    image: str | None = None,
    command: list[str] | None = None,
) -> dict[str, Any]:
    allow_execution = bool(runtime_plan.get("allowExecution", False))
    inferred_image = image or _infer_image(target_path)
    inferred_command = command or _infer_command(target_path)

    spec = {
        "engine": "docker",
        "mode": "planned",
        "allowExecution": allow_execution,
        "image": inferred_image,
        "command": inferred_command,
        "entrypointInferred": command is None,
        "workingDirectory": "/workspace/package",
        "readOnlyRootFs": runtime_plan.get("hardeningFlags", {}).get("readOnlyRootFs", True),
        "networkMode": runtime_plan.get("networkMode", "none"),
        "mounts": _normalize_mounts(runtime_plan.get("mounts", [])),
        "tmpfs": _build_tmpfs(runtime_plan.get("writablePaths", [])),
        "environmentAllowlist": runtime_plan.get("environmentAllowlist", []),
        "resources": runtime_plan.get("resources", {}),
        "hardeningFlags": runtime_plan.get("hardeningFlags", {}),
        "dockerCommand": [],
    }

    if allow_execution:
        spec["dockerCommand"] = _build_docker_command(spec, server)

    return spec


def build_launch_audit_event(
    server: dict[str, Any],
    policy_decision: dict[str, Any],
    runtime_plan: dict[str, Any],
    sandbox_spec: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    return {
        "eventType": "runtime-plan-generated",
        "generatedAt": generated_at,
        "serverName": server.get("name", ""),
        "serverVersion": server.get("version", ""),
        "decision": policy_decision.get("decision", ""),
        "runtimeProfile": runtime_plan.get("profileName", ""),
        "engine": sandbox_spec.get("engine", ""),
        "allowExecution": sandbox_spec.get("allowExecution", False),
        "networkMode": sandbox_spec.get("networkMode", ""),
        "mountCount": len(sandbox_spec.get("mounts", [])),
        "tmpfsCount": len(sandbox_spec.get("tmpfs", [])),
    }


def _infer_image(target_path: str) -> str:
    suffix = Path(target_path).suffix.lower()
    if suffix == ".py":
        return "python:3.11-slim"
    if suffix in {".js", ".mjs", ".cjs"}:
        return "node:20-alpine"
    if suffix in {".ts", ".tsx"}:
        return "node:20-alpine"
    return "ubuntu:24.04"


def _infer_command(target_path: str) -> list[str]:
    target = Path(target_path)
    suffix = target.suffix.lower()
    container_target = f"/workspace/package/{target.name}"
    if suffix == ".py":
        return ["python", container_target]
    if suffix in {".js", ".mjs", ".cjs"}:
        return ["node", container_target]
    if suffix in {".ts", ".tsx"}:
        return ["node", container_target]
    return ["sh", "-lc", f"echo 'Provide an explicit runtime command for {target.name}' && exit 1"]


def _normalize_mounts(mounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for mount in mounts:
        normalized.append(
            {
                "hostPath": mount.get("hostPath", ""),
                "containerPath": mount.get("containerPath", ""),
                "readOnly": bool(mount.get("readOnly", False)),
            }
        )
    return normalized


def _build_tmpfs(paths: list[str]) -> list[dict[str, Any]]:
    return [{"path": path, "sizeMb": 64} for path in paths]


def _build_docker_command(spec: dict[str, Any], server: dict[str, Any]) -> list[str]:
    command = ["docker", "run", "--rm"]

    if spec.get("readOnlyRootFs", True):
        command.append("--read-only")

    network_mode = spec.get("networkMode", "none")
    if network_mode == "none":
        command.extend(["--network", "none"])

    resources = spec.get("resources", {})
    memory_mb = resources.get("memoryMb")
    if memory_mb:
        command.extend(["--memory", f"{memory_mb}m"])

    process_limit = resources.get("processLimit")
    if process_limit:
        command.extend(["--pids-limit", str(process_limit)])

    for mount in spec.get("mounts", []):
        volume = f"{mount['hostPath']}:{mount['containerPath']}"
        if mount.get("readOnly", False):
            volume += ":ro"
        command.extend(["-v", volume])

    for tmpfs in spec.get("tmpfs", []):
        command.extend(["--tmpfs", f"{tmpfs['path']}:rw,noexec,nosuid,size={tmpfs['sizeMb']}m"])

    for env_name in spec.get("environmentAllowlist", []):
        command.extend(["-e", env_name])

    command.extend(["-w", spec.get("workingDirectory", "/workspace/package")])
    command.append(spec.get("image", "ubuntu:24.04"))
    command.extend(spec.get("command", []))
    return command
