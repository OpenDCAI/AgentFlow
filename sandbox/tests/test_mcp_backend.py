"""
Tests for the MCP backend skeleton and bridge-tool registration.
"""

import asyncio
import importlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest

from sandbox.server.backends.base import BackendConfig
from sandbox.server.config_loader import ConfigLoader
from sandbox.server.core.tool_executor import ToolExecutor

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "mcp"
    / "toolathlon_gym.py"
)


def remove_resources_modules():
    package_name = "sandbox.server.backends.resources"
    for module_name in list(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            sys.modules.pop(module_name, None)


def load_mcp_backend_module():
    remove_resources_modules()

    package_name = "sandbox.server.backends.resources"
    package = types.ModuleType(package_name)
    package.__path__ = [str(MODULE_PATH.parent.parent)]
    sys.modules[package_name] = package

    mcp_package_name = f"{package_name}.mcp"
    mcp_package = types.ModuleType(mcp_package_name)
    mcp_package.__path__ = [str(MODULE_PATH.parent)]
    sys.modules[mcp_package_name] = mcp_package

    spec = importlib.util.spec_from_file_location(
        f"{mcp_package_name}.toolathlon_gym",
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
            "enabled_mcp_servers": [],
            "workspace_root": str(tmp_path / "agentflow_mcp"),
        },
        description="MCP backend",
    )


def test_bind_server_registers_manifest_tools(tmp_path):
    module = load_mcp_backend_module()
    backend = module.ToolathlonGymBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()

    backend.bind_server(fake_server)

    assert "mcp:filesystem.list_directory" in fake_server._tools
    assert "mcp:terminal.run_command" in fake_server._tools
    assert fake_server._tool_resource_types["mcp:filesystem.list_directory"] == "mcp"


def test_resources_package_exports_mcp_backend():
    remove_resources_modules()

    resources = importlib.import_module("sandbox.server.backends.resources")
    mcp_module = importlib.import_module("sandbox.server.backends.resources.mcp")

    assert resources.MCPBackend is mcp_module.MCPBackend
    assert resources.ToolathlonGymBackend is mcp_module.ToolathlonGymBackend
    assert Path(resources.__file__).resolve() == (MODULE_PATH.parent.parent / "__init__.py").resolve()


def test_initialize_creates_worker_workspace(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    backend = module.ToolathlonGymBackend(config=build_backend_config(tmp_path))

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
    backend = module.ToolathlonGymBackend(config=build_backend_config(tmp_path))

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
    backend = module.ToolathlonGymBackend(config=build_backend_config(tmp_path))
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
    backend = module.ToolathlonGymBackend(config=build_backend_config(tmp_path))
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

    session = asyncio.run(
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

    assert recorded["shell"] is False
    assert recorded["command"][1].endswith("preprocess/main.py")
    assert recorded["command"][2:4] == ["--agent_workspace", str(Path(session["workspace"]))]
    assert recorded["command"][4:6] == ["--launch_time", "2026-03-07 10:00:00"]


def test_initialize_fails_when_preprocess_returns_error(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    backend = module.ToolathlonGymBackend(config=build_backend_config(tmp_path))
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
    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
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


def test_mcp_bridge_preserves_explicit_session_id_and_skips_runtime_injection(tmp_path):
    module = load_mcp_backend_module()
    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
                "enabled_mcp_servers": ["canvas"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
            },
        )
    )
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    captured = {}

    class FakeClient:
        async def call_tool(self, tool_name, arguments):
            captured["tool_name"] = tool_name
            captured["arguments"] = arguments
            return {"content": [{"type": "text", "text": "ok"}]}

    class FakeResourceRouter:
        async def get_session(self, worker_id, resource_type):
            assert worker_id == "worker-1"
            assert resource_type == "mcp"
            return {
                "session_id": "agentflow-session",
                "data": {"clients": {"canvas": FakeClient()}},
            }

        async def get_or_create_session(self, worker_id, resource_type, auto_created=False):
            del worker_id, resource_type, auto_created
            raise AssertionError("Did not expect temporary MCP session creation")

        async def refresh_session(self, worker_id, resource_type):
            assert worker_id == "worker-1"
            assert resource_type == "mcp"
            return True

        async def destroy_session(self, worker_id, resource_type):
            del worker_id, resource_type
            raise AssertionError("Did not expect MCP session destruction")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(),
    )
    result = asyncio.run(
        executor.execute(
            action="mcp:canvas.canvas_list_account_users",
            params={"session_id": "canvas-session", "page": 2},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] == 0
    assert captured["tool_name"] == "canvas_list_account_users"
    assert captured["arguments"] == {"session_id": "canvas-session", "page": 2}
    assert result["data"]["content"] == [{"type": "text", "text": "ok"}]


def test_bridge_tool_returns_clear_error_for_disabled_server(tmp_path):
    module = load_mcp_backend_module()
    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
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
    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
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
    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
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


def test_initialize_passes_env_overrides_to_process_config(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    captured = {}

    class FakeClient:
        def __init__(self, process_config):
            self.process_config = process_config

        async def start(self):
            return None

        async def initialize(self):
            return None

    def fake_load_mcp_process_config(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(module, "MCPStdioClient", FakeClient)
    monkeypatch.setattr(module, "load_mcp_process_config", fake_load_mcp_process_config)

    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
                "enabled_mcp_servers": ["filesystem"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
                "env_overrides": {"PGHOST": "toolathlon_pg", "PGPORT": "15432"},
            },
        )
    )

    asyncio.run(
        backend.initialize(
            "runner_123",
            {
                "task_dir": str(tmp_path / "task"),
                "copy_initial_workspace": False,
                "run_preprocess": False,
            },
        )
    )

    assert captured["process_env"]["PGHOST"] == "toolathlon_pg"
    assert captured["process_env"]["PGPORT"] == "15432"


def test_initialize_closes_started_clients_when_later_server_fails(tmp_path, monkeypatch):
    module = load_mcp_backend_module()
    created_clients = []

    class FakeClient:
        def __init__(self, process_config):
            self.process_config = process_config
            self.closed = False
            created_clients.append(self)

        async def start(self):
            return None

        async def initialize(self):
            if self.process_config.name == "terminal":
                raise RuntimeError("boom")

        async def close(self):
            self.closed = True

    def fake_load_mcp_process_config(**kwargs):
        return types.SimpleNamespace(name=kwargs["server_name"])

    monkeypatch.setattr(module, "MCPStdioClient", FakeClient)
    monkeypatch.setattr(module, "load_mcp_process_config", fake_load_mcp_process_config)

    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "mcp_servers_path": str(tmp_path / "mcp_servers"),
                "enabled_mcp_servers": ["filesystem", "terminal"],
                "workspace_root": str(tmp_path / "agentflow_mcp"),
            },
        )
    )

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(
            backend.initialize(
                "runner_123",
                {
                    "task_dir": str(tmp_path / "task"),
                    "copy_initial_workspace": False,
                    "run_preprocess": False,
                },
            )
        )

    assert [client.process_config.name for client in created_clients] == ["filesystem", "terminal"]
    assert created_clients[0].closed is True


def test_mcp_config_template_parses():
    loader = ConfigLoader()
    config_path = (
        Path(__file__).resolve().parents[2]
        / "configs"
        / "sandbox-server"
        / "mcp_config.json"
    )

    config = loader.load(str(config_path))

    assert "mcp" in config.resources
    assert (
        config.resources["mcp"].backend_class
        == "sandbox.server.backends.resources.mcp.toolathlon_gym.ToolathlonGymBackend"
    )
