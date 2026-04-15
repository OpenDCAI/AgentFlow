"""
Tests for the Code backend skeleton and bridge-tool registration.
"""

import asyncio
import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest

from sandbox.server.backends.base import BackendConfig
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.core.tool_executor import ToolExecutor

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "code.py"
)


def load_code_backend_module():
    package_name = "sandbox.server.backends.resources"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(MODULE_PATH.parent)]
        sys.modules[package_name] = package

    spec = importlib.util.spec_from_file_location(
        f"{package_name}.code",
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
            "claude_code_root": str(tmp_path / "claude-code-py"),
            "workspace_root": str(tmp_path / "agentflow_code"),
            "allow_bash": True,
        },
        description="Code backend",
    )


def create_fake_claude_code_root(tmp_path):
    root = tmp_path / "claude-code-py"
    tools_dir = root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    (root / "tool.py").write_text(
        "class Tool:\n"
        "    async def call(self, params, ctx):\n"
        "        raise NotImplementedError\n",
        encoding="utf-8",
    )

    (tools_dir / "__init__.py").write_text(
        "raise RuntimeError('tools package import should not happen')\n",
        encoding="utf-8",
    )

    (tools_dir / "file_tools.py").write_text(
        "from tool import Tool\n"
        "from pathlib import Path\n"
        "\n"
        "class ReadTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        file_path = Path(params['file_path'])\n"
        "        if not file_path.exists():\n"
        "            return f'Error: File not found: {file_path}'\n"
        "        return {'content': [{'type': 'text', 'text': file_path.read_text(encoding=\"utf-8\")}], 'params': params}\n"
        "\n"
        "class GlobTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        return {'glob': True, 'path': str(Path(params.get('path', '.'))), 'cwd': ctx.cwd, 'params': params}\n"
        "\n"
        "class GrepTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        return {'grep': True, 'path': str(Path(params.get('path', '.'))), 'cwd': ctx.cwd, 'params': params}\n"
        "\n"
        "class BashTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        raise RuntimeError('bash tool should not be invoked')\n",
        encoding="utf-8",
    )

    (tools_dir / "edit_tools.py").write_text(
        "from tool import Tool\n"
        "from pathlib import Path\n"
        "\n"
        "class EditTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        file_path = Path(params['file_path'])\n"
        "        if not file_path.exists():\n"
        "            return f'Error: File does not exist: {file_path}'\n"
        "        text = file_path.read_text(encoding='utf-8')\n"
        "        text = text.replace(params.get('old_string', ''), params.get('new_string', ''))\n"
        "        file_path.write_text(text, encoding='utf-8')\n"
        "        return {'edit': True, 'cwd': ctx.cwd, 'params': params}\n"
        "\n"
        "class WriteTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        file_path = Path(params['file_path'])\n"
        "        file_path.parent.mkdir(parents=True, exist_ok=True)\n"
        "        file_path.write_text(params.get('content', ''), encoding='utf-8')\n"
        "        return {'write': True, 'cwd': ctx.cwd, 'params': params}\n",
        encoding="utf-8",
    )
    return root


class FakeResourceRouter:
    def __init__(self, session_info):
        self._session_info = session_info

    async def get_session(self, worker_id, resource_type):
        del worker_id, resource_type
        return self._session_info

    async def get_or_create_session(self, worker_id, resource_type, auto_created=False):
        del worker_id, resource_type, auto_created
        raise AssertionError("unexpected temporary session creation")

    async def refresh_session(self, worker_id, resource_type):
        del worker_id, resource_type
        return True

    async def destroy_session(self, worker_id, resource_type):
        del worker_id, resource_type
        return True


def test_bind_server_registers_code_tools(tmp_path):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()

    backend.bind_server(fake_server)

    assert "code:read" in fake_server._tools
    assert "code:bash" in fake_server._tools
    assert fake_server._tool_resource_types["code:read"] == "code"
    assert fake_server._tool_resource_types["code:bash"] == "code"


def test_initialize_creates_worker_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))

    session = asyncio.run(backend.initialize("runner_123", {}))

    assert session["workspace"].endswith("runner_123")
    assert Path(session["workspace"]).exists()


def test_initialize_copies_source_dir(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "demo.py").write_text("print('hi')\n", encoding="utf-8")

    session = asyncio.run(
        backend.initialize("runner_123", {"source_dir": str(source_dir)})
    )

    copied = Path(session["workspace"]) / "demo.py"
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "print('hi')\n"


def test_load_claude_code_tools_uses_direct_file_loading(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))

    tools = backend._load_claude_code_tools()

    assert set(tools.keys()) == {"read", "glob", "grep", "bash", "edit", "write"}


def test_tool_executor_code_dispatch_returns_standard_success_response(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    runtime_workspace = tmp_path / "runtime-workspace"
    runtime_workspace.mkdir(parents=True)
    demo_file = runtime_workspace / "demo.py"
    demo_file.write_text("hello from demo\n", encoding="utf-8")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-1",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": str(demo_file)},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"]["content"][0]["text"] == "hello from demo\n"


def test_tool_executor_code_dispatch_preserves_trace_id(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    runtime_workspace = tmp_path / "runtime-workspace"
    runtime_workspace.mkdir(parents=True)
    demo_file = runtime_workspace / "demo.py"
    demo_file.write_text("hello from demo\n", encoding="utf-8")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-trace",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": str(demo_file)},
            worker_id="worker-1",
            trace_id="trace-preserve-1",
        )
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["meta"]["trace_id"] == "trace-preserve-1"


def test_tool_executor_blocks_bash_when_allow_bash_false(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    config = build_backend_config(tmp_path)
    config.default_config["allow_bash"] = False
    backend = module.CodeBackend(config=config)
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-2",
                "data": {"workspace": str(tmp_path / "runtime-workspace")},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={"command": "echo hi"},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "disabled" in result["message"].lower()


def test_code_write_relative_file_path_resolves_inside_session_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "runtime-workspace"
    runtime_workspace.mkdir(parents=True)
    process_cwd = tmp_path / "process-cwd"
    process_cwd.mkdir(parents=True)
    prev_cwd = Path.cwd()
    os.chdir(process_cwd)
    try:
        executor = ToolExecutor(
            tools=fake_server._tools,
            tool_name_index={},
            tool_resource_types=fake_server._tool_resource_types,
            resource_router=FakeResourceRouter(
                {
                    "session_id": "code-session-3",
                    "data": {"workspace": str(runtime_workspace)},
                }
            ),
        )

        result = asyncio.run(
            executor.execute(
                action="code:write",
                params={"file_path": "nested/output.txt", "content": "from workspace\n"},
                worker_id="worker-1",
                trace_id="trace-1",
            )
        )
    finally:
        os.chdir(prev_cwd)

    assert result["code"] == ErrorCode.SUCCESS
    assert (runtime_workspace / "nested" / "output.txt").read_text(encoding="utf-8") == (
        "from workspace\n"
    )
    assert not (process_cwd / "nested" / "output.txt").exists()


def test_code_read_error_prefix_is_returned_as_agentflow_error_response(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "runtime-workspace"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-4",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": "missing.txt"},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] != ErrorCode.SUCCESS
    assert result["message"].startswith("Error:")


def test_initialize_recreates_worker_workspace_without_stale_files(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    first_source = tmp_path / "source-first"
    second_source = tmp_path / "source-second"
    first_source.mkdir(parents=True)
    second_source.mkdir(parents=True)
    (first_source / "stale.py").write_text("print('old')\n", encoding="utf-8")
    (second_source / "fresh.py").write_text("print('new')\n", encoding="utf-8")

    first_session = asyncio.run(
        backend.initialize("runner_123", {"source_dir": str(first_source)})
    )
    second_session = asyncio.run(
        backend.initialize("runner_123", {"source_dir": str(second_source)})
    )

    assert first_session["workspace"] == second_session["workspace"]
    workspace = Path(second_session["workspace"])
    assert not (workspace / "stale.py").exists()
    assert (workspace / "fresh.py").exists()


def test_code_read_rejects_absolute_path_outside_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "runtime-workspace"
    runtime_workspace.mkdir(parents=True)
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("secret\n", encoding="utf-8")
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-5",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": str(outside_file)},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] != ErrorCode.SUCCESS


def test_code_write_rejects_parent_escape_outside_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "runtime-workspace"
    runtime_workspace.mkdir(parents=True)
    escaped_file = tmp_path / "escaped.txt"
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-6",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:write",
            params={"file_path": "../escaped.txt", "content": "escaped\n"},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] != ErrorCode.SUCCESS
    assert not escaped_file.exists()


def test_initialize_rejects_hostile_worker_id_without_deleting_outside_dir(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))

    outside_dir = tmp_path / "escaped"
    outside_dir.mkdir(parents=True)
    marker = outside_dir / "keep.txt"
    marker.write_text("do-not-delete\n", encoding="utf-8")

    with pytest.raises(ValueError):
        asyncio.run(backend.initialize("../escaped", {}))

    assert marker.exists()


def test_initialize_fails_when_claude_code_root_not_configured(tmp_path):
    module = load_code_backend_module()
    config = BackendConfig(
        enabled=True,
        default_config={
            "claude_code_root": "",
            "workspace_root": str(tmp_path / "agentflow_code"),
            "allow_bash": True,
        },
        description="Code backend",
    )
    backend = module.CodeBackend(config=config)

    with pytest.raises(ValueError, match="claude_code_root"):
        asyncio.run(backend.initialize("runner_123", {}))


def test_initialize_rejects_nonexistent_source_dir(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    missing_source = tmp_path / "missing-source"

    with pytest.raises(ValueError, match="source_dir"):
        asyncio.run(backend.initialize("runner_123", {"source_dir": str(missing_source)}))


def test_initialize_invalid_source_dir_leaves_no_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    missing_source = tmp_path / "missing-source"
    workspace = tmp_path / "agentflow_code" / "runner_123"

    with pytest.raises(ValueError, match="source_dir"):
        asyncio.run(backend.initialize("runner_123", {"source_dir": str(missing_source)}))

    assert not workspace.exists()


def test_initialize_unconfigured_claude_root_leaves_no_workspace(tmp_path):
    module = load_code_backend_module()
    config = BackendConfig(
        enabled=True,
        default_config={
            "claude_code_root": "",
            "workspace_root": str(tmp_path / "agentflow_code"),
            "allow_bash": True,
        },
        description="Code backend",
    )
    backend = module.CodeBackend(config=config)
    workspace = tmp_path / "agentflow_code" / "runner_123"

    with pytest.raises(ValueError, match="claude_code_root"):
        asyncio.run(backend.initialize("runner_123", {}))

    assert not workspace.exists()


def test_cleanup_removes_worker_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    session = asyncio.run(backend.initialize("runner_123", {}))
    workspace = Path(session["workspace"])

    assert workspace.exists()
    asyncio.run(backend.cleanup("runner_123", {"data": {"workspace": str(workspace)}}))

    assert not workspace.exists()


def test_cleanup_does_not_delete_workspace_outside_root(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    outside_workspace = tmp_path / "outside-workspace"
    outside_workspace.mkdir(parents=True)

    asyncio.run(
        backend.cleanup("runner_123", {"data": {"workspace": str(outside_workspace)}})
    )

    assert outside_workspace.exists()
