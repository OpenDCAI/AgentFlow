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


def test_cleanup_closes_session_clients(tmp_path):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(config=build_backend_config(tmp_path))

    class FakeClient:
        def __init__(self):
            self.closed = False

        async def close(self):
            self.closed = True

    client = FakeClient()

    asyncio.run(
        backend.cleanup(
            "runner_123",
            {"data": {"clients": {"filesystem": client}}},
        )
    )

    assert client.closed is True


def test_initialize_copies_initial_workspace(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(config=build_backend_config(tmp_path))
    task_dir = tmp_path / "task"
    initial_workspace = task_dir / "initial_workspace"
    initial_workspace.mkdir(parents=True)
    (initial_workspace / "seed.txt").write_text("hello\n", encoding="utf-8")

    async def fake_start_enabled_clients(workspace, task_context):
        return {}

    monkeypatch.setattr(backend, "_start_enabled_clients", fake_start_enabled_clients)

    session = asyncio.run(
        backend.initialize(
            "runner_123",
            {
                "task_dir": str(task_dir),
                "copy_initial_workspace": True,
                "run_preprocess": False,
            },
        )
    )

    assert (Path(session["workspace"]) / "seed.txt").exists()


def test_initialize_runs_preprocess_when_requested(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(config=build_backend_config(tmp_path))
    task_dir = tmp_path / "task"
    preprocess_dir = task_dir / "preprocess"
    preprocess_dir.mkdir(parents=True)
    (preprocess_dir / "main.py").write_text("print('ok')\n", encoding="utf-8")
    recorded = {}

    async def fake_start_enabled_clients(workspace, task_context):
        return {}

    def fake_run(command, shell, capture_output, text):
        recorded["command"] = command
        recorded["shell"] = shell
        recorded["capture_output"] = capture_output
        recorded["text"] = text

        class Result:
            returncode = 0
            stderr = ""

        return Result()

    monkeypatch.setattr(backend, "_start_enabled_clients", fake_start_enabled_clients)
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    asyncio.run(
        backend.initialize(
            "runner_123",
            {
                "task_dir": str(task_dir),
                "copy_initial_workspace": False,
                "run_preprocess": True,
                "launch_time": "2026-03-07 10:00:00 Friday",
            },
        )
    )

    assert "--agent_workspace" in recorded["command"]
    assert '--launch_time "2026-03-07 10:00:00"' in recorded["command"]


def test_initialize_fails_when_preprocess_returns_error(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(config=build_backend_config(tmp_path))
    task_dir = tmp_path / "task"
    preprocess_dir = task_dir / "preprocess"
    preprocess_dir.mkdir(parents=True)
    (preprocess_dir / "main.py").write_text("print('ok')\n", encoding="utf-8")

    async def fake_start_enabled_clients(workspace, task_context):
        return {}

    def fake_run(command, shell, capture_output, text):
        del command, shell, capture_output, text

        class Result:
            returncode = 1
            stderr = "boom"

        return Result()

    monkeypatch.setattr(backend, "_start_enabled_clients", fake_start_enabled_clients)
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    try:
        asyncio.run(
            backend.initialize(
                "runner_123",
                {
                    "task_dir": str(task_dir),
                    "copy_initial_workspace": False,
                    "run_preprocess": True,
                },
            )
        )
    except RuntimeError as exc:
        assert "preprocess" in str(exc)
    else:
        raise AssertionError("Expected preprocess failure to abort initialize()")


def test_bridge_tool_dispatches_to_matching_server_client(tmp_path):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "toolathlon_root": str(tmp_path / "toolathlon"),
                "enabled_mcp_servers": ["filesystem"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
            },
        )
    )
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    class FakeClient:
        async def call_tool(self, tool_name, arguments):
            assert tool_name == "list_directory"
            assert arguments == {"path": "."}
            return {"content": [{"type": "text", "text": "ok"}]}

    tool_handler = fake_server._tools["mcp:filesystem.list_directory"]
    result = asyncio.run(
        tool_handler(
            session_info={
                "session_id": "session-1",
                "data": {"clients": {"filesystem": FakeClient()}},
            },
            path=".",
        )
    )

    assert result["code"] == 0
    assert result["data"]["content"] == [{"type": "text", "text": "ok"}]


def test_bridge_tool_returns_clear_error_for_disabled_server(tmp_path):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "toolathlon_root": str(tmp_path / "toolathlon"),
                "enabled_mcp_servers": ["terminal"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
            },
        )
    )
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    tool_handler = fake_server._tools["mcp:filesystem.list_directory"]

    result = asyncio.run(
        tool_handler(
            session_info={"session_id": "session-1", "data": {"clients": {}}},
            path=".",
        )
    )

    assert result["code"] != 0
    assert "not enabled" in result["message"]


def test_bridge_tool_returns_clear_error_for_client_failure(tmp_path):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "toolathlon_root": str(tmp_path / "toolathlon"),
                "enabled_mcp_servers": ["filesystem"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
            },
        )
    )
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    class FakeClient:
        async def call_tool(self, tool_name, arguments):
            del tool_name, arguments
            raise RuntimeError("boom")

    tool_handler = fake_server._tools["mcp:filesystem.list_directory"]
    result = asyncio.run(
        tool_handler(
            session_info={
                "session_id": "session-1",
                "data": {"clients": {"filesystem": FakeClient()}},
            },
            path=".",
        )
    )

    assert result["code"] != 0
    assert "boom" in result["message"]


def test_bridge_tool_returns_clear_error_for_missing_client(tmp_path):
    module = load_mcp_backend_module()
    backend = module.MCPBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "toolathlon_root": str(tmp_path / "toolathlon"),
                "enabled_mcp_servers": ["filesystem"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
            },
        )
    )
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    tool_handler = fake_server._tools["mcp:filesystem.list_directory"]

    result = asyncio.run(
        tool_handler(
            session_info={"session_id": "session-1", "data": {"clients": {}}},
            path=".",
        )
    )

    assert result["code"] != 0
    assert "not available" in result["message"]
