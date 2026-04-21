# Code Backend Single-Repository Vendoring Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AgentFlow's `code` backend self-contained by vendoring the six upstream-style code tools into this repository, removing `claude_code_root`/`allow_bash`/`bash_timeout_seconds`, and adding an opt-in real rollout smoke.

**Architecture:** Keep `code` as a session-scoped sandbox backend with AgentFlow-owned workspace lifecycle and path-boundary enforcement. Replace all external-root loading with a small internal `code_vendor` package, route all six tools through the same vendored `tool.call(...)` path, and verify the result with updated sandbox tests plus an MCP-style env-gated real rollout smoke.

**Tech Stack:** Python 3.10, pytest, FastAPI sandbox server, pathlib/shutil, vendored upstream-style tool classes, RolloutPipeline, real LLM smoke via env-gated pytest collection + pytest CLI options

---

**Known baseline:** In this worktree, `PYTHONPATH=. pytest -q sandbox/tests/test_code_backend.py sandbox/tests/test_code_tool_schemas.py sandbox/tests/test_sandbox_config_loading.py rollout/tests/test_config.py rollout/tests/test_integration.py` passes (`68 passed, 2 skipped`). `pip install -r requirements.txt` still hits the existing unrelated `pyxcursor` dependency-resolution issue from the VM stack; do not block this plan on that package.

## File Map

### New files

- `sandbox/server/backends/resources/code_vendor/__init__.py`
  Internal package export surface for the vendored six-tool compatibility layer.
- `sandbox/server/backends/resources/code_vendor/tool.py`
  Minimal vendored `Tool` base class used by the six code tools.
- `sandbox/server/backends/resources/code_vendor/file_tools.py`
  Vendored upstream-style `ReadTool`, `GlobTool`, `GrepTool`, and `BashTool`.
- `sandbox/server/backends/resources/code_vendor/edit_tools.py`
  Vendored upstream-style `EditTool` and `WriteTool`.
- `sandbox/tests/test_code_vendor_tools.py`
  Focused behavior-contract tests for the vendored tool package independent of `CodeBackend`.
- `rollout/tests/conftest.py`
  Mirror the MCP real-smoke collection-gating pattern for `code` rollout tests and add pytest CLI options for real-smoke credentials.
- `rollout/tests/test_code_real_smoke.py`
  Opt-in real rollout smoke that starts sandbox, uses the real LLM path, and proves at least one real `code:*` call happens against a temporary fixture repo.

### Modified files

- `sandbox/server/backends/resources/code.py`
  Remove external-root logic and `bash` special casing; load vendored tools directly and execute all six through the same code path.
- `configs/sandbox-server/code_config.json`
  Remove deleted config fields and present the `code` backend as a native AgentFlow capability with only `workspace_root`.
- `sandbox/tests/test_code_backend.py`
  Delete obsolete external-root/bash-wrapper tests, keep valid workspace/boundary coverage, and rewrite tool-loading expectations around internal vendoring.
- `sandbox/tool_schemas/code_tools.py`
  Update `code-bash` description to remove backend-config-dependent availability wording.
- `sandbox/tests/test_code_tool_schemas.py`
  Update schema assertions to match the new `code-bash` description and keep the rest of the parameter contract coverage.
- `sandbox/tests/test_sandbox_config_loading.py`
  Replace the `CLAUDE_CODE_ROOT` env-expansion test with a config-loading assertion for the simplified `code` backend template.

### Intentionally unchanged files

- `rollout/core/config.py`
- `rollout/core/runner.py`
- `rollout/pipeline.py`
- `sandbox/tool_schemas/__init__.py`
- `sandbox/server/backends/resources/__init__.py`

The rollout and backend registration plumbing already supports the target design. Do not widen scope into rollout engine rewrites or unrelated backend refactors.

## Chunk 1: Vendor the Upstream-Style Tool Subset

### Task 1: Add the internal `code_vendor` package and behavior-contract tests

**Files:**
- Create: `sandbox/server/backends/resources/code_vendor/__init__.py`
- Create: `sandbox/server/backends/resources/code_vendor/tool.py`
- Create: `sandbox/server/backends/resources/code_vendor/file_tools.py`
- Create: `sandbox/server/backends/resources/code_vendor/edit_tools.py`
- Create: `sandbox/tests/test_code_vendor_tools.py`

- [ ] **Step 1: Write the failing vendored-tool tests**

Create `sandbox/tests/test_code_vendor_tools.py` with focused tests like:

```python
import asyncio
from pathlib import Path
from types import SimpleNamespace

from sandbox.server.backends.resources.code_vendor.file_tools import (
    BashTool,
    GlobTool,
    GrepTool,
    ReadTool,
)
from sandbox.server.backends.resources.code_vendor.edit_tools import EditTool, WriteTool


def test_read_tool_returns_line_numbered_content(tmp_path):
    target = tmp_path / "demo.py"
    target.write_text("first\nsecond\n", encoding="utf-8")
    ctx = SimpleNamespace(cwd=str(tmp_path))

    result = asyncio.run(ReadTool().call({"file_path": str(target)}, ctx))

    assert "1" in result
    assert "first" in result
    assert "second" in result


def test_edit_tool_requires_unique_match(tmp_path):
    target = tmp_path / "demo.py"
    target.write_text("x = 1\nx = 1\n", encoding="utf-8")
    ctx = SimpleNamespace(cwd=str(tmp_path))

    result = asyncio.run(
        EditTool().call(
            {
                "file_path": str(target),
                "old_string": "x = 1",
                "new_string": "x = 2",
            },
            ctx,
        )
    )

    assert result.startswith("Error:")
    assert "appears" in result


def test_bash_tool_combines_stdout_and_stderr(tmp_path):
    ctx = SimpleNamespace(cwd=str(tmp_path))

    result = asyncio.run(
        BashTool().call(
            {
                "command": "python -c \"import sys; print('out'); print('err', file=sys.stderr)\""
            },
            ctx,
        )
    )

    assert result == "out\n\n[stderr]:\nerr"
```

- [ ] **Step 2: Run the vendored-tool tests to verify they fail**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_vendor_tools.py
```

Expected: FAIL because the `code_vendor` package does not exist yet.

- [ ] **Step 3: Add the vendored tool package**

Create `sandbox/server/backends/resources/code_vendor/tool.py` with a minimal base:

```python
from __future__ import annotations

from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str

    @property
    @abstractmethod
    def input_schema(self) -> dict:
        ...

    @abstractmethod
    async def call(self, args: dict, ctx) -> str:
        ...

    def is_read_only(self, args: dict) -> bool:
        return False
```

Create `sandbox/server/backends/resources/code_vendor/file_tools.py` with vendored upstream-style implementations:

```python
from __future__ import annotations

import subprocess
from pathlib import Path

from .tool import Tool


class BashTool(Tool):
    name = "Bash"
    description = "Execute a shell command and return stdout/stderr."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "Shell command to run"}},
            "required": ["command"],
        }

    async def call(self, args: dict, ctx) -> str:
        result = subprocess.run(
            args["command"],
            shell=True,
            capture_output=True,
            text=True,
            cwd=ctx.cwd,
        )
        out = result.stdout
        if result.stderr:
            out += f"\n[stderr]:\n{result.stderr}"
        return out.strip() or "(no output)"

    def is_read_only(self, args: dict) -> bool:
        return False
```

Add matching vendored implementations for `ReadTool`, `GlobTool`, `GrepTool`, `EditTool`, and `WriteTool`, preserving the current upstream-style semantics already described in the approved spec. Keep imports package-local only; do not carry over `log.py`, `trace.py`, or a vendored tool executor.

Create `sandbox/server/backends/resources/code_vendor/__init__.py` to export the six tool classes.

- [ ] **Step 4: Run the vendored-tool tests**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_vendor_tools.py
```

Expected: PASS. The vendored tool package exists and captures the expected upstream-style behavior.

- [ ] **Step 5: Commit the vendored tool package**

```bash
git add sandbox/server/backends/resources/code_vendor/__init__.py \
        sandbox/server/backends/resources/code_vendor/tool.py \
        sandbox/server/backends/resources/code_vendor/file_tools.py \
        sandbox/server/backends/resources/code_vendor/edit_tools.py \
        sandbox/tests/test_code_vendor_tools.py
git commit -m "feat: vendor code backend tool subset"
```

## Chunk 2: Simplify `CodeBackend` to Use Vendored Tools Only

### Task 2: Rewrite `CodeBackend` around the internal tool package

**Files:**
- Modify: `sandbox/server/backends/resources/code.py`
- Modify: `sandbox/tests/test_code_backend.py`
- Modify: `configs/sandbox-server/code_config.json`

- [ ] **Step 1: Rewrite the backend tests around the new design**

In `sandbox/tests/test_code_backend.py`:

- delete external-root helper factories such as `create_fake_claude_code_root()` and `create_marker_claude_code_root()`
- delete all tests whose only purpose is external-root loading, root-local support modules, or per-root loader isolation
- delete all `allow_bash` and `bash_timeout_seconds` tests
- add/keep failing tests like:

```python
def build_backend_config(tmp_path):
    return BackendConfig(
        enabled=True,
        default_config={
            "workspace_root": str(tmp_path / "agentflow_code"),
        },
        description="Code backend",
    )


def test_initialize_does_not_require_external_root(tmp_path):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))

    session = asyncio.run(backend.initialize("runner_123", {}))

    assert Path(session["workspace"]).exists()


def test_load_code_tools_uses_internal_vendor_package(tmp_path):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))

    tools = backend._load_code_tools()

    assert set(tools) == {"read", "glob", "grep", "bash", "edit", "write"}
    assert tools["bash"].__class__.__module__.endswith("code_vendor.file_tools")


def test_tool_executor_runs_bash_via_vendored_tool(tmp_path):
    module = load_code_backend_module()
    backend = module.CodeBackend(config=build_backend_config(tmp_path))
    fake_server = FakeServer()
    backend.bind_server(fake_server)
    workspace = tmp_path / "agentflow_code" / "worker-1"
    workspace.mkdir(parents=True)

    executor = ToolExecutor(
        tools=fake_server._tools,
        tool_name_index={},
        tool_resource_types=fake_server._tool_resource_types,
        resource_router=FakeResourceRouter(
            {"session_id": "sid", "data": {"workspace": str(workspace)}}
        ),
    )

    result = asyncio.run(
        executor.execute(
            action="code:bash",
            params={"command": "pwd"},
            worker_id="worker-1",
            trace_id="trace-1",
        )
    )

    assert result["code"] == ErrorCode.SUCCESS
    assert result["data"].strip() == str(workspace.resolve(strict=False))
```

- [ ] **Step 2: Run the rewritten backend tests to verify they fail**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_backend.py -k "does_not_require_external_root or internal_vendor_package or runs_bash_via_vendored_tool"
```

Expected: FAIL because `CodeBackend` still depends on `claude_code_root` and still special-cases `bash`.

- [ ] **Step 3: Rewrite `sandbox/server/backends/resources/code.py`**

Update `CodeBackend` to:

- keep only `workspace_root` in its default config
- rename the internal tool loader to something neutral like `_load_code_tools()`
- import vendored classes directly, for example:

```python
from sandbox.server.backends.resources.code_vendor.file_tools import (
    BashTool,
    GlobTool,
    GrepTool,
    ReadTool,
)
from sandbox.server.backends.resources.code_vendor.edit_tools import EditTool, WriteTool
```

- cache vendored instances per backend instance:

```python
self._tool_instances = {
    "read": ReadTool(),
    "glob": GlobTool(),
    "grep": GrepTool(),
    "bash": BashTool(),
    "edit": EditTool(),
    "write": WriteTool(),
}
```

- remove these methods entirely:
  - `_get_claude_code_root()`
  - `_validate_claude_code_root_prerequisites()`
  - `_load_root_support_modules()`
  - `_temporary_module_aliases()`
  - `_load_module_from_path()`
  - `_run_bash_command()`

- remove any `tool_name == "bash"` branch in `_dispatch()`
- after session/workspace validation and path normalization, always run:

```python
tool = self._load_code_tools()[tool_name]
ctx = SimpleNamespace(cwd=str(workspace))
result = await tool.call(normalized_params, ctx)
```

- keep AgentFlow-owned path normalization and workspace identity enforcement exactly as the valid existing tests expect

Update `configs/sandbox-server/code_config.json` so the `code` backend config becomes:

```json
"config": {
  "workspace_root": "/tmp/agentflow_code"
}
```

and update the description string to describe the backend as vendored/internal rather than powered by an external repository.

- [ ] **Step 4: Run the backend regression subset**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_backend.py
```

Expected: PASS after the obsolete tests/helpers are removed and the remaining coverage is adapted to the internal vendored model.

- [ ] **Step 5: Commit the backend simplification**

```bash
git add sandbox/server/backends/resources/code.py \
        sandbox/tests/test_code_backend.py \
        configs/sandbox-server/code_config.json
git commit -m "refactor: vendor code backend runtime"
```

## Chunk 3: Refresh Schema and Config Tests Around the New Contract

### Task 3: Update schema docs, config-loading tests, and obsolete assertions

**Files:**
- Modify: `sandbox/tool_schemas/code_tools.py`
- Modify: `sandbox/tests/test_code_tool_schemas.py`
- Modify: `sandbox/tests/test_sandbox_config_loading.py`

- [ ] **Step 1: Write the failing schema/config assertions**

Update the tests to the new expected contract:

```python
def test_code_bash_description_mentions_workspace_shell_execution():
    schema = _code_schemas_by_name()["code-bash"]
    description = schema["description"].lower()

    assert "workspace" in description
    assert "shell command" in description
    assert "backend config" not in description


def test_load_server_config_keeps_workspace_root_for_code_backend(tmp_path):
    config_path = tmp_path / "code_config.json"
    raw_config = {
        "resources": {
            "code": {
                "enabled": True,
                "config": {
                    "workspace_root": "/tmp/agentflow_code"
                },
            }
        }
    }
    config_path.write_text(json.dumps(raw_config), encoding="utf-8")

    sandbox = Sandbox(config=SandboxConfig(server_config_path=str(config_path)))
    loaded = sandbox._load_server_config()

    assert loaded["resources"]["code"]["config"]["workspace_root"] == "/tmp/agentflow_code"
```

- [ ] **Step 2: Run the schema/config tests to verify they fail**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_tool_schemas.py sandbox/tests/test_sandbox_config_loading.py
```

Expected: FAIL because the current schema text still mentions backend-config-dependent availability and the config-loading test still asserts `CLAUDE_CODE_ROOT` expansion.

- [ ] **Step 3: Update schema text and config-loading coverage**

In `sandbox/tool_schemas/code_tools.py`, change `code-bash` to something like:

```python
{
    "name": "code-bash",
    "description": "Run a shell command in the coding workspace using the current workspace as the working directory.",
    "parameters": [
        {
            "name": "command",
            "type": "string",
            "description": "Shell command to execute.",
            "required": True,
        }
    ],
}
```

In `sandbox/tests/test_sandbox_config_loading.py`, replace the `CLAUDE_CODE_ROOT` test with the simplified `workspace_root` expectation and remove `monkeypatch.delenv("CLAUDE_CODE_ROOT", ...)`.

- [ ] **Step 4: Run the updated schema/config regression suite**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_tool_schemas.py \
                      sandbox/tests/test_sandbox_config_loading.py \
                      rollout/tests/test_config.py
```

Expected: PASS. The code tool docs and config-loading tests now reflect the new single-repository contract.

- [ ] **Step 5: Commit the schema/config cleanup**

```bash
git add sandbox/tool_schemas/code_tools.py \
        sandbox/tests/test_code_tool_schemas.py \
        sandbox/tests/test_sandbox_config_loading.py
git commit -m "test: align code backend schema and config coverage"
```

## Chunk 4: Add the Opt-In Real Rollout Smoke

### Task 4: Add MCP-style env-gated real `code` rollout smoke support

**Files:**
- Create: `rollout/tests/conftest.py`
- Create: `rollout/tests/test_code_real_smoke.py`

- [ ] **Step 1: Write the smoke test first**

Create `rollout/tests/test_code_real_smoke.py` with a real-smoke shape like:

```python
import json
from pathlib import Path

from rollout import RolloutConfig, RolloutPipeline


def test_code_real_rollout_smoke(tmp_path, code_real_settings):
    fixture_repo = tmp_path / "fixture_repo"
    fixture_repo.mkdir()
    nested = fixture_repo / "nested"
    nested.mkdir()
    token = "AF_CODE_SMOKE_TOKEN_7F3A91"
    (nested / "TOKEN.txt").write_text(token + "\n", encoding="utf-8")

    benchmark_path = tmp_path / "benchmark.jsonl"
    benchmark_path.write_text(
        json.dumps(
            {
                "id": "code-real-smoke",
                "question": "Use the available code tools to read nested/TOKEN.txt. Reply with only the exact token.",
                "answer": token,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    config = RolloutConfig(
        benchmark_name="code_real_smoke",
        data_path=str(benchmark_path),
        output_dir=str(tmp_path / "out"),
        model_name=code_real_settings["model"],
        api_key=code_real_settings["api_key"],
        base_url=code_real_settings["base_url"],
        max_turns=5,
        available_tools=["code-*"],
        resource_types=["code"],
        resource_init_configs={"code": {"content": {"source_dir": str(fixture_repo)}}},
        sandbox_config_path="configs/sandbox-server/code_config.json",
        sandbox_auto_start=True,
        evaluate_results=False,
        save_trajectories=True,
        number_of_tasks=1,
    )

    summary = RolloutPipeline(config, output_dir=str(tmp_path / "out")).run()

    assert summary.total_tasks == 1
    assert summary.successful_tasks == 1
```

- [ ] **Step 2: Run collection to verify the smoke currently fails**

Run:

```bash
PYTHONPATH=. pytest -q rollout/tests/test_code_real_smoke.py --collect-only
```

Expected: FAIL because the new smoke file or its `code_real_settings` fixture does not exist yet.

- [ ] **Step 3: Add MCP-style collection gating and credential CLI options**

Create `rollout/tests/conftest.py`:

```python
import os
from pathlib import Path

import pytest


_REAL_CODE_TEST_FILES = {
    "test_code_real_smoke.py",
}


def pytest_addoption(parser):
    parser.addoption("--real-api-key", action="store", default="")
    parser.addoption("--real-base-url", action="store", default="")
    parser.addoption("--real-model", action="store", default="")


def pytest_ignore_collect(collection_path, config):
    if os.environ.get("AGENTFLOW_RUN_CODE_REAL") == "1":
        return False

    path = Path(str(collection_path))
    return path.name in _REAL_CODE_TEST_FILES


@pytest.fixture
def code_real_settings(request):
    api_key = request.config.getoption("--real-api-key")
    base_url = request.config.getoption("--real-base-url")
    model = request.config.getoption("--real-model")
    if not api_key or not base_url or not model:
        pytest.skip(
            "Provide --real-api-key, --real-base-url, and --real-model to run code_real smoke tests."
        )
    return {"api_key": api_key, "base_url": base_url, "model": model}
```

Then complete `rollout/tests/test_code_real_smoke.py` so it also:

- locates the results file written by `RolloutPipeline`
- loads the single saved result
- asserts there is at least one `code:*` tool call in the trajectory
- asserts the final answer equals the unique token
- asserts the token appears in the tool-result chain

- [ ] **Step 4: Verify collection gating behavior**

Run:

```bash
PYTHONPATH=. pytest -q rollout/tests/test_code_real_smoke.py --collect-only
```

Expected: no tests collected from this file unless opt-in is enabled, matching the MCP real-smoke pattern.

Run:

```bash
AGENTFLOW_RUN_CODE_REAL=1 PYTHONPATH=. pytest -q rollout/tests/test_code_real_smoke.py --collect-only
```

Expected: PASS. The real-smoke file is now collected explicitly, matching MCP's env-gated behavior.

- [ ] **Step 5: Commit the real-smoke scaffolding**

```bash
git add rollout/tests/conftest.py \
        rollout/tests/test_code_real_smoke.py
git commit -m "test: add opt-in code rollout real smoke"
```

## Chunk 5: Final Verification and Live Smoke Run

### Task 5: Run the full targeted regression suite and the real smoke with supplied credentials

**Files:**
- No code changes expected

- [ ] **Step 1: Run the full targeted regression suite**

Run:

```bash
PYTHONPATH=. pytest -q sandbox/tests/test_code_vendor_tools.py \
                      sandbox/tests/test_code_backend.py \
                      sandbox/tests/test_code_tool_schemas.py \
                      sandbox/tests/test_sandbox_config_loading.py \
                      rollout/tests/test_config.py \
                      rollout/tests/test_integration.py
```

Expected: PASS. The vendored tool package, the simplified backend, schema/config coverage, and rollout baseline all pass together.

- [ ] **Step 2: Run the real rollout smoke with explicit credentials**

Run:

```bash
AGENTFLOW_RUN_CODE_REAL=1 PYTHONPATH=. pytest -q rollout/tests/test_code_real_smoke.py \
    --real-api-key '<temporary-api-key>' \
    --real-base-url '<base-url>' \
    --real-model '<model-name>' \
    -s
```

Expected: PASS. Sandbox starts, the `code` session is created, at least one real `code:*` tool call occurs, and the final answer matches the unique token from the fixture repo.

- [ ] **Step 3: Inspect the real-smoke output**

Verify in the saved trajectory/result payload that:

- the trajectory contains at least one `code:*` tool call
- at least one `code:read` or `code:glob` appears
- the token from `nested/TOKEN.txt` is present in tool-result observations
- the final predicted answer equals the token exactly

- [ ] **Step 4: Commit the integrated result**

```bash
git status --short
git add sandbox/server/backends/resources/code_vendor \
        sandbox/server/backends/resources/code.py \
        configs/sandbox-server/code_config.json \
        sandbox/tests/test_code_vendor_tools.py \
        sandbox/tests/test_code_backend.py \
        sandbox/tool_schemas/code_tools.py \
        sandbox/tests/test_code_tool_schemas.py \
        sandbox/tests/test_sandbox_config_loading.py \
        rollout/tests/conftest.py \
        rollout/tests/test_code_real_smoke.py
git commit -m "refactor: vendor code backend tools into agentflow"
```

- [ ] **Step 5: Record final verification notes**

Capture:

- exact targeted pytest command and pass result
- exact `AGENTFLOW_RUN_CODE_REAL=1 ... pytest ...` command used
- whether the real smoke passed
- any residual risk, especially around powerful `bash` behavior and live-model variability

## Execution Notes

- Use `PYTHONPATH=.` for pytest commands in this repository unless the execution harness already injects the repo root.
- Keep path-boundary enforcement in `CodeBackend`; do not push it into the vendored tool files.
- Do not leave any `claude_code_root`, `allow_bash`, or `bash_timeout_seconds` references behind in tests or config templates.
- Do not widen the real-smoke scope into general rollout refactoring.

Plan complete and saved to `docs/superpowers/plans/2026-04-16-code-backend-single-repo-vendoring.md`. Ready to execute?
