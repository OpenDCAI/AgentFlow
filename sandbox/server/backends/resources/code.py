"""
Code backend skeleton for lightweight coding workspace integration.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import time
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
                },
                description="Code backend",
            )
        super().__init__(config)
        self._tool_instances: dict[str, Any] | None = None

    def bind_server(self, server) -> None:
        super().bind_server(server)
        for tool_name in ("read", "glob", "grep", "bash", "edit", "write"):
            server.register_tool(
                f"code:{tool_name}",
                self._make_bridge_tool(tool_name),
                resource_type="code",
            )

    async def initialize(self, worker_id: str, config: dict) -> dict:
        workspace = self._prepare_workspace(worker_id)
        source_dir = self._resolve_source_dir(config)

        if source_dir:
            self._copy_source_dir(source_dir, workspace)

        self._load_claude_code_tools()
        return {
            "workspace": str(workspace),
            "source_dir": str(source_dir) if source_dir else "",
        }

    async def cleanup(self, worker_id: str, session_info: dict) -> None:
        del worker_id, session_info
        return None

    def _get_claude_code_root(self) -> Path:
        value = self.get_default_config().get("claude_code_root") or ""
        return Path(value) if value else Path(".")

    def _get_workspace_root(self) -> Path:
        value = self.get_default_config().get("workspace_root") or "/tmp/agentflow_code"
        return Path(value)

    def _prepare_workspace(self, worker_id: str) -> Path:
        workspace = self._get_workspace_root() / worker_id
        if workspace.exists():
            shutil.rmtree(workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace

    def _resolve_source_dir(self, config: dict | None) -> Path | None:
        config = config or {}
        value = config.get("source_dir")
        if not value:
            return None
        return Path(value)

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
        root = str(root_path)
        inserted = False
        if root and root not in sys.path:
            sys.path.insert(0, root)
            inserted = True

        try:
            file_tools = self._load_module_from_path(
                "_agentflow_code_file_tools",
                root_path / "tools" / "file_tools.py",
            )
            edit_tools = self._load_module_from_path(
                "_agentflow_code_edit_tools",
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
        finally:
            if inserted and root in sys.path:
                sys.path.remove(root)

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

        if tool_name == "bash" and not self.get_default_config().get("allow_bash", False):
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message="code:bash is disabled by backend config (allow_bash=False)",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
            )

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
            )

        workspace = (
            ((session_info or {}).get("data") or {}).get("workspace")
            or str(self._get_workspace_root())
        )
        ctx = SimpleNamespace(cwd=workspace)
        normalized_params = self._normalize_tool_params(
            tool_name=tool_name,
            params=params,
            workspace=Path(workspace),
        )
        try:
            result = await tool.call(normalized_params, ctx)
        except Exception as exc:
            return build_error_response(
                code=ErrorCode.EXECUTION_ERROR,
                message=str(exc),
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
            )

        if isinstance(result, str) and result.startswith("Error:"):
            return build_error_response(
                code=ErrorCode.BUSINESS_FAILURE,
                message=result,
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
            )

        return build_success_response(
            data=result,
            tool=full_name,
            execution_time_ms=(time.time() - start_time) * 1000,
            resource_type=self.name,
            session_id=session_id,
        )

    def _normalize_tool_params(
        self,
        tool_name: str,
        params: dict[str, Any],
        workspace: Path,
    ) -> dict[str, Any]:
        normalized = dict(params)

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
                continue
            normalized[key] = str(workspace / value_path)

        return normalized
