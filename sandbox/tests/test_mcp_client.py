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


def make_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


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


def test_load_mcp_process_config_prefers_toolathlon_configs_next_to_local_servers(tmp_path):
    module = load_mcp_client_module()
    toolathlon_root = tmp_path / "toolathlon"
    config_dir = toolathlon_root / "configs" / "mcp_servers"
    local_servers_dir = toolathlon_root / "local_servers"
    config_dir.mkdir(parents=True)
    local_servers_dir.mkdir()
    (config_dir / "canvas.yaml").write_text(
        """
type: stdio
name: canvas
params:
  command: node
  args:
    - ${local_servers_paths}/mcp-canvas-lms/build/index.js
  env:
    CANVAS_API_TOKEN: placeholder
  cwd: ${agent_workspace}
client_session_timeout_seconds: 10
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        server_name="canvas",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == "node"
    assert config.args == [str(local_servers_dir / "mcp-canvas-lms" / "build" / "index.js")]
    assert config.env["CANVAS_API_TOKEN"] == "placeholder"
    assert config.cwd == str(tmp_path / "workspace")
    assert config.timeout_seconds == 10


def test_discover_mcp_config_dir_requires_toolathlon_local_servers_layout(tmp_path):
    module = load_mcp_client_module()
    toolathlon_root = tmp_path / "toolathlon"
    config_dir = toolathlon_root / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (toolathlon_root / "custom_servers").mkdir()
    (toolathlon_root / "local_servers").mkdir()

    assert module.discover_mcp_config_dir(toolathlon_root / "custom_servers") is None
    assert module.discover_mcp_config_dir(toolathlon_root / "local_servers") == config_dir


def test_discover_mcp_config_dir_requires_real_directory(tmp_path):
    module = load_mcp_client_module()
    toolathlon_root = tmp_path / "toolathlon"
    local_servers_dir = toolathlon_root / "local_servers"
    local_servers_dir.mkdir(parents=True)
    config_path = toolathlon_root / "configs" / "mcp_servers"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("not a directory\n", encoding="utf-8")

    assert module.discover_mcp_config_dir(local_servers_dir) is None


def test_load_mcp_process_config_resolves_toolathlon_local_servers_path(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (config_dir / "filesystem.yaml").write_text(
        """
type: stdio
name: filesystem
params:
  command: node
  args:
    - ${local_servers_paths}/filesystem/environment/dist/index.js
    - ${agent_workspace}
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        server_name="filesystem",
        agent_workspace="/tmp/agentflow-worker",
        mcp_servers_path="/tmp/toolathlon/local_servers",
        config_dir=config_dir,
    )

    assert config.command == "node"
    assert config.args == [
        "/tmp/toolathlon/local_servers/filesystem/environment/dist/index.js",
        "/tmp/agentflow-worker",
    ]


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


def test_load_mcp_process_config_sets_workspace_uv_cache_for_uv_servers(tmp_path):
    module = load_mcp_client_module()
    workspace = tmp_path / "workspace"
    local_servers_dir = tmp_path / "toolathlon" / "local_servers"
    (local_servers_dir / "mcp-snowflake-server").mkdir(parents=True)

    config = module.load_mcp_process_config(
        server_name="snowflake",
        agent_workspace=str(workspace),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == "uv"
    assert config.env["UV_CACHE_DIR"] == str(workspace / ".cache" / "uv")


def test_load_mcp_process_config_preserves_existing_uv_cache_dir(tmp_path):
    module = load_mcp_client_module()
    workspace = tmp_path / "workspace"
    local_servers_dir = tmp_path / "toolathlon" / "local_servers"
    (local_servers_dir / "mcp-snowflake-server").mkdir(parents=True)

    config = module.load_mcp_process_config(
        server_name="snowflake",
        agent_workspace=str(workspace),
        mcp_servers_path=str(local_servers_dir),
        process_env={"UV_CACHE_DIR": "/tmp/custom-uv-cache"},
    )

    assert config.env["UV_CACHE_DIR"] == "/tmp/custom-uv-cache"


def test_load_mcp_process_config_does_not_inject_uv_cache_for_custom_config_dir(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "custom-configs"
    config_dir.mkdir(parents=True)
    (config_dir / "custom-uv.yaml").write_text(
        """
type: stdio
name: custom-uv
params:
  command: uv
  args:
    - run
    - python
    - server.py
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        server_name="custom-uv",
        agent_workspace=str(tmp_path / "workspace"),
        config_dir=config_dir,
        process_env={},
    )

    assert config.command == "uv"
    assert "UV_CACHE_DIR" not in config.env


def test_load_mcp_process_config_keeps_direct_python_fast_path_when_venv_exists(tmp_path):
    module = load_mcp_client_module()
    local_servers_dir = tmp_path / "toolathlon" / "local_servers"
    project_dir = local_servers_dir / "yahoo-finance-mcp"
    make_executable(project_dir / ".venv" / "bin" / "python3")
    (project_dir / "server.py").write_text("print('ok')\n", encoding="utf-8")

    config = module.load_mcp_process_config(
        server_name="yahoo-finance",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == str(project_dir / ".venv" / "bin" / "python3")
    assert config.args == ["server.py"]
    assert config.cwd == str(project_dir)


def test_load_mcp_process_config_falls_back_to_uv_for_yahoo_finance_without_venv_launcher(tmp_path):
    module = load_mcp_client_module()
    local_servers_dir = tmp_path / "toolathlon" / "local_servers"
    project_dir = local_servers_dir / "yahoo-finance-mcp"
    project_dir.mkdir(parents=True)
    (project_dir / "server.py").write_text("print('ok')\n", encoding="utf-8")

    config = module.load_mcp_process_config(
        server_name="yahoo-finance",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == "uv"
    assert config.args == ["--directory", str(project_dir), "run", "python", "server.py"]
    assert config.cwd == str(project_dir)


def test_load_mcp_process_config_does_not_fallback_when_bundled_entrypoint_is_missing(tmp_path):
    module = load_mcp_client_module()
    local_servers_dir = tmp_path / "toolathlon" / "local_servers"
    project_dir = local_servers_dir / "yahoo-finance-mcp"
    project_dir.mkdir(parents=True)

    config = module.load_mcp_process_config(
        server_name="yahoo-finance",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == str(project_dir / ".venv" / "bin" / "python3")
    assert config.args == ["server.py"]
    assert config.cwd == str(project_dir)


def test_load_mcp_process_config_falls_back_to_uv_for_youtube_transcript_when_launcher_unusable(
    tmp_path,
):
    module = load_mcp_client_module()
    local_servers_dir = tmp_path / "toolathlon" / "local_servers"
    project_dir = local_servers_dir / "mcp-youtube-transcript"
    launcher = project_dir / ".venv" / "bin" / "python3"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    launcher.chmod(0o644)
    (project_dir / "run_server.py").write_text("print('ok')\n", encoding="utf-8")

    config = module.load_mcp_process_config(
        server_name="youtube-transcript",
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == "uv"
    assert config.args == ["--directory", str(project_dir), "run", "python", "run_server.py"]
    assert config.cwd == str(project_dir)


@pytest.mark.parametrize(
    ("server_name", "project_subdir", "entrypoint"),
    [
        ("yahoo-finance", "yahoo-finance-mcp", "server.py"),
        ("youtube-transcript", "mcp-youtube-transcript", "run_server.py"),
    ],
)
def test_load_mcp_process_config_falls_back_to_uv_for_discovered_toolathlon_python_servers(
    tmp_path,
    server_name,
    project_subdir,
    entrypoint,
):
    module = load_mcp_client_module()
    toolathlon_root = tmp_path / "toolathlon"
    config_dir = toolathlon_root / "configs" / "mcp_servers"
    local_servers_dir = toolathlon_root / "local_servers"
    project_dir = local_servers_dir / project_subdir
    config_dir.mkdir(parents=True)
    project_dir.mkdir(parents=True)
    (project_dir / entrypoint).write_text("print('ok')\n", encoding="utf-8")
    (config_dir / f"{server_name}.yaml").write_text(
        f"""
type: stdio
name: {server_name}
params:
  command: ${{local_servers_paths}}/{project_subdir}/.venv/bin/python3
  args:
    - {entrypoint}
  cwd: ${{local_servers_paths}}/{project_subdir}
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        server_name=server_name,
        agent_workspace=str(tmp_path / "workspace"),
        mcp_servers_path=str(local_servers_dir),
        process_env={},
    )

    assert config.command == "uv"
    assert config.args == ["--directory", str(project_dir), "run", "python", entrypoint]
    assert config.cwd == str(project_dir)


def assert_resolved_runtime_paths(config) -> None:
    all_values = [config.command, config.cwd, *config.args]
    for value in all_values:
        assert "${local_servers_paths}" not in value
        assert "/environment/" not in value


def assert_arg_contains_path(config, expected_path: str) -> None:
    assert expected_path in config.args


def assert_python_server_launch(config, server_subdir: str, fallback_entrypoint: str) -> None:
    expected_project_dir = f"/toolathlon/local_servers/{server_subdir}"
    assert config.cwd == expected_project_dir

    if config.command.endswith("/.venv/bin/python3"):
        assert config.command == f"{expected_project_dir}/.venv/bin/python3"
        if fallback_entrypoint == "server.py":
            assert config.args == ["server.py"]
        else:
            assert config.args[0] == "-c"
            assert "mcp_youtube_transcript" in config.args[1]
            assert expected_project_dir in config.args[1]
        return

    assert "--directory" in config.args
    assert_arg_contains_path(config, expected_project_dir)
    assert "run" in config.args
    assert fallback_entrypoint in config.args


@pytest.mark.parametrize(
    ("server_name", "expected"),
    [
        (
            "canvas",
            {
                "launch": "node",
                "server_subdir": "mcp-canvas-lms",
                "entrypoint_suffix": "/build/index.js",
                "cwd": "/workspace",
                "timeout_seconds": 10,
                "env_subset": {
                    "CANVAS_API_TOKEN": "placeholder",
                    "CANVAS_DOMAIN": "localhost:8080",
                    "NODE_TLS_REJECT_UNAUTHORIZED": "0",
                },
            },
        ),
        (
            "snowflake",
            {
                "launch": "uv",
                "server_subdir": "mcp-snowflake-server",
                "entrypoint": "mcp_snowflake_server",
                "cwd": "/workspace",
                "timeout_seconds": 120,
                "env_subset": {
                    "PG_HOST": "toolathlon_pg",
                    "PG_PORT": "5432",
                    "PG_DATABASE": "toolathlon_gym",
                    "PG_USER": "eigent",
                    "PG_PASSWORD": "camel",
                },
            },
        ),
        (
            "woocommerce",
            {
                "launch": "node",
                "server_subdir": "woocommerce-mcp",
                "entrypoint_suffix": "/dist/index.js",
                "cwd": "/workspace",
                "timeout_seconds": 10,
                "env_subset": {
                    "WORDPRESS_SITE_URL": "http://localhost:8081",
                    "WOOCOMMERCE_CONSUMER_KEY": "placeholder",
                    "WOOCOMMERCE_CONSUMER_SECRET": "placeholder",
                },
            },
        ),
        (
            "yahoo-finance",
            {
                "launch": "python_or_uv",
                "server_subdir": "yahoo-finance-mcp",
                "fallback_entrypoint": "server.py",
                "cwd": "/toolathlon/local_servers/yahoo-finance-mcp",
                "timeout_seconds": 60,
                "env_subset": {},
            },
        ),
        (
            "youtube",
            {
                "launch": "node",
                "server_subdir": "youtube-mcp-server",
                "entrypoint_suffix": "/dist/index.js",
                "cwd": "/workspace",
                "timeout_seconds": 120,
                "env_subset": {
                    "PG_HOST": "postgres",
                    "PG_PORT": "5432",
                    "PG_DATABASE": "toolathlon",
                    "PG_USER": "postgres",
                    "PG_PASSWORD": "postgres",
                },
            },
        ),
        (
            "youtube-transcript",
            {
                "launch": "python_or_uv",
                "server_subdir": "mcp-youtube-transcript",
                "fallback_entrypoint": "run_server.py",
                "cwd": "/toolathlon/local_servers/mcp-youtube-transcript",
                "timeout_seconds": 20,
                "env_subset": {
                    "PG_HOST": "postgres",
                    "PG_PORT": "5432",
                    "PG_DATABASE": "toolathlon",
                    "PG_USER": "postgres",
                    "PG_PASSWORD": "postgres",
                },
            },
        ),
        (
            "rail_12306",
            {
                "launch": "node",
                "server_subdir": "12306-mcp",
                "entrypoint_suffix": "/build/index.js",
                "cwd": "/workspace",
                "timeout_seconds": 20,
                "env_subset": {
                    "PG_HOST": "postgres",
                    "PG_PORT": "5432",
                    "PG_DATABASE": "toolathlon",
                    "PG_USER": "postgres",
                    "PG_PASSWORD": "postgres",
                },
            },
        ),
        (
            "filesystem",
            {
                "launch": "node_with_workspace_arg",
                "server_subdir": "filesystem",
                "entrypoint_suffix": "/dist/index.js",
                "cwd": "/workspace",
                "timeout_seconds": 300,
                "env_subset": {},
            },
        ),
    ],
)
def test_bundled_mcp_runtime_configs_match_current_toolathlon_layout(server_name, expected):
    module = load_mcp_client_module()

    config = module.load_mcp_process_config(
        server_name=server_name,
        agent_workspace="/workspace",
        mcp_servers_path="/toolathlon/local_servers",
        process_env={},
    )

    assert_resolved_runtime_paths(config)
    assert config.cwd == expected["cwd"]
    assert config.timeout_seconds == expected["timeout_seconds"]

    launch = expected["launch"]
    if launch == "node":
        assert_arg_contains_path(
            config,
            f"/toolathlon/local_servers/{expected['server_subdir']}{expected['entrypoint_suffix']}",
        )
    elif launch == "node_with_workspace_arg":
        assert_arg_contains_path(
            config,
            f"/toolathlon/local_servers/{expected['server_subdir']}{expected['entrypoint_suffix']}",
        )
        assert_arg_contains_path(config, "/workspace")
    elif launch == "uv":
        expected_project_dir = f"/toolathlon/local_servers/{expected['server_subdir']}"
        assert "--directory" in config.args
        assert_arg_contains_path(config, expected_project_dir)
        assert "run" in config.args
        assert expected["entrypoint"] in config.args
    elif launch == "python_or_uv":
        assert_python_server_launch(
            config,
            server_subdir=expected["server_subdir"],
            fallback_entrypoint=expected["fallback_entrypoint"],
        )
    else:
        raise AssertionError(f"Unknown launch mode: {launch}")

    for key, value in expected["env_subset"].items():
        assert config.env[key] == value
