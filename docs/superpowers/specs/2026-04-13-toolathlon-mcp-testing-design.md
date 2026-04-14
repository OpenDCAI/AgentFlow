# Toolathlon-GYM MCP Testing Design

Date: 2026-04-13
Status: Approved for planning

## Summary

Validate the new Toolathlon-GYM MCP integration in two layers:

- a server-layer test suite that proves AgentFlow can initialize real MCP servers and successfully dispatch real tool calls
- a domain-layer smoke suite that proves the integrated MCP stack can support representative multi-tool workflows across Toolathlon-GYM's six data domains

The server layer is the gate for correctness of the MCP backend itself. The domain layer is the gate for realism and task-level confidence.

## Goals

- Reuse AgentFlow's existing tests as the baseline regression suite.
- Keep the MCP-specific verification simple enough to run repeatedly during development.
- Distinguish "backend wiring is correct" from "representative workflows are viable".
- Allow safe parallel execution where MCP servers are isolated enough to avoid cross-test interference.
- Keep an explicit full-startup test for the combined MCP environment.

## Non-Goals

- Do not use one giant end-to-end benchmark run as the primary MCP correctness signal.
- Do not require every Toolathlon-GYM task to be executed during MCP validation.
- Do not assume all 25 MCP servers are equally safe to run in parallel.
- Do not treat data-domain tests as a replacement for per-server integration tests.

## Constraints

- AgentFlow's current rollout and sandbox tests remain part of the default verification baseline.
- Real MCP tests must use Toolathlon-GYM's checked-in server YAMLs and local server implementations.
- Parallel execution is opt-in and only applies to servers proven not to share unsafe mutable state.
- Combined "all enabled servers" startup verification must run serially.

## Recommended Approach

Adopt a two-layer MCP test strategy:

1. Existing AgentFlow tests remain the regression baseline.
2. Add MCP server-layer smoke tests for the real backend and real MCP servers.
3. Add MCP domain-layer smoke tests for the six Toolathlon-GYM data domains.
4. Classify each server as either:
   - `A`: safe to run in parallel as a single-server smoke case
   - `B`: run serially because parallel safety is unknown or false
5. Keep one serial "all enabled servers startup" test that validates the combined MCP configuration can initialize end-to-end.

This design keeps diagnosis crisp:

- server-layer failures indicate MCP backend/config/runtime wiring problems
- domain-layer failures indicate realistic workflow gaps
- all-servers startup failures indicate combined-environment fragility

## Layer 1: Server-Layer Validation

### Purpose

The server layer proves that AgentFlow's `MCPBackend` can:

- load real Toolathlon-GYM YAML configuration
- resolve placeholders correctly
- initialize real stdio MCP subprocesses
- store live clients in session state
- dispatch real tool calls through AgentFlow's bridge layer

This is the direct validation of the newly added MCP integration.

### Test Structure

Use one MCP E2E test module with three groups of tests:

1. Existing MCP unit/integration tests in `sandbox/tests/test_mcp_tool_schemas.py`, `sandbox/tests/test_mcp_client.py`, and `sandbox/tests/test_mcp_backend.py`
2. New real single-server smoke tests
3. New real all-servers startup smoke test

The new real smoke tests should build a backend session through `MCPBackend.initialize()` and call MCP bridge tools through AgentFlow's normal dispatch path.

### A/B Classification

Each MCP server belongs to exactly one class:

- `A`: safe for parallel single-server smoke execution
- `B`: serial only

`A` means all of the following are true:

- the server runs as an isolated stdio child process
- the test gives it a unique `workspace_root`, `worker_id`, and temporary directory
- the server does not rely on a fixed shared port or equivalent singleton process
- the server does not mutate shared external state in a way that can corrupt other tests

If any item is false, unknown, or expensive to prove, the server is `B`.

This makes classification intentionally conservative.

### Initial Classification Direction

Based on the current Toolathlon-GYM YAMLs:

- `filesystem` is a strong `A` candidate because it is stdio-based and scoped to `${agent_workspace}`
- `terminal` is also a strong `A` candidate because it is stdio-based and both `ALLOWED_DIR` and `cwd` are scoped to `${agent_workspace}`
- servers with fixed internal ports, shared browser state, shared credentials, or shared mutable external services should default to `B`

The classification artifact should live in code as a small maintained list, not in human memory.

### Single-Server Smoke Contract

Each server-layer smoke case should validate only the smallest useful real behavior:

- backend session initializes successfully with `enabled_mcp_servers=[server_name]`
- expected client handle exists in session state
- one representative MCP tool call succeeds
- the returned payload contains a minimal expected signal

Examples:

- `filesystem`: create a file in the per-test workspace, then list or read it
- `terminal`: run a stable command such as `pwd` or `printf`, then assert expected output
- data-backed servers: issue one read-only query or list-style tool call against the seeded local environment

### All-Servers Startup Test

Keep one serial combined startup test with all configured servers enabled.

Its purpose is narrower than the single-server suite:

- confirm the combined MCP configuration can initialize in one session
- confirm no server immediately breaks shared environment assumptions
- catch cross-server startup conflicts that do not appear in isolated tests

This test should focus on startup success and light sanity checks, not on exhaustively calling one tool from every server again.

## Layer 2: Domain-Layer Validation

### Purpose

Toolathlon-GYM defines six data domains backed by local datasets:

- `canvas`
- `snowflake`
- `woocommerce`
- `yahoo_finance`
- `youtube`
- `train`

These domains are business-data scenarios, not replacements for MCP server identities. They should therefore be tested as representative workflows, not as backend startup surrogates.

### Why Domain Tests Matter

Server-layer validation can show that `filesystem`, `terminal`, `emails`, or `snowflake` each work in isolation. It cannot show that the integrated environment behaves plausibly for real task shapes.

Domain-layer smoke tests fill that gap by validating a small number of realistic cross-tool flows, such as:

- read data from a domain source
- perform a lightweight transformation
- write or package output through one or two productivity/file tools

### Domain Smoke Design

Create one smoke scenario per domain. Each scenario should be intentionally small and deterministic.

Recommended domain patterns:

- `canvas`: read course or submission data and materialize a tiny report artifact
- `snowflake`: run a read-only query from one enterprise subdomain and write a compact result artifact
- `woocommerce`: read customers/orders and produce a lightweight summary file
- `yahoo_finance`: read a small slice of financial data and produce a normalized output artifact
- `youtube`: read channel/video/transcript metadata and store a compact summary
- `train`: query routes or schedules and write a structured trip summary

Each domain smoke should prefer:

- read-mostly behavior
- minimal output surface
- stable seeded data
- minimal dependence on LLM reasoning

The goal is to verify integrated toolchain viability, not agent intelligence.

## Execution Strategy

### Baseline

Run AgentFlow's existing tests plus the MCP unit/integration suite first. This protects against regressions before real-environment smoke tests begin.

### Controller and Subagent Model

The test system uses an explicit controller/subagent split.

The controller is responsible for all shared concerns:

- preparing and validating the shared base environment
- owning the authoritative `A`/`B` server classification
- deciding which server-layer cases may run in parallel
- creating per-case isolated runtime inputs such as workspace roots, worker IDs, temp directories, and logs
- owning shared base config, shared fixtures, shared environment variables, and shared infrastructure policy
- running the serial all-servers startup test

Subagents are workers for isolated test execution, not owners of the shared environment.

Subagents may:

- execute assigned single-server or domain smoke cases
- inspect failures within their assigned case
- modify only server-specific or case-specific test assets when explicitly allowed

Subagents may not:

- modify shared environment policy
- mutate shared base config or common fixtures used by unrelated cases
- change controller-owned port allocation or global isolation rules
- repair shared infrastructure from inside an isolated case

If a failure is traced to shared infrastructure, ownership returns to the controller. This keeps parallel work from corrupting the common environment.

### Parallel Policy

Parallelization is allowed only for `A`-class single-server smoke cases.

Serial execution is required for:

- every `B`-class server case
- the all-servers startup test
- any domain smoke test that depends on shared mutable infrastructure and has not been proven parallel-safe

### Isolation Requirements

Every real MCP smoke case must have:

- a unique test workspace root
- a unique worker ID
- a unique temporary directory tree
- unique test-local output paths and logs

Shared base infrastructure may be prepared once, but it must be treated as read-only by test cases.

## Error Handling and Diagnosis

Failures should be attributable to one layer whenever possible:

- if single-server smoke fails, treat it as a server/backend integration issue
- if all-servers startup fails but single-server smokes pass, treat it as a combined-environment interaction issue
- if domain smoke fails while server-layer tests pass, treat it as a workflow or data/tool-composition issue

Test output should clearly report:

- server name
- A/B class
- whether failure happened during initialization or tool execution
- workspace path or temp directory for debugging

## Verification Plan

Minimum validation before implementation is considered complete:

1. Existing AgentFlow baseline tests pass at the expected baseline level.
2. MCP unit/integration tests pass.
3. `filesystem` and `terminal` real single-server smokes pass.
4. The remaining servers are classified into `A` or `B`.
5. At least one serial all-servers startup test passes.
6. One smoke workflow for each of the six data domains passes.

## Open Decisions Resolved

The design adopts the following decisions from brainstorming:

- keep only two server classes: `A` and `B`
- use server-layer tests as the primary correctness gate for MCP integration
- use domain-layer tests as a second confidence layer, not as a replacement
- allow parallel execution only where safety is proven
- keep the combined all-servers startup check serial

## Next Step

After this design is approved and reviewed, write an implementation plan that:

- defines the concrete test files and fixtures
- specifies the initial `A`/`B` server list
- assigns exact smoke operations for each domain
- defines the local and CI execution commands
