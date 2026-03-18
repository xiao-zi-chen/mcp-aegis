from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Protocol


class RunnerAdapter(Protocol):
    engine: str
    adapter_name: str

    def detect_capabilities(self, timeout_seconds: int | None = 5) -> dict[str, Any]:
        ...

    def has_launch_command(self) -> bool:
        ...

    def execute(self, timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
        ...


@dataclass(slots=True)
class DockerRunnerAdapter:
    sandbox_spec: dict[str, Any]
    engine: str = "docker"
    adapter_name: str = "docker"

    def detect_capabilities(self, timeout_seconds: int | None = 5) -> dict[str, Any]:
        command = self._command()
        binary = command[0] if command else self.engine
        capabilities = _base_capabilities(self.engine, self.adapter_name, binary)

        resolved_binary = shutil.which(binary)
        if resolved_binary is None:
            capabilities["reason"] = f"{binary} executable not available"
            return capabilities

        capabilities["binaryAvailable"] = True
        capabilities["resolvedBinary"] = resolved_binary

        try:
            completed = subprocess.run(
                [binary, "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            capabilities["reason"] = f"{binary} version probe timed out"
            return capabilities
        except OSError as exc:
            capabilities["reason"] = str(exc)
            return capabilities

        if completed.returncode == 0:
            capabilities["daemonReachable"] = True
            capabilities["executeSupported"] = True
            capabilities["version"] = completed.stdout.strip()
            return capabilities

        capabilities["reason"] = (completed.stderr or completed.stdout).strip() or "docker daemon not reachable"
        return capabilities

    def has_launch_command(self) -> bool:
        return bool(self._command())

    def execute(self, timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            self._command(),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )

    def _command(self) -> list[str]:
        command = self.sandbox_spec.get("dockerCommand", [])
        return command if isinstance(command, list) else []


@dataclass(slots=True)
class UnsupportedRunnerAdapter:
    sandbox_spec: dict[str, Any]

    @property
    def engine(self) -> str:
        return str(self.sandbox_spec.get("engine", "unknown"))

    @property
    def adapter_name(self) -> str:
        return "unsupported"

    def detect_capabilities(self, timeout_seconds: int | None = 5) -> dict[str, Any]:
        del timeout_seconds

        command = self._command()
        binary = command[0] if command else self.engine
        capabilities = _base_capabilities(self.engine, self.adapter_name, binary)

        resolved_binary = shutil.which(binary)
        if resolved_binary is not None:
            capabilities["binaryAvailable"] = True
            capabilities["resolvedBinary"] = resolved_binary

        capabilities["reason"] = f"{self.engine} engine is not supported by this runner"
        return capabilities

    def has_launch_command(self) -> bool:
        return bool(self._command())

    def execute(self, timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
        del timeout_seconds
        raise RuntimeError(f"{self.engine} engine is not supported by this runner")

    def _command(self) -> list[str]:
        for key in ("dockerCommand", "command"):
            command = self.sandbox_spec.get(key, [])
            if isinstance(command, list) and command:
                return command
        return []


def resolve_runner_adapter(sandbox_spec: dict[str, Any]) -> RunnerAdapter:
    engine = str(sandbox_spec.get("engine", "docker")).lower()
    if engine == "docker":
        return DockerRunnerAdapter(sandbox_spec=sandbox_spec)
    return UnsupportedRunnerAdapter(sandbox_spec=sandbox_spec)


def _base_capabilities(engine: str, adapter_name: str, binary: str) -> dict[str, Any]:
    return {
        "engine": engine,
        "adapter": adapter_name,
        "binary": binary,
        "resolvedBinary": "",
        "binaryAvailable": False,
        "daemonReachable": False,
        "executeSupported": False,
        "version": "",
        "reason": "",
    }
