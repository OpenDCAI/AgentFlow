# 💃 DocDancer: Towards Agentic Document-Grounded Information Seeking

This guide walks through the full pipeline of using the AgentFlow framework with **DocDancer (Doc QA Agent)**, from data synthesis to model inference.

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

DocDancer is a **Document Understanding agent** that answers complex multi-hop reasoning questions in long and multimodal element documents by searching and reading the content. The pipeline has five stages:

```
Sandbox Setup → QA Synthesis → Trajectory Synthesis → Model Training → Inference & Evaluation
```

AgentFlow provides two core tools for DocDancer:

| Tool | Description | Parameters |
|------|-------------|------------|
| `doc_search` | Search for keywords in document headings, paragraphs, tables, and image captions | `key_words`: array of keyword strings, `max_search_results`: max results per keyword (optional) |
| `doc_read` | Read document sections and extract information using visual language model, processing both text and images | `section_ids`: array of section IDs, `goal`: extraction objective, `max_image_num`: max visual inputs (optional), `max_text_token`: max text length (optional) |

---

## Prerequisites

1. **Install AgentFlow**

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

2. **Prepare API Keys**

The DocDancer Sandbox requires the following external services (configured in `configs/sandbox-server/doc_config.json`):

- **OpenAI-compatible API Key**: For LLM calls (supports OpenRouter and other compatible endpoints)
- **VLM API Key**: For visual language model calls used by `doc_read` tool (default: OpenAI-compatible API, configurable in `configs/sandbox-server/doc_config.json`)

3. **Prepare Seed Data**

Seed file is located at `seeds/doc/seeds.jsonl`, one JSON object per line:

```jsonl
{"content": "<?xml version='1.0' encoding='utf-8'?>\n<Outline><Section section_id=\"1\" start_page_num=\"1\" end_page_num=\"1.0\"><Paragraph page_num=\"1.0\" first_sentence=\"arXiv:2210.024442v1 [cs.CV] 5 Oct 2022\" /><Title page_num=\"1.0\">Making Your First Choice: To Address Cold Start Problem in Vision Active Learning</Title></Section> ... </Outline>", "kwargs": {"seed_path": "seeds/doc/seed/2210.02442v1"}}
```

- `content` (required): The document outline in XML format, which is the preprocessed `outline.xml` file (see `./projects/docdancer/PDF_preprocess` for preprocessing details)
- `kwargs` (required): A dictionary containing `seed_path`, which is the absolute path to the preprocessed document folder

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AgentFlow DocDancer Pipeline                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Sandbox Server                                             │
│  ┌─────────────────┐                                                │
│  │ doc_config.json │──▶ Start doc_search / doc_read tool service    │
│  └─────────────────┘                                                │
│          │                                                          │
│          ▼                                                          │
│  Step 2: QA Synthesis                                               │
│  ┌─────────────────┐    ┌──────────┐    ┌───────────────────┐       │
│  │ doc_config.json │──▶ │  Seeds   │──▶ │  synthesized_qa   │       │
│  └─────────────────┘    └──────────┘    │  + trajectories   │       │
│                                         └───────────────────┘       │
│          │                                                          │
│          ▼                                                          │
│  Step 3: Trajectory Rollout                                         │
│  ┌──────────────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ doc_trajectory.json  │──▶ │  benchmark   │──▶ │  trajectory  │   │
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
│  │  doc_infer.json  │──▶ │  benchmark   │──▶ │  infer_results   │   │
│  └──────────────────┘    └──────────────┘    │  + evaluation    │   │
│                                              └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Start the Sandbox Server

The Sandbox server provides the tool execution environment (`doc_search`, `doc_read`) for the agent.

**Command:**

```bash
./start_sandbox_server.sh --config configs/sandbox-server/doc_config.json
```

> **Note:** `--port` and `--host` flags are ignored; use `server.url` / `server.port` in the config file instead.

**Config file** `configs/sandbox-server/doc_config.json`:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "title": "Sandbox HTTP Service (Document Tools)",
    "description": "Document tools with configurable defaults",
    "session_ttl": 300
  },
  "apis": {
    "doc": {
      "seed_path": "seeds/doc/seed/2210.02442v1",
      "max_search_results": 10,
      "max_image_num": 10,
      "max_text_token": 20000,
      "vlm_model": "openai/gpt-4o-mini",
      "vlm_api_key": "${OPENAI_API_KEY}",
      "vlm_api_url": "https://openrouter.ai/api/v1",
      "vlm_max_tokens": 16384,
      "vlm_timeout": 300,
      "vlm_retry_max_attempts": 10
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
| `apis.doc.seed_path` | Default seed path (can be overridden by seed.jsonl kwargs) |
| `apis.doc.max_search_results` | Max search results per keyword (default `10`) |
| `apis.doc.max_image_num` | Max visual inputs per read operation (default `10`) |
| `apis.doc.max_text_token` | Max text length in characters (default `20000`) |
| `apis.doc.vlm_model` | Visual language model name for doc_read tool |
| `apis.doc.vlm_api_key` | VLM API key (supports environment variables like `${OPENAI_API_KEY}`) |
| `apis.doc.vlm_api_url` | VLM API base URL |
| `apis.doc.vlm_max_tokens` | Max tokens for VLM responses |
| `apis.doc.vlm_timeout` | VLM API timeout in seconds |
| `apis.doc.vlm_retry_max_attempts` | Max retry attempts for VLM API calls |

**Verification:**

After startup, the terminal will display the listening port. Ensure the Sandbox server is running before proceeding to Steps 2–5.

---

## Step 2: Synthesize QA Data

### Prepare Seed Data

Seed data is the starting point for QA synthesis. Each seed represents a **preprocessed document** with its XML outline. The agent uses it as a starting point to perform multi-hop document exploration — searching for relevant sections, reading content across multiple pages, building information chains from text and visual elements (figures, tables, charts), and ultimately generating multi-hop reasoning QA pairs from the exploration trajectory.

In short: **Seeds determine which documents the agent explores. Different seeds produce training data across different document types and domains.**

**Seed file format**

JSONL format (one JSON object per line), stored at `seeds/doc/seeds.jsonl`:

```jsonl
{"content": "<?xml version='1.0' encoding='utf-8'?>\n<Outline><Section section_id=\"1\" start_page_num=\"1\" end_page_num=\"1.0\"><Paragraph page_num=\"1.0\" first_sentence=\"arXiv:2210.024442v1 [cs.CV] 5 Oct 2022\" /><Title page_num=\"1.0\">Making Your First Choice: To Address Cold Start Problem in Vision Active Learning</Title></Section> ... </Outline>", "kwargs": {"seed_path": "seeds/doc/seed/2210.02442v1"}}
```

| Field | Required | Description |
|-------|----------|-------------|
| `content` | ✅ Yes | The document outline in XML format (preprocessed `outline.xml` file). This provides the document structure including sections, headings, paragraphs, images, and tables. |
| `kwargs` | ✅ Yes | Dictionary containing `seed_path` (required), which is the absolute path to the preprocessed document folder containing the document images, XML files, and other processed assets. |

Once seed data is ready, point the `seeds_file` field in `configs/synthesis/doc_config.json` to your file path.

---

### Run QA Synthesis

This step uses an LLM agent to explore documents based on seed data and automatically generate high-quality multi-hop reasoning QA pairs that require visual and textual evidence from multiple pages.

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

synthesize(config_path="configs/synthesis/doc_config.json")
```

Or via CLI:

```bash
python -m synthesis.pipeline \
    --config configs/synthesis/doc_config.json \
    --seeds seeds/doc/seeds.jsonl \
    --output-dir synthesis_results
```

**Config file** `configs/synthesis/doc_config.json` — key fields:

```json
{
  "model_name": "openai/gpt-oss-120b",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "https://openrouter.ai/api/v1",
  
  "max_depth": 20,
  "branching_factor": 2,
  "depth_threshold": 2,
  "min_depth": 3,
  "max_selected_traj": 2,
  "path_similarity_threshold": 0.7,
  
  "sandbox_server_url": "http://127.0.0.1:18890",
  "available_tools": ["doc_search", "doc_read"],
  
  "sampling_tips": [
    "Explore parsed PDF documents to gather evidence for multi-hop, visual-grounded Q&A",
    "Focus on multi-page evidence (combine at least TWO different pages/sections)",
    "Ensure visual elements are involved (charts, figures, tables, or page layouts)",
    "Require multi-hop reasoning (e.g., cross-reference + computation, footnote + chart reading)",
    "Use doc_search to find visuals, tables, footnotes with keywords like: Figure, Chart, Table, panel, footnote",
    "Use doc_read to extract detailed information from sections with specific goals",
    "Chain across pages: after finding a chart/table, search for its discussion elsewhere",
    "Collect content-based clues (captions, axis labels, legend items, headers) instead of explicit locations",
    "Do NOT use page numbers, section IDs, or explicit figure/table numbers in questions",
    "Note: seed_path is automatically provided from seed.jsonl kwargs, you don't need to specify it when calling doc_search or doc_read",
    "Avoid broad document counts, word-frequency counting, or repeating identical tool calls"
  ],
  
  "synthesis_tips": [
    "Create questions requiring multi-hop reasoning (>=3 hops)",
    "Keep questions concise (<=5 sentences)",
    "Answers should be specific facts (names, dates, locations, numbers)",
    "Ensure answer is grounded in trajectory evidence",
    "Provide clear reasoning steps",
    "Every QA must satisfy ALL constraints: multi-page (>=2 pages), visual-grounded (involve charts/figures/tables), multi-hop (>=2 reasoning points)",
    "Do NOT mention page numbers, section IDs, or explicit figure/table numbers in questions",
    "Use content-based clues (caption phrases, axis labels, legend items, headers) to identify evidence",
    "Preferred templates: text claim + chart verification, table + chart consistency, footnote-constrained mapping, layout comparison",
    "Disallowed: single-hop lookups, broad document counts, word-frequency questions",
    "If trajectory doesn't support all constraints, choose a different question. Never guess or hallucinate"
  ],
  
  "seeds_file": "seeds/doc/seeds.jsonl",
  "output_dir": "results/doc"
}
```

**Config parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_name` | - | LLM model for synthesis (OpenAI-compatible format) |
| `max_depth` | `20` | Max exploration depth of the trajectory tree |
| `branching_factor` | `2` | Number of branches per node |
| `depth_threshold` | `2` | Min depth before branching starts |
| `min_depth` | `3` | Min depth for a trajectory to be selected |
| `max_selected_traj` | `2` | Max trajectories selected per seed |
| `path_similarity_threshold` | `0.7` | Similarity threshold for trajectory deduplication |
| `sampling_tips` | - | Hints guiding the agent's document exploration behavior |
| `synthesis_tips` | - | Hints guiding QA generation with visual and multi-page constraints |
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

pipeline(config_path="configs/trajectory/doc_trajectory.json")
```

Or via CLI:

```bash
python -m rollout.pipeline \
    --config configs/trajectory/doc_trajectory.json \
    --output-dir trajectory_results/doc
```

**Config file** `configs/trajectory/doc_trajectory.json` — key fields:

```json
{
  "benchmark_name": "doc_trajectory",
  "model_name": "openai/gpt-oss-120b",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "https://openrouter.ai/api/v1",

  "max_turns": 40,
  "available_tools": ["doc_search", "doc_read"],
  "sandbox_server_url": "http://127.0.0.1:18890",
  
  "system_prompt": [
    "You are an expert research assistant tasked with answering questions based on document content.",
    "You will be provided with an XML outline of the document.",
    "If you need more comprehensive, detailed, or accurate information from the document to fully address the user's query, you need to use the provided tool."
  ],

  "evaluate_results": false,
  "data_path": "benchmark/doc_benchmark.jsonl",
  "output_dir": "trajectory_results/doc",

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

**Benchmark data format** (`benchmark/doc_benchmark.jsonl`):

```jsonl
{"doc_id": "task_001", "doc_type": "Administration/Industry file", "question": "\nI've uploaded a document, and below is the outline in XML format:\n<?xml version='1.0' encoding='utf-8'?>\n<Outline>...</Outline>\n\nAnswer the following question based on the content of the document:\nWho is the commanding officer in the first figure on the second page?\n", "answer": "Capt. John W. Sanders", "evidence_pages": "[2]", "evidence_sources": "['Figure', 'Pure-text (Plain-text)']", "answer_format": "Str", "kwargs": {"seed_path": "benchmark/doc_benchmark/Input/0b85477387a9d0cc33fca0f4becaa0e5"}}
{"doc_id": "task_002", "doc_type": "Administration/Industry file", "question": "...", "answer": "Not answerable", "evidence_pages": "[]", "evidence_sources": "[]", "answer_format": "None", "kwargs": {"seed_path": "benchmark/doc_benchmark/Input/0b85477387a9d0cc33fca0f4becaa0e5"}}
```

| Field | Required | Description |
|-------|----------|-------------|
| `doc_id` | ✅ Yes | Unique identifier for the document task |
| `doc_type` | Optional | Document type/category |
| `question` | ✅ Yes | The question to answer (includes document outline in XML format) |
| `answer` | ✅ Yes | Ground truth answer |
| `evidence_pages` | Optional | List of page numbers containing evidence (as string representation of list) |
| `evidence_sources` | Optional | List of evidence source types (as string representation of list) |
| `answer_format` | Optional | Answer format: `Str`, `Int`, `List`, `None`, etc. |
| `kwargs` | ✅ Yes | Dictionary containing `seed_path` (absolute path to preprocessed document folder) |

Supported field aliases:
- `doc_id` / `task_id` / `id`
- `question` / `query` / `input`
- `answer` / `ground_truth` / `expected`


**Output:**

Results are saved to `trajectory_results/doc/`:

| File | Description |
|------|-------------|
| `results_doc_trajectory_{timestamp}.jsonl` | Trajectory results for each task |

---

## Step 4: Model Training & Deployment

After training a model with data from Steps 2 and 3, deploy it using vLLM.

**Deploy with vLLM:**

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name docagent \
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

pipeline(config_path="configs/infer/doc_infer.json")
```

**Config file** `configs/infer/doc_infer.json` — key fields:

```json
{
  "benchmark_name": "doc_infer",
  "model_name": "gpt-4.1-2025-04-14",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "https://openrouter.ai/api/v1",
  
  "max_turns": 50,
  "max_retries": 3,
  "max_workers": 1,
  
  "available_tools": ["doc_search", "doc_read"],
  
  "system_prompt": [
    "You are an expert research assistant tasked with answering questions based on document content.",
    "You will be provided with an XML outline of the document.",
    "If you need more comprehensive, detailed, or accurate information from the document to fully address the user's query, you need to use the provided tool."
  ],
  
  "evaluate_results": false,
  "data_path": "benchmark/doc_benchmark.jsonl",
  "output_dir": "infer_results/doc",
  
  "save_results": true,
  "save_trajectories": true,
  "parallel": false
}
```

**Key config fields:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_turns` | `50` | Max conversation turns per task |
| `max_retries` | `3` | Max LLM call retries |
| `evaluate_results` | `false` | Whether to evaluate results (set to `true` for evaluation) |
| `evaluation_metric` | - | Evaluation metric (e.g., `"contains_answer"`, `"exact_match"`) |
| `evaluator_model_name` | - | LLM model for evaluation (if using LLM-based evaluation) |
| `data_path` | - | Path to benchmark data file |
| `output_dir` | - | Output directory for results |

**Output** (saved to `infer_results/doc/`):

| File | Description |
|------|-------------|
| `results_doc_infer_{timestamp}.jsonl` | Inference results for each task |
| `evaluation_doc_infer_{timestamp}.json` | Evaluation details (includes `average_score` if evaluation enabled) |
| `summary_doc_infer_{timestamp}.json` | Run summary |

**Evaluation**

For benchmarking, we strictly follow the official evaluation procedures of [MMLongDoc-Bench](https://github.com/mayubo2333/MMLongBench-Doc) and [DocBench](https://github.com/Anni-Zou/DocBench). All reported results are computed using their publicly available evaluation scripts to ensure fair and consistent comparison.

For the LasJ metric used in MMLongDoc-Bench, please refer to the detailed evaluation prompt in [LasJ_prompt_for_MMLongDocBench.md](./projects/docdancer/eval/LasJ_prompt_for_MMLongDocBench.md) as outlined in the paper.


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
