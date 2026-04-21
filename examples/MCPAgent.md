# MCPAgent: MCP Tool Agent — 3-Step Example Guide (No Training/Deployment/Inference)

This guide explains how to use AgentFlow's MCP example pipeline to generate QA data and trajectory data for six domains: `canvas`, `snowflake`, `woocommerce`, `yahoo_finance`, `youtube`, and `train`.

This example is intentionally limited to sandbox startup, QA synthesis, and trajectory rollout. Later training, deployment, and infer workflows are not covered yet.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Overview](#pipeline-overview)
- [Step 1: Start the Sandbox Server](#step-1-start-the-sandbox-server)
- [Step 2: Synthesize QA Data](#step-2-synthesize-qa-data)
- [Step 3: Synthesize Trajectory Data](#step-3-synthesize-trajectory-data)
- [Configuration Reference](#configuration-reference)
- [FAQ](#faq)

---

## Overview

MCPAgent is an example agent that talks to Toolathlon-GYM MCP servers through AgentFlow's sandbox server. The shared sandbox config is `configs/sandbox-server/mcp_config.json`, and the MCP server bundle is resolved from `${TOOLATHLON_GYM_ROOT}/local_servers`.

The current example scope covers six domains:

- `canvas`
- `snowflake`
- `woocommerce`
- `yahoo_finance`
- `youtube`
- `train`

## Prerequisites

Before running the example:

- `cd AgentFlow`
- `export OPENAI_API_KEY=...`
- `export OPENAI_API_URL=...`
- `export TOOLATHLON_GYM_ROOT=/path/to/toolathlon_gym`
- Have an already prepared and already running Toolathlon-GYM environment
- Ensure `node` and `uv` are installed

## Pipeline Overview

The verified MCP example pipeline in this repo is:

```text
Sandbox Setup -> QA Synthesis -> Trajectory Rollout
```

All synthesis configs use the shared sandbox config `configs/sandbox-server/mcp_config.json`. The example stops after QA synthesis and trajectory rollout, so training, deployment, and infer/evaluation flows are not covered.

## Step 1: Start the Sandbox Server

Start the sandbox server once before running synthesis or rollout:

```bash
./start_sandbox_server.sh --config configs/sandbox-server/mcp_config.json
```

## Step 2: Synthesize QA Data

Run the synthesis pipeline once per domain:

```bash
python3 synthesis/pipeline.py \
  --config configs/synthesis/mcp_canvas_config.json \
  --seeds seeds/mcp/canvas_seeds.jsonl \
  --output-dir results/mcp_canvas

python3 synthesis/pipeline.py \
  --config configs/synthesis/mcp_snowflake_config.json \
  --seeds seeds/mcp/snowflake_seeds.jsonl \
  --output-dir results/mcp_snowflake

python3 synthesis/pipeline.py \
  --config configs/synthesis/mcp_woocommerce_config.json \
  --seeds seeds/mcp/woocommerce_seeds.jsonl \
  --output-dir results/mcp_woocommerce

python3 synthesis/pipeline.py \
  --config configs/synthesis/mcp_yahoo_finance_config.json \
  --seeds seeds/mcp/yahoo_finance_seeds.jsonl \
  --output-dir results/mcp_yahoo_finance

python3 synthesis/pipeline.py \
  --config configs/synthesis/mcp_youtube_config.json \
  --seeds seeds/mcp/youtube_seeds.jsonl \
  --output-dir results/mcp_youtube

python3 synthesis/pipeline.py \
  --config configs/synthesis/mcp_train_config.json \
  --seeds seeds/mcp/train_seeds.jsonl \
  --output-dir results/mcp_train
```

> Note: in this repo, synthesis currently writes to the fixed aggregation directory `results/ds_synthesized_qa/`, even if you provide a different `--output-dir`.

- QA: `results/ds_synthesized_qa/synthesized_qa.jsonl`
- Trajectory: `results/ds_synthesized_qa/trajectories.jsonl`

These runs synthesize QA pairs and save the corresponding tool-use traces for the selected MCP domain.

## Step 3: Synthesize Trajectory Data

Run the rollout pipeline for trajectory-only data:

```bash
python -m rollout.pipeline \
  --config configs/trajectory/mcp_canvas_trajectory.json \
  --output-dir trajectory_results/mcp_canvas

python -m rollout.pipeline \
  --config configs/trajectory/mcp_snowflake_trajectory.json \
  --output-dir trajectory_results/mcp_snowflake

python -m rollout.pipeline \
  --config configs/trajectory/mcp_woocommerce_trajectory.json \
  --output-dir trajectory_results/mcp_woocommerce

python -m rollout.pipeline \
  --config configs/trajectory/mcp_yahoo_finance_trajectory.json \
  --output-dir trajectory_results/mcp_yahoo_finance

python -m rollout.pipeline \
  --config configs/trajectory/mcp_youtube_trajectory.json \
  --output-dir trajectory_results/mcp_youtube

python -m rollout.pipeline \
  --config configs/trajectory/mcp_train_trajectory.json \
  --output-dir trajectory_results/mcp_train
```

This stage produces rollout trajectories only. Training, deployment, and infer-oriented serving flows are not covered in this example yet.

## Configuration Reference

### Shared Sandbox Config

File: `configs/sandbox-server/mcp_config.json`

Important fields:

- `mcp_servers_path`: `${TOOLATHLON_GYM_ROOT}/local_servers`
- `enabled_mcp_servers`: includes the concrete MCP server identifiers from `configs/sandbox-server/mcp_config.json`, plus shared helpers such as `filesystem` and the YouTube transcript server. Most example domains use the same name as the server, but some differ: `yahoo_finance -> yahoo-finance` and `train -> rail_12306`.
- `env_overrides`: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `CANVAS_DOMAIN`, `WORDPRESS_SITE_URL`

### Synthesis Configs

Files:

- `configs/synthesis/mcp_canvas_config.json`
- `configs/synthesis/mcp_snowflake_config.json`
- `configs/synthesis/mcp_woocommerce_config.json`
- `configs/synthesis/mcp_yahoo_finance_config.json`
- `configs/synthesis/mcp_youtube_config.json`
- `configs/synthesis/mcp_train_config.json`

These configs point to the shared MCP sandbox and the domain-specific seeds for QA synthesis.

### Trajectory Configs

Files:

- `configs/trajectory/mcp_canvas_trajectory.json`
- `configs/trajectory/mcp_snowflake_trajectory.json`
- `configs/trajectory/mcp_woocommerce_trajectory.json`
- `configs/trajectory/mcp_yahoo_finance_trajectory.json`
- `configs/trajectory/mcp_youtube_trajectory.json`
- `configs/trajectory/mcp_train_trajectory.json`

These configs run trajectory-only rollout for each MCP domain.

## FAQ

### What does this example cover?

It covers sandbox startup, QA synthesis, and trajectory rollout for the six MCP domains in this repo.

### Which external tools do I need ready first?

You need a prepared Toolathlon-GYM environment, plus `node` and `uv`, because the MCP backend launches Toolathlon-GYM local servers from `${TOOLATHLON_GYM_ROOT}/local_servers`.

### Why are training and deployment missing?

This example is scoped to data generation only. Later training, deployment, and infer/evaluation workflows are not covered yet.
