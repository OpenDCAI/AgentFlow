"""
Toolathlon-GYM MCP backend for AgentFlow.
"""

import os
import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import (
    build_error_response,
    build_success_response,
)
from sandbox.tool_schemas.mcp import get_mcp_tool_schemas

from .client import MCPStdioClient, load_mcp_process_config

logger = logging.getLogger("MCPBackend")


class ToolathlonGymBackend(Backend):
    name = "mcp"
    description = "MCP Backend - Toolathlon-GYM stdio MCP integration"
    version = "1.0.0"

    def __init__(self, config: BackendConfig | None = None):
        if config is None:
            config = BackendConfig(
                enabled=True,
                default_config={
                    "enabled_mcp_servers": [],
                    "workspace_root": "/tmp/agentflow_mcp",
                },
                description="MCP backend",
            )
        super().__init__(config)

    def bind_server(self, server) -> None:
        super().bind_server(server)
        for schema in get_mcp_tool_schemas():
            full_name = schema["name"]
            server.register_tool(
                full_name,
                self._make_bridge_tool(full_name),
                resource_type="mcp",
            )

    async def initialize(self, worker_id: str, config: dict) -> dict:
        workspace = self._prepare_workspace(worker_id)
        task_context = self._resolve_task_context(config)
        task_dir = Path(task_context["task_dir"]) if task_context["task_dir"] else None

        if task_dir and task_context["copy_initial_workspace"]:
            self._copy_initial_workspace(task_dir / "initial_workspace", workspace)
        if task_dir and task_context["run_preprocess"]:
            self._run_preprocess(
                task_dir,
                workspace,
                launch_time=task_context.get("launch_time"),
            )

        clients = await self._start_enabled_clients(workspace, task_context)
        return {
            "workspace": str(workspace),
            "task_context": task_context,
            "clients": clients,
        }

    async def cleanup(self, worker_id: str, session_info: dict) -> None:
        del worker_id
        data = (session_info or {}).get("data") or {}
        await self._close_clients(data.get("clients") or {})

    def _prepare_workspace(self, worker_id: str) -> Path:
        workspace = self._get_workspace_root() / worker_id
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace

    def _resolve_task_context(self, config: dict | None) -> dict[str, Any]:
        config = config or {}
        return {
            "task_dir": config.get("task_dir", ""),
            "copy_initial_workspace": bool(config.get("copy_initial_workspace", False)),
            "run_preprocess": bool(config.get("run_preprocess", False)),
            "launch_time": config.get("launch_time"),
        }

    def _resolve_enabled_servers(self) -> list[str]:
        servers = self.get_default_config().get("enabled_mcp_servers") or []
        return [str(server) for server in servers]

    def _copy_initial_workspace(self, source_dir: Path, target_dir: Path) -> None:
        if not source_dir.exists():
            return
        for child in source_dir.iterdir():
            destination = target_dir / child.name
            if child.is_dir():
                shutil.copytree(child, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(child, destination)

    def _run_preprocess(
        self,
        task_dir: Path,
        workspace: Path,
        *,
        launch_time: str | None = None,
    ) -> None:
        script_path = task_dir / "preprocess" / "main.py"
        if not script_path.exists():
            return

        command = [
            sys.executable,
            str(script_path),
            "--agent_workspace",
            str(workspace),
        ]
        cleaned_launch_time = " ".join((launch_time or "").split()[:2])
        if cleaned_launch_time:
            command.extend(["--launch_time", cleaned_launch_time])

        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            message = (result.stderr or "").strip() or "unknown error"
            raise RuntimeError(f"preprocess failed: {message}")

    async def _start_enabled_clients(
        self,
        workspace: Path,
        task_context: dict[str, Any],
    ) -> dict[str, MCPStdioClient]:
        clients: dict[str, MCPStdioClient] = {}
        mcp_servers_path = self._get_mcp_servers_path()
        process_env = dict(os.environ)
        process_env.update(self.get_default_config().get("env_overrides") or {})
        try:
            for server_name in self._resolve_enabled_servers():
                process_config = load_mcp_process_config(
                    server_name=server_name,
                    agent_workspace=str(workspace),
                    mcp_servers_path=mcp_servers_path,
                    task_dir=task_context.get("task_dir", ""),
                    process_env=process_env,
                )
                client = MCPStdioClient(process_config)
                await client.start()
                await client.initialize()
                clients[server_name] = client
        except Exception:
            await self._close_clients(clients)
            raise
        return clients

    async def _close_clients(self, clients: dict[str, MCPStdioClient]) -> None:
        for client in clients.values():
            await client.close()

    def _make_bridge_tool(self, full_name: str):
        async def bridge_tool(session_info: dict, **params):
            return await self._dispatch(full_name, session_info, params)

        bridge_tool.__name__ = full_name.replace(":", "_").replace(".", "_")
        return bridge_tool

    async def _dispatch(
        self,
        full_name: str,
        session_info: dict,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        start_time = time.time()
        session_id = (session_info or {}).get("session_id")
        server_name, tool_name = self._parse_bridge_name(full_name)

        if server_name not in self._resolve_enabled_servers():
            return build_error_response(
                code=ErrorCode.BACKEND_NOT_INITIALIZED,
                message=f"MCP server '{server_name}' is not enabled in the current session",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
            )

        clients = ((session_info or {}).get("data") or {}).get("clients") or {}
        client = clients.get(server_name)
        if client is None:
            return build_error_response(
                code=ErrorCode.RESOURCE_NOT_INITIALIZED,
                message=f"MCP client for server '{server_name}' is not available",
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
            )

        try:
            result = await client.call_tool(tool_name, params)
        except TimeoutError as exc:
            return build_error_response(
                code=ErrorCode.TIMEOUT_ERROR,
                message=str(exc),
                tool=full_name,
                execution_time_ms=(time.time() - start_time) * 1000,
                resource_type=self.name,
                session_id=session_id,
            )
        except Exception as exc:
            return build_error_response(
                code=ErrorCode.DEPENDENCY_FAILURE,
                message=str(exc),
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

    def _get_mcp_servers_path(self) -> str | None:
        """Return the configured path to MCP server executables, or None."""
        value = self.get_default_config().get("mcp_servers_path")
        if value:
            return str(value)
        # Backward compat: derive from toolathlon_root.
        toolathlon_root = self.get_default_config().get("toolathlon_root")
        if toolathlon_root:
            return str(Path(toolathlon_root) / "local_servers")
        return None

    def _get_workspace_root(self) -> Path:
        value = self.get_default_config().get("workspace_root") or "/tmp/agentflow_mcp"
        return Path(value)

    def _parse_bridge_name(self, full_name: str) -> tuple[str, str]:
        tool_ref = full_name.split(":", 1)[1]
        server_name, tool_name = tool_ref.split(".", 1)
        return server_name, tool_name
