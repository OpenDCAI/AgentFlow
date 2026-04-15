# Code Backend Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `code` resource backend to AgentFlow that provides an isolated per-session coding workspace by reusing the six lightweight tool implementations from `claude-code-py`.

**Architecture:** Follow the MCP integration pattern: add prompt-visible static tool schemas plus one runtime `CodeBackend` resource. The backend dynamically imports the lightweight `claude-code-py` tool classes, creates a workspace for each session, enforces workspace path boundaries for file-oriented tools, and exposes bridge tools like `code:read` and `code:bash`.

**Tech Stack:** Python 3.10, FastAPI sandbox server, pytest, pathlib/shutil, dynamic imports via `importlib`/`sys.path`, subprocess-backed shell execution through reused `claude-code-py` tools

---

**Known baseline:** In this worktree, `pytest -q rollout/tests/test_config.py sandbox/tests/test_mcp_tool_schemas.py sandbox/tests/test_mcp_backend.py` passes (`30 passed`). `pip install -r requirements.txt` hits an unrelated existing `pyxcursor` package-resolution issue from the VM stack; do not block `code` backend work on that dependency gap.

## File Map

### New files

- `sandbox/tool_schemas/code_tools.py`
  Static prompt-time schema definitions for the six `code-*` tools.
- `sandbox/server/backends/resources/code.py`
  `CodeBackend` runtime implementation: dynamic `claude-code-py` tool loading, workspace/session setup, path-boundary enforcement, bridge dispatch, and bash gating.
- `sandbox/tests/test_code_tool_schemas.py`
  Static schema coverage and filtering tests for `code-*` tools.
- `sandbox/tests/test_code_backend.py`
  Backend tests for registration, workspace initialization, `source_dir` copying, path rejection, bridge dispatch, and bash gating.
- `configs/sandbox-server/code_config.json`
  Example sandbox config for enabling the new `code` resource backend.

### Modified files

- `sandbox/tool_schemas/__init__.py`
  Merge `code` schemas into the global tool catalog.
- `sandbox/server/backends/resources/__init__.py`
  Export `CodeBackend` for consistency with other resource backends.

### Intentionally unchanged files

- `rollout/core/config.py`
- `rollout/core/runner.py`
- `sandbox/server/config_loader.py`
- `claude-code-py/*`

The current rollout/resource plumbing already supports a new backend resource once tool schemas and backend registration are in place. Do not expand the scope into packaging or modifying `claude-code-py` itself in v1.

## Chunk 1: Static Tool Catalog

### Task 1: Add prompt-time `code-*` tool schemas

**Files:**
- Create: `sandbox/tool_schemas/code_tools.py`
- Modify: `sandbox/tool_schemas/__init__.py`
- Test: `sandbox/tests/test_code_tool_schemas.py`
- Regression: `sandbox/tests/test_tool_schemas.py`

- [ ] **Step 1: Write the failing schema tests**

```python
from sandbox.tool_schemas import get_all_tool_names, get_tool_schemas, get_tools_by_resource


def test_code_tools_visible_in_global_catalog():
    names = get_all_tool_names()
    assert "code-read" in names
    assert "code-bash" in names


def test_code_wildcard_filtering():
    schemas = get_tool_schemas(["code-*"])
    names = {schema["name"] for schema in schemas}
    assert names == {
        "code-read",
        "code-glob",
        "code-grep",
        "code-bash",
        "code-edit",
        "code-write",
    }


def test_code_tools_by_resource():
    schemas = get_tools_by_resource("code")
    assert {schema["name"] for schema in schemas} == {
        "code-read",
        "code-glob",
        "code-grep",
        "code-bash",
        "code-edit",
        "code-write",
    }
```

- [ ] **Step 2: Run the schema tests to verify they fail**

Run:

```bash
pytest -q sandbox/tests/test_code_tool_schemas.py
```

Expected: FAIL because `code_tools.py` does not exist and the global tool catalog does not include any `code-*` schemas.

- [ ] **Step 3: Add the static `code` schema file**

Create `sandbox/tool_schemas/code_tools.py` with this structure:

```python
from typing import Any, Dict, List


def get_code_tool_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "name": "code-read",
            "description": "Read a text file from the current code workspace and return its contents with line numbers.",
            "parameters": [
                {"name": "file_path", "type": "string", "description": "Path to the file to read.", "required": True},
                {"name": "offset", "type": "integer", "description": "Start line number (1-indexed).", "required": False},
                {"name": "limit", "type": "integer", "description": "Maximum number of lines to return.", "required": False},
            ],
        },
        {
            "name": "code-glob",
            "description": "Find files in the current code workspace using a glob pattern.",
            "parameters": [
                {"name": "pattern", "type": "string", "description": "Glob pattern such as '**/*.py'.", "required": True},
                {"name": "path", "type": "string", "description": "Optional workspace-relative search root.", "required": False},
            ],
        },
        {
            "name": "code-grep",
            "description": "Search file contents in the current code workspace using a regex pattern.",
            "parameters": [
                {"name": "pattern", "type": "string", "description": "Regex pattern to search for.", "required": True},
                {"name": "path", "type": "string", "description": "Optional workspace-relative search root.", "required": False},
                {"name": "glob", "type": "string", "description": "Optional filename filter such as '*.py'.", "required": False},
            ],
        },
        {
            "name": "code-bash",
            "description": "Run a shell command in the current code workspace. Availability depends on backend config.",
            "parameters": [
                {"name": "command", "type": "string", "description": "Shell command to run.", "required": True},
            ],
        },
        {
            "name": "code-edit",
            "description": "Perform an exact string replacement in a workspace file. Set replace_all=true to replace every occurrence.",
            "parameters": [
                {"name": "file_path", "type": "string", "description": "Path to the file to edit.", "required": True},
                {"name": "old_string", "type": "string", "description": "Exact text to replace.", "required": True},
                {"name": "new_string", "type": "string", "description": "Replacement text.", "required": True},
                {"name": "replace_all", "type": "boolean", "description": "Replace all matches instead of one unique match.", "required": False},
            ],
        },
        {
            "name": "code-write",
            "description": "Write full file contents into a workspace file, creating parent directories if needed.",
            "parameters": [
                {"name": "file_path", "type": "string", "description": "Path to the file to write.", "required": True},
                {"name": "content", "type": "string", "description": "Full content to write.", "required": True},
            ],
        },
    ]
```

Update `sandbox/tool_schemas/__init__.py` to:

- import `get_code_tool_schemas`
- append it to `all_schemas`
- leave wildcard behavior unchanged because existing `-*` wildcard handling already covers `code-*`
- include `get_code_tool_schemas` in `__all__`

- [ ] **Step 4: Run schema regression tests**

Run:

```bash
pytest -q sandbox/tests/test_code_tool_schemas.py sandbox/tests/test_tool_schemas.py
```

Expected: PASS. The new `code` schema tests pass, and the existing generic schema tests still pass.

- [ ] **Step 5: Commit the schema work**

```bash
git add sandbox/tool_schemas/code_tools.py \
        sandbox/tool_schemas/__init__.py \
        sandbox/tests/test_code_tool_schemas.py
git commit -m "feat: add static code tool schemas"
```

## Chunk 2: Backend Skeleton and Workspace Lifecycle

### Task 2: Add `CodeBackend` with dynamic tool loading and workspace initialization

**Files:**
- Create: `sandbox/server/backends/resources/code.py`
- Modify: `sandbox/server/backends/resources/__init__.py`
- Test: `sandbox/tests/test_code_backend.py`

- [ ] **Step 1: Write failing backend tests for registration and initialization**

```python
import asyncio
from pathlib import Path

from sandbox.server.backends.base import BackendConfig


def test_bind_server_registers_code_tools(tmp_path):
    backend = CodeBackend(
        config=BackendConfig(
            enabled=True,
            default_config={
                "claude_code_root": str(tmp_path / "claude-code-py"),
                "workspace_root": str(tmp_path / "agentflow_code"),
                "allow_bash": True,
            },
        )
    )
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    assert "code:read" in fake_server._tools
    assert "code:bash" in fake_server._tools


def test_initialize_creates_worker_workspace(tmp_path, monkeypatch):
    backend = build_code_backend(tmp_path, monkeypatch)
    session = asyncio.run(backend.initialize("runner_123", {}))
    assert session["workspace"].endswith("runner_123")
    assert Path(session["workspace"]).exists()


def test_initialize_copies_source_dir(tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "demo.py").write_text("print('hi')\n", encoding="utf-8")
    backend = build_code_backend(tmp_path, monkeypatch)
    session = asyncio.run(backend.initialize("runner_123", {"source_dir": str(source_dir)}))
    assert (Path(session["workspace"]) / "demo.py").read_text(encoding="utf-8") == "print('hi')\n"
```

- [ ] **Step 2: Run the backend tests to verify they fail**

Run:

```bash
pytest -q sandbox/tests/test_code_backend.py -k "registers_code_tools or creates_worker_workspace or copies_source_dir"
```

Expected: FAIL because `code.py` and its test helpers do not exist yet.

- [ ] **Step 3: Add the backend skeleton and dynamic tool loader**

Create `sandbox/server/backends/resources/code.py` with the following top-level shape:

```python
import shutil
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import build_error_response, build_success_response


class CodeBackend(Backend):
    name = "code"
    description = "Code Backend - lightweight coding workspace integration"
    version = "1.0.0"

    def __init__(self, config: BackendConfig | None = None):
        ...
        self._tool_factory_cache = None

    def bind_server(self, server) -> None:
        super().bind_server(server)
        for tool_name in ("read", "glob", "grep", "bash", "edit", "write"):
            server.register_tool(
                f"code:{tool_name}",
                self._make_bridge_tool(tool_name),
                resource_type="code",
            )

    async def initialize(self, worker_id: str, config: dict) -> dict[str, Any]:
        workspace = self._prepare_workspace(worker_id)
        source_dir = self._resolve_source_dir(config)
        if source_dir is not None:
            self._copy_source_dir(source_dir, workspace)
        return {"workspace": str(workspace), "source_dir": str(source_dir) if source_dir else ""}

    async def cleanup(self, worker_id: str, session_info: dict) -> None:
        return None
```

Add helper methods for:

- `_get_claude_code_root()`
- `_get_workspace_root()`
- `_prepare_workspace(worker_id)`
- `_resolve_source_dir(config)`
- `_copy_source_dir(source_dir, workspace)`
- `_load_claude_code_tools()`

Dynamic loading requirements:

- temporarily insert `claude_code_root` into `sys.path`
- import `tools.file_tools` and `tools.edit_tools`
- instantiate the six tool classes
- cache them per backend instance so bind/dispatch does not re-import every call

Update `sandbox/server/backends/resources/__init__.py` to export `CodeBackend`.

- [ ] **Step 4: Run the registration and initialization tests**

Run:

```bash
pytest -q sandbox/tests/test_code_backend.py -k "registers_code_tools or creates_worker_workspace or copies_source_dir"
```

Expected: PASS. The backend registers six `code:*` bridge tools and creates/copies workspaces correctly.

- [ ] **Step 5: Commit the backend skeleton**

```bash
git add sandbox/server/backends/resources/code.py \
        sandbox/server/backends/resources/__init__.py \
        sandbox/tests/test_code_backend.py
git commit -m "feat: add code backend workspace lifecycle"
```

## Chunk 3: Path Enforcement and File-Oriented Bridge Dispatch

### Task 3: Add path normalization, workspace-boundary checks, and bridge dispatch for file tools

**Files:**
- Modify: `sandbox/server/backends/resources/code.py`
- Modify: `sandbox/tests/test_code_backend.py`

- [ ] **Step 1: Write failing tests for path safety and file-tool dispatch**

```python
def test_code_read_dispatches_to_reused_tool(tmp_path, monkeypatch):
    backend = build_code_backend(tmp_path, monkeypatch)
    workspace = tmp_path / "agentflow_code" / "runner_123"
    workspace.mkdir(parents=True)
    (workspace / "demo.py").write_text("print('ok')\n", encoding="utf-8")
    result = asyncio.run(
        backend._dispatch(
            "read",
            {"session_id": "sid", "data": {"workspace": str(workspace)}},
            {"file_path": "demo.py"},
        )
    )
    assert result["status"] == "success"
    assert "print('ok')" in str(result["data"])


def test_code_rejects_path_escape(tmp_path, monkeypatch):
    backend = build_code_backend(tmp_path, monkeypatch)
    workspace = tmp_path / "agentflow_code" / "runner_123"
    workspace.mkdir(parents=True)
    result = asyncio.run(
        backend._dispatch(
            "read",
            {"session_id": "sid", "data": {"workspace": str(workspace)}},
            {"file_path": "../escape.txt"},
        )
    )
    assert result["status"] == "error"
    assert "workspace" in result["message"].lower()


def test_code_write_then_read_round_trip(tmp_path, monkeypatch):
    backend = build_code_backend(tmp_path, monkeypatch)
    workspace = tmp_path / "agentflow_code" / "runner_123"
    workspace.mkdir(parents=True)
    write_result = asyncio.run(
        backend._dispatch(
            "write",
            {"session_id": "sid", "data": {"workspace": str(workspace)}},
            {"file_path": "pkg/demo.py", "content": "value = 1\n"},
        )
    )
    read_result = asyncio.run(
        backend._dispatch(
            "read",
            {"session_id": "sid", "data": {"workspace": str(workspace)}},
            {"file_path": "pkg/demo.py"},
        )
    )
    assert write_result["status"] == "success"
    assert "value = 1" in str(read_result["data"])
```

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run:

```bash
pytest -q sandbox/tests/test_code_backend.py -k "dispatches_to_reused_tool or rejects_path_escape or round_trip"
```

Expected: FAIL because `_dispatch()` either does not exist yet or does not normalize paths and call the reused tool implementations.

- [ ] **Step 3: Implement path normalization and bridge dispatch**

Inside `sandbox/server/backends/resources/code.py`, add focused helpers:

```python
def _resolve_workspace_path(self, workspace: Path, user_path: str) -> Path:
    candidate = Path(user_path)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    resolved = candidate.resolve()
    workspace_resolved = workspace.resolve()
    if resolved != workspace_resolved and workspace_resolved not in resolved.parents:
        raise ValueError(f"Path escapes workspace: {user_path}")
    return resolved


def _normalize_params(self, tool_name: str, workspace: Path, params: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(params)
    if tool_name in {"read", "edit", "write"} and "file_path" in normalized:
        normalized["file_path"] = str(self._resolve_workspace_path(workspace, normalized["file_path"]))
    if tool_name in {"glob", "grep"} and "path" in normalized:
        normalized["path"] = str(self._resolve_workspace_path(workspace, normalized["path"]))
    return normalized
```

Then add `_dispatch()`:

```python
async def _dispatch(self, tool_name: str, session_info: dict, params: dict[str, Any]) -> dict[str, Any]:
    workspace = Path(((session_info or {}).get("data") or {}).get("workspace", ""))
    if not workspace:
        return build_error_response(...)

    try:
        normalized = self._normalize_params(tool_name, workspace, params)
    except ValueError as exc:
        return build_error_response(...)

    ctx = SimpleNamespace(cwd=str(workspace))
    tool = self._load_claude_code_tools()[tool_name]
    result = await tool.call(normalized, ctx)
    return build_success_response(data=result, tool=f"code:{tool_name}", ...)
```

Bridge wrappers created by `bind_server()` should call this `_dispatch()`.

- [ ] **Step 4: Run backend dispatch tests**

Run:

```bash
pytest -q sandbox/tests/test_code_backend.py -k "dispatches_to_reused_tool or rejects_path_escape or round_trip"
```

Expected: PASS. The file-oriented bridge tools reuse the imported `claude-code-py` tool behavior while enforcing workspace path boundaries.

- [ ] **Step 5: Commit the file-tool bridge work**

```bash
git add sandbox/server/backends/resources/code.py \
        sandbox/tests/test_code_backend.py
git commit -m "feat: add code backend file tool dispatch"
```

## Chunk 4: Bash Gating, Config Template, and Final Verification

### Task 4: Add `code:bash`, sandbox config, and final targeted verification

**Files:**
- Modify: `sandbox/server/backends/resources/code.py`
- Create: `configs/sandbox-server/code_config.json`
- Modify: `sandbox/tests/test_code_backend.py`

- [ ] **Step 1: Write failing tests for bash gating and workspace execution**

```python
def test_code_bash_respects_allow_bash_flag(tmp_path, monkeypatch):
    backend = build_code_backend(tmp_path, monkeypatch, allow_bash=False)
    workspace = tmp_path / "agentflow_code" / "runner_123"
    workspace.mkdir(parents=True)
    result = asyncio.run(
        backend._dispatch(
            "bash",
            {"session_id": "sid", "data": {"workspace": str(workspace)}},
            {"command": "pwd"},
        )
    )
    assert result["status"] == "error"
    assert "disabled" in result["message"].lower()


def test_code_bash_runs_in_workspace(tmp_path, monkeypatch):
    backend = build_code_backend(tmp_path, monkeypatch, allow_bash=True)
    workspace = tmp_path / "agentflow_code" / "runner_123"
    workspace.mkdir(parents=True)
    result = asyncio.run(
        backend._dispatch(
            "bash",
            {"session_id": "sid", "data": {"workspace": str(workspace)}},
            {"command": "pwd"},
        )
    )
    assert result["status"] == "success"
    assert str(workspace) in str(result["data"])
```

- [ ] **Step 2: Run the bash tests to verify they fail**

Run:

```bash
pytest -q sandbox/tests/test_code_backend.py -k "allow_bash_flag or runs_in_workspace"
```

Expected: FAIL because the backend does not yet special-case bash or expose an example sandbox config.

- [ ] **Step 3: Implement bash gating and timeout handling**

In `sandbox/server/backends/resources/code.py`:

- add backend default config fields:
  - `claude_code_root`
  - `workspace_root`
  - `allow_bash`
  - `bash_timeout_seconds`
- reject `code:bash` when `allow_bash` is false
- keep `command` as the only public parameter
- execute the reused `BashTool` with `ctx.cwd=workspace`

Use a timeout wrapper around the awaited `tool.call(...)`, for example:

```python
result = await asyncio.wait_for(
    tool.call(normalized, ctx),
    timeout=float(self.get_default_config().get("bash_timeout_seconds", 30)),
)
```

Return backend-level error responses for:

- bash disabled
- timeout

Create `configs/sandbox-server/code_config.json` with this structure:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "session_ttl": 300
  },
  "resources": {
    "code": {
      "enabled": true,
      "description": "Lightweight coding backend powered by claude-code-py tools",
      "backend_class": "sandbox.server.backends.resources.code.CodeBackend",
      "config": {
        "claude_code_root": "/home/a1/sdb/dxd/claude-code-py",
        "workspace_root": "/tmp/agentflow_code",
        "allow_bash": true,
        "bash_timeout_seconds": 30
      }
    }
  },
  "warmup": {
    "enabled": false,
    "resources": []
  }
}
```

- [ ] **Step 4: Run the full targeted verification suite**

Run:

```bash
pytest -q sandbox/tests/test_code_tool_schemas.py \
          sandbox/tests/test_code_backend.py \
          sandbox/tests/test_tool_schemas.py \
          rollout/tests/test_config.py
```

Expected: PASS. The new code backend tests pass and existing targeted regression coverage stays green.

- [ ] **Step 5: Commit the final backend integration**

```bash
git add sandbox/server/backends/resources/code.py \
        configs/sandbox-server/code_config.json \
        sandbox/tests/test_code_backend.py
git commit -m "feat: add lightweight code backend"
```

## Chunk 5: Optional Rollout Smoke and Handoff

### Task 5: Add a minimal rollout-facing smoke check and handoff notes

**Files:**
- Modify: `docs/superpowers/specs/2026-04-15-code-backend-design.md` only if implementation materially diverged
- Optional local temp file: `tmp/code_backend_smoke.json` or equivalent scratch config, not committed

- [ ] **Step 1: Create a minimal local smoke config**

Use an untracked scratch config that exercises:

- `resource_types=["code"]`
- `available_tools=["code-*"]`
- `resource_init_configs["code"]["content"]["source_dir"]` pointing at a tiny local fixture repo

Example shape:

```json
{
  "benchmark_name": "code_smoke",
  "data_path": "tmp/code_smoke.jsonl",
  "model_name": "your-model",
  "api_key": "test-key",
  "base_url": "http://localhost:8000/v1",
  "available_tools": ["code-*"],
  "resource_types": ["code"],
  "resource_init_configs": {
    "code": {
      "content": {
        "source_dir": "/tmp/code_fixture_repo"
      }
    }
  },
  "sandbox_config_path": "configs/sandbox-server/code_config.json",
  "max_turns": 5,
  "evaluate_results": false
}
```

- [ ] **Step 2: Run one manual smoke execution if a suitable model endpoint is available**

Run:

```bash
python -m rollout.pipeline --config tmp/code_backend_smoke.json
```

Expected: the runner starts, creates a `code` session, loads `code-*` tools, and executes at least one tool call against the workspace.

If no suitable model endpoint is available in the environment, explicitly note that this smoke step was skipped and rely on the targeted pytest suite.

- [ ] **Step 3: Update the design/spec only if implementation deviated**

If implementation differs from the approved design in any material way, amend:

```bash
$EDITOR docs/superpowers/specs/2026-04-15-code-backend-design.md
```

Otherwise skip this step.

- [ ] **Step 4: Produce final verification notes**

Capture:

- exact test commands run
- whether rollout smoke was run or skipped
- any unresolved limitation, especially that `bash` uses only weak `cwd` confinement in v1

- [ ] **Step 5: Commit any final doc adjustments**

```bash
git add docs/superpowers/specs/2026-04-15-code-backend-design.md
git commit -m "docs: align code backend spec with implementation"
```

Only make this commit if the spec actually changed.
