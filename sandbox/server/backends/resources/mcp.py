"""
MCP backend skeleton for Toolathlon-GYM integration.
"""

from pathlib import Path
from typing import Any

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.tool_schemas.mcp_tools import get_mcp_tool_schemas

from .mcp_client import MCPStdioClient, load_mcp_process_config


class MCPBackend(Backend):
    name = "mcp"
    description = "MCP Backend - Toolathlon-GYM stdio MCP integration"
    version = "1.0.0"

    def __init__(self, config: BackendConfig | None = None):
        if config is None:
            config = BackendConfig(
                enabled=True,
                default_config={
                    "toolathlon_root": "",
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

    async def _start_enabled_clients(
        self,
        workspace: Path,
        task_context: dict[str, Any],
    ) -> dict[str, MCPStdioClient]:
        clients: dict[str, MCPStdioClient] = {}
        toolathlon_root = self._get_toolathlon_root()
        for server_name in self._resolve_enabled_servers():
            process_config = load_mcp_process_config(
                toolathlon_root=toolathlon_root,
                server_name=server_name,
                agent_workspace=str(workspace),
                task_dir=task_context.get("task_dir", ""),
            )
            client = MCPStdioClient(process_config)
            await client.start()
            await client.initialize()
            clients[server_name] = client
        return clients

    async def _close_clients(self, clients: dict[str, MCPStdioClient]) -> None:
        for client in clients.values():
            await client.close()

    def _make_bridge_tool(self, full_name: str):
        async def bridge_tool(session_info: dict, **params):
            del session_info, params
            raise NotImplementedError(
                f"Bridge dispatch for '{full_name}' is implemented in Task 4"
            )

        bridge_tool.__name__ = full_name.replace(":", "_").replace(".", "_")
        return bridge_tool

    def _get_toolathlon_root(self) -> Path:
        value = self.get_default_config().get("toolathlon_root")
        return Path(value) if value else Path(".")

    def _get_workspace_root(self) -> Path:
        value = self.get_default_config().get("workspace_root") or "/tmp/agentflow_mcp"
        return Path(value)
