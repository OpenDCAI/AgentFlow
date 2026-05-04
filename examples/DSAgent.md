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
bash install.sh
```

> **Options:** `bash install.sh --ml` to include ML/DL dependencies (torch, transformers), `--all` for everything. See `bash install.sh --help` for details.

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

### If You Enable Skills

If you want to enable skill selection and injection for QA synthesis, add the skill-related fields to `configs/synthesis/ds_config.json`:

```json
{
  "description_path": "configs/synthesis/instructions/ds_instruction.md",
  "skills_root": "synthesis/skills",
  "skill_group": "data_analysis",
  "skill": {
    "enabled": true,
    "min_global_skills": 5,
    "max_global_skills": 10
  }
}
```

When `skill.enabled=true`, markdown structured extraction is recommended but not mandatory. If extraction is incomplete, pipeline still runs and falls back to full markdown text for global skill selection, then injects selected skills into phase prompts.

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
- `description_path`: (optional) path to instruction markdown file — alternative to inline `sampling_tips`/`synthesis_tips`

> **Tip — Instruction Markdown with LLM Fallback:** Instead of specifying `sampling_tips` / `selecting_tips` / `synthesis_tips` inline in the JSON config, you can point `description_path` to a markdown file containing all guidance in free-form natural language. The pipeline uses a two-stage parser (regex + LLM fallback) to automatically extract structured fields. This is especially useful when guidance is long or written in prose.

### Skill Config for Synthesis

Use these fields in synthesis config (for example `configs/synthesis/ds_config.json`):

```json
{
  "description_path": "configs/synthesis/instructions/ds_instruction.md",
  "skills_root": "synthesis/skills",
  "skill_group": "data_analysis",
  "skill": {
    "enabled": true,
    "max_category_count": 2,
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

Instruction markdown (for example `configs/synthesis/instructions/ds_instruction.md`) supports these blocks:
- `description`
- `sampling_tips`
- `selecting_tips`
- `synthesis_tips`
- `qa_examples`

#### Two-stage Parsing with LLM Fallback

The instruction markdown is parsed in two stages:

1. **Regex-based parsing** (zero-cost, deterministic): Extracts structured blocks using `key: value` line format. Works best when the markdown follows the strict key-block format above.
2. **LLM fallback** (triggered automatically): When regex parsing is incomplete (missing required blocks) and model credentials (`api_key` + `base_url`) are configured, the pipeline automatically calls the LLM to extract structured fields from free-form / colloquial markdown.

This means you can write instruction markdown in **natural language prose** (headings, paragraphs, bullet points) without strict `key: value` formatting — the LLM fallback will intelligently extract the required fields.

> **Note:** The LLM fallback uses a single API call with a structured-data extraction prompt. If the provider does not support `response_format={"type": "json_object"}`, the pipeline automatically retries without that constraint.

#### Behavior by Skill Mode

- `skill.enabled=false`: strict mode. All blocks above are required after parsing (regex + LLM fallback combined); if still incomplete, synthesis terminates with an error.
- `skill.enabled=true`: tolerant mode. Structured extraction is recommended but not mandatory. If extraction is incomplete even after LLM fallback, pipeline falls back to full markdown text for global skill selection, continues synthesis, and uses skill guidance as phase injection.

Meaning of key fields:

| Field | Default | Description |
|------|---------|-------------|
| `description_path` | `null` | Instruction markdown path. Recommended blocks: `description`, `sampling_tips`, `selecting_tips`, `synthesis_tips`, `qa_examples`. |
| `skills_root` | `synthesis/skills` | Skill library root path. Relative path is resolved from project root. |
| `skill_group` | inferred from `resource_types` | Optional fixed category. For DSAgent, set `"data_analysis"` for strict category scoping. |
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

### Skill Library Structure

Default root:

`AgentFlow/synthesis/skills`

Expected layout:

```text
synthesis/skills/
  data_analysis/                         # 一级类别（Agent 类型）
    <skill-id>/
      SKILL.md                           # skill 定义（name/description + capability）
      references/
        EXPLORATION.md                   # sampler 阶段注入
        SELECTION.md                     # selector 阶段注入
        SYNTHESIS.md                     # synthesizer 阶段注入
```

### How to Upload Your Own DS Skills

1. Create a new folder under `synthesis/skills/data_analysis/<your-skill-id>/`.
2. Add `SKILL.md` with frontmatter fields `name` and `description`.
3. In `SKILL.md`, optionally provide reusable QA demos as paired lines:
   - `**Real Question**: ...`
   - `**Real Answer**: ...`
4. Add `references/EXPLORATION.md`, `references/SELECTION.md`, `references/SYNTHESIS.md`.

---

## FAQ

### 1) What is seed_path? What if it’s wrong?

`seed_path` must be the **directory containing your CSV files**. If it is wrong, tools won’t find the CSVs (e.g., `ds_read_csv` will report “File does not exist”).

### 2) What is rollout?

Rollout means running the agent on a question/benchmark with multi-step tool usage (forming a trajectory), producing an answer, and saving the full tool-use trace as trajectory data (useful for training, debugging, and reproducibility).

### 3) Why are Step 4/5 missing?

Because this repo has not performed model training and vLLM deployment, we intentionally do not include “training & deployment” or “inference & evaluation” steps in this DSAgent guide.
