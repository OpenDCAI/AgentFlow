"""
Tests for the Code backend skeleton and bridge-tool registration.
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


def test_bind_server_registers_code_tools(tmp_path):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()

    backend.bind_server(fake_server)

    assert "code:read" in fake_server._tools
    assert "code:bash" in fake_server._tools
    assert fake_server._tool_resource_types["code:read"] == "code"
    assert fake_server._tool_resource_types["code:bash"] == "code"


def test_initialize_creates_worker_workspace(tmp_path, monkeypatch):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    monkeypatch.setattr(backend, "_load_claude_code_tools", lambda: {})

    session = asyncio.run(backend.initialize("runner_123", {}))

    assert session["workspace"].endswith("runner_123")
    assert Path(session["workspace"]).exists()


def test_initialize_copies_source_dir(tmp_path, monkeypatch):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "demo.py").write_text("print('hi')\n", encoding="utf-8")
    monkeypatch.setattr(backend, "_load_claude_code_tools", lambda: {})

    session = asyncio.run(
        backend.initialize("runner_123", {"source_dir": str(source_dir)})
    )

    copied = Path(session["workspace"]) / "demo.py"
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "print('hi')\n"
