# 📚 RAGAgent: Knowledge-Base Grounded Agent — Data Synthesis & Inference Guide

This guide walks through the full pipeline of using the AgentFlow framework with **RAGAgent (Retrieval-Augmented Generation Agent)**, from data synthesis to model inference.

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

RAGAgent is a **knowledge-base grounded agent** that answers questions by retrieving relevant text chunks from a **local RAG index** (DenseE5 + Faiss) and then synthesizing an answer with an LLM. The pipeline has five stages:

```
Sandbox Setup → QA Synthesis → Trajectory Synthesis → Model Training → Inference & Evaluation
```

AgentFlow provides core tools for RAGAgent:

| Tool | Description | Parameters |
|------|-------------|------------|
| `rag_search` | Retrieve the most relevant text chunks from the pre-built RAG index | `query`: query string, `top_k`: number of chunks (optional, default 10) |

> **Naming note:** the framework accepts multiple equivalent tool-name variants, including `rag_search`, `rag-search`, and `rag:search`.

---

## Prerequisites

1. **Install AgentFlow**

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

2. **Prepare API Keys**

- **OpenAI-compatible API Key**: For LLM calls in synthesis/rollout/inference (supports OpenRouter and compatible endpoints)

3. **Prepare Local RAG Resources**

The RAG sandbox backend loads a pre-built retrieval stack. Provide these paths via environment variables (recommended, avoids committing absolute paths):

- `RAG_EMBEDDING_MODEL_PATH`: local embedding model path (E5-compatible)
- `RAG_INDEX_PATH`: Faiss index path
- `RAG_CORPUS_PATH`: corpus JSONL path

### Download Links (ModelScope / Hugging Face)

You can download an example E5 embedding model, FAISS index, and corpus JSONL from either ModelScope or Hugging Face:

| Resource | ModelScope | Hugging Face |
|----------|------------|--------------|
| E5 embedding model | https://modelscope.cn/models/yamseyoung/e5-base-v2 | https://huggingface.co/intfloat/e5-base-v2 |
| Wiki-18 FAISS index | https://modelscope.cn/datasets/yamseyoung/wiki-18-e5-index | https://huggingface.co/datasets/PeterJinGo/wiki-18-e5-index |
| Wiki-18 corpus (JSONL) | https://modelscope.cn/datasets/yamseyoung/wiki-18-corpus | https://huggingface.co/datasets/PeterJinGo/wiki-18-corpus |

After downloading, set `RAG_EMBEDDING_MODEL_PATH`, `RAG_INDEX_PATH`, and `RAG_CORPUS_PATH` to the local paths on your machine.

Example:

```bash
export RAG_EMBEDDING_MODEL_PATH=/path/to/e5-model
export RAG_INDEX_PATH=/path/to/faiss.index
export RAG_CORPUS_PATH=/path/to/corpus.jsonl
```

> **Tip:** If your corpus is large, the backend can use an accompanying offset file for fast random access (e.g., `corpus.offsets` or `corpus.jsonl.offsets`). If no offset file is found, it will fall back to loading the full corpus into memory.

4. **Prepare Seed Data**

Seed file is located at `seeds/rag/seeds.jsonl`, one JSON object per line:

```jsonl
{"content": "Python programming language", "kwargs": {}}
{"content": "Machine learning", "kwargs": {}}
```

- `content` (required): starting entity/topic description for the agent to explore the knowledge base from
- `kwargs` (optional): extra metadata, defaults to `{}`

### Files Needed (Checklist)

Make sure the following files/configs exist before running the pipeline:

- RAG resources (local paths)
  - E5 embedding model directory (for `RAG_EMBEDDING_MODEL_PATH`)
  - FAISS index file (for `RAG_INDEX_PATH`)
  - Corpus JSONL file (for `RAG_CORPUS_PATH`)
- Seeds: `seeds/rag/seeds.jsonl`
- Sandbox server config: `configs/sandbox-server/rag_config.json`
- Synthesis config: `configs/synthesis/rag_config.json`
- Trajectory config: `configs/trajectory/rag_trajectory.json`
- Inference config: `configs/infer/rag_infer.json`
- Benchmark: `benchmark/rag_benchmark.jsonl`

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AgentFlow RAGAgent Pipeline                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Sandbox Server                                             │
│  ┌─────────────────┐                                                │
│  │  rag_config.json │──▶ Start rag_search tool service               │
│  └─────────────────┘                                                │
│          │                                                          │
│          ▼                                                          │
│  Step 2: QA Synthesis                                               │
│  ┌─────────────────┐    ┌──────────┐    ┌───────────────────┐       │
│  │  rag_config.json │──▶ │  Seeds   │──▶ │  synthesized_qa   │       │
│  └─────────────────┘    └──────────┘    │  + trajectories   │       │
│                                         └───────────────────┘       │
│          │                                                          │
│          ▼                                                          │
│  Step 3: Trajectory Rollout                                         │
│  ┌──────────────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  rag_trajectory.json  │──▶ │  benchmark   │──▶ │  trajectory  │   │
│  └──────────────────────┘    └──────────────┘    │  results     │   │
│                                                  └──────────────┘   │
│          │                                                          │
│          ▼                                                          │
│  Step 4: Model Training & Serving (vLLM)                            │
│                                                                     │
│          │                                                          │
│          ▼                                                          │
│  Step 5: Inference & Evaluation                                     │
│  ┌──────────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  rag_infer.json   │──▶ │  benchmark   │──▶ │  infer_results   │   │
│  └──────────────────┘    └──────────────┘    │  + evaluation    │   │
│                                              └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Start the Sandbox Server

The Sandbox server provides the tool execution environment for `rag_search`.

**Command:**

```bash
./start_sandbox_server.sh --config configs/sandbox-server/rag_config.json
```

> **Note:** `--port` and `--host` flags are ignored; use `server.url` / `server.port` in the config file instead.

**Config file** `configs/sandbox-server/rag_config.json`:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "session_ttl": 600
  },
  "resources": {
    "rag": {
      "enabled": true,
      "description": "RAG retrieval backend - document search (E5 + Faiss)",
      "backend_class": "sandbox.server.backends.resources.rag.RAGBackend",
      "config": {
        "model_name": "${RAG_EMBEDDING_MODEL_PATH}",
        "index_path": "${RAG_INDEX_PATH}",
        "corpus_path": "${RAG_CORPUS_PATH}",
        "device": "cuda:2",
        "default_top_k": 10,
        "batcher_trigger_batch_size": 16,
        "batcher_max_batch_size": 32,
        "batcher_max_wait_time": 0.05
      }
    }
  },
  "warmup": {
    "enabled": true,
    "resources": ["rag"]
  }
}
```

**Key config fields:**

| Field | Description |
|-------|-------------|
| `server.url` | Sandbox server listen address |
| `server.port` | Server port (default `18890`) |
| `server.session_ttl` | Session TTL in seconds |
| `resources.rag.backend_class` | RAG backend implementation class |
| `resources.rag.config.model_name` | Embedding model path (E5-compatible) |
| `resources.rag.config.index_path` | Faiss index path |
| `resources.rag.config.corpus_path` | Corpus JSONL path |
| `resources.rag.config.device` | Device spec (`cpu`, `cuda:0`, or `cuda:0/cuda:1`) |
| `resources.rag.config.default_top_k` | Default retrieval size |
| `warmup.enabled` | Warm up backends at startup |

**Verification:**

After startup, ensure the server is running before proceeding to Steps 2–5.

---

## Step 2: Synthesize QA Data

### Prepare Seed Data

Seed data is the starting point for QA synthesis. Each seed represents a **topic/entity description**. The agent uses it as a starting point to perform multi-hop exploration over the indexed knowledge — retrieving relevant chunks, chaining evidence, and generating multi-hop reasoning QA pairs from the exploration trajectory.

In short: **Seeds determine where the agent starts. Different seeds produce training data across different domains.**

### Run QA Synthesis

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

synthesize(config_path="configs/synthesis/rag_config.json")
```

Or via CLI:

```bash
python -m synthesis.pipeline \
    --config configs/synthesis/rag_config.json \
    --seeds seeds/rag/seeds.jsonl \
    --output-dir synthesis_results/rag
```

**Config file** `configs/synthesis/rag_config.json` — key fields:

```json
{
  "model_name": "openai/gpt-oss-120b",
  "api_key": "${OPENROUTER_API_KEY}",
  "base_url": "https://openrouter.ai/api/v1",
  "max_depth": 10,
  "branching_factor": 2,
  "depth_threshold": 2,
  "min_depth": 3,
  "max_selected_traj": 2,
  "path_similarity_threshold": 0.7,
  "resource_types": ["rag"],
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": true,
  "sandbox_config_path": "configs/sandbox-server/rag_config.json",
  "sandbox_timeout": 120,
  "available_tools": ["rag-search"],
  "seeds_file": "seeds/rag/seeds.jsonl",
  "output_dir": "results",
  "description_path": "configs/synthesis/instructions/rag_instruction.md",
  "skill": {
    "enabled": false
  }
}
```

Instruction markdown (`description_path`) should be placed under:
- `configs/synthesis/instructions/rag_instruction.md`

Recommended markdown blocks:
- `description`
- `sampling_tips`
- `selecting_tips`
- `synthesis_tips`
- `qa_examples`

If you do **not** use skills (`skill.enabled=false`):
- the markdown format above is required by synthesis (strict mode);
- missing required blocks will trigger warning + stop synthesis.

### If You Enable Skills

If you want to enable skill selection and injection for QA synthesis, use the skill-related config as shown below:

```json
{
  "description_path": "configs/synthesis/instructions/rag_instruction.md",
  "skills_root": "synthesis/skills",
  "skill": {
    "enabled": true,
    "min_global_skills": 5,
    "max_global_skills": 10
  }
}
```

When `skill.enabled=true`, markdown structured extraction is recommended but not mandatory. If extraction is incomplete, pipeline still runs and falls back to full markdown text for global skill selection, then injects selected skills into phase prompts.

**Output files:**

| File | Description |
|------|-------------|
| `results/synthesized_qa.jsonl` | Synthesized QA pairs (one JSON per line) |
| `results/trajectories.jsonl` | Corresponding agent trajectories (tool calls + reasoning traces) |

---

## Step 3: Synthesize Trajectory Data

This step runs the agent on benchmark data via the Rollout Pipeline to generate trajectory data for training.

**Usage:**

```python
from rollout import pipeline

pipeline(config_path="configs/trajectory/rag_trajectory.json")
```

Or via CLI:

```bash
python -m rollout.pipeline \
    --config configs/trajectory/rag_trajectory.json \
    --output-dir trajectory_results/rag
```

**Config file** `configs/trajectory/rag_trajectory.json` — key fields:

```json
{
  "benchmark_name": "rag_trajectory",
  "model_name": "gpt-4.1-2025-04-14",
  "api_key": "${OPENROUTER_API_KEY}",
  "base_url": "https://openrouter.ai/api/v1",
  "max_turns": 50,
  "available_tools": ["rag_search"],
  "sandbox_server_url": "http://127.0.0.1:18890",
  "evaluate_results": false,
  "data_path": "benchmark/rag_benchmark.jsonl",
  "output_dir": "trajectory_results/rag",
  "save_results": true,
  "save_trajectories": true,
  "trajectory_only": true
}
```

**Benchmark data format** (`benchmark/rag_benchmark.jsonl`):

```jsonl
{"id": "task_001", "question": "What is the capital of France?", "answer": "Paris"}
{"id": "task_002", "question": "Who wrote the play 'Romeo and Juliet'?", "answer": "William Shakespeare"}
```

**Output:**

Results are saved to `trajectory_results/rag/`:

| File | Description |
|------|-------------|
| `results_rag_trajectory_{timestamp}.jsonl` | Trajectory results for each task |

---

## Step 4: Model Training & Deployment

After training a model with data from Steps 2 and 3, deploy it using vLLM.

**Deploy with vLLM:**

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name ragagent \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8222
```

Once deployed, the model serves an OpenAI-compatible API at `http://localhost:8222`.

---

## Step 5: Inference & Evaluation

Run inference on the benchmark with the trained model and evaluate results.

**Usage:**

```python
from rollout import pipeline

pipeline(config_path="configs/infer/rag_infer.json")
```

**Config file** `configs/infer/rag_infer.json` — key fields:

```json
{
  "benchmark_name": "rag_infer",
  "model_name": "YOUR_MODEL_NAME",
  "api_key": "",
  "base_url": "VLLM_URL",
  "max_turns": 50,
  "max_retries": 3,
  "max_workers": 1,
  "available_tools": ["rag_search"],
  "evaluate_results": true,
  "evaluation_metric": "f1_score",
  "evaluator_model_name": "openai/gpt-oss-120b",
  "sandbox_server_url": "http://127.0.0.1:18890",
  "data_path": "benchmark/rag_benchmark.jsonl",
  "output_dir": "infer_results/rag",
  "save_results": true,
  "save_trajectories": true
}
```

**Output** (saved to `infer_results/rag/`):

| File | Description |
|------|-------------|
| `results_rag_infer_{timestamp}.jsonl` | Inference results for each task |
| `evaluation_rag_infer_{timestamp}.json` | Evaluation details (includes `average_score`) |
| `summary_rag_infer_{timestamp}.json` | Run summary |

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

### Skill Config for Synthesis

Use these fields in synthesis config (for example `configs/synthesis/rag_config_with_skill.json`):

```json
{
  "description_path": "configs/synthesis/instructions/rag_instruction.md",
  "skills_root": "synthesis/skills",
  "skill": {
    "enabled": true,
    "max_category_count": 1,
    "min_global_skills": 5,
    "max_global_skills": 10,
    "max_desc_chars": 800,
    "max_ref_chars": 3000,
    "temperature": 0.2,
    "max_skill_examples": 8,
    "max_total_qa_examples": 24
  }
}
```

### Instruction Markdown Format Requirements

Instruction markdown (for example `configs/synthesis/instructions/rag_instruction.md`) supports these blocks:
- `description`
- `sampling_tips`
- `selecting_tips`
- `synthesis_tips`
- `qa_examples`

Behavior by skill mode:
- `skill.enabled=false`: strict mode. All blocks above are required; missing blocks will print a warning and terminate synthesis.
- `skill.enabled=true`: tolerant mode. Structured extraction is recommended but not mandatory. If extraction is incomplete, pipeline falls back to full markdown text for global skill selection, continues synthesis, and uses skill guidance as phase injection.

Meaning of key fields:

| Field | Default | Description |
|------|---------|-------------|
| `description_path` | `null` | Instruction markdown path. Recommended blocks: `description`, `sampling_tips`, `selecting_tips`, `synthesis_tips`, `qa_examples`. |
| `skills_root` | `synthesis/skills` | Skill library root path. Relative path is resolved from project root. |
| `skill.enabled` | `false` | Whether to enable global skill selection and prompt injection. |
| `skill.max_category_count` | `2` | Max skill categories selected in stage-1 category selection. |
| `skill.min_global_skills` | `5` | Minimum skills selected in one global selection run. |
| `skill.max_global_skills` | `10` | Maximum skills selected in one global selection run. |
| `skill.max_desc_chars` | `800` | Max description length per skill when shown to selector LLM. |
| `skill.max_ref_chars` | `3000` | Max injected reference length per phase per skill. |
| `skill.temperature` | `0.2` | Temperature for skill-selection LLM calls. |
| `skill.max_skill_examples` | `8` | Max QA examples collected from selected `SKILL.md` files. |
| `skill.max_total_qa_examples` | `24` | Max merged QA examples finally passed to synthesizer prompt. |
| `skill.include` | `[]` | Optional explicit skill IDs to force include (bypass LLM selection). |
| `skill.exclude` | `[]` | Optional skill IDs to block from candidate pool. |

`selection_mode` in `skills_used.json`:

| Value | Meaning |
|------|---------|
| `disabled` | Skill is turned off; original tips/examples path is used. |
| `explicit_include` | Skills are taken from `skill.include` after validation. |
| `llm_global` | One-time LLM global selection (category -> skills) is applied. |


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

### Skill Library Structure

Default root:

`AgentFlow/synthesis/skills`

Expected layout:

```text
synthesis/skills/
  rag/                                   # 一级类别（Agent 类型）
    <skill-id>/
      SKILL.md                           # skill 定义（name/description + capability）
      references/
        EXPLORATION.md                   # sampler 阶段注入
        SELECTION.md                     # selector 阶段注入
        SYNTHESIS.md                     # synthesizer 阶段注入
```

### How to Upload Your Own RAG Skills

1. Create a new folder under `synthesis/skills/rag/<your-skill-id>/`.
2. Add `SKILL.md` with frontmatter fields `name` and `description`.
3. In `SKILL.md`, optionally provide reusable QA demos as paired lines:
   - `**Real Question**: ...`
   - `**Real Answer**: ...`
4. Add `references/EXPLORATION.md`, `references/SELECTION.md`, `references/SYNTHESIS.md`.

---

## FAQ

**Q: Tool name is `rag_search` or `rag-search` or `rag:search`?**

A: All of them are accepted. Internally the Sandbox normalizes variants like `rag_search` / `rag-search` to the canonical backend tool `rag:search`.

**Q: Why does `rag_search` return a single `context` string instead of a JSON list?**

A: The RAG backend formats retrieved chunks into a single string for prompt-friendly insertion. Increase `top_k` to retrieve more chunks.

**Q: My server fails on startup with missing paths.**

A: Ensure `RAG_EMBEDDING_MODEL_PATH`, `RAG_INDEX_PATH`, and `RAG_CORPUS_PATH` are set (or hardcode them in `configs/sandbox-server/rag_config.json`).
