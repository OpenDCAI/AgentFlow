## Code Backend Single-Repository Vendoring Design

Date: 2026-04-15
Status: Approved for planning
Supersedes: `docs/superpowers/specs/2026-04-15-code-backend-design.md`

## Summary

AgentFlow's current `code` backend depends on an external `claude-code-py` source tree through `claude_code_root`. That makes the feature non-portable, couples runtime behavior to a closed or separately managed repository, and introduces an avoidable configuration requirement.

This design replaces that approach with an internal vendored compatibility layer inside AgentFlow. AgentFlow will vendor the minimal upstream code-tool subset it actually needs, and the `code` backend will load those vendored classes directly from the AgentFlow repository.

The backend remains a session-scoped resource backend with per-worker workspaces and AgentFlow-owned path-boundary enforcement. The six exposed coding tools remain:

- `code:read`
- `code:glob`
- `code:grep`
- `code:bash`
- `code:edit`
- `code:write`

Unlike the current implementation, all six tools, including `bash`, will execute through vendored upstream-style tool classes. AgentFlow will stop treating `bash` as a separately wrapped special case.

## Problem Statement

The current design has three architectural problems:

- It requires `claude_code_root` in sandbox config, which breaks single-repository portability.
- It relies on dynamic source loading from another tree, which is brittle and hard to reason about.
- It contains an internal inconsistency: `code:bash` is nominally part of the reused six-tool set, but in practice it bypasses the loaded upstream `BashTool` and runs through an AgentFlow-specific subprocess wrapper.

These are not desirable "advanced configuration" choices. They are design mistakes for a feature that should ship as a self-contained AgentFlow capability.

## Goals

- Make the `code` backend runnable from the AgentFlow repository alone.
- Keep the six coding tools behaviorally aligned with the upstream lightweight tool implementations.
- Remove all dependency on external `claude-code-py` runtime paths and dynamic import plumbing.
- Keep `code` as a session-scoped backend with isolated worker workspaces.
- Preserve AgentFlow's existing rollout and sandbox abstractions.
- Add a clear test strategy that covers unit behavior, backend integration, and a real rollout smoke path.

## Non-Goals

- Do not vendor the full `claude-code-py` runtime.
- Do not vendor query loops, skills, tracing, memory loading, or sub-agent functionality.
- Do not add hard shell sandboxing.
- Do not redesign rollout configuration, sandbox protocols, or tool schema conventions.
- Do not keep backward compatibility for `claude_code_root`, `allow_bash`, or `bash_timeout_seconds`.

## Core Decisions

### 1. Vendor a minimal compatibility layer

AgentFlow will vendor only the minimal code-tool slice needed for the `code` backend:

- a minimal `Tool` base class
- `ReadTool`
- `GlobTool`
- `GrepTool`
- `BashTool`
- `EditTool`
- `WriteTool`

The vendored code should be a small, clearly bounded package inside AgentFlow, with only the minimum import adjustments required to make it internal and self-contained.

### 2. Remove the external-root model completely

The new design deletes the idea that AgentFlow should discover coding tools from another source tree at runtime.

Delete these concepts from implementation, config, tests, and docs:

- `claude_code_root`
- dynamic import of upstream files
- root-local support-module loading
- compatibility tests that verify loading from an external tree

This is an intentional removal, not a soft deprecation.

### 3. Treat `bash` as a normal member of the six-tool set

The vendored `BashTool` will be used the same way as the other five vendored tools: through the common tool-loading path and `tool.call(params, ctx)` execution model.

Delete these concepts from implementation, config, tests, and docs:

- `allow_bash`
- `bash_timeout_seconds`
- AgentFlow-specific `_run_bash_command()` behavior
- config-availability messaging for `code-bash`

The `code` backend will expose all six tools all the time.

### 4. Keep AgentFlow-owned environment boundaries

Vendoring the tool classes does not move workspace safety into the vendored code. AgentFlow still owns:

- per-worker workspace creation
- `source_dir` copying
- worker/session identity checks
- file-path normalization relative to workspace
- path-escape rejection for file-oriented tools

This separation keeps the vendored code small and keeps environment policy at the backend boundary where AgentFlow already owns session state.

## Architecture

### Vendored package layout

Add a dedicated internal package for the vendored code tools, for example:

- `sandbox/server/backends/resources/code_vendor/__init__.py`
- `sandbox/server/backends/resources/code_vendor/tool.py`
- `sandbox/server/backends/resources/code_vendor/file_tools.py`
- `sandbox/server/backends/resources/code_vendor/edit_tools.py`

The package name should make it obvious that this is a bounded internal compatibility layer, not a general-purpose reimplementation of `claude-code-py`.

### Backend responsibilities

`CodeBackend` remains responsible for:

- registering the six `code:*` bridge tools
- creating and cleaning per-worker workspaces
- copying optional `source_dir` contents into the session workspace
- validating the session workspace against the worker id
- enforcing file-path boundaries for file-oriented tools
- instantiating and caching the six vendored tool classes

`CodeBackend` no longer needs:

- `_get_claude_code_root()`
- `_validate_claude_code_root_prerequisites()`
- `_load_root_support_modules()`
- dynamic module alias installation
- `_run_bash_command()`
- any `bash`-only dispatch branch

### Runtime flow

The runtime flow becomes:

1. `initialize()` validates `worker_id`, prepares a staged workspace, and optionally copies `source_dir`.
2. The backend ensures vendored tool instances are loaded from the repository itself.
3. The staged workspace becomes the active workspace.
4. Bridge dispatch resolves the worker session workspace.
5. For file-oriented tools, AgentFlow normalizes and bounds path-like parameters to the workspace.
6. The backend creates a minimal context adapter with `cwd=<workspace>`.
7. All six tools execute through the same vendored `tool.call(...)` path.
8. AgentFlow wraps results into standard backend success/error responses.

### Minimal context adapter

The vendored six-tool subset only needs a tiny runtime context:

```python
SimpleNamespace(cwd=str(workspace))
```

No full agent runtime model is needed.

## Tool Behavior Contract

The tool surface remains unchanged:

- prompt-visible schemas stay `code-read`, `code-glob`, `code-grep`, `code-bash`, `code-edit`, `code-write`
- runtime names stay `code:read`, `code:glob`, `code:grep`, `code:bash`, `code:edit`, `code:write`
- parameter names remain aligned with the vendored upstream tool classes

Behaviorally, the backend should preserve:

- line-numbered `read` output
- recursive globbing behavior
- recursive grep behavior with optional file filter
- exact-match edit semantics with uniqueness checks
- full-file overwrite semantics for `write`
- upstream-style shell execution behavior for `bash`

AgentFlow should not add new `bash`-specific runtime policy once vendoring is complete.

## Configuration Design

### Backend config

After the redesign, `code` backend config should keep only what is still meaningfully owned by AgentFlow:

- `workspace_root`

The config example should therefore look like:

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
      "description": "Lightweight coding backend with vendored upstream-style tools",
      "backend_class": "sandbox.server.backends.resources.code.CodeBackend",
      "config": {
        "workspace_root": "/tmp/agentflow_code"
      }
    }
  },
  "warmup": {
    "enabled": false,
    "resources": []
  }
}
```

### Session init config

Session init remains intentionally small:

- `source_dir`: optional directory copied into the session workspace

Rollout-facing use stays:

- `resource_types=["code"]`
- `available_tools=["code-*"]`
- `resource_init_configs["code"]["content"]["source_dir"]`

## Testing Strategy

The testing changes must be explicit. This work is not only about adding tests; it also requires deleting tests and rewriting tests that lock in the old design mistake.

### Delete old tests

Delete tests that exist only to validate the old external-root or AgentFlow-specific bash wrapper model, including categories such as:

- external `claude_code_root` requirement
- fake external upstream roots
- dynamic loading from another repository
- root-local support-module loading
- isolated-per-root loader behavior
- `allow_bash` gating
- `bash_timeout_seconds`
- AgentFlow-specific `bash` input validation that no longer exists in the vendored-upstream model
- config-template checks that still mention deleted fields
- env-var expansion tests whose only purpose was `CLAUDE_CODE_ROOT`

### Modify existing tests

Keep and adapt the tests that remain valid for the new architecture:

- tool registration tests
- workspace initialization and `source_dir` copy tests
- workspace recreation tests
- cleanup safety tests
- `worker_id` validation tests
- session workspace identity and boundary tests
- file-path normalization and escape rejection tests
- successful bridge dispatch and standard response-shape tests
- tool schema presence/filtering/parameter-contract tests

Schema tests must update descriptions so `code-bash` no longer claims backend-config-dependent availability.

### Add new tests

Add new focused tests for the vendored model:

- vendored tool loading from the internal package
- all six tools executing through the same tool-call path
- vendored `BashTool` behavior contract
- vendored `EditTool`/`WriteTool` behavior contract where existing bridge tests do not already cover it

### Add a rollout-facing smoke test

Add one end-to-end rollout smoke that exercises the real rollout-to-sandbox-to-code-backend path.

The smoke should:

- live under `rollout/tests/`
- follow the MCP real-smoke opt-in pattern
- not be collected in default pytest execution
- require explicit manual invocation, for example by setting `AGENTFLOW_RUN_CODE_REAL=1`
- use a real LLM response path and a real sandbox/code backend path

This smoke should not mock sandbox components. It should really:

- start sandbox
- create a `code` session
- copy a tiny fixture repo into the workspace
- expose `code-*` tools through rollout
- execute at least one real `code:*` tool call

Recommended smoke structure:

1. Create a temporary fixture repo with a uniquely identifiable file, for example `nested/TOKEN.txt`.
2. Write a hard-to-guess token into that file.
3. Create a one-task benchmark asking the agent to use code tools to read the file and return only the exact token.
4. Run `RolloutPipeline` with:
   - `available_tools=["code-*"]`
   - `resource_types=["code"]`
   - `resource_init_configs["code"]["content"]["source_dir"]=fixture_repo`
   - `sandbox_config_path="configs/sandbox-server/code_config.json"`
   - `sandbox_auto_start=True`
   - `number_of_tasks=1`
   - `evaluate_results=False`
   - `save_trajectories=True`
5. Assert that:
   - the task succeeds
   - the trajectory contains at least one `code:*` tool call
   - the final answer equals the token
   - the token appears in the observed tool-result chain

Credential provisioning for that opt-in real smoke remains an execution-time concern and must not be hardcoded into repository defaults.

## Documentation Changes

Update all user-facing and internal docs that still describe the deleted design:

- `configs/sandbox-server/code_config.json`
- `sandbox/tests/test_sandbox_config_loading.py`
- `sandbox/tests/test_code_tool_schemas.py`
- any code-backend README/tutorial snippets
- the prior `2026-04-15-code-backend-design.md` should be treated as superseded

The resulting documentation should consistently present the `code` backend as a native AgentFlow capability.

## Risks

- Vendored code can drift from future upstream changes.
  Mitigation: treat the vendored subset as an intentionally frozen internal compatibility layer and cover it with explicit behavior tests.

- Real rollout smoke tests can be flaky because they depend on live model behavior and external connectivity.
  Mitigation: keep them opt-in and strongly constrain the task prompt and fixture.

- `bash` remains powerful because it executes shell commands relative to the workspace but without OS-level isolation.
  Mitigation: document this clearly as an inherent property of the `code` backend rather than disguising it behind partial configuration toggles.

## Recommended Implementation Order

1. Vendor the minimal upstream six-tool compatibility layer into AgentFlow.
2. Simplify `CodeBackend` to load vendored tools directly and remove all external-root logic.
3. Remove `bash` special handling so all six tools share one execution path.
4. Simplify `code` backend config to `workspace_root` only.
5. Update schema descriptions and sandbox config examples.
6. Delete old tests tied to the removed design.
7. Adapt retained backend and schema tests.
8. Add vendored-tool behavior coverage.
9. Add the opt-in real rollout smoke.

## Decision

AgentFlow should stop treating the `code` backend as a thin adapter over an external source tree and instead ship a self-contained, vendored upstream-style compatibility layer inside the repository.

This restores the intended product boundary:

- AgentFlow owns the coding environment as a native feature
- all six code tools are internally available
- rollout and sandbox integration stay unchanged
- the repository becomes portable again
