"""
Code backend skeleton for lightweight coding workspace integration.
"""

from __future__ import annotations

import asyncio
from contextlib import contextmanager
import importlib.util
import os
import re
import signal
import shutil
import sys
import time
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import (
    build_error_response,
    build_success_response,
)


class CodeBackend(Backend):
    name = "code"
    description = "Code Backend - lightweight coding workspace integration"
    version = "1.0.0"

    def __init__(self, config: BackendConfig | None = None):
        if config is None:
            config = BackendConfig(
                enabled=True,
                default_config={
                    "claude_code_root": "",
                    "workspace_root": "/tmp/agentflow_code",
                    "allow_bash": False,
                    "bash_timeout_seconds": 30,
                },
                description="Code backend",
            )
        super().__init__(config)
        self._tool_instances: dict[str, Any] | None = None
        self._module_namespace = f"_agentflow_code_backend_{id(self)}"

    def bind_server(self, server) -> None:
        super().bind_server(server)
        for tool_name in ("read", "glob", "grep", "bash", "edit", "write"):
            server.register_tool(
                f"code:{tool_name}",
                self._make_bridge_tool(tool_name),
                resource_type="code",
            )

    async def initialize(self, worker_id: str, config: dict) -> dict:
        source_dir = self._resolve_source_dir(config)
        self._validate_claude_code_root_prerequisites()
        workspace, staged_workspace, previous_workspace = self._prepare_workspace(worker_id)

        try:
            if source_dir:
                self._copy_source_dir(source_dir, staged_workspace)

            self._load_claude_code_tools()
            self._commit_prepared_workspace(workspace, staged_workspace, previous_workspace)
        except Exception:
            if staged_workspace.exists():
                shutil.rmtree(staged_workspace)
            if previous_workspace is not None and previous_workspace.exists() and not workspace.exists():
                previous_workspace.rename(workspace)
            raise

        return {
            "workspace": str(workspace),
            "source_dir": str(source_dir) if source_dir else "",
        }

    async def cleanup(self, worker_id: str, session_info: dict) -> None:
        workspace_value = ((session_info or {}).get("data") or {}).get("workspace")
        if not isinstance(workspace_value, str) or not workspace_value.strip():
            return None

        try:
            workspace = Path(workspace_value).resolve()
            workspace_root = self._get_workspace_root().resolve()
            expected_workspace = (workspace_root / self._validate_worker_id(worker_id)).resolve(
                strict=False
            )
            workspace.relative_to(workspace_root)
        except (OSError, RuntimeError, ValueError, TypeError):
            return None

        if workspace != expected_workspace:
            return None
        if workspace.exists() and workspace.is_dir():
            shutil.rmtree(workspace)
        return None

    def _get_claude_code_root(self) -> Path | None:
        value = self.get_default_config().get("claude_code_root")
        if not isinstance(value, str) or not value.strip():
            return None
        return Path(value)

    def _get_workspace_root(self) -> Path:
        value = self.get_default_config().get("workspace_root") or "/tmp/agentflow_code"
        return Path(value)

    def _prepare_workspace(self, worker_id: str) -> tuple[Path, Path, Path | None]:
        safe_worker_id = self._validate_worker_id(worker_id)
        workspace_root = self._get_workspace_root()
        workspace_root.mkdir(parents=True, exist_ok=True)
        workspace = workspace_root / safe_worker_id
        staged_workspace = workspace_root / f".{safe_worker_id}.staged-{uuid.uuid4().hex}"
        previous_workspace = (
            workspace_root / f".{safe_worker_id}.previous-{uuid.uuid4().hex}"
            if workspace.exists()
            else None
        )
        staged_workspace.mkdir(parents=True, exist_ok=False)
        return workspace, staged_workspace, previous_workspace

    def _commit_prepared_workspace(
        self,
        workspace: Path,
        staged_workspace: Path,
        previous_workspace: Path | None,
    ) -> None:
        if previous_workspace is not None:
            workspace.rename(previous_workspace)
        staged_workspace.rename(workspace)
        if previous_workspace is not None and previous_workspace.exists():
            shutil.rmtree(previous_workspace)

    def _validate_worker_id(self, worker_id: str) -> str:
        if not isinstance(worker_id, str) or not worker_id:
            raise ValueError("worker_id must be a non-empty string")
        if worker_id in {".", ".."}:
            raise ValueError("worker_id contains unsafe path traversal")
        if worker_id != Path(worker_id).name:
            raise ValueError("worker_id must be a single safe path component")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", worker_id):
            raise ValueError("worker_id contains unsupported characters")
        return worker_id

    def _resolve_source_dir(self, config: dict | None) -> Path | None:
        config = config or {}
        value = config.get("source_dir")
        if not value:
            return None
        source_dir = Path(value)
        if not source_dir.exists():
            raise ValueError(f"source_dir does not exist: {source_dir}")
        if not source_dir.is_dir():
            raise ValueError(f"source_dir is not a directory: {source_dir}")
        return source_dir

    def _copy_source_dir(self, source_dir: Path, workspace: Path) -> None:
        if not source_dir.exists():
            return
        for child in source_dir.iterdir():
            destination = workspace / child.name
            if child.is_dir():
                shutil.copytree(child, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(child, destination)

    def _load_claude_code_tools(self) -> dict[str, Any]:
        if self._tool_instances is not None:
            return self._tool_instances

        root_path = self._get_claude_code_root()
        if root_path is None:
            raise ValueError("claude_code_root is not configured")

        support_modules = self._load_root_support_modules(root_path)
        with self._temporary_module_aliases(support_modules):
            tool_module = self._load_module_from_path(
                f"{self._module_namespace}.tool",
                root_path / "tool.py",
            )
            with self._temporary_module_aliases({"tool": tool_module}):
                file_tools = self._load_module_from_path(
                    f"{self._module_namespace}.file_tools",
                    root_path / "tools" / "file_tools.py",
                )
                edit_tools = self._load_module_from_path(
                    f"{self._module_namespace}.edit_tools",
                    root_path / "tools" / "edit_tools.py",
                )

        self._tool_instances = {
            "read": file_tools.ReadTool(),
            "glob": file_tools.GlobTool(),
            "grep": file_tools.GrepTool(),
            "bash": file_tools.BashTool(),
            "edit": edit_tools.EditTool(),
            "write": edit_tools.WriteTool(),
        }
        return self._tool_instances

    def _validate_claude_code_root_prerequisites(self) -> None:
        root_path = self._get_claude_code_root()
        if root_path is None:
            raise ValueError("claude_code_root is not configured")

        required_paths = (
            root_path / "tool.py",
            root_path / "tools" / "file_tools.py",
            root_path / "tools" / "edit_tools.py",
        )
        for required_path in required_paths:
            if not required_path.exists():
                raise ValueError(f"claude_code_root is missing required file: {required_path}")

    def _load_root_support_modules(self, root_path: Path) -> dict[str, Any]:
        support_modules: dict[str, Any] = {}
        pending_modules = {
            module_name: root_path / f"{module_name}.py"
            for module_name in ("log", "trace")
            if (root_path / f"{module_name}.py").exists()
        }

        while pending_modules:
            made_progress = False
            for module_name, module_path in list(pending_modules.items()):
                try:
                    with self._temporary_module_aliases(support_modules):
                        support_modules[module_name] = self._load_module_from_path(
                            f"{self._module_namespace}.{module_name}",
                            module_path,
                        )
                except ModuleNotFoundError as exc:
                    if exc.name in pending_modules:
                        continue
                    raise
                else:
                    del pending_modules[module_name]
                    made_progress = True

            if not made_progress:
                unresolved = ", ".join(sorted(pending_modules))
                raise ImportError(f"Unable to resolve root support modules: {unresolved}")

        return support_modules

    @contextmanager
    def _temporary_module_aliases(self, aliases: dict[str, Any]):
        previous_modules: dict[str, Any] = {}
        for module_name, module in aliases.items():
            previous_modules[module_name] = sys.modules.get(module_name)
            sys.modules[module_name] = module
        try:
            yield
        finally:
            for module_name, previous_module in previous_modules.items():
                if previous_module is None:
                    sys.modules.pop(module_name, None)
                else:
                    sys.modules[module_name] = previous_module

    def _load_module_from_path(self, module_name: str, path: Path):
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load module from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _make_bridge_tool(self, tool_name: str):
        async def bridge_tool(session_info: dict, **params):
            return await self._dispatch(tool_name, session_info, params)

        bridge_tool.__name__ = f"code_{tool_name}"
        return bridge_tool

    async def _dispatch(
        self,
        tool_name: str,
        session_info: dict,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        start_time = time.time()
        full_name = f"{self.name}:{tool_name}"
        session_id = (session_info or {}).get("session_id")
        runtime_params = dict(params or {})
        trace_id = runtime_params.pop("trace_id", None)
        worker_id = runtime_params.pop("worker_id", None)
        runtime_params.pop("session_id", None)

        if tool_name == "bash" and not self.get_default_config().get("allow_bash", False):
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message="code:bash is disabled by backend config (allow_bash=False)",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )

        tool = None
        if tool_name != "bash":
            tools = self._load_claude_code_tools()
            tool = tools.get(tool_name)
            if tool is None:
                return build_error_response(
                    code=ErrorCode.INVALID_REQUEST_FORMAT,
                    message=f"Unknown code tool: {tool_name}",
                    tool=full_name,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    resource_type=self.name,
                    session_id=session_id,
                    trace_id=trace_id,
                )

        workspace_value = ((session_info or {}).get("data") or {}).get("workspace")
        if not isinstance(workspace_value, str) or not workspace_value.strip():
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message="Invalid session workspace: missing or empty data.workspace",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )

        try:
            workspace = Path(workspace_value).resolve(strict=False)
            workspace_root = self._get_workspace_root().resolve()
            expected_workspace = (workspace_root / self._validate_worker_id(worker_id)).resolve(
                strict=False
            )
            workspace.relative_to(workspace_root)
        except (OSError, RuntimeError, ValueError, TypeError):
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message="Invalid session workspace: must resolve inside workspace_root",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )

        if workspace != expected_workspace or not workspace.exists() or not workspace.is_dir():
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message="Invalid session workspace: must match existing worker workspace",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )

        ctx = SimpleNamespace(cwd=str(workspace))
        try:
            normalized_params = self._normalize_tool_params(
                tool_name=tool_name,
                params=runtime_params,
                workspace=workspace,
            )
        except ValueError as exc:
            error_code = ErrorCode.BUSINESS_FAILURE
            if tool_name == "bash":
                error_code = ErrorCode.INVALID_INPUT
            return build_error_response(
                code=error_code,
                message=str(exc),
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )
        try:
            if tool_name == "bash":
                bash_timeout_seconds = float(
                    self.get_default_config().get("bash_timeout_seconds", 30)
                )
                try:
                    result = await self._run_bash_command(
                        command=normalized_params["command"],
                        workspace=workspace,
                        timeout_seconds=bash_timeout_seconds,
                    )
                except asyncio.TimeoutError:
                    return build_error_response(
                        code=ErrorCode.TIMEOUT_ERROR,
                        message="code:bash execution timeout",
                        tool=full_name,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        resource_type=self.name,
                        session_id=session_id,
                        trace_id=trace_id,
                    )
            else:
                result = await tool.call(normalized_params, ctx)
        except Exception as exc:
            return build_error_response(
                code=ErrorCode.EXECUTION_ERROR,
                message=str(exc),
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )

        if isinstance(result, str) and result.startswith("Error:"):
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message=result,
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
                trace_id=trace_id,
            )

        return build_success_response(
            data=result,
            tool=full_name,
            execution_time_ms=(time.time() - start_time) * 1000,
            resource_type=self.name,
            session_id=session_id,
            trace_id=trace_id,
        )

    async def _run_bash_command(
        self,
        command: str,
        workspace: Path,
        timeout_seconds: float,
    ) -> str:
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=str(workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            if proc.returncode is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            await proc.communicate()
            raise

        stdout_text = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
        stderr_text = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

        out = stdout_text
        if stderr_text:
            out += f"\n[stderr]:\n{stderr_text}"
        return out.strip() or "(no output)"

    def _normalize_tool_params(
        self,
        tool_name: str,
        params: dict[str, Any],
        workspace: Path,
    ) -> dict[str, Any]:
        normalized = dict(params)
        workspace_path = workspace.resolve(strict=False)

        path_keys: tuple[str, ...] = ()
        if tool_name in {"read", "edit", "write"}:
            path_keys = ("file_path",)
        elif tool_name in {"glob", "grep"}:
            path_keys = ("path",)

        for key in path_keys:
            raw_value = normalized.get(key)
            if not isinstance(raw_value, str) or not raw_value:
                continue
            value_path = Path(raw_value)
            if value_path.is_absolute():
                resolved = value_path.resolve(strict=False)
            else:
                resolved = (workspace_path / value_path).resolve(strict=False)

            try:
                resolved.relative_to(workspace_path)
            except ValueError as exc:
                raise ValueError(
                    f"Path parameter '{key}' must stay inside workspace"
                ) from exc

            normalized[key] = str(resolved)

        if tool_name == "glob":
            pattern = normalized.get("pattern")
            if (
                isinstance(pattern, str)
                and pattern
                and re.search(r"(^|[\\/])\.\.([\\/]|$)", pattern)
            ):
                raise ValueError("Glob pattern must not contain parent traversal segments")

        if tool_name == "bash":
            if "command" not in normalized:
                raise ValueError("Parameter 'command' is required")
            command = normalized.get("command")
            if not isinstance(command, str):
                raise ValueError("Parameter 'command' must be a string")
            if not command.strip():
                raise ValueError("Parameter 'command' must not be empty")

        return normalized
