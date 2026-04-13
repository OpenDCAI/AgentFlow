"""
Tests for the MCP backend skeleton and bridge-tool registration.
"""

import asyncio
import importlib.util
import sys
import types
from pathlib import Path

from sandbox.server.backends.base import BackendConfig

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "mcp.py"
)


def load_mcp_backend_module():
    package_name = "sandbox.server.backends.resources"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(MODULE_PATH.parent)]
        sys.modules[package_name] = package

    spec = importlib.util.spec_from_file_location(
        f"{package_name}.mcp",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeServer:
    def __init__(self):
        self._tools = {}
        self._tool_resource_types = {}

    def register_tool(self, name, func, resource_type=None):
        self._tools[name] = func
        if resource_type is not None:
            self._tool_resource_types[name] = resource_type


def build_backend_config(tmp_path):
    return BackendConfig(
        enabled=True,
        default_config={
            "toolathlon_root": str(tmp_path / "toolathlon"),
            "enabled_mcp_servers": [],
            "workspace_root": str(tmp_path / "agentflow_mcp"),
        },
        description="MCP backend",
    )


def test_bind_server_registers_manifest_tools(tmp_path):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()

    backend.bind_server(fake_server)

    assert "mcp:filesystem.list_directory" in fake_server._tools
    assert "mcp:terminal.run_command" in fake_server._tools
    assert fake_server._tool_resource_types["mcp:filesystem.list_directory"] == "mcp"


def test_initialize_creates_worker_workspace(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(config=build_backend_config(tmp_path))

    async def fake_start_enabled_clients(workspace, task_context):
        return {}

    monkeypatch.setattr(backend, "_start_enabled_clients", fake_start_enabled_clients)

    session = asyncio.run(
        backend.initialize(
            "runner_123",
            {
                "task_dir": "/tmp/task",
                "copy_initial_workspace": False,
                "run_preprocess": False,
            },
        )
    )

    assert session["workspace"].endswith("runner_123")
    assert Path(session["workspace"]).exists()
    assert session["task_context"]["task_dir"] == "/tmp/task"
    assert session["clients"] == {}
