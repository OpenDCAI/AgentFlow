"""
Code backend skeleton for lightweight coding workspace integration.
"""

from __future__ import annotations

import importlib
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from sandbox.server.backends.base import Backend, BackendConfig


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

        root = str(self._get_claude_code_root())
        inserted = False
        if root and root not in sys.path:
            sys.path.insert(0, root)
            inserted = True

        try:
            file_tools = importlib.import_module("tools.file_tools")
            edit_tools = importlib.import_module("tools.edit_tools")
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
        tools = self._load_claude_code_tools()
        tool = tools[tool_name]
        workspace = (
            ((session_info or {}).get("data") or {}).get("workspace")
            or str(self._get_workspace_root())
        )
        ctx = SimpleNamespace(cwd=workspace)
        result = await tool.call(params, ctx)
        return {"content": [{"type": "text", "text": str(result)}]}
