# MCPAgent: MCP Data Synthesis Guide (Canvas Example)

This guide explains how to use AgentFlow's MCP backend to synthesize QA and trajectory data from the MCP server snapshots integrated into this repo. It focuses on the data synthesis flow and uses Canvas communication as a concrete example.

AgentFlow itself only talks to the MCP endpoints configured in `configs/sandbox-server/mcp_config.json`. Those endpoints can point either to real services or to an optional local mock runtime.

Note: this guide covers data synthesis only. It does not cover model training or deployment.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Overview](#pipeline-overview)
- [Step 1: Prepare MCP Endpoints](#step-1-prepare-mcp-endpoints)
- [Step 2: Start the Sandbox Server](#step-2-start-the-sandbox-server)
- [Step 3: Synthesize QA Data](#step-3-synthesize-qa-data)
- [Configuration Reference](#configuration-reference)
- [FAQ](#faq)

---

## Overview

AgentFlow's MCP backend wraps a set of MCP servers behind the sandbox server. The synthesis pipeline then samples tool-use trajectories and turns them into QA data.

For the Canvas communication example in this repo, the relevant synthesis config is:

- `configs/synthesis/mcp.json`

The sandbox entrypoint is:

- `configs/sandbox-server/mcp_config.json`

At a high level, the flow is:

```
MCP endpoints -> Sandbox server (MCP backend) -> Synthesis pipeline -> QA + trajectories
```

The important boundary is that AgentFlow only sees endpoint values. It does not need to know whether those endpoints are backed by real APIs or by a local mock runtime.

---

## Prerequisites

### 1) Install AgentFlow

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

### 2) Configure LLM credentials

The example Canvas synthesis config reads its API key from the environment:

```bash
export OPENROUTER_API_KEY='YOUR_KEY'
```

If you change the model or provider, update `model_name`, `api_key`, and `base_url` in `configs/synthesis/mcp.json` accordingly.

### 3) Prepare seed data

The Canvas example uses a JSONL seed file. By default, the path comes from the `seeds_file` field in `configs/synthesis/mcp.json`. You can keep that default or override it with `--seeds`.

This file uses JSONL format, one JSON object per line. Example:

```jsonl
{"content":"Communication triage: instructors with large Canvas courses want an agent to inspect inbox conversations, course context, announcements, discussion topics, and gradebook signals to decide which student communications need attention.","kwargs":{}}
```

You can reuse the provided file or replace it with your own JSONL file and pass it through `--seeds`.

### 4) MCP server snapshots are already wired in

For the MCP integration in this repo, the copied MCP server snapshots and the main mock database snapshot from [toolathlon_gym](https://github.com/eigent-ai/toolathlon_gym) have already been wired in. You do not need to manually copy vendor resources or import database snapshots before running the example below.

If you choose the optional mock runtime, its shim scripts still expect `TOOLATHLON_GYM_ROOT` to point at the exported MCP server snapshot root directory.

### 5) Choose endpoint source: real services or optional mock runtime

`configs/sandbox-server/mcp_config.json` reads these AgentFlow-side endpoint variables:

- `AGENTFLOW_MCP_CANVAS_ENDPOINT`
- `AGENTFLOW_MCP_NOTION_ENDPOINT`
- `AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT`

These are just endpoint values. They can point to real services, or to the optional local mock runtime described below.

#### Option A: Point AgentFlow at real services

Export whichever endpoints you want AgentFlow to use:

```bash
export AGENTFLOW_MCP_CANVAS_ENDPOINT='canvas.example.edu:443'
export AGENTFLOW_MCP_NOTION_ENDPOINT='https://notion.example.internal'
export AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT='https://shop.example.internal'
```

#### Option B: Start the optional local mock runtime

The mock runtime is extra infrastructure. AgentFlow does not depend on it unless you choose to point the MCP endpoints at it.

The mock runtime in this repo uses the copied mock database setup and local HTTP shims from [toolathlon_gym](https://github.com/eigent-ai/toolathlon_gym) for:

- `canvas`
- `notion`
- `woocommerce`

It also requires local `docker compose`, `node`, and the exported MCP server snapshot root referenced by `TOOLATHLON_GYM_ROOT`.

1. Copy the mock runtime env file:

```bash
cp sandbox/server/backends/resources/mcp/mock_runtime/.env.example \
  sandbox/server/backends/resources/mcp/mock_runtime/.env
```

2. Generate a local Canvas TLS certificate and key:

```bash
mkdir -p sandbox/server/backends/resources/mcp/mock_runtime/certs

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout sandbox/server/backends/resources/mcp/mock_runtime/certs/canvas-key.pem \
  -out sandbox/server/backends/resources/mcp/mock_runtime/certs/canvas-cert.pem \
  -subj "/CN=127.0.0.1" \
  -days 365 \
  -addext "subjectAltName=IP:127.0.0.1,DNS:localhost"
```

3. Export the MCP server snapshot root used by the runtime scripts:

```bash
export TOOLATHLON_GYM_ROOT=/path/to/exported_mcp_snapshot
```

4. If you keep the default local ports from `.env.example`, the MCP endpoint variables are optional because `mcp_config.json` already has matching fallbacks. Exporting them explicitly is still a good idea:

```bash
export AGENTFLOW_MCP_CANVAS_ENDPOINT='127.0.0.1:38080'
export AGENTFLOW_MCP_NOTION_ENDPOINT='http://127.0.0.1:38081'
export AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT='http://127.0.0.1:38082'
```

5. Start the mock runtime:

```bash
bash sandbox/server/backends/resources/mcp/mock_runtime/scripts/start_mock_runtime.sh
```

6. Check runtime health:

```bash
bash sandbox/server/backends/resources/mcp/mock_runtime/scripts/status_mock_runtime.sh
```

For more detail on the mock runtime, see `sandbox/server/backends/resources/mcp/mock_runtime/README.md`.

---

## Pipeline Overview

The MCP synthesis pipeline in this repo is:

```
Endpoint preparation
  -> Sandbox server with MCP backend
  -> Trajectory tree sampling
  -> Trajectory selection
  -> QA synthesis
  -> synthesized_qa.jsonl + trajectories.jsonl
```

For the Canvas example, the synthesis config already points at the MCP sandbox config:

- `sandbox_config_path = configs/sandbox-server/mcp_config.json`

It also enables sandbox auto-start:

- `sandbox_auto_start = true`

That means you can either start the sandbox server yourself first, or let the synthesis pipeline start it when needed.

---

## Step 1: Prepare MCP Endpoints

Before starting the sandbox, make sure the MCP endpoints referenced by `configs/sandbox-server/mcp_config.json` resolve to something reachable.

You have two supported choices:

1. Real service endpoints
2. The optional local mock runtime

For the Canvas example, either choice is valid. AgentFlow only sees endpoint values and sends requests to them through the MCP backend.

---

## Step 2: Start the Sandbox Server

Start the sandbox server with the MCP backend config:

```bash
./start_sandbox_server.sh --config configs/sandbox-server/mcp_config.json
```

Optional health check:

```bash
curl http://127.0.0.1:18890/health
```

Expected result:

```json
{"status":"healthy"}
```

If you prefer, you can skip this manual step and rely on `sandbox_auto_start=true` in the synthesis config.

---

## Step 3: Synthesize QA Data

Use the MCP synthesis config as the example entrypoint:

- `configs/synthesis/mcp.json`

Run:

```bash
python -m synthesis.pipeline \
  --config configs/synthesis/mcp.json \
  --seeds /path/to/canvas_communication.jsonl \
  --output-dir results/canvas_communication
```

This produces:

- `results/canvas_communication/synthesized_qa.jsonl`
- `results/canvas_communication/trajectories.jsonl`

If you want to use the default seed file from `configs/synthesis/mcp.json`, you can omit `--seeds`. If you want a smaller smoke run, create a short JSONL file with one or a few seeds and pass that path through `--seeds`.

---

## Configuration Reference

### MCP sandbox config

File:

- `configs/sandbox-server/mcp_config.json`

Key fields:

- `resources.mcp.config.enabled_mcp_servers`: MCP servers to enable inside the backend
- `resources.mcp.config.workspace_root`: working directory exposed to MCP servers that need local workspace access
- `resources.mcp.config.env_overrides`: maps AgentFlow-side endpoint variables to the native environment variables expected by each MCP server
- `warmup.enabled` / `warmup.resources`: optional sandbox warmup configuration

The current endpoint mapping is:

- `AGENTFLOW_MCP_CANVAS_ENDPOINT -> CANVAS_DOMAIN`
- `AGENTFLOW_MCP_NOTION_ENDPOINT -> BASE_URL`
- `AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT -> WORDPRESS_SITE_URL`

### Canvas synthesis config

File:

- `configs/synthesis/mcp.json`

Key fields:

- `model_name`, `api_key`, `base_url`: LLM configuration
- `sandbox_server_url`: sandbox server address
- `sandbox_auto_start`: whether the synthesis pipeline should start the sandbox automatically
- `sandbox_config_path`: sandbox config path used when auto-start is enabled
- `available_tools`: tool families exposed to the synthesis agent
- `seeds_file`: default seed JSONL path
- `max_depth`, `branching_factor`, `max_selected_traj`: trajectory sampling and selection controls

---

## FAQ

### 1) Is the mock runtime required?

No. The mock runtime is optional. You can point AgentFlow at real MCP-backed services instead.

### 2) Does AgentFlow know whether it is talking to a real service or a mock backend?

No. AgentFlow only uses the endpoint values configured for the MCP backend.

### 3) Why does the Canvas endpoint look different from Notion and WooCommerce?

The AgentFlow-side names are unified as `AGENTFLOW_MCP_*_ENDPOINT`, but the underlying MCP servers expect different native variables. In the current config, Canvas is passed through `CANVAS_DOMAIN`, while Notion and WooCommerce expect full base URLs.

### 4) Do I have to start the sandbox server manually?

No. The provided Canvas synthesis config already has `sandbox_auto_start=true`. Manual startup is still useful when you want to separate sandbox bring-up from synthesis execution.

### 5) What should I check if synthesis fails after the sandbox starts?

Check the following first:

- the MCP endpoints resolve to reachable services
- `OPENROUTER_API_KEY` or your chosen provider credentials are set correctly
- your seed file path is correct
- the selected model/provider combination is compatible with your synthesis workload
