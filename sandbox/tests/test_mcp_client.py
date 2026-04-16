"""
Tests for the lightweight MCP stdio client and Toolathlon YAML resolution.
"""

import asyncio
import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "mcp"
    / "client.py"
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


def test_resolve_mcp_value_leaves_unknown_placeholders_as_literals(tmp_path):
    module = load_mcp_client_module()

    result = module.resolve_mcp_value(
        "${unsupported}/filesystem/dist/index.js",
        local_servers_path="/opt/toolathlon/local_servers",
        agent_workspace=str(tmp_path / "workspace"),
        task_dir=str(tmp_path / "task"),
    )

    assert result == "${unsupported}/filesystem/dist/index.js"


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
            server_name="bad",
            agent_workspace=str(tmp_path / "workspace"),
            config_dir=config_dir,
        )


def test_load_mcp_process_config_finds_yaml_by_name_when_filename_differs(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (tmp_path / "local_servers").mkdir()
    (config_dir / "npx-fetch.yaml").write_text(
        """
type: stdio
name: fetch
params:
  command: node
  args:
    - ${local_servers_paths}/mcp-npx-fetch/dist/index.js
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        server_name="fetch",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(tmp_path / "local_servers"),
        config_dir=config_dir,
    )

    assert config.name == "fetch"
    assert config.command == "node"
    assert config.args[0].endswith("/local_servers/mcp-npx-fetch/dist/index.js")


@pytest.mark.anyio
async def test_stdio_client_initialize_and_list_tools(monkeypatch):
    module = load_mcp_client_module()
    create_kwargs = {}

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

        async def communicate(self):
            return b"", b""

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
        create_kwargs.update(kwargs)
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
    assert create_kwargs["stderr"] is module.asyncio.subprocess.PIPE
    assert any(b'"method": "initialize"' in payload for payload in process.stdin.writes)
    assert any(b'"method": "notifications/initialized"' in payload for payload in process.stdin.writes)
    assert any(b'"method": "tools/list"' in payload for payload in process.stdin.writes)


@pytest.mark.anyio
async def test_stdio_client_ignores_mismatched_response_id(monkeypatch):
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

        def terminate(self):
            self.returncode = 0

        async def wait(self):
            return self.returncode

        async def communicate(self):
            return b"", b""

    process = FakeProcess(
        [
            json.dumps({"jsonrpc": "2.0", "id": 999, "result": {"serverInfo": {"name": "stale"}}}).encode()
            + b"\n",
            json.dumps({"jsonrpc": "2.0", "id": 0, "result": {"serverInfo": {}}}).encode() + b"\n",
            json.dumps({"jsonrpc": "2.0", "id": 7, "result": {"tools": [{"name": "wrong"}]}}).encode()
            + b"\n",
            json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "right"}]}}).encode()
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

    assert tools == [{"name": "right"}]


@pytest.mark.anyio
async def test_close_kills_process_after_wait_timeout(monkeypatch):
    module = load_mcp_client_module()

    class FakeProcess:
        def __init__(self):
            self.returncode = None
            self.terminated = False
            self.killed = False

        def terminate(self):
            self.terminated = True

        def kill(self):
            self.killed = True
            self.returncode = -9

        async def wait(self):
            return self.returncode

        async def communicate(self):
            return b"", b""

    async def fake_wait_for(awaitable, timeout):
        if timeout == 5.0:
            awaitable.close()
            raise TimeoutError("simulated timeout")
        return await awaitable

    monkeypatch.setattr(module.asyncio, "wait_for", fake_wait_for)

    client = module.MCPStdioClient(
        module.MCPProcessConfig(
            name="filesystem",
            command="node",
            args=["server.js"],
            env={"FOO": "bar"},
            cwd="/tmp/workspace",
            timeout_seconds=30.0,
        )
    )
    process = FakeProcess()
    client._process = process

    await client.close()

    assert client._process is None
    assert process.terminated is True
    assert process.killed is True


@pytest.mark.anyio
async def test_stdio_client_serializes_concurrent_requests(monkeypatch):
    module = load_mcp_client_module()
    active_reads = 0
    max_active_reads = 0

    async def fake_send(payload):
        del payload
        return None

    async def fake_read_response(expected_request_id=None):
        del expected_request_id
        nonlocal active_reads, max_active_reads
        active_reads += 1
        max_active_reads = max(max_active_reads, active_reads)
        await asyncio.sleep(0)
        active_reads -= 1
        return {"result": {"content": []}}

    client = module.MCPStdioClient(
        module.MCPProcessConfig(
            name="filesystem",
            command="node",
            args=["server.js"],
            env={"FOO": "bar"},
            cwd="/tmp/workspace",
            timeout_seconds=30.0,
        )
    )
    client._process = object()
    monkeypatch.setattr(client, "_send", fake_send)
    monkeypatch.setattr(client, "_read_response", fake_read_response)

    await asyncio.gather(
        client.call_tool("list_directory", {"path": "."}),
        client.call_tool("read_text_file", {"path": "README.md"}),
    )

    assert max_active_reads == 1


def test_load_mcp_process_config_resolves_with_mcp_servers_path(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "configs"
    config_dir.mkdir(parents=True)
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
        server_name="filesystem",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(tmp_path / "mcp_servers"),
        config_dir=config_dir,
    )

    assert config.command == "node"
    assert config.args[0].endswith("/mcp_servers/filesystem/dist/index.js")
    assert config.args[1] == str(tmp_path / "workspace")
    assert config.env["ALLOWED_DIR"] == str(tmp_path / "workspace")
    assert config.cwd == str(tmp_path / "workspace")
    assert config.timeout_seconds == 42


def test_load_mcp_process_config_backward_compat_toolathlon_root(tmp_path):
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
  cwd: ${agent_workspace}
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
    assert "/local_servers/" in config.args[0]


def test_load_mcp_process_config_uses_process_env_overrides(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "configs"
    config_dir.mkdir(parents=True)
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
        server_name="postgres",
        agent_workspace=str(tmp_path / "workspace"),
        config_dir=config_dir,
        process_env={"PGHOST": "from_process", "PGPORT": "15432"},
    )

    assert config.env["PG_HOST"] == "from_process"
    assert config.env["PG_PORT"] == "15432"
