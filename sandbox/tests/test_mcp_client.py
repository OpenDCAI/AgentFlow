"""
Tests for the lightweight MCP stdio client and Toolathlon YAML resolution.
"""

import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "mcp_client.py"
)


def load_mcp_client_module():
    spec = importlib.util.spec_from_file_location("sandbox_mcp_client", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_resolve_toolathlon_placeholders(tmp_path):
    module = load_mcp_client_module()

    resolved = module.resolve_mcp_value(
        "${local_servers_paths}/filesystem/dist/index.js",
        local_servers_path="/opt/toolathlon/local_servers",
        agent_workspace=str(tmp_path / "workspace"),
        task_dir=str(tmp_path / "task"),
    )

    assert resolved == "/opt/toolathlon/local_servers/filesystem/dist/index.js"


def test_resolve_mcp_value_rejects_unknown_placeholder(tmp_path):
    module = load_mcp_client_module()

    with pytest.raises(ValueError, match="placeholder"):
        module.resolve_mcp_value(
            "${unsupported}/filesystem/dist/index.js",
            local_servers_path="/opt/toolathlon/local_servers",
            agent_workspace=str(tmp_path / "workspace"),
            task_dir=str(tmp_path / "task"),
        )


def test_pg_env_bridge_prefers_libpq_overrides():
    module = load_mcp_client_module()

    env = module.build_server_env(
        yaml_env={"PG_HOST": "postgres", "PG_PORT": "5432"},
        process_env={"PGHOST": "toolathlon_pg", "PGPORT": "15432"},
    )

    assert env["PG_HOST"] == "toolathlon_pg"
    assert env["PG_PORT"] == "15432"


def test_load_mcp_process_config_rejects_non_stdio_type(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (config_dir / "bad.yaml").write_text(
        """
type: http
name: bad
params:
  command: python
  args: []
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="stdio"):
        module.load_mcp_process_config(
            toolathlon_root=tmp_path,
            server_name="bad",
            agent_workspace=str(tmp_path / "workspace"),
            config_dir=config_dir,
        )


@pytest.mark.anyio
async def test_stdio_client_initialize_and_list_tools(monkeypatch):
    module = load_mcp_client_module()

    class FakeWriter:
        def __init__(self):
            self.writes = []

        def write(self, data):
            self.writes.append(data)

        async def drain(self):
            return None

    class FakeReader:
        def __init__(self, messages):
            self._messages = list(messages)

        async def readline(self):
            if not self._messages:
                return b""
            return self._messages.pop(0)

    class FakeProcess:
        def __init__(self, messages):
            self.stdin = FakeWriter()
            self.stdout = FakeReader(messages)
            self.stderr = FakeReader([])
            self.returncode = None
            self.terminated = False

        def terminate(self):
            self.terminated = True
            self.returncode = 0

        async def wait(self):
            return self.returncode

    process = FakeProcess(
        [
            json.dumps({"jsonrpc": "2.0", "id": 0, "result": {"serverInfo": {}}}).encode() + b"\n",
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {"tools": [{"name": "list_directory"}]},
                }
            ).encode()
            + b"\n",
        ]
    )

    async def fake_create_subprocess_exec(*args, **kwargs):
        return process

    monkeypatch.setattr(
        module.asyncio,
        "create_subprocess_exec",
        fake_create_subprocess_exec,
    )

    client = module.MCPStdioClient(
        module.MCPProcessConfig(
            name="filesystem",
            command="node",
            args=["server.js"],
            env={"FOO": "bar"},
            cwd="/tmp/workspace",
            timeout_seconds=5.0,
        )
    )

    await client.start()
    await client.initialize()
    tools = await client.list_tools()
    await client.close()

    assert tools == [{"name": "list_directory"}]
    assert process.terminated is True
    assert any(b'"method": "initialize"' in payload for payload in process.stdin.writes)
    assert any(b'"method": "notifications/initialized"' in payload for payload in process.stdin.writes)
    assert any(b'"method": "tools/list"' in payload for payload in process.stdin.writes)


def test_load_mcp_process_config_resolves_toolathlon_defaults(tmp_path):
    module = load_mcp_client_module()
    toolathlon_root = tmp_path / "toolathlon"
    config_dir = toolathlon_root / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (toolathlon_root / "local_servers").mkdir()
    (config_dir / "filesystem.yaml").write_text(
        """
type: stdio
name: filesystem
params:
  command: node
  args:
    - ${local_servers_paths}/filesystem/dist/index.js
    - ${agent_workspace}
  env:
    ALLOWED_DIR: ${agent_workspace}
  cwd: ${agent_workspace}
client_session_timeout_seconds: 42
cache_tools_list: true
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        toolathlon_root=toolathlon_root,
        server_name="filesystem",
        agent_workspace=str(tmp_path / "workspace"),
    )

    assert config.command == "node"
    assert config.args[0].endswith("/local_servers/filesystem/dist/index.js")
    assert config.args[1] == str(tmp_path / "workspace")
    assert config.env["ALLOWED_DIR"] == str(tmp_path / "workspace")
    assert config.cwd == str(tmp_path / "workspace")
    assert config.timeout_seconds == 42


def test_load_mcp_process_config_uses_process_env_overrides(tmp_path):
    module = load_mcp_client_module()
    toolathlon_root = tmp_path / "toolathlon"
    config_dir = toolathlon_root / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (toolathlon_root / "local_servers").mkdir()
    (config_dir / "postgres.yaml").write_text(
        """
type: stdio
name: postgres
params:
  command: node
  args: []
  env:
    PG_HOST: from_yaml
    PG_PORT: "5432"
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        toolathlon_root=toolathlon_root,
        server_name="postgres",
        agent_workspace=str(tmp_path / "workspace"),
        process_env={"PGHOST": "from_process", "PGPORT": "15432"},
    )

    assert config.env["PG_HOST"] == "from_process"
    assert config.env["PG_PORT"] == "15432"
