# Toolathlon-GYM MCP Backend Design

Date: 2026-04-12
Status: Approved for planning

## Summary

Add Toolathlon-GYM MCP servers to AgentFlow as one new backend resource, `mcp`, while preserving AgentFlow's current behavior:

- minimal changes to existing architecture
- global static tool-schema registration
- `available_tools = []` still means "do not filter"
- runtime availability may be narrower than prompt-visible tools

The result is a new `MCPBackend` that manages Toolathlon-GYM MCP servers at runtime, plus a new static MCP tool catalog that is merged into AgentFlow's existing tool schema set.

## Goals

- Expose Toolathlon-GYM MCP tools to AgentFlow agents.
- Keep existing AgentFlow native environments and configs working unchanged.
- Reuse AgentFlow's current backend, session, and `available_tools` model.
- Concentrate MCP-specific complexity inside one new backend.
- Support task-aware MCP initialization for Toolathlon-GYM-style workloads.

## Non-Goals

- Do not redesign AgentFlow's global tool loading model.
- Do not make tool visibility strictly match runtime-enabled backends.
- Do not implement 25 independent MCP backends.
- Do not refactor native backends just because MCP is being added.

## Constraints

- Follow AgentFlow's existing semantics as closely as possible.
- Prefer the smallest viable architecture change.
- Preserve the current "static visible tool set, narrower runtime set" behavior.
- Treat MCP as a new resource type, not as a replacement for existing tools.

## Recommended Approach

Implement:

1. A single runtime backend: `sandbox/server/backends/resources/mcp.py`
2. A static MCP schema catalog: `sandbox/tool_schemas/mcp_tools.py`
3. A small merge into `sandbox/tool_schemas/__init__.py`
4. MCP-specific sandbox config, for example `configs/sandbox-server/mcp_config.json`

This keeps the old architecture intact:

- agent/tool prompt path stays static
- sandbox execution path stays backend/session based
- MCP runtime complexity is isolated inside `MCPBackend`

## Architecture

### Existing AgentFlow pattern

Today AgentFlow effectively has:

- static tool schemas for agent prompting
- runtime backend loading for real execution
- `available_tools` as a filter over the static schema set

This means prompt-visible tools are already not strictly bound to loaded backends.

### New MCP fit

MCP should follow the same pattern:

- MCP tools are added to the global static schema set
- runtime MCP server startup is handled by one `mcp` backend
- `enabled_mcp_servers` affects runtime startup only
- `available_tools` continues to filter prompt-visible tools only

### Internal MCP layering

The internal structure of the new backend is:

- `MCPBackend`
  - session initialization
  - workspace preparation
  - task-context handling
  - MCP client lifecycle
  - tool dispatch

- runtime MCP servers
  - `filesystem`
  - `snowflake`
  - `emails`
  - `excel`
  - and the rest of the Toolathlon-GYM server set

- MCP tools
  - exposed to AgentFlow as tool-level entries such as `mcp:filesystem.read_file`

This extra server layer exists only inside `MCPBackend`; it does not change AgentFlow's top-level abstractions.

## Tool Naming

Use namespaced tool names:

- `mcp:filesystem.read_file`
- `mcp:snowflake.run_query`
- `mcp:emails.send_email`

Reasons:

- keeps source server explicit
- avoids collisions with native tools
- scales naturally across many MCP servers

## Configuration Design

### Native configs

Native AgentFlow configs stay unchanged.

- native sandbox configs continue to use `resources`, `apis`, and `warmup`
- rollout and synthesis configs continue to use `available_tools`

### MCP sandbox config

Add a sandbox config that loads the new `mcp` resource. The important global fields are:

- `toolathlon_root`
- `enabled_mcp_servers`
- `workspace_root`
- `env_overrides`

Example shape:

```json
{
  "resources": {
    "mcp": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.mcp.MCPBackend",
      "config": {
        "toolathlon_root": "/path/to/toolathlon_gym",
        "enabled_mcp_servers": ["filesystem", "terminal", "snowflake"],
        "workspace_root": "/tmp/agentflow_mcp",
        "env_overrides": {
          "PGHOST": "toolathlon_pg",
          "PGPORT": "5432",
          "PGUSER": "eigent",
          "PGPASSWORD": "camel",
          "PGDATABASE": "toolathlon_gym"
        }
      }
    }
  }
}
```

### MCP task/session context

Some required MCP inputs are task-specific and should be passed during session initialization, not hardcoded globally:

- `task_dir`
- `copy_initial_workspace`
- `run_preprocess`

These are needed because Toolathlon-GYM tasks may depend on:

- `initial_workspace`
- `preprocess/main.py`
- task-local files such as `email_config.json`

## Runtime Data Flow

### Prompt/tool loading

When AgentFlow builds prompt-time tools:

1. native static schemas are loaded as today
2. MCP static schemas are also loaded
3. `available_tools` filters the combined static set

If `available_tools` is empty:

- the prompt-visible set is the full static set
- this includes native tools plus MCP tools

This deliberately preserves current AgentFlow semantics.

### Session initialization

When `mcp` is included in `resource_types`:

1. AgentFlow creates an `mcp` session through normal backend initialization
2. `MCPBackend.initialize()` prepares a workspace under `workspace_root`
3. optional task setup is run:
   - copy `initial_workspace`
   - run `preprocess/main.py`
4. enabled MCP server YAML configs are resolved
5. MCP clients are started and connected
6. session state stores:
   - workspace path
   - resolved task directory
   - server registry
   - MCP client handles

### Tool execution

When the agent calls an MCP tool:

1. AgentFlow resolves the tool name to the `mcp` resource
2. the registered MCP bridge tool parses the server and tool portion
3. the backend finds the matching MCP client from session state
4. the backend sends an MCP `tools/call`
5. the MCP result is wrapped into AgentFlow's normal response format

### Cleanup

`MCPBackend.cleanup()` should:

- close MCP client connections
- terminate MCP subprocesses
- release temporary handles

Workspace contents should remain by default for debugging and task-output inspection.

## Parameter Coverage

The Toolathlon-GYM MCP YAMLs currently rely on these template variables:

- `${local_servers_paths}`
- `${agent_workspace}`
- `${task_dir}`

No additional MCP template-variable family was found in the current repository scan.

The design must also handle runtime environment overrides because some MCP configs or preprocess logic assume hostnames such as:

- `postgres`
- `toolathlon_pg`
- `localhost:8080`
- `localhost:8081`

## Error Handling

### Configuration errors

Fail session initialization if:

- `toolathlon_root` is missing or invalid
- a configured MCP server name is unknown
- required YAML/config files cannot be found

### Task-context errors

Fail session initialization if task-specific requirements are missing, such as:

- missing `task_dir`
- missing `email_config.json` when required
- failed `preprocess/main.py`

### MCP startup errors

Fail session initialization if an enabled MCP server cannot:

- start
- initialize
- return `tools/list`

### Tool call errors

Do not destroy the whole `mcp` session on a single tool failure.

Return a normal AgentFlow tool error for:

- unsupported tool name
- disabled server
- MCP `tools/call` error
- timeout

### Visibility/runtime mismatch

If a prompt-visible MCP tool belongs to a server that is not enabled at runtime, return an explicit runtime error such as:

`MCP server 'notion' is not enabled in the current session`

## Testing Strategy

### Static schema tests

Verify:

- MCP schemas are included in `get_tool_schemas()`
- MCP tools participate in `available_tools` filtering
- name matching works for expected MCP prefixes

### Backend initialization tests

Verify:

- valid `mcp` config creates a session
- invalid MCP server names fail fast
- workspace creation works
- task context wiring works

### Runtime smoke tests

Add smoke coverage for a small representative set first:

- `filesystem`
- `terminal`
- `snowflake`
- `emails`
- `excel`

These tests should execute through AgentFlow, not only through Toolathlon-GYM's own MCP tester.

### End-to-end agent tests

Run at least small prompt-to-tool-call flows where:

- MCP tools appear in the prompt tool list
- the model calls one or more MCP tools
- the sandbox executes them successfully

## Accepted Trade-Offs

This design intentionally preserves some existing AgentFlow behavior:

- prompt-visible tools may exceed runtime-enabled tools
- MCP schemas are static rather than live-discovered
- `available_tools = []` means full static visibility, not strict runtime visibility

These are intentional choices to preserve compatibility and minimize architectural change.

## Alternatives Considered

### 25 independent MCP backends

Rejected because it duplicates connection management, schema handling, and cleanup logic.

### Runtime-discovered MCP schemas only

Rejected because it would require a larger rethink of AgentFlow's current static prompt-tool model.

### Conditional MCP schema inclusion

Rejected because the user explicitly chose to preserve the current globally static semantics.

## Implementation Outline

1. Add MCP static schema module and merge it into the existing tool schema registry.
2. Add `MCPBackend` as a new backend resource.
3. Implement YAML resolution and MCP client startup using Toolathlon-GYM conventions.
4. Add session-time task context support.
5. Add sandbox config template for MCP usage.
6. Add static, backend, and smoke tests.

## Open Risks

- Toolathlon-GYM MCP schemas may drift over time from the static AgentFlow copy.
- Some MCP servers may have environment assumptions that differ across host and container setups.
- Prompt quality may degrade when all MCP tools are visible with `available_tools = []`, but this is consistent with the preserved AgentFlow model.

## Decision

Proceed with:

- global static MCP schema inclusion
- one runtime `MCPBackend`
- no behavior change for native environments
- no attempt to fix existing global static visibility semantics during this feature
