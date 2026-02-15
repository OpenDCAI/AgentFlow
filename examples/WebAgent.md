# 🖱️ WebAgent: Deep Research Agent — Data Synthesis & Inference Guide

This guide walks through the full pipeline of using the AgentFlow framework with **WebAgent (Deep Research Agent)**, from data synthesis to model inference.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Overview](#pipeline-overview)
- [Step 1: Start the Sandbox Server](#step-1-start-the-sandbox-server)
- [Step 2: Synthesize QA Data](#step-2-synthesize-qa-data)
- [Step 3: Synthesize Trajectory Data](#step-3-synthesize-trajectory-data)
- [Step 4: Model Training & Deployment](#step-4-model-training--deployment)
- [Step 5: Inference & Evaluation](#step-5-inference--evaluation)
- [Configuration Reference](#configuration-reference)
- [FAQ](#faq)

---

## Overview

WebAgent is a **web-based deep research agent** that answers complex multi-hop reasoning questions by searching and browsing the internet. The pipeline has five stages:

```
Sandbox Setup → QA Synthesis → Trajectory Synthesis → Model Training → Inference & Evaluation
```

AgentFlow provides two core tools for WebAgent:

| Tool | Description | Parameters |
|------|-------------|------------|
| `web_search` | Batch web search, returns results for each query | `query`: array of search query strings |
| `web_visit` | Visit web pages and extract relevant content based on a goal | `urls`: array of URLs, `goal`: extraction objective |

---

## Prerequisites

1. **Install AgentFlow**

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

2. **Prepare API Keys**

The WebAgent Sandbox requires the following external services (configured in `configs/sandbox-server/web_config.json`):

- **Serper API Key**: For Google search ([serper.dev](https://serper.dev))
- **Jina API Key**: For web content extraction ([jina.ai](https://jina.ai))
- **OpenAI-compatible API Key**: For LLM calls (supports OpenRouter and other compatible endpoints)

3. **Prepare Seed Data**

Seed file is located at `seeds/web/seeds.jsonl`, one JSON object per line:

```jsonl
{"content": "Python programming language", "kwargs": {}}
{"content": "Machine learning", "kwargs": {}}
{"content": "Natural language processing", "kwargs": {}}
```

- `content` (required): A seed entity or topic. The agent will explore the web around this topic.
- `kwargs` (optional): Additional parameters, defaults to `{}`.

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AgentFlow WebAgent Pipeline                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Sandbox Server                                             │
│  ┌─────────────────┐                                                │
│  │  web_config.json │──▶ Start web_search / web_visit tool service  │
│  └─────────────────┘                                                │
│          │                                                          │
│          ▼                                                          │
│  Step 2: QA Synthesis                                               │
│  ┌─────────────────┐    ┌──────────┐    ┌───────────────────┐       │
│  │  web_config.json │──▶ │  Seeds   │──▶ │  synthesized_qa   │      │
│  └─────────────────┘    └──────────┘    │  + trajectories   │      │
│                                          └───────────────────┘      │
│          │                                                          │
│          ▼                                                          │
│  Step 3: Trajectory Rollout                                         │
│  ┌──────────────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  web_trajectory.json  │──▶ │  benchmark   │──▶ │  trajectory  │  │
│  └──────────────────────┘    └──────────────┘    │  results     │  │
│                                                   └──────────────┘  │
│          │                                                          │
│          ▼                                                          │
│  Step 4: Model Training & Serving (vLLM)                            │
│                                                                     │
│          │                                                          │
│          ▼                                                          │
│  Step 5: Inference & Evaluation                                     │
│  ┌──────────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  web_infer.json   │──▶ │  benchmark   │──▶ │  infer_results   │  │
│  └──────────────────┘    └──────────────┘    │  + evaluation    │  │
│                                               └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Start the Sandbox Server

The Sandbox server provides the tool execution environment (`web_search`, `web_visit`) for the agent.

**Command:**

```bash
./start_sandbox_server.sh --config configs/sandbox-server/web_config.json
```

> **Note:** `--port` and `--host` flags are ignored; use `server.url` / `server.port` in the config file instead.

**Config file** `configs/sandbox-server/web_config.json`:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "log_level": "DEBUG"
  },
  "apis": {
    "websearch": {
      "serper_api_key": "<YOUR_SERPER_API_KEY>",
      "jina_api_key": "<YOUR_JINA_API_KEY>",
      "visit_method": "jina",
      "content_limit": 50000,
      "enable_llm_summary": true,
      "summary_model": "openai/gpt-oss-120b",
      "openai_api_key": "<YOUR_OPENAI_API_KEY>",
      "openai_api_url": "https://openrouter.ai/api/v1"
    }
  }
}
```

**Key config fields:**

| Field | Description |
|-------|-------------|
| `server.url` | Sandbox server listen address |
| `server.port` | Server port (default `18890`) |
| `server.log_level` | Log level: `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `apis.websearch.serper_api_key` | Serper search API key |
| `apis.websearch.jina_api_key` | Jina web extraction API key |
| `apis.websearch.visit_method` | Web visit method, recommended `"jina"` |
| `apis.websearch.content_limit` | Max characters per extraction |
| `apis.websearch.enable_llm_summary` | Enable LLM summarization of extracted content |
| `apis.websearch.summary_model` | LLM model used for summarization |

**Verification:**

After startup, the terminal will display the listening port. Ensure the Sandbox server is running before proceeding to Steps 2–5.

---

## Step 2: Synthesize QA Data

### Prepare Seed Data

Seed data is the starting point for QA synthesis. Each seed represents a **topic or entity** (e.g., "Python programming language", "Machine learning"). The agent uses it as a starting point to perform multi-hop web exploration — searching the topic, visiting related pages, building information chains, and ultimately generating multi-hop reasoning QA pairs from the exploration trajectory.

In short: **Seeds determine where the agent starts exploring. Different seeds produce training data across different domains and topics.**

**Seed file format**

JSONL format (one JSON object per line), stored at `seeds/web/seeds.jsonl`:

```jsonl
{"content": "Python programming language", "kwargs": {}}
{"content": "Machine learning", "kwargs": {}}
{"content": "Natural language processing", "kwargs": {}}
{"content": "Deep learning frameworks", "kwargs": {}}
```

| Field | Required | Description |
|-------|----------|-------------|
| `content` | ✅ Yes | Seed topic or entity. The agent will search and explore the web around this topic. |
| `kwargs` | Optional | Extra parameter dict for custom info in the synthesis pipeline. Defaults to `{}`. |

Once seed data is ready, point the `seeds_file` field in `configs/synthesis/web_config.json` to your file path.

---

### Run QA Synthesis

This step uses an LLM agent to explore the web based on seed data and automatically generate high-quality multi-hop reasoning QA pairs.

**Core flow:**

```
Seed → Trajectory Tree Sampling (TrajectorySampler)
     → Trajectory Selection (TrajectorySelector)
     → QA Synthesis (QASynthesizer)
     → Output QA pairs + trajectories
```

**Usage:**

```python
from synthesis import synthesize

synthesize(config_path="configs/synthesis/web_config.json")
```

Or via CLI:

```bash
python -m synthesis.pipeline \
    --config configs/synthesis/web_config.json \
    --seeds seeds/web/seeds.jsonl \
    --output-dir synthesis_results
```

**Config file** `configs/synthesis/web_config.json` — key fields:

```json
{
  "model_name": "openai/gpt-oss-120b",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "https://openrouter.ai/api/v1",

  "max_depth": 50,
  "branching_factor": 2,
  "depth_threshold": 2,
  "min_depth": 3,
  "max_selected_traj": 2,
  "path_similarity_threshold": 0.7,

  "sandbox_server_url": "http://127.0.0.1:18890",
  "available_tools": ["web_search", "web_visit"],

  "sampling_tips": [
    "Explore deeply to build multi-hop reasoning chains",
    "Focus on gathering specific facts and evidence",
    "Use web tools to find relevant information",
    "Build dependency chains (A→B→C→D...)",
    "Capture hard metadata (dates, versions, IDs, counts)",
    "Use web_visit at least once to extract evidence from specific pages"
  ],

  "synthesis_tips": [
    "Create questions requiring multi-hop reasoning (>=3 hops)",
    "Keep questions concise (<=5 sentences)",
    "Answers should be specific facts (names, dates, locations)",
    "Ensure answer is grounded in trajectory evidence",
    "Provide clear reasoning steps",
    "Ensure web_visit evidence is required to answer"
  ],

  "seeds_file": "seeds/web/seeds.jsonl",
  "output_dir": "results"
}
```

**Config parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_name` | - | LLM model for synthesis (OpenAI-compatible format) |
| `max_depth` | `50` | Max exploration depth of the trajectory tree |
| `branching_factor` | `2` | Number of branches per node |
| `depth_threshold` | `2` | Min depth before branching starts |
| `min_depth` | `3` | Min depth for a trajectory to be selected |
| `max_selected_traj` | `2` | Max trajectories selected per seed |
| `path_similarity_threshold` | `0.7` | Similarity threshold for trajectory deduplication |
| `sampling_tips` | - | Hints guiding the agent's exploration behavior |
| `synthesis_tips` | - | Hints guiding QA generation |
| `seeds_file` | - | Path to seed data file (JSONL) |
| `sandbox_server_url` | `http://127.0.0.1:18890` | Sandbox server address (must match Step 1) |

**Output files:**

| File | Description |
|------|-------------|
| `results/synthesized_qa.jsonl` | Synthesized QA pairs (one JSON per line) |
| `results/trajectories.jsonl` | Corresponding agent exploration trajectories |

---

## Step 3: Synthesize Trajectory Data

This step runs the agent on benchmark data via the Rollout Pipeline to generate trajectory data for training.

**Usage:**

```python
from rollout import pipeline

pipeline(config_path="configs/trajectory/web_trajectory.json")
```

Or via CLI:

```bash
python -m rollout.pipeline \
    --config configs/trajectory/web_trajectory.json \
    --output-dir trajectory_results/web
```

**Config file** `configs/trajectory/web_trajectory.json` — key fields:

```json
{
  "benchmark_name": "web_trajectory",
  "model_name": "openai/gpt-oss-120b",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "https://openrouter.ai/api/v1",

  "max_turns": 40,
  "available_tools": ["web_search", "web_visit"],
  "sandbox_server_url": "http://127.0.0.1:18890",

  "system_prompt": [
    "You are a web research assistant that can search and browse the internet.",
    "",
    "## Available Tools",
    "1. web_search - Search the web with multiple queries",
    "2. web_visit - Visit web pages and extract content",
    "",
    "## Strategy",
    "1. Formulate effective search queries",
    "2. Search for relevant information",
    "3. Visit promising URLs to get detailed information",
    "4. Synthesize findings into a clear answer",
    "",
    "## Tips",
    "- Use specific, targeted queries",
    "- Visit multiple sources for verification",
    "- Provide clear, factual answers with sources"
  ],

  "evaluate_results": false,
  "data_path": "benchmark/web_benchmark.jsonl",
  "output_dir": "trajectory_results/web",

  "save_results": true,
  "save_trajectories": true,
  "trajectory_only": true
}
```

**Key config fields:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_turns` | `40` | Max conversation turns per task |
| `system_prompt` | - | Agent system prompt (string or string array) |
| `evaluate_results` | `false` | Only generates trajectories, no evaluation |
| `trajectory_only` | `true` | Save trajectories only (auto-disables evaluation) |
| `data_path` | - | Path to benchmark data file |

**Benchmark data format** (`benchmark/web_benchmark.jsonl`):

```jsonl
{"id": "web_001", "question": "What is the current population of Tokyo, Japan?", "answer": "approximately 14 million"}
{"id": "web_002", "question": "When was Python programming language first released?", "answer": "1991"}
```

Supported field aliases:
- `id` / `task_id`
- `question` / `query` / `input`
- `answer` / `ground_truth` / `expected`

**Output:**

Results are saved to `trajectory_results/web/`:

| File | Description |
|------|-------------|
| `results_web_trajectory_{timestamp}.jsonl` | Trajectory results for each task |

---

## Step 4: Model Training & Deployment

After training a model with data from Steps 2 and 3, deploy it using vLLM.

**Deploy with vLLM:**

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name webagent \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8222
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `--model` | Path to trained model or HuggingFace model name |
| `--served-model-name` | Model name exposed by the service, used in API calls |
| `--tensor-parallel-size` | Tensor parallelism size, set based on GPU count |
| `--enable-auto-tool-choice` | Enable automatic tool selection (required for agent scenarios) |
| `--tool-call-parser` | Tool call parser; WebAgent uses `hermes` format |
| `--port` | Service port |

Once deployed, the model serves an OpenAI-compatible API at `http://localhost:8222`.

---

## Step 5: Inference & Evaluation

Run inference on the benchmark with the trained model and evaluate results.

**Usage:**

```python
from rollout import pipeline

pipeline(config_path="configs/infer/web_infer.json")
```

**Config file** `configs/infer/web_infer.json` — key fields:

```json
{
  "benchmark_name": "web_infer",
  "model_name": "openai/gpt-oss-120b",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "https://openrouter.ai/api/v1",

  "max_turns": 40,
  "available_tools": ["web_search", "web_visit"],
  "sandbox_server_url": "http://127.0.0.1:18890",

  "evaluate_results": true,
  "evaluation_metric": "contains_answer",
  "evaluator_model_name": "openai/gpt-oss-120b",
  "evaluator_api_key": "<YOUR_API_KEY>",
  "evaluator_base_url": "https://openrouter.ai/api/v1",

  "data_path": "benchmark/web_benchmark.jsonl",
  "output_dir": "infer_results/web",

  "save_results": true,
  "save_trajectories": true
}
```

**Output** (saved to `infer_results/web/`):

| File | Description |
|------|-------------|
| `results_web_infer_{timestamp}.jsonl` | Inference results for each task |
| `evaluation_web_infer_{timestamp}.json` | Evaluation details (includes `average_score`) |
| `summary_web_infer_{timestamp}.json` | Run summary |

---

## Configuration Reference

### Synthesis Config (`SynthesisConfig`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` | `"gpt-4.1-2025-04-14"` | LLM model name |
| `api_key` | `str` | `""` | API key |
| `base_url` | `str` | `""` | API base URL |
| `available_tools` | `list[str]` | `[]` | Available tools |
| `seeds_file` | `str` | `None` | Seed file path |
| `output_dir` | `str` | `None` | Output directory |
| `max_depth` | `int` | `5` | Max trajectory tree depth |
| `branching_factor` | `int` | `2` | Branching factor |
| `depth_threshold` | `int` | `3` | Depth threshold before branching |
| `min_depth` | `int` | `2` | Min trajectory depth |
| `max_selected_traj` | `int` | `3` | Max selected trajectories |
| `path_similarity_threshold` | `float` | `0.7` | Path similarity threshold |
| `sandbox_server_url` | `str` | `"http://127.0.0.1:18890"` | Sandbox server address |
| `number_of_seed` | `int` | `None` | Limit number of seeds to process |

### Rollout Config (`RolloutConfig`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` | `"gpt-4.1-2025-04-14"` | LLM model name |
| `api_key` | `str` | `""` | API key |
| `base_url` | `str` | `""` | API base URL |
| `max_turns` | `int` | `100` | Max conversation turns |
| `max_retries` | `int` | `3` | Max LLM call retries |
| `available_tools` | `list[str]` | `[]` | Available tools |
| `system_prompt` | `str` | Built-in default | System prompt |
| `evaluate_results` | `bool` | `true` | Whether to evaluate results |
| `evaluation_metric` | `str` | `"exact_match"` | Evaluation metric |
| `data_path` | `str` | `None` | Benchmark data path |
| `output_dir` | `str` | `None` | Output directory |
| `sandbox_server_url` | `str` | `"http://127.0.0.1:18890"` | Sandbox server address |
| `save_results` | `bool` | `true` | Whether to save results |
| `save_trajectories` | `bool` | `true` | Whether to save trajectories |
| `trajectory_only` | `bool` | `false` | Save trajectories only |
| `parallel` | `bool` | `false` | Enable parallel execution |

---
