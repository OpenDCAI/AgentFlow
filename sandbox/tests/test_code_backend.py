"""
Tests for the Code backend skeleton and bridge-tool registration.
"""

import asyncio
import importlib.util
import itertools
import os
import sys
from pathlib import Path
import types

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
VENDOR_PACKAGE_DIR = MODULE_PATH.parent / "code_vendor"


def install_resources_package_stub():
    package_name = "sandbox.server.backends.resources"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(MODULE_PATH.parent)]
        sys.modules[package_name] = package

    vendor_package_name = f"{package_name}.code_vendor"
    if vendor_package_name not in sys.modules:
        package_spec = importlib.util.spec_from_file_location(
            vendor_package_name,
            VENDOR_PACKAGE_DIR / "__init__.py",
            submodule_search_locations=[str(VENDOR_PACKAGE_DIR)],
        )
        package = importlib.util.module_from_spec(package_spec)
        assert package_spec is not None
        assert package_spec.loader is not None
        sys.modules[vendor_package_name] = package
        package_spec.loader.exec_module(package)

    for module_name in ("tool", "file_tools", "edit_tools"):
        full_name = f"{vendor_package_name}.{module_name}"
        if full_name in sys.modules:
            continue
        module_spec = importlib.util.spec_from_file_location(
            full_name,
            VENDOR_PACKAGE_DIR / f"{module_name}.py",
        )
        module = importlib.util.module_from_spec(module_spec)
        assert module_spec is not None
        assert module_spec.loader is not None
        sys.modules[full_name] = module
        module_spec.loader.exec_module(module)


def remove_resources_modules():
    package_name = "sandbox.server.backends.resources"
    for module_name in list(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            sys.modules.pop(module_name, None)


def load_code_backend_module():
    install_resources_package_stub()
    unique_id = next(_MODULE_LOAD_COUNTER)
    module_name = f"_test_code_backend_{unique_id}"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
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


def build_backend_config(tmp_path):
    return BackendConfig(
        enabled=True,
        default_config={
            "workspace_root": str(tmp_path / "agentflow_code"),
        },
        description="Code backend",
    )


def build_backend(tmp_path):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    return module, backend


def bind_backend_tools(backend):
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    return fake_server


def build_executor(fake_server, session_info):
    return ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(session_info),
    )


def execute_tool(executor, action, *, params, worker_id, trace_id):
    return asyncio.run(
        executor.execute(
            action=action,
            params=params,
            worker_id=worker_id,
            trace_id=trace_id,
        )
    )


def test_bind_server_registers_code_tools(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)

    assert "code:read" in fake_server._tools
    assert "code:bash" in fake_server._tools
    assert fake_server._tool_resource_types["code:read"] == "code"
    assert fake_server._tool_resource_types["code:bash"] == "code"


def test_initialize_does_not_require_external_root(tmp_path):
    _, backend = build_backend(tmp_path)

    session = asyncio.run(backend.initialize("runner_123", {}))

    assert session["workspace"].endswith("runner_123")
    assert Path(session["workspace"]).exists()


def test_initialize_copies_source_dir(tmp_path):
    _, backend = build_backend(tmp_path)
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "demo.py").write_text("print('hi')\n", encoding="utf-8")

    session = asyncio.run(
        backend.initialize("runner_123", {"source_dir": str(source_dir)})
    )

    copied = Path(session["workspace"]) / "demo.py"
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "print('hi')\n"


def test_load_code_tools_uses_internal_vendor_package(tmp_path):
    _, backend = build_backend(tmp_path)

    tools = backend._load_code_tools()

    assert set(tools.keys()) == {"read", "glob", "grep", "bash", "edit", "write"}
    assert type(tools["read"]).__module__ == (
        "sandbox.server.backends.resources.code_vendor.file_tools"
    )
    assert type(tools["edit"]).__module__ == (
        "sandbox.server.backends.resources.code_vendor.edit_tools"
    )
    assert backend._load_code_tools() is tools


def test_tool_executor_code_dispatch_returns_standard_success_response(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    demo_file = runtime_workspace / "demo.py"
    demo_file.write_text("hello from demo\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-1",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": str(demo_file)},
        worker_id="worker-1",
        trace_id="trace-1",
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"] == "   1→hello from demo"


def test_tool_executor_code_dispatch_preserves_trace_id(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    demo_file = runtime_workspace / "demo.py"
    demo_file.write_text("hello from demo\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-trace",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": str(demo_file)},
        worker_id="worker-1",
        trace_id="trace-preserve-1",
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["meta"]["trace_id"] == "trace-preserve-1"


def test_tool_executor_runs_bash_via_vendored_tool(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-bash",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:bash",
        params={"command": "pwd"},
        worker_id="worker-1",
        trace_id="trace-bash",
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"] == str(runtime_workspace.resolve(strict=False))


def test_tool_executor_non_bash_timeout_uses_standard_error_handling(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)

    class TimeoutReadTool:
        async def call(self, params, ctx):
            del params, ctx
            raise asyncio.TimeoutError("read timeout")

    tools = backend._load_code_tools()
    backend._tool_instances = dict(tools)
    backend._tool_instances["read"] = TimeoutReadTool()

    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    demo_file = runtime_workspace / "demo.py"
    demo_file.write_text("hello from demo\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-read-timeout",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": str(demo_file)},
        worker_id="worker-1",
        trace_id="trace-read-timeout",
    )

    assert result["code"] == ErrorCode.EXECUTION_ERROR
    assert result["message"] == "read timeout"


def test_code_write_relative_file_path_resolves_inside_session_workspace(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    process_cwd = tmp_path / "process-cwd"
    process_cwd.mkdir(parents=True)
    prev_cwd = Path.cwd()
    os.chdir(process_cwd)
    try:
        executor = build_executor(
            fake_server,
            {
                "session_id": "code-session-3",
                "data": {"workspace": str(runtime_workspace)},
            },
        )

        result = execute_tool(
            executor,
            "code:write",
            params={"file_path": "nested/output.txt", "content": "from workspace\n"},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    finally:
        os.chdir(prev_cwd)

    assert result["code"] == ErrorCode.SUCCESS
    assert (runtime_workspace / "nested" / "output.txt").read_text(encoding="utf-8") == (
        "from workspace\n"
    )
    assert not (process_cwd / "nested" / "output.txt").exists()


def test_code_read_error_prefix_is_returned_as_agentflow_error_response(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-4",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": "missing.txt"},
        worker_id="worker-1",
        trace_id="trace-1",
    )

    assert result["code"] != ErrorCode.SUCCESS
    assert result["message"].startswith("Error:")


def test_tool_executor_rejects_missing_session_workspace_without_fallback(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    workspace_root = tmp_path / "agentflow_code"
    workspace_root.mkdir(parents=True, exist_ok=True)
    fallback_file = workspace_root / "fallback.txt"
    fallback_file.write_text("must-not-read\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-missing-workspace",
            "data": {},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": "fallback.txt"},
        worker_id="worker-1",
        trace_id="trace-missing-workspace",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_malformed_session_workspace_without_fallback(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-malformed-workspace",
            "data": {"workspace": 123},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": "fallback.txt"},
        worker_id="worker-1",
        trace_id="trace-malformed-workspace",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_nonexistent_session_workspace_under_workspace_root(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    nonexistent_workspace = tmp_path / "agentflow_code" / "worker-1"
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-nonexistent-workspace",
            "data": {"workspace": str(nonexistent_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": "demo.py"},
        worker_id="worker-1",
        trace_id="trace-nonexistent-workspace",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_mismatched_session_workspace_under_workspace_root(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    mismatched_workspace = tmp_path / "agentflow_code" / "other-worker"
    mismatched_workspace.mkdir(parents=True)
    demo_file = mismatched_workspace / "demo.py"
    demo_file.write_text("should-not-read\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-mismatched-workspace",
            "data": {"workspace": str(mismatched_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": str(demo_file)},
        worker_id="worker-1",
        trace_id="trace-mismatched-workspace",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_tool_executor_rejects_session_workspace_outside_workspace_root(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    outside_workspace = tmp_path / "outside-workspace"
    outside_workspace.mkdir(parents=True)
    demo_file = outside_workspace / "demo.py"
    demo_file.write_text("outside\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-outside-workspace",
            "data": {"workspace": str(outside_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": str(demo_file)},
        worker_id="worker-1",
        trace_id="trace-outside-workspace",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "session workspace" in result["message"].lower()


def test_initialize_recreates_worker_workspace_without_stale_files(tmp_path):
    _, backend = build_backend(tmp_path)
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
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("secret\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-5",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:read",
        params={"file_path": str(outside_file)},
        worker_id="worker-1",
        trace_id="trace-1",
    )

    assert result["code"] != ErrorCode.SUCCESS


def test_code_write_rejects_parent_escape_outside_workspace(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    escaped_file = tmp_path / "escaped.txt"
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-6",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:write",
        params={"file_path": "../escaped.txt", "content": "escaped\n"},
        worker_id="worker-1",
        trace_id="trace-1",
    )

    assert result["code"] != ErrorCode.SUCCESS
    assert not escaped_file.exists()


def test_code_glob_rejects_parent_traversal_pattern(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-glob-parent-traversal",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:glob",
        params={"path": ".", "pattern": "../*"},
        worker_id="worker-1",
        trace_id="trace-glob-parent-traversal",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "pattern" in result["message"].lower()


def test_code_glob_rejects_embedded_parent_traversal_pattern(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    (runtime_workspace / "nested").mkdir(parents=True)
    (runtime_workspace / "nested" / "demo.py").write_text(
        "print('safe')\n",
        encoding="utf-8",
    )
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-glob-embedded-traversal",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:glob",
        params={"path": ".", "pattern": "**/../*"},
        worker_id="worker-1",
        trace_id="trace-glob-embedded-traversal",
    )

    assert result["code"] == ErrorCode.BUSINESS_FAILURE
    assert "pattern" in result["message"].lower()


def test_code_glob_allows_safe_workspace_pattern(tmp_path):
    _, backend = build_backend(tmp_path)
    fake_server = bind_backend_tools(backend)
    runtime_workspace = tmp_path / "agentflow_code" / "worker-1"
    runtime_workspace.mkdir(parents=True)
    safe_file = runtime_workspace / "nested" / "demo.py"
    safe_file.parent.mkdir(parents=True)
    safe_file.write_text("print('ok')\n", encoding="utf-8")
    executor = build_executor(
        fake_server,
        {
            "session_id": "code-session-glob-safe",
            "data": {"workspace": str(runtime_workspace)},
        },
    )

    result = execute_tool(
        executor,
        "code:glob",
        params={"path": ".", "pattern": "**/*.py"},
        worker_id="worker-1",
        trace_id="trace-glob-safe",
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"] == str(safe_file.resolve(strict=False))


def test_initialize_rejects_hostile_worker_id_without_deleting_outside_dir(tmp_path):
    _, backend = build_backend(tmp_path)
    outside_dir = tmp_path / "escaped"
    outside_dir.mkdir(parents=True)
    marker = outside_dir / "keep.txt"
    marker.write_text("do-not-delete\n", encoding="utf-8")

    with pytest.raises(ValueError):
        asyncio.run(backend.initialize("../escaped", {}))

    assert marker.exists()


def test_initialize_rejects_nonexistent_source_dir(tmp_path):
    _, backend = build_backend(tmp_path)
    missing_source = tmp_path / "missing-source"

    with pytest.raises(ValueError, match="source_dir"):
        asyncio.run(backend.initialize("runner_123", {"source_dir": str(missing_source)}))


def test_initialize_invalid_source_dir_leaves_no_workspace(tmp_path):
    _, backend = build_backend(tmp_path)
    missing_source = tmp_path / "missing-source"
    workspace = tmp_path / "agentflow_code" / "runner_123"

    with pytest.raises(ValueError, match="source_dir"):
        asyncio.run(backend.initialize("runner_123", {"source_dir": str(missing_source)}))

    assert not workspace.exists()


def test_cleanup_removes_worker_workspace(tmp_path):
    _, backend = build_backend(tmp_path)
    session = asyncio.run(backend.initialize("runner_123", {}))
    workspace = Path(session["workspace"])

    assert workspace.exists()
    asyncio.run(backend.cleanup("runner_123", {"data": {"workspace": str(workspace)}}))

    assert not workspace.exists()


def test_cleanup_does_not_delete_workspace_outside_root(tmp_path):
    _, backend = build_backend(tmp_path)
    outside_workspace = tmp_path / "outside-workspace"
    outside_workspace.mkdir(parents=True)

    asyncio.run(
        backend.cleanup("runner_123", {"data": {"workspace": str(outside_workspace)}})
    )

    assert outside_workspace.exists()


def test_cleanup_does_not_delete_nested_under_root_non_worker_path(tmp_path):
    _, backend = build_backend(tmp_path)
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
        == "Lightweight coding backend powered by vendored internal tools"
    )
    assert config.resources["code"].config == {"workspace_root": "/tmp/agentflow_code"}
    assert config.warmup.enabled is False
    assert config.warmup.resources == []


def test_create_server_loads_code_backend_via_config_loader(tmp_path):
    workspace_root = tmp_path / "agentflow_code"
    remove_resources_modules()
    loader = ConfigLoader()
    loader.load_from_dict(
        {
            "server": {
                "title": "Code backend smoke",
                "session_ttl": 300,
            },
            "resources": {
                "code": {
                    "enabled": True,
                    "description": "Code backend",
                    "backend_class": "sandbox.server.backends.resources.code.CodeBackend",
                    "config": {
                        "workspace_root": str(workspace_root),
                    },
                }
            },
            "warmup": {
                "enabled": False,
                "resources": [],
            },
        }
    )

    server = loader.create_server(host="127.0.0.1", port=0)
    resources_package = sys.modules["sandbox.server.backends.resources"]
    code_module = sys.modules["sandbox.server.backends.resources.code"]

    assert "code" in server._backends
    assert "code:read" in server._tools
    assert server._tool_resource_types["code:read"] == "code"
    assert Path(resources_package.__file__).resolve() == (MODULE_PATH.parent / "__init__.py").resolve()
    assert Path(code_module.__file__).resolve() == MODULE_PATH.resolve()
