## MCP and Coding Examples Design

Date: 2026-04-20
Status: Approved for planning

## Summary

AgentFlow now has MCP and `code` backends, but the repository still lacks official example guides and matching example assets for them. This design adds two new examples that stay aligned with the current example set in structure, tone, and scope:

- `examples/MCPAgent.md`
- `examples/CodingAgent.md`

Both examples will follow the lighter three-step pattern already used by `DSAgent`:

- Step 1: Start the Sandbox Server
- Step 2: Synthesize QA Data
- Step 3: Synthesize Trajectory Data

They will ship with the configs, seeds, and benchmark files needed to make those steps runnable.

## Problem Statement

The repository already contains:

- a working MCP backend with 25 Toolathlon-GYM MCP servers
- a working `code` backend with six coding tools
- sandbox config templates for both backends
- tests that prove both backends work at the backend level

What is missing is the user-facing example layer:

- no official `MCPAgent` example document
- no official `CodingAgent` example document
- no matching synthesis configs
- no matching trajectory configs
- no seeds for either example
- no benchmark data for MCP rollout
- no committed benchmark data for coding rollout

Without these assets, the new backends are discoverable in code but not presented as first-class AgentFlow example workflows.

## Goals

- Add official MCP and Coding example guides under `examples/`.
- Keep both guides stylistically aligned with the current example set.
- Keep document granularity aligned with current examples rather than exposing design or orchestration internals.
- Limit both examples to the currently practical scope: sandbox startup, QA synthesis, and trajectory rollout.
- Add the configs and data assets needed to support those examples.
- Use demo-scale seeds and benchmarks that are easy to run and verify.
- Make MCP example tasks operate against the initialized Toolathlon-GYM mock database.
- Make Coding example tasks operate against a known demo repository copied into the coding workspace.

## Non-Goals

- Do not turn either example into a full Toolathlon task replay framework.
- Do not document or expose internal validation strategy, subagent orchestration, or workspace isolation rationale in the example docs.
- Do not add Step 4 and Step 5 sections for training, deployment, or infer/eval.
- Do not introduce extra registry files or config-generation layers just to organize domains.
- Do not require MCP `task_dir`, `initial_workspace`, or `preprocess` flows for the example path.
- Do not make CodingAgent depend on an arbitrary external repository whose contents are unknown to the repository.

## User-Facing Outcome

After this work, the repository will present MCP and Coding the same way it already presents RAG, Doc, DS, and Text2SQL:

- a dedicated example document
- a sandbox config entry point
- a synthesis config
- a trajectory config
- seed data
- benchmark data where rollout needs it

The examples will read like the existing examples and will not require readers to understand internal backend architecture.

## Core Decisions

### 1. Both new examples use the three-step DS-style structure

`MCPAgent.md` and `CodingAgent.md` will both mirror the scope of `examples/DSAgent.md` rather than the five-step examples.

Each document will include:

- Overview
- Prerequisites
- Pipeline Overview
- Step 1: Start the Sandbox Server
- Step 2: Synthesize QA Data
- Step 3: Synthesize Trajectory Data
- Configuration Reference
- FAQ

Each document will explicitly note that the repository currently covers data synthesis and trajectory rollout for that example, but not the later training/deployment/infer stages as an official example workflow.

### 2. MCPAgent is a domain-level demo over the initialized Toolathlon-GYM database

The MCP example will use Toolathlon-GYM as the backing environment, but it will not replay full Toolathlon task directories.

Instead, it will use:

- the initialized Toolathlon-GYM mock PostgreSQL database
- the MCP servers exposed through AgentFlow
- small domain-level seeds
- small domain-level rollout benchmarks

This keeps the example aligned with the rest of the repository's example style while still using the real MCP domain data.

### 3. MCPAgent reuses `configs/sandbox-server/mcp_config.json`

The existing MCP sandbox config path remains the canonical entry point:

- `configs/sandbox-server/mcp_config.json`

This file will be updated so its default `enabled_mcp_servers` matches the exact server subset needed by the official example domains, rather than the full 25-server backend surface:

- `canvas`
- `snowflake`
- `woocommerce`
- `yahoo-finance`
- `youtube`
- `youtube-transcript`
- `rail_12306`
- `filesystem`

This keeps Step 1 aligned with the example scope while still allowing all six documented domains to run from the shared MCP sandbox entry point.

This is an intentional example-oriented default, not a removal of backend capability. The current checked-in `mcp_config.json` already enables only a subset of servers today, and full-surface MCP usage will remain available by expanding `enabled_mcp_servers` in the same file or in a user-local copy outside the official examples.

The same config will also define an explicit MCP server path contract so the checked-in MCP YAMLs can resolve `${local_servers_paths}` at runtime. The planned default is an environment-backed path such as:

- `mcp_servers_path: "${TOOLATHLON_GYM_ROOT}/local_servers"`

The implementation will rely on the existing MCP backend translation layer: `ToolathlonGymBackend` passes `mcp_servers_path` into the MCP YAML loader, and that loader substitutes the value into `${local_servers_paths}` when resolving each bundled server YAML.
In other words, `mcp_servers_path` is the JSON config field name, while `${local_servers_paths}` is the existing MCP YAML placeholder name for the same `local_servers/` directory.

The current repository version of `configs/sandbox-server/mcp_config.json` does not yet define `mcp_servers_path`; adding that field is part of this example work.

No separate `mcp_all_config.json` or metadata registry file will be introduced.

### 4. MCP tool exposure is defined by server wildcard, not hand-picked tool names

For each MCP domain config, `available_tools` will expose tools via server wildcard patterns such as:

- `mcp:canvas.*`
- `mcp:snowflake.*`
- `mcp:filesystem.*`

This avoids silent omission of tools from an included MCP server namespace and keeps the config surface simple.

### 5. MCP resource init config stays minimal

The MCP backend supports session init fields such as:

- `task_dir`
- `copy_initial_workspace`
- `run_preprocess`
- `launch_time`

Those fields are only needed when running task-directory-style Toolathlon tasks.

For the MCP example path in this design, the session only needs a normal MCP workspace plus access to the initialized mock database through the configured MCP servers. Therefore:

- `resource_types` will include `["mcp"]`
- `resource_init_configs.mcp.content` will be omitted or empty in example configs

### 6. CodingAgent uses a repository-local demo repo via `source_dir`

The coding backend always creates its own workspace, but a meaningful coding task needs actual repository contents inside that workspace.

Therefore the official Coding example will use:

- a small demo repository committed inside AgentFlow
- `resource_types=["code"]`
- `resource_init_configs["code"]["content"]["source_dir"]` pointing to that demo repository through the explicit repo-root contract `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`

AgentFlow's config loader already expands `${VAR}` placeholders before backend initialization, so no new path resolver is needed for this contract. The official docs will require exporting `AGENTFLOW_REPO_ROOT` after `cd AgentFlow`, and Step 2 / Step 3 will use that variable consistently. Users can later replace `source_dir` with their own repository path, but the official example will ship with a known default so its seeds and benchmark remain correct.

### 7. CodingAgent uses demo-scale mixed tasks

CodingAgent will use a small mixed task set:

- read-only repository inspection tasks
- one or more controlled edit tasks with straightforward verification

This preserves the intended coding flavor without making the example depend on large or fragile repository setups.

### 8. Keep the docs at current example granularity

The example docs should not explain design trade-offs, internal isolation, subagent strategy, or backend reasoning unless the current example set already does so.

They should look and read like the existing repository examples:

- concrete commands
- config file references
- short explanations of required inputs
- key config field summaries
- brief FAQs

## MCPAgent Design

### Covered domains

The MCP example will cover the six data-rich Toolathlon-GYM domains already reflected in current MCP integration smoke tests:

- `canvas`
- `snowflake`
- `woocommerce`
- `yahoo_finance`
- `youtube`
- `train`

The docs will cover all six domains, but each domain is still a small demo workflow rather than a long end-to-end enterprise task.

Server name mapping will follow the current MCP backend naming:

- `yahoo_finance` uses MCP server `yahoo-finance`
- `train` uses MCP server `rail_12306`

### Sandbox prerequisites and server subset

`examples/MCPAgent.md` will document the minimum local prerequisites needed for Step 1 to be runnable:

- a local `toolathlon_gym` checkout that has already completed its own setup and is running before AgentFlow starts
- `TOOLATHLON_GYM_ROOT` pointing to that checkout
- the MCP server bundle reachable at `${TOOLATHLON_GYM_ROOT}/local_servers`
- required local runtimes such as `node` and `uv`
- the following planned example defaults in `configs/sandbox-server/mcp_config.json`:
  - `PGHOST=localhost`
  - `PGPORT=5432`
  - `PGUSER=eigent`
  - `PGPASSWORD=camel`
  - `PGDATABASE=toolathlon_gym`
  - `CANVAS_DOMAIN=localhost:8080`
  - `WORDPRESS_SITE_URL=http://localhost:8081`

AgentFlow will not bootstrap the Toolathlon-GYM services itself in the official example. If a local setup differs from those defaults, the doc will show them as explicit override points in `mcp_config.json`.

The checked-in MCP sandbox config will enable only the shared example subset listed in Core Decision 3, so warmup behavior matches the domains covered by the example doc.

### Files to add

Add:

- `examples/MCPAgent.md`
- `configs/synthesis/mcp_canvas_config.json`
- `configs/synthesis/mcp_snowflake_config.json`
- `configs/synthesis/mcp_woocommerce_config.json`
- `configs/synthesis/mcp_yahoo_finance_config.json`
- `configs/synthesis/mcp_youtube_config.json`
- `configs/synthesis/mcp_train_config.json`
- `configs/trajectory/mcp_canvas_trajectory.json`
- `configs/trajectory/mcp_snowflake_trajectory.json`
- `configs/trajectory/mcp_woocommerce_trajectory.json`
- `configs/trajectory/mcp_yahoo_finance_trajectory.json`
- `configs/trajectory/mcp_youtube_trajectory.json`
- `configs/trajectory/mcp_train_trajectory.json`
- `seeds/mcp/canvas_seeds.jsonl`
- `seeds/mcp/snowflake_seeds.jsonl`
- `seeds/mcp/woocommerce_seeds.jsonl`
- `seeds/mcp/yahoo_finance_seeds.jsonl`
- `seeds/mcp/youtube_seeds.jsonl`
- `seeds/mcp/train_seeds.jsonl`
- `benchmark/mcp_canvas_benchmark.jsonl`
- `benchmark/mcp_snowflake_benchmark.jsonl`
- `benchmark/mcp_woocommerce_benchmark.jsonl`
- `benchmark/mcp_yahoo_finance_benchmark.jsonl`
- `benchmark/mcp_youtube_benchmark.jsonl`
- `benchmark/mcp_train_benchmark.jsonl`

Modify:

- `configs/sandbox-server/mcp_config.json`

### Synthesis config shape

Each `configs/synthesis/mcp_<domain>_config.json` will follow the same structure as existing synthesis configs and will include:

- model settings
- sandbox settings
- `resource_types: ["mcp"]`
- `available_tools` using MCP server wildcards
- domain-specific `sampling_tips`
- domain-specific `synthesis_tips`
- small `qa_examples`
- `seeds_file`
- `output_dir`

These configs will rely on the shared MCP sandbox startup path above rather than redefining server startup details per domain.

### Trajectory config shape

Each `configs/trajectory/mcp_<domain>_trajectory.json` will follow the same shape as existing rollout trajectory configs and will include:

- `benchmark_name`
- model settings
- sandbox settings
- `resource_types: ["mcp"]`
- `available_tools` using MCP server wildcards
- `system_prompt`
- `data_path`
- `output_dir`
- `save_results`
- `save_trajectories`
- `trajectory_only: true`
- `evaluate_results: false`

### MCP domain tool exposure

Planned MCP wildcard exposure:

- `canvas`
  - `mcp:canvas.*`
  - `mcp:filesystem.*`

- `snowflake`
  - `mcp:snowflake.*`
  - `mcp:filesystem.*`

- `woocommerce`
  - `mcp:woocommerce.*`
  - `mcp:filesystem.*`

- `yahoo_finance`
  - `mcp:yahoo-finance.*`
  - `mcp:filesystem.*`

- `youtube`
  - `mcp:youtube.*`
  - `mcp:youtube-transcript.*`
  - `mcp:filesystem.*`

- `train`
  - `mcp:rail_12306.*`
  - `mcp:filesystem.*`

### Seeds and benchmark style

MCP seeds and benchmarks will be demo-scale and domain-focused.

They should validate that the MCP backend and domain server set work cleanly inside AgentFlow, not replicate the full complexity of Toolathlon task packs.

Expected MCP task style:

- query real mock data from the target domain
- optionally save a result artifact into the workspace through filesystem tools
- produce answers that are easy to verify in a small benchmark

Benchmark correctness will be defined by the final textual answer in each benchmark row. Workspace artifact creation is allowed as an illustrative side effect, but it is not required for benchmark success and will not be treated as a scoring criterion in the official example data.

Examples of target task shape:

- list a small set of course or user information from Canvas
- query a small Snowflake-backed table result
- inspect WooCommerce customer or order data
- fetch Yahoo Finance stock information
- search YouTube content or transcript metadata
- look up railway station or route information

### MCP example document shape

`examples/MCPAgent.md` will stay at the same granularity as current examples:

- one shared sandbox setup section
- one synthesis step covering all six domain configs
- one trajectory step covering all six domain configs
- a compact configuration reference
- a short FAQ

It will not explain internal domain orchestration, workspace strategy, or design rationale.

## CodingAgent Design

### Sandbox entry point

`examples/CodingAgent.md` will reuse the existing coding sandbox config entry point:

- `configs/sandbox-server/code_config.json`

Step 1 in the Coding example will start that config directly, matching the current repository pattern of reusing a checked-in sandbox config rather than introducing a second coding sandbox file.

### Files to add

Add:

- `examples/CodingAgent.md`
- `configs/synthesis/code_config.json`
- `configs/trajectory/code_trajectory.json`
- `seeds/code/seeds.jsonl`
- `seeds/code/seed/demo_repo/README.md`
- `seeds/code/seed/demo_repo/app.py`
- `seeds/code/seed/demo_repo/config/app_config.json`
- `seeds/code/seed/demo_repo/lib/helpers.py`
- `seeds/code/seed/demo_repo/tests/smoke_test.py`
- `benchmark/code_benchmark.jsonl`

The demo repository under `seeds/code/seed/demo_repo/` should be small, stable, and easy to understand.

### Synthesis config shape

`configs/synthesis/code_config.json` will follow existing synthesis config structure and include:

- model settings
- sandbox settings
- `resource_types: ["code"]`
- `resource_init_configs.code.content.source_dir` using the explicit repo-root contract `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`
- `available_tools: ["code-*"]`
- coding-specific `sampling_tips`
- coding-specific `synthesis_tips`
- small `qa_examples`
- `seeds_file`
- `output_dir`

### Trajectory config shape

`configs/trajectory/code_trajectory.json` will follow existing rollout config structure and include:

- `benchmark_name`
- model settings
- sandbox settings
- `resource_types: ["code"]`
- `resource_init_configs.code.content.source_dir` using the same explicit repo-root contract `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`
- `available_tools: ["code-*"]`
- coding-specific `system_prompt`
- `data_path`
- `output_dir`
- `save_results`
- `save_trajectories`
- `trajectory_only: true`
- `evaluate_results: false`

### Demo repository shape

The demo repository should be intentionally small and support both task types:

- repository inspection
- controlled edit and verification

The repo should include a few files such as:

- `README.md` describing the tiny app
- `app.py` as the main entry file
- `config/app_config.json` with one or two settings used by the app
- `lib/helpers.py` with at least one helper imported by `app.py`
- `tests/smoke_test.py` for a minimal verification path

The goal is not realism through size. The goal is stable, example-quality coding tasks.

### Seeds and benchmark style

Coding seeds should focus on repository understanding prompts.

Coding benchmark tasks should be few and simple, mixing:

- read-only tasks such as locating files, reading configuration values, or identifying relationships
- edit tasks such as replacing a placeholder string or updating a simple setting

The benchmark should be authored against the committed demo repository so expected answers remain stable.

Benchmark contract:

- read-only tasks will use the standard `id` + `question` + `answer` shape
- edit tasks will still run under `trajectory_only: true` and `evaluate_results: false`, so they are for trajectory capture rather than auto-grading
- edit-task rows will include a short expected completion statement in `answer` plus metadata such as `target_files` and `check_command` to document the intended post-run verification path
- those extra verification fields will live under benchmark `metadata`, so existing rollout loaders can safely ignore them
- the recommended verification path for edit tasks will be the committed `tests/smoke_test.py`, not rollout-time automatic scoring

### Coding example document shape

`examples/CodingAgent.md` will mirror the style and scope of `examples/DSAgent.md`:

- Overview
- Prerequisites
- Pipeline Overview
- Step 1: Start the Sandbox Server
- Step 2: Synthesize QA Data
- Step 3: Synthesize Trajectory Data
- Configuration Reference
- FAQ

It will explicitly state that the repository currently covers data synthesis and trajectory rollout for this coding example, but not later training/deployment/infer steps as part of the official example.

## Validation Expectations

The implementation should be considered correct only if:

- the new example docs match the style and granularity of current examples
- the new configs parse successfully
- `configs/sandbox-server/mcp_config.json` resolves MCP server executables through the documented `TOOLATHLON_GYM_ROOT` contract
- MCP synthesis and rollout configs align with the real MCP backend surface
- Coding synthesis and rollout configs align with the real code backend surface
- the demo seeds and benchmarks are internally consistent with the assets they target
- representative runs can be executed by following the example documents
- Coding Step 1, QA synthesis, and rollout remain runnable when the documented `cd AgentFlow` plus `export AGENTFLOW_REPO_ROOT=$(pwd)` prerequisite is followed

## Open Questions Resolved

- Use `configs/sandbox-server/mcp_config.json` directly: yes
- Add a separate MCP registry file: no
- Use server wildcards instead of hand-picked MCP tool names: yes
- Use Toolathlon task-directory initialization for the example path: no
- Use Toolathlon-GYM mock database as the MCP data source: yes
- Add official infer/eval steps for MCP or Coding examples: no
- Use a repository-local demo repo for CodingAgent: yes

## Implementation Readiness

This design is ready for implementation planning. The work is focused, bounded, and does not require redesigning backend behavior. The main deliverables are user-facing docs, example configs, and small example data assets.
