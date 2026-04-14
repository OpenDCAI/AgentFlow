# Toolathlon-GYM MCP Testing Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a real MCP smoke suite for AgentFlow that validates Toolathlon-GYM integration at both the server layer and the six-domain workflow layer.

**Architecture:** Keep AgentFlow's existing MCP unit tests as the first regression gate, then add an opt-in real-environment smoke layer that uses `ConfigLoader.load_from_dict(...)`, `HTTPServiceServer`, `ResourceRouter`, and `ToolExecutor` directly without booting FastAPI. Put all shared environment discovery, A/B server classification, and case matrices in controller-owned helper modules; keep the executable pytest modules worker-safe and thin.

**Tech Stack:** Python 3.10, pytest, asyncio/anyio, AgentFlow sandbox server, Toolathlon-GYM local MCP servers, Dockerized PostgreSQL, stdio MCP subprocesses

---

**Known baseline in this worktree:** `pytest -q` currently reports `84 passed, 2 skipped`.

## File Map

### New files

- `sandbox/tests/mcp_real_env.py`
  Controller-owned shared environment contract. Discovers `toolathlon_gym`, builds controller env overrides, creates configured `HTTPServiceServer` instances, executes tools through `server._executor.execute(...)`, and guarantees per-worker cleanup.
- `sandbox/tests/mcp_real_cases.py`
  Controller-owned case registry. Holds the authoritative `ALL_MCP_SERVERS` list, the `A`/`B` partition, the per-server smoke matrix, and the six domain smoke scenarios.
- `sandbox/tests/test_mcp_real_server_smokes.py`
  Worker-safe server-layer real smoke tests: controller classification sanity, `filesystem`+`terminal` bootstrap smoke, per-server A/B single-server smokes, and the serial all-enabled startup test.
- `sandbox/tests/test_mcp_real_domain_smokes.py`
  Worker-safe domain-layer real smoke tests for `canvas`, `snowflake`, `woocommerce`, `yahoo_finance`, `youtube`, and `train`.

### Existing files that may need modification if real smokes expose runtime gaps

- `sandbox/server/backends/resources/mcp.py`
  Real-session startup, client lifecycle, cleanup, and bridge dispatch.
- `sandbox/server/backends/resources/mcp_client.py`
  YAML resolution, process env construction, stdio subprocess startup, timeout behavior.
- `sandbox/tests/test_mcp_backend.py`
  Regression tests for any backend bug fixed while making the real smoke suite pass.
- `sandbox/tests/test_mcp_client.py`
  Regression tests for any YAML/env/runtime bug fixed while making the real smoke suite pass.

### Intentionally unchanged files

- `sandbox/tests/test_mcp_tool_schemas.py`
- `sandbox/tool_schemas/mcp_tool_manifest.json`
- `rollout/tests/*`
- `sandbox/tests/test_tool_schemas.py`

This plan adds runtime validation, not another schema catalog pass.

## Ownership Map

### Controller-owned artifacts

- `sandbox/tests/mcp_real_env.py`
- `sandbox/tests/mcp_real_cases.py`
- shared environment variables and runtime policy
- the authoritative `A`/`B` classification
- all-servers startup orchestration

### Worker-safe artifacts

- `sandbox/tests/test_mcp_real_server_smokes.py`
- `sandbox/tests/test_mcp_real_domain_smokes.py`
- server-specific fixes in `sandbox/server/backends/resources/mcp.py`
- server-specific fixes in `sandbox/server/backends/resources/mcp_client.py`
- matching regression tests in `sandbox/tests/test_mcp_backend.py`
- matching regression tests in `sandbox/tests/test_mcp_client.py`

Workers must not change controller-owned environment policy or reclassify servers from `B` to `A` inside their own slice. If a failing case points to shared environment policy, hand ownership back to the controller chunk.

## Shared Environment Contract

The real smoke suite is opt-in. The default `pytest -q` baseline must stay at `84 passed, 2 skipped` and must not start real MCP subprocesses.

The controller enables the real suite by exporting:

```bash
export AGENTFLOW_RUN_MCP_REAL=1
export TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym
export AGENTFLOW_MCP_PGHOST=127.0.0.1
export AGENTFLOW_MCP_PGPORT=5432
export AGENTFLOW_MCP_PGUSER=eigent
export AGENTFLOW_MCP_PGPASSWORD=camel
export AGENTFLOW_MCP_PGDATABASE=toolathlon_gym
export AGENTFLOW_MCP_CANVAS_DOMAIN=localhost:8080
export AGENTFLOW_MCP_WOOCOMMERCE_SITE_URL=http://localhost:8081
```

If the suite runs inside a Toolathlon container on `toolathlon_net`, the controller may override `AGENTFLOW_MCP_PGHOST=toolathlon_pg` instead.

Shared environment bootstrap happens once before worker execution:

```bash
cd /home/a1/sdb/dxd/toolathlon_gym
docker compose up -d postgres
docker inspect --format '{{.State.Health.Status}}' toolathlon_pg
```

Expected: the second command prints `healthy`.

Real-test helper behavior:

- If `AGENTFLOW_RUN_MCP_REAL` is unset, the real smoke modules skip at collection with one explicit reason.
- If `AGENTFLOW_RUN_MCP_REAL=1` but a required prerequisite is missing, the helper fails fast with an actionable error instead of silently passing or skipping.
- Every case gets a unique `worker_id`, unique workspace root, and `finally` cleanup via `await server.resource_router.destroy_worker_sessions(worker_id)`.

## Required Server Coverage

`sandbox/tests/mcp_real_cases.py` must enumerate all 25 Toolathlon-GYM MCP servers:

- `arxiv-latex`
- `arxiv_local`
- `canvas`
- `emails`
- `excel`
- `fetch`
- `filesystem`
- `google_calendar`
- `google_forms`
- `google_sheet`
- `howtocook`
- `memory`
- `notion`
- `pdf-tools`
- `playwright_with_chunk`
- `pptx`
- `rail_12306`
- `scholarly`
- `snowflake`
- `terminal`
- `woocommerce`
- `word`
- `yahoo-finance`
- `youtube`
- `youtube-transcript`

Initial classification is intentionally conservative:

- `A`: `filesystem`, `terminal`
- `B`: every other server above

Do not promote a server from `B` to `A` in this first pass unless the controller explicitly proves it is parallel-safe.

## Required Domain Coverage

`sandbox/tests/mcp_real_cases.py` must define exactly six domain smoke scenarios:

- `canvas`
- `snowflake`
- `woocommerce`
- `yahoo_finance`
- `youtube`
- `train`

Each domain scenario must enable the domain server plus `filesystem`, perform one deterministic read, write one compact artifact into the per-test workspace, then verify the artifact exists and is non-empty.

## Chunk 1: Controller Scaffold

### Task 1: Add controller-owned helper modules and the `filesystem` + `terminal` bootstrap smoke

**Files:**
- Create: `sandbox/tests/mcp_real_env.py`
- Create: `sandbox/tests/mcp_real_cases.py`
- Create: `sandbox/tests/test_mcp_real_server_smokes.py`

- [ ] **Step 1: Write the failing bootstrap tests**

Add these first tests to `sandbox/tests/test_mcp_real_server_smokes.py`:

```python
import pytest

from sandbox.server.backends.error_codes import ErrorCode
from sandbox.tests.mcp_real_cases import (
    ALL_MCP_SERVERS,
    FILESYSTEM_TERMINAL_BOOTSTRAP_CASE,
    PARALLEL_SAFE_MCP_SERVERS,
    SERIAL_ONLY_MCP_SERVERS,
)
from sandbox.tests.mcp_real_env import (
    build_real_mcp_server,
    cleanup_worker,
    execute_tool,
    require_real_mcp_enabled,
)


pytestmark = require_real_mcp_enabled()


def test_server_partition_is_complete():
    assert set(ALL_MCP_SERVERS) == set(PARALLEL_SAFE_MCP_SERVERS) | set(SERIAL_ONLY_MCP_SERVERS)
    assert set(PARALLEL_SAFE_MCP_SERVERS).isdisjoint(SERIAL_ONLY_MCP_SERVERS)


@pytest.mark.anyio
async def test_filesystem_terminal_shared_session_smoke(tmp_path):
    server = build_real_mcp_server(
        enabled_mcp_servers=FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["enabled_mcp_servers"],
        workspace_root=tmp_path / "workspaces",
    )
    worker_id = "filesystem-terminal-bootstrap"
    try:
        write_result = await execute_tool(
            server,
            worker_id,
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["write_action"],
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["write_params"],
        )
        assert write_result["code"] == ErrorCode.SUCCESS

        run_result = await execute_tool(
            server,
            worker_id,
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["verify_action"],
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["verify_params"],
        )
        assert run_result["code"] == ErrorCode.SUCCESS
        assert FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["expected_signal"] in str(run_result["data"])
    finally:
        await cleanup_worker(server, worker_id)
```

- [ ] **Step 2: Run the bootstrap tests to verify they fail**

Run:

```bash
pytest sandbox/tests/test_mcp_real_server_smokes.py -k 'partition or filesystem_terminal_shared_session_smoke' -v
```

Expected: FAIL because the helper modules do not exist yet.

- [ ] **Step 3: Implement controller-owned helpers with explicit environment policy**

In `sandbox/tests/mcp_real_env.py`, implement:

```python
def require_real_mcp_enabled():
    """Return a module-level pytest mark that skips unless AGENTFLOW_RUN_MCP_REAL=1."""
    ...
def discover_toolathlon_root() -> Path: ...
def controller_env_overrides() -> dict[str, str]:
    return {
        "PGHOST": os.environ["AGENTFLOW_MCP_PGHOST"],
        "PGPORT": os.environ["AGENTFLOW_MCP_PGPORT"],
        "PGUSER": os.environ["AGENTFLOW_MCP_PGUSER"],
        "PGPASSWORD": os.environ["AGENTFLOW_MCP_PGPASSWORD"],
        "PGDATABASE": os.environ["AGENTFLOW_MCP_PGDATABASE"],
        "CANVAS_DOMAIN": os.getenv("AGENTFLOW_MCP_CANVAS_DOMAIN", "localhost:8080"),
        "WORDPRESS_SITE_URL": os.getenv(
            "AGENTFLOW_MCP_WOOCOMMERCE_SITE_URL",
            "http://localhost:8081",
        ),
    }


def require_controller_prereqs() -> None:
    """
    Fail fast when a real run is explicitly enabled but the controller forgot:
    - AGENTFLOW_RUN_MCP_REAL=1
    - a resolvable TOOLATHLON_GYM_ROOT (or a known fallback sibling path)
    - AGENTFLOW_MCP_PGHOST / AGENTFLOW_MCP_PGPORT / AGENTFLOW_MCP_PGUSER /
      AGENTFLOW_MCP_PGPASSWORD / AGENTFLOW_MCP_PGDATABASE
    - local runtimes required by Toolathlon YAMLs, at minimum `node` and `uv`
    - a valid Toolathlon config dir at <toolathlon_root>/configs/mcp_servers
    """
    ...


def build_real_mcp_server(*, enabled_mcp_servers: list[str], workspace_root: Path):
    require_controller_prereqs()
    loader = ConfigLoader()
    loader.load_from_dict(
        {
            "server": {"title": "MCP smoke", "session_ttl": 300},
            "resources": {
                "mcp": {
                    "enabled": True,
                    "backend_class": "sandbox.server.backends.resources.mcp.MCPBackend",
                    "config": {
                        "toolathlon_root": str(discover_toolathlon_root()),
                        "enabled_mcp_servers": enabled_mcp_servers,
                        "workspace_root": str(workspace_root),
                        "env_overrides": controller_env_overrides(),
                    },
                }
            },
        }
    )
    return loader.create_server(host="127.0.0.1", port=0)


async def execute_tool(server, worker_id: str, action: str, params: dict) -> dict:
    return await server._executor.execute(action=action, params=params, worker_id=worker_id)


async def cleanup_worker(server, worker_id: str) -> None:
    await server.resource_router.destroy_worker_sessions(worker_id)
```

In `sandbox/tests/mcp_real_cases.py`, start with:

```python
ALL_MCP_SERVERS = (
    "arxiv-latex",
    "arxiv_local",
    "canvas",
    "emails",
    "excel",
    "fetch",
    "filesystem",
    "google_calendar",
    "google_forms",
    "google_sheet",
    "howtocook",
    "memory",
    "notion",
    "pdf-tools",
    "playwright_with_chunk",
    "pptx",
    "rail_12306",
    "scholarly",
    "snowflake",
    "terminal",
    "woocommerce",
    "word",
    "yahoo-finance",
    "youtube",
    "youtube-transcript",
)
PARALLEL_SAFE_MCP_SERVERS = ("filesystem", "terminal")
SERIAL_ONLY_MCP_SERVERS = tuple(
    name for name in ALL_MCP_SERVERS if name not in PARALLEL_SAFE_MCP_SERVERS
)
FILESYSTEM_TERMINAL_BOOTSTRAP_CASE = {
    "enabled_mcp_servers": ["filesystem", "terminal"],
    "write_action": "mcp:filesystem.write_file",
    "write_params": {"path": "hello.txt", "content": "bootstrap\\n"},
    "verify_action": "mcp:terminal.run_command",
    "verify_params": {"command": "cat hello.txt"},
    "expected_signal": "bootstrap",
}
```

The required call site is `pytestmark = require_real_mcp_enabled()` at the top of each real-smoke test module. Keep the fail-fast controller preflight inside `build_real_mcp_server(...)` so the default baseline skips cleanly, but an explicitly enabled real run errors immediately when the shared environment is not prepared.

- [ ] **Step 4: Run the bootstrap tests with the controller environment enabled**

Run:

```bash
AGENTFLOW_RUN_MCP_REAL=1 \
TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym \
AGENTFLOW_MCP_PGHOST=127.0.0.1 \
AGENTFLOW_MCP_PGPORT=5432 \
AGENTFLOW_MCP_PGUSER=eigent \
AGENTFLOW_MCP_PGPASSWORD=camel \
AGENTFLOW_MCP_PGDATABASE=toolathlon_gym \
pytest sandbox/tests/test_mcp_real_server_smokes.py -k 'partition or filesystem_terminal_shared_session_smoke' -v
```

Expected: PASS for the partition test and PASS for the bootstrap smoke after `docker compose up -d postgres`; if the controller forgot to prepare the environment, FAIL with a direct preflight message.

- [ ] **Step 5: Commit the controller scaffold**

```bash
git add sandbox/tests/mcp_real_env.py \
        sandbox/tests/mcp_real_cases.py \
        sandbox/tests/test_mcp_real_server_smokes.py
git commit -m "test: add real mcp smoke scaffolding"
```

## Chunk 2: Server-Layer Smokes

### Task 2: Expand the server-layer suite to the full A/B matrix and the serial all-enabled startup test

**Files:**
- Modify: `sandbox/tests/mcp_real_cases.py`
- Modify: `sandbox/tests/test_mcp_real_server_smokes.py`
- Modify if needed: `sandbox/server/backends/resources/mcp.py`
- Modify if needed: `sandbox/server/backends/resources/mcp_client.py`
- Test if needed: `sandbox/tests/test_mcp_backend.py`
- Test if needed: `sandbox/tests/test_mcp_client.py`

- [ ] **Step 1: Write the failing parametrized server-layer tests**

Extend `sandbox/tests/test_mcp_real_server_smokes.py` with:

```python
@pytest.mark.anyio
@pytest.mark.parametrize("server_name", PARALLEL_SAFE_MCP_SERVERS)
async def test_single_server_parallel_safe_smoke(server_name, tmp_path):
    await assert_single_server_smoke(server_name, tmp_path)


@pytest.mark.anyio
@pytest.mark.parametrize("server_name", SERIAL_ONLY_MCP_SERVERS)
async def test_single_server_serial_smoke(server_name, tmp_path):
    await assert_single_server_smoke(server_name, tmp_path)


@pytest.mark.anyio
async def test_all_enabled_mcp_servers_startup_serial(tmp_path):
    server = build_real_mcp_server(
        enabled_mcp_servers=list(ALL_MCP_SERVERS),
        workspace_root=tmp_path / "all-enabled",
    )
    worker_id = "all-enabled-startup"
    try:
        session = await server.resource_router.get_or_create_session(worker_id, "mcp")
        clients = session["data"]["clients"]
        assert set(clients) == set(ALL_MCP_SERVERS)
    finally:
        await cleanup_worker(server, worker_id)
```

- [ ] **Step 2: Run the new server-layer tests to verify they fail**

Run:

```bash
AGENTFLOW_RUN_MCP_REAL=1 \
TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym \
pytest sandbox/tests/test_mcp_real_server_smokes.py -k 'single_server_parallel_safe_smoke or single_server_serial_smoke or all_enabled_mcp_servers_startup_serial' -v
```

Expected: FAIL because `assert_single_server_smoke(...)` and the full smoke registry are not implemented yet.

- [ ] **Step 3: Populate the authoritative server smoke matrix**

In `sandbox/tests/mcp_real_cases.py`, add a `SERVER_SMOKE_CASES` dictionary that covers all 25 servers. Use `/home/a1/sdb/dxd/toolathlon_gym/test_mcp_servers.py::SMOKE_CALLS` as the starting point, then translate each entry to AgentFlow action names like `mcp:<server>.<tool>`.

Minimum required shape:

```python
SERVER_SMOKE_CASES = {
    "filesystem": {
        "action": "mcp:filesystem.list_directory",
        "params": {"path": "."},
        "expected_signal": ".",
    },
    "terminal": {
        "action": "mcp:terminal.run_command",
        "params": {"command": "pwd"},
        "expected_signal": "workspaces",
    },
}
```

Add one entry for every server above, including:

- `canvas` -> `mcp:canvas.canvas_list_courses`
- `snowflake` -> `mcp:snowflake.read_query`
- `woocommerce` -> `mcp:woocommerce.woo_customers_list`
- `yahoo-finance` -> `mcp:yahoo-finance.get_stock_info`
- `youtube` -> `mcp:youtube.videos_searchVideos`
- `rail_12306` -> `mcp:rail_12306.get-station-code-by-names`

In `sandbox/tests/test_mcp_real_server_smokes.py`, implement:

```python
async def assert_single_server_smoke(server_name: str, tmp_path: Path) -> None:
    case = SERVER_SMOKE_CASES[server_name]
    server = build_real_mcp_server(
        enabled_mcp_servers=[server_name],
        workspace_root=tmp_path / server_name,
    )
    worker_id = f"{server_name}-smoke"
    try:
        result = await execute_tool(server, worker_id, case["action"], case["params"])
        assert result["code"] == ErrorCode.SUCCESS
        assert case["expected_signal"] in str(result["data"])
    finally:
        await cleanup_worker(server, worker_id)
```

- [ ] **Step 4: If the new real smokes expose backend bugs, lock them with unit tests first**

Examples:

- If env overrides are not reaching real subprocesses, add a failing regression test in `sandbox/tests/test_mcp_backend.py`.
- If a real YAML shape or timeout path is mishandled, add a failing regression test in `sandbox/tests/test_mcp_client.py`.

Run the focused failing unit tests first:

```bash
pytest sandbox/tests/test_mcp_backend.py -v
pytest sandbox/tests/test_mcp_client.py -v
```

Expected: any newly added regression test fails before the source patch and passes after the patch.

- [ ] **Step 5: Run the full server-layer suite**

Run:

```bash
AGENTFLOW_RUN_MCP_REAL=1 \
TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym \
AGENTFLOW_MCP_PGHOST=127.0.0.1 \
AGENTFLOW_MCP_PGPORT=5432 \
AGENTFLOW_MCP_PGUSER=eigent \
AGENTFLOW_MCP_PGPASSWORD=camel \
AGENTFLOW_MCP_PGDATABASE=toolathlon_gym \
pytest sandbox/tests/test_mcp_real_server_smokes.py -v
```

Expected: PASS for `filesystem` and `terminal`; remaining cases either PASS or fail with clearly attributed server names. Continue fixing until the full module passes in the prepared controller environment.

- [ ] **Step 6: Commit the server-layer matrix**

```bash
git add sandbox/tests/mcp_real_cases.py \
        sandbox/tests/test_mcp_real_server_smokes.py \
        sandbox/server/backends/resources/mcp.py \
        sandbox/server/backends/resources/mcp_client.py \
        sandbox/tests/test_mcp_backend.py \
        sandbox/tests/test_mcp_client.py
git commit -m "test: add real mcp server smoke coverage"
```

## Chunk 3: Domain Smokes And Verification

### Task 3: Add six domain-layer workflow smokes and run the final verification bundle

**Files:**
- Modify: `sandbox/tests/mcp_real_env.py`
- Modify: `sandbox/tests/mcp_real_cases.py`
- Create: `sandbox/tests/test_mcp_real_domain_smokes.py`
- Modify if needed: `sandbox/server/backends/resources/mcp.py`
- Modify if needed: `sandbox/server/backends/resources/mcp_client.py`
- Test if needed: `sandbox/tests/test_mcp_backend.py`
- Test if needed: `sandbox/tests/test_mcp_client.py`

- [ ] **Step 1: Write the failing six-domain smoke tests**

Create `sandbox/tests/test_mcp_real_domain_smokes.py`:

```python
import json
from pathlib import Path

import pytest

from sandbox.server.backends.error_codes import ErrorCode
from sandbox.tests.mcp_real_cases import DOMAIN_SMOKE_CASES
from sandbox.tests.mcp_real_env import build_real_mcp_server, cleanup_worker, execute_tool


@pytest.mark.anyio
@pytest.mark.parametrize("domain_name", DOMAIN_SMOKE_CASES.keys())
async def test_domain_smoke(domain_name, tmp_path):
    case = DOMAIN_SMOKE_CASES[domain_name]
    server = build_real_mcp_server(
        enabled_mcp_servers=case["enabled_mcp_servers"],
        workspace_root=tmp_path / domain_name,
    )
    worker_id = f"{domain_name}-domain-smoke"
    try:
        read_result = await execute_tool(server, worker_id, case["read_action"], case["read_params"])
        assert read_result["code"] == ErrorCode.SUCCESS

        payload_text = json.dumps(read_result["data"], ensure_ascii=False)
        write_result = await execute_tool(
            server,
            worker_id,
            "mcp:filesystem.write_file",
            {"path": case["artifact_path"], "content": payload_text},
        )
        assert write_result["code"] == ErrorCode.SUCCESS

        verify_result = await execute_tool(
            server,
            worker_id,
            "mcp:filesystem.read_text_file",
            {"path": case["artifact_path"]},
        )
        assert verify_result["code"] == ErrorCode.SUCCESS
        assert case["expected_signal"] in str(verify_result["data"])
    finally:
        await cleanup_worker(server, worker_id)
```

- [ ] **Step 2: Run the domain smoke tests to verify they fail**

Run:

```bash
AGENTFLOW_RUN_MCP_REAL=1 \
TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym \
pytest sandbox/tests/test_mcp_real_domain_smokes.py -v
```

Expected: FAIL because `DOMAIN_SMOKE_CASES` does not exist yet.

- [ ] **Step 3: Fill in the six deterministic domain scenarios**

In `sandbox/tests/mcp_real_cases.py`, add:

```python
DOMAIN_SMOKE_CASES = {
    "canvas": {
        "enabled_mcp_servers": ["canvas", "filesystem"],
        "read_action": "mcp:canvas.canvas_list_courses",
        "read_params": {"include_ended": False},
        "artifact_path": "reports/canvas_courses.json",
        "expected_signal": "course",
    },
    "snowflake": {
        "enabled_mcp_servers": ["snowflake", "filesystem"],
        "read_action": "mcp:snowflake.read_query",
        "read_params": {
            "query": 'SELECT employee_id, department FROM sf_data."HR_ANALYTICS__PUBLIC__EMPLOYEES" LIMIT 3'
        },
        "artifact_path": "reports/snowflake_hr.json",
        "expected_signal": "employee",
    },
    "woocommerce": {
        "enabled_mcp_servers": ["woocommerce", "filesystem"],
        "read_action": "mcp:woocommerce.woo_customers_list",
        "read_params": {"perPage": 2, "page": 1},
        "artifact_path": "reports/woocommerce_customers.json",
        "expected_signal": "customer",
    },
    "yahoo_finance": {
        "enabled_mcp_servers": ["yahoo-finance", "filesystem"],
        "read_action": "mcp:yahoo-finance.get_stock_info",
        "read_params": {"ticker": "AAPL"},
        "artifact_path": "reports/yahoo_finance_aapl.json",
        "expected_signal": "AAPL",
    },
    "youtube": {
        "enabled_mcp_servers": ["youtube", "filesystem"],
        "read_action": "mcp:youtube.videos_searchVideos",
        "read_params": {"query": "toolathlon", "maxResults": 2},
        "artifact_path": "reports/youtube_search.json",
        "expected_signal": "video",
    },
    "train": {
        "enabled_mcp_servers": ["rail_12306", "filesystem"],
        "read_action": "mcp:rail_12306.get-station-code-by-names",
        "read_params": {"stationNames": "北京南|上海虹桥"},
        "artifact_path": "reports/train_station_codes.json",
        "expected_signal": "北京南",
    },
}
```

Add any domain-specific readiness checks to `sandbox/tests/mcp_real_env.py` only if a domain truly has an extra prerequisite beyond the shared controller environment.

- [ ] **Step 4: Run the domain smoke module until it passes**

Run:

```bash
AGENTFLOW_RUN_MCP_REAL=1 \
TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym \
AGENTFLOW_MCP_PGHOST=127.0.0.1 \
AGENTFLOW_MCP_PGPORT=5432 \
AGENTFLOW_MCP_PGUSER=eigent \
AGENTFLOW_MCP_PGPASSWORD=camel \
AGENTFLOW_MCP_PGDATABASE=toolathlon_gym \
AGENTFLOW_MCP_CANVAS_DOMAIN=localhost:8080 \
AGENTFLOW_MCP_WOOCOMMERCE_SITE_URL=http://localhost:8081 \
pytest sandbox/tests/test_mcp_real_domain_smokes.py -v
```

Expected: PASS in the prepared local environment; if a domain dependency is missing, FAIL with that domain name and prerequisite in the message.

- [ ] **Step 5: Run the final verification bundle**

Run:

```bash
pytest -q
pytest sandbox/tests/test_mcp_tool_schemas.py sandbox/tests/test_mcp_client.py sandbox/tests/test_mcp_backend.py -v
AGENTFLOW_RUN_MCP_REAL=1 \
TOOLATHLON_GYM_ROOT=/home/a1/sdb/dxd/toolathlon_gym \
AGENTFLOW_MCP_PGHOST=127.0.0.1 \
AGENTFLOW_MCP_PGPORT=5432 \
AGENTFLOW_MCP_PGUSER=eigent \
AGENTFLOW_MCP_PGPASSWORD=camel \
AGENTFLOW_MCP_PGDATABASE=toolathlon_gym \
AGENTFLOW_MCP_CANVAS_DOMAIN=localhost:8080 \
AGENTFLOW_MCP_WOOCOMMERCE_SITE_URL=http://localhost:8081 \
pytest sandbox/tests/test_mcp_real_server_smokes.py sandbox/tests/test_mcp_real_domain_smokes.py -v
```

Expected:

- `pytest -q` stays at `84 passed, 2 skipped`
- MCP unit tests pass
- real server-layer smokes pass
- six domain smokes pass

- [ ] **Step 6: Commit the domain suite and verification-ready state**

```bash
git add sandbox/tests/mcp_real_env.py \
        sandbox/tests/mcp_real_cases.py \
        sandbox/tests/test_mcp_real_domain_smokes.py \
        sandbox/server/backends/resources/mcp.py \
        sandbox/server/backends/resources/mcp_client.py \
        sandbox/tests/test_mcp_backend.py \
        sandbox/tests/test_mcp_client.py
git commit -m "test: add toolathlon mcp domain smokes"
```
