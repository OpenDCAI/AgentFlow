# 📊 DSAgent: CSV / Table Data Agent — Data Synthesis Guide (No Training/Deployment)

This guide is based on [WebAgent.md](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/examples/WebAgent.md). It explains how to use AgentFlow’s **DS toolchain** to generate **QA** and **Trajectory** data grounded in local CSV files.

Note: This repository currently covers **data synthesis (QA + trajectories)** only. **Model training and deployment (vLLM)** have not been done, so this guide intentionally does **not** include “Step 4 / Step 5”.

## 📋 Table of Contents

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

DSAgent is a **CSV/table data analysis agent**. It performs multi-step reasoning by calling DS tools (dataset inspection, CSV preview, Python execution in sandbox), and then synthesizes QA pairs and trajectories from those tool-use traces.

AgentFlow provides 3 core tools for DS (tool names should not include `:`):

| Tool | Description | Parameters |
|------|-------------|------------|
| `ds_inspect_data` | Scan the dataset directory and summarize CSV schemas/shapes/missingness | none |
| `ds_read_csv` | Preview the first N rows of a CSV | `csv_file`, `max_rows` |
| `ds_run_python` | Run Python in sandbox (pandas/numpy/sklearn, etc.) for analysis | `code`, `return_vars` (optional) |

---

## Prerequisites

### 1) Install AgentFlow

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

### 2) Configure LLM credentials (recommended: env vars)

The DS configs in this repo are set up to read credentials from environment variables (to avoid committing secrets).

```bash
export OPENAI_API_KEY='YOUR_KEY'
export OPENAI_API_URL='https://openrouter.ai/api/v1'
```

Relevant config files:
- DS Sandbox: [configs/sandbox-server/ds_config.json](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/configs/sandbox-server/ds_config.json)
- DS Synthesis: [configs/synthesis/ds_config.json](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/configs/synthesis/ds_config.json)

### 3) Prepare seed data (CSV input directory)

DS seeds use JSONL format (one JSON object per line). The key field is `kwargs.seed_path`, which must point to the **directory containing the CSV files**.

Example:

```jsonl
{"content": "Analyze the data in the provided CSV files.", "kwargs": {"seed_path": "seeds/ds/seed"}}
```

- `content`: starting description that guides what to explore/analyze
- `kwargs.seed_path`: CSV directory path (relative or absolute)

Default DS seed file:
- [seeds/ds/seeds.jsonl](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/seeds/ds/seeds.jsonl)

---

## Pipeline Overview

The DS synthesis pipeline (verified in this repo):

```
Sandbox Setup → QA Synthesis (+ Trajectories)
```

Internally, the QA synthesis flow is the same pattern as WebAgent:

```
Seed → Trajectory Tree Sampling (TrajectorySampler)
     → Trajectory Selection (TrajectorySelector)
     → QA Synthesis (QASynthesizer)
     → Output synthesized_qa.jsonl + trajectories.jsonl
```

---

## Step 1: Start the Sandbox Server

The sandbox server provides the execution environment for DS tools (`ds_inspect_data / ds_read_csv / ds_run_python`).

**Command:**

```bash
./start_sandbox_server.sh --config configs/sandbox-server/ds_config.json
```

> Note: you can also enable `sandbox_auto_start=true` in synthesis/rollout configs to auto-start the sandbox (you will see the server being started in logs).

---

## Step 2: Synthesize QA Data

This step generates QA pairs grounded in the CSV directory specified by `seed_path`, and also saves the corresponding trajectories.

### Run (CLI)

```bash
python3 synthesis/pipeline.py \
  --config configs/synthesis/ds_config.json \
  --seeds seeds/ds/seeds.jsonl \
  --output-dir results/any_dir
```

> Note: in this repo, the code redirects the output directory to a fixed aggregation directory `results/ds_synthesized_qa/` so runs append incrementally into the same files.

### Output files (aggregation directory)

- QA: `results/ds_synthesized_qa/synthesized_qa.jsonl`
- Trajectory: `results/ds_synthesized_qa/trajectories.jsonl`

(Both files are written in **append mode**.)

---

## Step 3: Synthesize Trajectory Data

If you want to run a benchmark “rollout” to generate **trajectory-only** data (without QA synthesis), use the rollout pipeline (same idea as WebAgent).

Config file:
- [configs/trajectory/ds_trajectory.json](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/configs/trajectory/ds_trajectory.json)

Run:

```bash
python -m rollout.pipeline \
  --config configs/trajectory/ds_trajectory.json \
  --output-dir trajectory_results/ds
```

Notes:
- With `trajectory_only=true`, rollout saves trajectories and skips evaluation.
- Inference/evaluation typically requires a callable inference endpoint plus benchmarks with ground-truth answers. This guide does not cover that because training/deployment is not part of the current scope.

---

## Configuration Reference

### DS Sandbox Config

File: [configs/sandbox-server/ds_config.json](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/configs/sandbox-server/ds_config.json)

Key fields:
- `server.url / server.port`: sandbox host and port
- `apis.ds.openai_api_key / apis.ds.openai_api_url`: used for LLM summaries (recommended via env vars)

### DS Synthesis Config

File: [configs/synthesis/ds_config.json](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/configs/synthesis/ds_config.json)

Key fields:
- `model_name / api_key / base_url`: LLM config (OpenAI-compatible)
- `available_tools`: must include `ds_inspect_data / ds_read_csv / ds_run_python`
- `seeds_file`: seed JSONL path
- `max_depth / branching_factor / max_selected_traj`: controls sampling depth/width and QA volume
- `sampling_tips / synthesis_tips`: guidance/constraints for exploration and QA generation

---

## FAQ

### 1) What is seed_path? What if it’s wrong?

`seed_path` must be the **directory containing your CSV files**. If it is wrong, tools won’t find the CSVs (e.g., `ds_read_csv` will report “File does not exist”).

### 2) What is rollout?

Rollout means running the agent on a question/benchmark with multi-step tool usage (forming a trajectory), producing an answer, and saving the full tool-use trace as trajectory data (useful for training, debugging, and reproducibility).

### 3) Why are Step 4/5 missing?

Because this repo has not performed model training and vLLM deployment, we intentionally do not include “training & deployment” or “inference & evaluation” steps in this DSAgent guide.
