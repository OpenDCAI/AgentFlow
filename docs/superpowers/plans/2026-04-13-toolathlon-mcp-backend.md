# Toolathlon MCP Backend Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Toolathlon-GYM MCP support to AgentFlow with one new `mcp` backend, globally static MCP tool schemas, and no behavior change for native environments.

**Architecture:** Keep AgentFlow's current split between static prompt-time tool schemas and runtime backend loading. Implement a lightweight local MCP stdio client plus a single `MCPBackend` that registers bridge tools like `mcp:filesystem.list_directory`, manages task-aware session setup, and dispatches tool calls to enabled Toolathlon-GYM MCP servers.

**Tech Stack:** Python 3.10, FastAPI sandbox server, pytest, JSON/YAML config loading, subprocess-based stdio JSON-RPC MCP clients

---

**Known baseline:** In this worktree, `pytest` currently has 3 unrelated failures in rollout config/integration tests. Use the targeted test commands below while implementing this feature; do not block MCP work on fixing those existing failures.

## File Map

### New files

- `sandbox/tool_schemas/mcp_tool_manifest.json`
  Static snapshot of Toolathlon-GYM MCP tools and their parameter metadata. This is the prompt-time source of truth for MCP tool visibility.
- `sandbox/tool_schemas/mcp_tools.py`
  Loads the MCP manifest and exposes `get_mcp_tool_schemas()`.
- `sandbox/server/backends/resources/mcp_client.py`
  Lightweight stdio MCP client plus Toolathlon-GYM YAML resolution helpers. It should load server YAMLs from `<toolathlon_root>/configs/mcp_servers` and resolve local server paths against `<toolathlon_root>/local_servers`.
- `sandbox/server/backends/resources/mcp.py`
  `MCPBackend` runtime orchestration: workspace setup, optional task preprocessing, MCP client lifecycle, bridge-tool registration, and tool dispatch.
- `sandbox/tests/test_mcp_tool_schemas.py`
  Static schema and wildcard/filtering tests for MCP tools.
- `sandbox/tests/test_mcp_client.py`
  Unit tests for YAML resolution, env override behavior, and MCP stdio client protocol flow.
- `sandbox/tests/test_mcp_backend.py`
  Unit tests for backend registration, session setup, workspace behavior, and dispatch/error paths.
- `configs/sandbox-server/mcp_config.json`
  MCP sandbox config template for AgentFlow.

### Modified files

- `sandbox/tool_schemas/__init__.py`
  Merge MCP schemas into the static tool catalog and extend wildcard handling to support per-server patterns like `mcp:filesystem.*`.
- `sandbox/server/backends/resources/__init__.py`
  Export `MCPBackend` for consistency with existing resource backends.

### Intentionally unchanged files

- `rollout/core/runner.py`
- `synthesis/core/sampler.py`
- `sandbox/server/config_loader.py`

These already support the needed behavior once MCP schemas are globally registered and `mcp` is added as a normal backend resource.

**Implementation boundary:** keep the first version intentionally narrow. Toolathlon-GYM's checked-in MCP YAMLs currently use `type: stdio`, `name`, `params`, `client_session_timeout_seconds`, and `cache_tools_list`. Support `type: stdio` plus the fields needed to launch the process; reject unknown transport types early, and ignore `cache_tools_list` at runtime because prompt-time tool visibility comes from the static manifest instead of live MCP introspection.

## Chunk 1: Static MCP Tool Catalog

### Task 1: Add MCP static schema catalog and wildcard support

**Files:**
- Create: `sandbox/tool_schemas/mcp_tool_manifest.json`
- Create: `sandbox/tool_schemas/mcp_tools.py`
- Modify: `sandbox/tool_schemas/__init__.py`
- Test: `sandbox/tests/test_mcp_tool_schemas.py`

- [ ] **Step 1: Write the failing schema tests**

```python
from sandbox.tool_schemas import get_tool_schemas, get_all_tool_names


def test_mcp_schemas_are_globally_visible():
    names = get_all_tool_names()
    assert "mcp:filesystem.list_directory" in names
    assert "mcp:snowflake.list_databases" in names


def test_mcp_per_server_wildcard_filtering():
    schemas = get_tool_schemas(["mcp:filesystem.*"])
    names = [s["name"] for s in schemas]
    assert "mcp:filesystem.list_directory" in names
    assert all(name.startswith("mcp:filesystem.") for name in names)


def test_mcp_specific_tool_filtering():
    schemas = get_tool_schemas(["mcp:terminal.run_command"])
    assert [s["name"] for s in schemas] == ["mcp:terminal.run_command"]
```

- [ ] **Step 2: Run the schema tests to verify they fail**

Run:

```bash
pytest sandbox/tests/test_mcp_tool_schemas.py -v
```

Expected: FAIL because `mcp_tools.py` and the manifest do not exist yet, or because `get_tool_schemas()` does not include MCP schemas and does not understand `mcp:filesystem.*`.

- [ ] **Step 3: Add the static MCP manifest and loader**

Use this manifest structure:

```json
[
  {
    "name": "mcp:filesystem.list_directory",
    "description": "List files and directories in a workspace path.",
    "parameters": [
      {"name": "path", "type": "string", "description": "Directory path", "required": true}
    ],
    "server": "filesystem",
    "tool": "list_directory"
  }
]
```

Implement the loader like this:

```python
import json
from pathlib import Path
from typing import Any, Dict, List


_MANIFEST_PATH = Path(__file__).with_name("mcp_tool_manifest.json")


def get_mcp_tool_schemas() -> List[Dict[str, Any]]:
    with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
```

Update `sandbox/tool_schemas/__init__.py` to:

- import `get_mcp_tool_schemas`
- append MCP schemas to `all_schemas`
- support wildcard patterns ending in `.*` in addition to the existing `:*`, `_ *`, and `-*` variants

Use Toolathlon-GYM's MCP `tools/list` output or checked YAML/server definitions as the source of truth while building the manifest. The checked-in manifest must cover all 25 supported MCP servers, not just the sample tools above.

- [ ] **Step 4: Run the schema tests to verify they pass**

Run:

```bash
pytest sandbox/tests/test_mcp_tool_schemas.py sandbox/tests/test_tool_schemas.py -v
```

Expected: PASS for the new MCP-specific tests and no regression in existing static schema tests.

- [ ] **Step 5: Commit the static catalog work**

```bash
git add sandbox/tool_schemas/mcp_tool_manifest.json \
        sandbox/tool_schemas/mcp_tools.py \
        sandbox/tool_schemas/__init__.py \
        sandbox/tests/test_mcp_tool_schemas.py
git commit -m "feat: add static toolathlon mcp tool catalog"
```

## Chunk 2: Lightweight MCP Client Infrastructure

### Task 2: Add a local stdio MCP client and Toolathlon YAML resolver

**Files:**
- Create: `sandbox/server/backends/resources/mcp_client.py`
- Test: `sandbox/tests/test_mcp_client.py`

- [ ] **Step 1: Write the failing client/resolver tests**

```python
def test_resolve_toolathlon_placeholders(tmp_path):
    resolved = resolve_mcp_value(
        "${local_servers_paths}/filesystem/dist/index.js",
        local_servers_path="/opt/toolathlon/local_servers",
        agent_workspace=str(tmp_path / "workspace"),
        task_dir=str(tmp_path / "task"),
    )
    assert resolved == "/opt/toolathlon/local_servers/filesystem/dist/index.js"


def test_pg_env_bridge_prefers_libpq_overrides():
    env = build_server_env(
        yaml_env={"PG_HOST": "postgres", "PG_PORT": "5432"},
        process_env={"PGHOST": "toolathlon_pg", "PGPORT": "15432"},
    )
    assert env["PG_HOST"] == "toolathlon_pg"
    assert env["PG_PORT"] == "15432"


def test_load_mcp_process_config_rejects_non_stdio_type(tmp_path):
    ...
    assert "stdio" in str(exc_info.value)


@pytest.mark.asyncio
async def test_stdio_client_initialize_and_list_tools(monkeypatch):
    client = MCPStdioClient(config=process_config)
    # fake subprocess/stdout interactions here
    assert await client.list_tools() == [{"name": "list_directory"}]
```

- [ ] **Step 2: Run the client tests to verify they fail**

Run:

```bash
pytest sandbox/tests/test_mcp_client.py -v
```

Expected: FAIL because `mcp_client.py` does not exist yet.

- [ ] **Step 3: Implement the resolver and stdio MCP client**

Implement focused units:

```python
@dataclass
class MCPProcessConfig:
    name: str
    command: str
    args: list[str]
    env: dict[str, str]
    cwd: str
    timeout_seconds: float


def resolve_mcp_value(value: Any, *, local_servers_path: str, agent_workspace: str, task_dir: str) -> Any:
    ...


def load_mcp_process_config(... ) -> MCPProcessConfig:
    ...


class MCPStdioClient:
    async def start(self) -> None: ...
    async def initialize(self) -> None: ...
    async def list_tools(self) -> list[dict]: ...
    async def call_tool(self, tool_name: str, arguments: dict) -> dict: ...
    async def close(self) -> None: ...
```

Required behavior:

- resolve `${local_servers_paths}`, `${agent_workspace}`, and `${task_dir}`
- derive `config_dir` as `<toolathlon_root>/configs/mcp_servers` and `local_servers_path` as `<toolathlon_root>/local_servers`
- merge YAML env plus process env
- bridge `PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD` into `PG_HOST/PG_PORT/PG_DATABASE/PG_USER/PG_PASSWORD`
- read `client_session_timeout_seconds` into `MCPProcessConfig.timeout_seconds`
- require `type == "stdio"` for Toolathlon-GYM YAMLs in this first version
- ignore `cache_tools_list` because static schemas are already provided by `mcp_tool_manifest.json`
- support stdio JSON-RPC methods:
  - `initialize`
  - `tools/list`
  - `tools/call`

- [ ] **Step 4: Run the client tests to verify they pass**

Run:

```bash
pytest sandbox/tests/test_mcp_client.py -v
```

Expected: PASS for placeholder resolution, env bridging, and mocked protocol flow.

- [ ] **Step 5: Commit the client infrastructure**

```bash
git add sandbox/server/backends/resources/mcp_client.py \
        sandbox/tests/test_mcp_client.py
git commit -m "feat: add lightweight mcp stdio client"
```

## Chunk 3: MCP Backend Runtime Wiring

### Task 3: Register MCP bridge tools and create session-scoped runtime state

**Files:**
- Create: `sandbox/server/backends/resources/mcp.py`
- Modify: `sandbox/server/backends/resources/__init__.py`
- Test: `sandbox/tests/test_mcp_backend.py`

- [ ] **Step 1: Write the failing backend registration tests**

```python
def test_bind_server_registers_manifest_tools(fake_server):
    backend = MCPBackend(config=backend_config)
    backend.bind_server(fake_server)
    assert "mcp:filesystem.list_directory" in fake_server._tools
    assert "mcp:terminal.run_command" in fake_server._tools


def test_initialize_creates_worker_workspace(tmp_path, monkeypatch):
    backend = MCPBackend(config=backend_config_with_workspace(tmp_path))
    session = asyncio.run(
        backend.initialize(
            "runner_123",
            {"task_dir": "/tmp/task", "copy_initial_workspace": False, "run_preprocess": False},
        )
    )
    assert session["workspace"].endswith("runner_123")
```

- [ ] **Step 2: Run the backend registration tests to verify they fail**

Run:

```bash
pytest sandbox/tests/test_mcp_backend.py::test_bind_server_registers_manifest_tools \
       sandbox/tests/test_mcp_backend.py::test_initialize_creates_worker_workspace -v
```

Expected: FAIL because `MCPBackend` does not exist yet.

- [ ] **Step 3: Implement `MCPBackend` registration and lifecycle skeleton**

Implement these responsibilities:

```python
class MCPBackend(Backend):
    name = "mcp"

    def bind_server(self, server) -> None:
        super().bind_server(server)
        for schema in get_mcp_tool_schemas():
            full_name = schema["name"]
            server.register_tool(full_name, self._make_bridge_tool(full_name), resource_type="mcp")

    async def initialize(self, worker_id: str, config: dict) -> dict:
        workspace = self._prepare_workspace(worker_id)
        task_context = self._resolve_task_context(config)
        clients = await self._start_enabled_clients(workspace, task_context)
        return {"workspace": workspace, "task_context": task_context, "clients": clients}

    async def cleanup(self, worker_id: str, session_info: dict) -> None:
        await self._close_clients(session_info["data"]["clients"])
```

Also export `MCPBackend` from `sandbox/server/backends/resources/__init__.py`.

- [ ] **Step 4: Run the backend registration tests to verify they pass**

Run:

```bash
pytest sandbox/tests/test_mcp_backend.py::test_bind_server_registers_manifest_tools \
       sandbox/tests/test_mcp_backend.py::test_initialize_creates_worker_workspace -v
```

Expected: PASS for bridge registration and worker-scoped workspace creation.

- [ ] **Step 5: Commit the backend skeleton**

```bash
git add sandbox/server/backends/resources/mcp.py \
        sandbox/server/backends/resources/__init__.py \
        sandbox/tests/test_mcp_backend.py
git commit -m "feat: add mcp backend skeleton"
```

### Task 4: Implement task-aware setup, dispatch, and runtime error paths

**Files:**
- Modify: `sandbox/server/backends/resources/mcp.py`
- Test: `sandbox/tests/test_mcp_backend.py`

- [ ] **Step 1: Write the failing dispatch and task-context tests**

```python
def test_initialize_copies_initial_workspace(tmp_path, monkeypatch):
    ...
    assert (workspace / "seed.txt").exists()


def test_initialize_runs_preprocess_when_requested(monkeypatch):
    ...
    assert "--agent_workspace" in recorded_command
    assert "--launch_time \\\"2026-03-07 10:00:00\\\"" in recorded_command


def test_bridge_tool_dispatches_to_matching_server_client():
    result = asyncio.run(tool_handler(path="."))
    assert result["code"] == 0
    assert result["data"]["content"] == [{"type": "text", "text": "ok"}]


def test_bridge_tool_returns_clear_error_for_disabled_server():
    response = asyncio.run(tool_handler(path="."))
    assert response["code"] != 0
    assert "not enabled" in response["message"]
```

- [ ] **Step 2: Run the new backend tests to verify they fail**

Run:

```bash
pytest sandbox/tests/test_mcp_backend.py -k "initial_workspace or preprocess or dispatch or disabled_server" -v
```

Expected: FAIL because the skeleton backend does not yet perform task setup or tool dispatch.

- [ ] **Step 3: Implement task setup and bridge dispatch**

Add focused helpers inside `mcp.py`:

```python
def _prepare_workspace(self, worker_id: str) -> Path: ...
def _copy_initial_workspace(self, source_dir: Path, target_dir: Path) -> None: ...
def _run_preprocess(self, task_dir: Path, workspace: Path) -> None: ...
def _resolve_enabled_servers(self) -> list[str]: ...
def _make_bridge_tool(self, full_name: str): ...
async def _dispatch(self, full_name: str, session_info: dict, params: dict) -> dict: ...
```

Required behavior:

- `task_dir` is session-scoped, not global
- `copy_initial_workspace` copies task files into the session workspace
- `run_preprocess` runs the task's preprocess entry when requested
- accept optional `launch_time` in session config and mirror Toolathlon-GYM's current preprocess invocation by appending `--agent_workspace` plus a cleaned `--launch_time` argument
- bridge tool parses `mcp:{server}.{tool}`
- successful bridge calls wrap MCP payloads with `build_success_response(...)` instead of returning raw MCP JSON
- runtime errors are clear when:
  - server is not enabled
  - client is missing
  - MCP `tools/call` fails

- [ ] **Step 4: Run the backend tests to verify they pass**

Run:

```bash
pytest sandbox/tests/test_mcp_backend.py -v
```

Expected: PASS for workspace setup, optional preprocess, dispatch, and disabled-server errors.

- [ ] **Step 5: Commit the runtime behavior**

```bash
git add sandbox/server/backends/resources/mcp.py \
        sandbox/tests/test_mcp_backend.py
git commit -m "feat: implement mcp backend runtime dispatch"
```

## Chunk 4: Config Template and Verification

### Task 5: Add the MCP sandbox config template and run targeted verification

**Files:**
- Create: `configs/sandbox-server/mcp_config.json`
- Test: `sandbox/tests/test_mcp_backend.py`

- [ ] **Step 1: Write a failing config-template test**

```python
from sandbox.server.config_loader import ConfigLoader


def test_mcp_config_template_parses():
    loader = ConfigLoader()
    config = loader.load("configs/sandbox-server/mcp_config.json")
    assert "mcp" in config.resources
    assert config.resources["mcp"].backend_class == "sandbox.server.backends.resources.mcp.MCPBackend"
```

- [ ] **Step 2: Run the config-template test to verify it fails**

Run:

```bash
pytest sandbox/tests/test_mcp_backend.py::test_mcp_config_template_parses -v
```

Expected: FAIL because the config template does not exist yet.

- [ ] **Step 3: Add `configs/sandbox-server/mcp_config.json` with env-driven defaults**

Use a template shaped like this:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "session_ttl": 600
  },
  "resources": {
    "mcp": {
      "enabled": true,
      "description": "Toolathlon-GYM MCP backend",
      "backend_class": "sandbox.server.backends.resources.mcp.MCPBackend",
      "config": {
        "toolathlon_root": "${TOOLATHLON_ROOT}",
        "enabled_mcp_servers": ["filesystem", "terminal", "snowflake"],
        "workspace_root": "${TOOLATHLON_WORKSPACE_ROOT:-/tmp/agentflow_mcp}",
        "env_overrides": {
          "PGHOST": "${PGHOST:-toolathlon_pg}",
          "PGPORT": "${PGPORT:-5432}",
          "PGUSER": "${PGUSER:-eigent}",
          "PGPASSWORD": "${PGPASSWORD:-camel}",
          "PGDATABASE": "${PGDATABASE:-toolathlon_gym}"
        }
      }
    }
  },
  "warmup": {
    "enabled": true,
    "resources": ["mcp"]
  }
}
```

- [ ] **Step 4: Run targeted verification**

Run:

```bash
pytest sandbox/tests/test_mcp_tool_schemas.py \
       sandbox/tests/test_mcp_client.py \
       sandbox/tests/test_mcp_backend.py -v
python -m json.tool configs/sandbox-server/mcp_config.json >/dev/null
```

Expected:

- all new MCP tests PASS
- JSON validation exits 0

Optional manual smoke, only if Toolathlon-GYM runtime dependencies are available:

```bash
python - <<'PY'
import asyncio
from sandbox import Sandbox

async def main():
    sandbox = Sandbox(
        server_url="http://127.0.0.1:18890",
        worker_id="mcp_smoke",
        auto_start_server=True,
        server_config_path="configs/sandbox-server/mcp_config.json",
        warmup_resources=["mcp"],
    )
    await sandbox.start()
    try:
        await sandbox.create_session({
            "mcp": {
                "task_dir": "/home/a1/sdb/dxd/toolathlon_gym/tasks/finalpool/howtocook-event-menu-ppt",
                "copy_initial_workspace": False,
                "run_preprocess": False,
                "launch_time": "2026-03-07 10:00:00"
            }
        })
        tools = await sandbox.get_tools()
        assert any(t["full_name"] == "mcp:filesystem.list_directory" for t in tools)
        print("MCP smoke check passed")
    finally:
        await sandbox.close()

asyncio.run(main())
PY
```

Expected: `MCP smoke check passed`

- [ ] **Step 5: Commit the config template and verification changes**

```bash
git add configs/sandbox-server/mcp_config.json \
        sandbox/tests/test_mcp_backend.py
git commit -m "feat: add mcp sandbox config template"
```

## Final Verification

- [ ] Run the full MCP-targeted verification suite:

```bash
pytest sandbox/tests/test_tool_schemas.py \
       sandbox/tests/test_mcp_tool_schemas.py \
       sandbox/tests/test_mcp_client.py \
       sandbox/tests/test_mcp_backend.py -v
```

Expected: PASS for all MCP-related tests.

- [ ] Record the known unrelated baseline failures without fixing them in this feature:

```bash
pytest -q || true
```

Expected: the same existing unrelated rollout failures remain unless something outside MCP changed.

- [ ] Prepare the implementation branch for review:

```bash
git status
git log --oneline --decorate -5
```

Expected: clean working tree and a short series of focused MCP commits.
