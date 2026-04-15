"""
Tests for the Code backend skeleton and bridge-tool registration.
"""

import asyncio
import importlib.util
import itertools
import os
import time
import shlex
import sys
from pathlib import Path

import pytest

from sandbox.server.backends.base import BackendConfig
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.config_loader import ConfigLoader
from sandbox.server.core.tool_executor import ToolExecutor

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "code.py"
)


def load_code_backend_module():
    unique_id = next(_MODULE_LOAD_COUNTER)
    module_name = f"_test_code_backend_{unique_id}"
    spec = importlib.util.spec_from_file_location(
        module_name,
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_MODULE_LOAD_COUNTER = itertools.count()


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
            "bash_timeout_seconds": 30,
        },
        description="Code backend",
    )


def create_fake_claude_code_root(tmp_path):
    root = tmp_path / "claude-code-py"
    tools_dir = root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    (root / "log.py").write_text(
        "ROOT_LOG_MARKER = 'log-helper'\n",
        encoding="utf-8",
    )

    (root / "trace.py").write_text(
        "ROOT_TRACE_MARKER = 'trace-helper'\n",
        encoding="utf-8",
    )

    (root / "tool.py").write_text(
        "from log import ROOT_LOG_MARKER\n"
        "from trace import ROOT_TRACE_MARKER\n"
        "\n"
        "class Tool:\n"
        "    ROOT_LOG_MARKER = ROOT_LOG_MARKER\n"
        "    ROOT_TRACE_MARKER = ROOT_TRACE_MARKER\n"
        "\n"
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
        "import asyncio\n"
        "from pathlib import Path\n"
        "import glob\n"
        "\n"
        "class ReadTool(Tool):\n"
        "    def __init__(self):\n"
        "        self.loaded_log_marker = self.ROOT_LOG_MARKER\n"
        "        self.loaded_trace_marker = self.ROOT_TRACE_MARKER\n"
        "\n"
        "    async def call(self, params, ctx):\n"
        "        file_path = Path(params['file_path'])\n"
        "        if not file_path.exists():\n"
        "            return f'Error: File not found: {file_path}'\n"
        "        return file_path.read_text(encoding='utf-8')\n"
        "\n"
        "class GlobTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        base = Path(params.get('path', '.'))\n"
        "        pattern = params.get('pattern', '*')\n"
        "        matches = sorted(glob.glob(pattern, root_dir=str(base), recursive=True))\n"
        "        return [str((base / match).resolve(strict=False)) for match in matches]\n"
        "\n"
        "class GrepTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        return f\"Found 0 matches in {Path(params.get('path', '.'))}\"\n"
        "\n"
        "class BashTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        command = params.get('command', '')\n"
        "        if command == 'pwd':\n"
        "            return ctx.cwd\n"
        "        if command.startswith('sleep '):\n"
        "            await asyncio.sleep(float(command.split(' ', 1)[1]))\n"
        "            return 'slept'\n"
        "        return f\"ran: {command}\"\n",
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
        "        return f\"Updated {file_path}\"\n"
        "\n"
        "class WriteTool(Tool):\n"
        "    async def call(self, params, ctx):\n"
        "        file_path = Path(params['file_path'])\n"
        "        file_path.parent.mkdir(parents=True, exist_ok=True)\n"
        "        file_path.write_text(params.get('content', ''), encoding='utf-8')\n"
        "        return f\"Wrote {file_path}\"\n",
        encoding="utf-8",
    )
    return root


def create_marker_claude_code_root(tmp_path, root_name: str, marker: str):
    root = tmp_path / root_name
    tools_dir = root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    (root / "tool.py").write_text(
        f"class Tool:\n"
        f"    ROOT_MARKER = {marker!r}\n"
        "    async def call(self, params, ctx):\n"
        "        return self.ROOT_MARKER\n",
        encoding="utf-8",
    )

    (tools_dir / "file_tools.py").write_text(
        "from tool import Tool\n"
        "\n"
        "class ReadTool(Tool):\n"
        "    def __init__(self):\n"
        "        self.loaded_marker = self.ROOT_MARKER\n"
        "\n"
        "class GlobTool(Tool):\n"
        "    pass\n"
        "\n"
        "class GrepTool(Tool):\n"
        "    pass\n"
        "\n"
        "class BashTool(Tool):\n"
        "    pass\n",
        encoding="utf-8",
    )

    (tools_dir / "edit_tools.py").write_text(
        "from tool import Tool\n"
        "\n"
        "class EditTool(Tool):\n"
        "    pass\n"
        "\n"
        "class WriteTool(Tool):\n"
        "    pass\n",
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


def test_load_claude_code_tools_supports_root_local_tool_dependencies(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))

    tools = backend._load_claude_code_tools()

    assert tools["read"].loaded_log_marker == "log-helper"
    assert tools["read"].loaded_trace_marker == "trace-helper"


def test_load_code_backend_module_does_not_install_resources_package_in_sys_modules():
    package_name = "sandbox.server.backends.resources"
    previous = sys.modules.pop(package_name, None)

    try:
        module = load_code_backend_module()
        assert hasattr(module, "CodeBackend")
        assert package_name not in sys.modules
    finally:
        if previous is not None:
            sys.modules[package_name] = previous


def test_load_claude_code_tools_is_isolated_per_backend_root(tmp_path):
    module = load_code_backend_module()
    root_a = create_marker_claude_code_root(tmp_path, "claude-code-a", "root-a")
    root_b = create_marker_claude_code_root(tmp_path, "claude-code-b", "root-b")

    config_a = build_backend_config(tmp_path)
    config_a.default_config["claude_code_root"] = str(root_a)
    backend_a = module.CodeBackend(config=config_a)

    config_b = build_backend_config(tmp_path)
    config_b.default_config["claude_code_root"] = str(root_b)
    backend_b = module.CodeBackend(config=config_b)

    tools_a = backend_a._load_claude_code_tools()
    tools_b = backend_b._load_claude_code_tools()

    assert tools_a["read"].loaded_marker == "root-a"
    assert tools_b["read"].loaded_marker == "root-b"


def test_tool_executor_code_dispatch_returns_standard_success_response(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
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
    assert result["data"] == "hello from demo\n"


def test_tool_executor_code_dispatch_preserves_trace_id(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
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
                "data": {
                    "workspace": str(tmp_path / "agentflow_code" / "runtime-workspace")
                },
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


def test_tool_executor_runs_bash_in_session_workspace_when_enabled(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-bash-enabled",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={"command": "pwd"},
            worker_id="worker-1",
            trace_id="trace-bash-enabled",
        )
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"].strip() == str(runtime_workspace.resolve(strict=False))


def test_tool_executor_bash_success_formats_stdout_and_stderr_like_upstream(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-bash-format",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={
                "command": (
                    f"{shlex.quote(sys.executable)} -c "
                    "\"import sys; print('stdout-line'); print('stderr-line', file=sys.stderr)\""
                )
            },
            worker_id="worker-1",
            trace_id="trace-bash-format",
        )
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"] == "stdout-line\n\n[stderr]:\nstderr-line"


def test_tool_executor_returns_timeout_error_when_bash_exceeds_limit(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    config = build_backend_config(tmp_path)
    config.default_config["bash_timeout_seconds"] = 0.01
    backend = module.CodeBackend(config=config)
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-bash-timeout",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={
                "command": (
                    f"{shlex.quote(sys.executable)} -c "
                    "\"import time; time.sleep(2)\""
                )
            },
            worker_id="worker-1",
            trace_id="trace-bash-timeout",
        )
    )

    assert result["code"] == ErrorCode.TIMEOUT_ERROR
    assert "timeout" in result["message"].lower()


def test_tool_executor_bash_timeout_returns_promptly_for_blocking_command(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    config = build_backend_config(tmp_path)
    config.default_config["bash_timeout_seconds"] = 0.1
    backend = module.CodeBackend(config=config)
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-bash-real-timeout",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    start = time.monotonic()
    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={
                "command": (
                    f"{shlex.quote(sys.executable)} -c "
                    "\"import time; time.sleep(5)\""
                )
            },
            worker_id="worker-1",
            trace_id="trace-bash-real-timeout",
        )
    )
    elapsed = time.monotonic() - start

    assert result["code"] == ErrorCode.TIMEOUT_ERROR
    assert elapsed < 2.0


def test_tool_executor_bash_rejects_missing_command(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-bash-missing-command",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={},
            worker_id="worker-1",
            trace_id="trace-bash-missing-command",
        )
    )

    assert result["code"] == ErrorCode.INVALID_INPUT
    assert "command" in result["message"].lower()


def test_tool_executor_bash_rejects_non_string_command(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-bash-non-string-command",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={"command": 123},
            worker_id="worker-1",
            trace_id="trace-bash-non-string-command",
        )
    )

    assert result["code"] == ErrorCode.INVALID_INPUT
    assert "command" in result["message"].lower()


def test_tool_executor_non_bash_timeout_uses_standard_error_handling(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    class TimeoutReadTool:
        async def call(self, params, ctx):
            del params, ctx
            raise asyncio.TimeoutError("read timeout")

    backend._load_claude_code_tools = lambda: {"read": TimeoutReadTool()}

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    demo_file = runtime_workspace / "demo.py"
    demo_file.write_text("hello from demo\n", encoding="utf-8")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-read-timeout",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": str(demo_file)},
            worker_id="worker-1",
            trace_id="trace-read-timeout",
        )
    )

    assert result["code"] == ErrorCode.EXECUTION_ERROR
    assert result["message"] == "read timeout"


def test_code_write_relative_file_path_resolves_inside_session_workspace(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
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

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
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


def test_tool_executor_rejects_missing_session_workspace_without_fallback(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    workspace_root = tmp_path / "agentflow_code"
    workspace_root.mkdir(parents=True, exist_ok=True)
    fallback_file = workspace_root / "fallback.txt"
    fallback_file.write_text("must-not-read\n", encoding="utf-8")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-missing-workspace",
                "data": {},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": "fallback.txt"},
            worker_id="worker-1",
            trace_id="trace-missing-workspace",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_malformed_session_workspace_without_fallback(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-malformed-workspace",
                "data": {"workspace": 123},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": "fallback.txt"},
            worker_id="worker-1",
            trace_id="trace-malformed-workspace",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_nonexistent_session_workspace_under_workspace_root(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    nonexistent_workspace = tmp_path / "agentflow_code" / "worker-1"

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-nonexistent-workspace",
                "data": {"workspace": str(nonexistent_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": "demo.py"},
            worker_id="worker-1",
            trace_id="trace-nonexistent-workspace",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_mismatched_session_workspace_under_workspace_root(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    mismatched_workspace = tmp_path / "agentflow_code" / "other-worker"
    mismatched_workspace.mkdir(parents=True)
    demo_file = mismatched_workspace / "demo.py"
    demo_file.write_text("should-not-read\n", encoding="utf-8")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-mismatched-workspace",
                "data": {"workspace": str(mismatched_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": str(demo_file)},
            worker_id="worker-1",
            trace_id="trace-mismatched-workspace",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_session_workspace_outside_workspace_root(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    outside_workspace = tmp_path / "outside-workspace"
    outside_workspace.mkdir(parents=True)
    demo_file = outside_workspace / "demo.py"
    demo_file.write_text("outside\n", encoding="utf-8")

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-outside-workspace",
                "data": {"workspace": str(outside_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:read",
            params={"file_path": str(demo_file)},
            worker_id="worker-1",
            trace_id="trace-outside-workspace",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


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

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
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

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
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


def test_code_glob_rejects_parent_traversal_pattern(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-glob-parent-traversal",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:glob",
            params={"path": ".", "pattern": "../*"},
            worker_id="worker-1",
            trace_id="trace-glob-parent-traversal",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "pattern" in result["message"].lower()


def test_code_glob_rejects_embedded_parent_traversal_pattern(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    (runtime_workspace / "nested").mkdir(parents=True)
    (runtime_workspace / "nested" / "demo.py").write_text("print('safe')\n", encoding="utf-8")
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-glob-embedded-traversal",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:glob",
            params={"path": ".", "pattern": "**/../*"},
            worker_id="worker-1",
            trace_id="trace-glob-embedded-traversal",
        )
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "pattern" in result["message"].lower()


def test_code_glob_allows_safe_workspace_pattern(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    safe_file = runtime_workspace / "nested" / "demo.py"
    safe_file.parent.mkdir(parents=True)
    safe_file.write_text("print('ok')\n", encoding="utf-8")
    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {
                "session_id": "code-session-glob-safe",
                "data": {"workspace": str(runtime_workspace)},
            }
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:glob",
            params={"path": ".", "pattern": "**/*.py"},
            worker_id="worker-1",
            trace_id="trace-glob-safe",
        )
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"] == [str(safe_file.resolve(strict=False))]


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


def test_initialize_unconfigured_claude_root_preserves_existing_workspace(tmp_path):
    module = load_code_backend_module()
    workspace_root = tmp_path / "agentflow_code"
    workspace = workspace_root / "runner_123"
    workspace.mkdir(parents=True)
    marker = workspace / "keep.txt"
    marker.write_text("preserve-me\n", encoding="utf-8")

    config = BackendConfig(
        enabled=True,
        default_config={
            "claude_code_root": "",
            "workspace_root": str(workspace_root),
            "allow_bash": True,
        },
        description="Code backend",
    )
    backend = module.CodeBackend(config=config)

    with pytest.raises(ValueError, match="claude_code_root"):
        asyncio.run(backend.initialize("runner_123", {}))

    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "preserve-me\n"


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


def test_cleanup_does_not_delete_nested_under_root_non_worker_path(tmp_path):
    module = load_code_backend_module()
    create_fake_claude_code_root(tmp_path)
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    nested_workspace = tmp_path / "agentflow_code" / "shared" / "cache"
    nested_workspace.mkdir(parents=True)

    asyncio.run(
        backend.cleanup("runner_123", {"data": {"workspace": str(nested_workspace)}})
    )

    assert nested_workspace.exists()


def test_code_config_template_parses():
    loader = ConfigLoader()
    config_path = (
        Path(__file__).resolve().parents[2]
        / "configs"
        / "sandbox-server"
        / "code_config.json"
    )

    config = loader.load(str(config_path))

    assert "code" in config.resources
    assert (
        config.resources["code"].backend_class
        == "sandbox.server.backends.resources.code.CodeBackend"
    )
    assert config.server.session_ttl == 300
    assert (
        config.resources["code"].description
        == "Lightweight coding backend powered by claude-code-py tools"
    )
    assert config.resources["code"].config["bash_timeout_seconds"] == 30
    assert config.warmup.enabled is False
    assert config.warmup.resources == []
