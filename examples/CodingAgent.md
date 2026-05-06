# 💻 CodingAgent: Local Repository Coding Backend — Data Synthesis & Debugging Guide

This guide explains how to use AgentFlow's **Coding Backend** for **repository-grounded data synthesis** and **backend debugging**.

Note: this guide covers **sandbox startup, synthesis runs, and debugging only**. It does **not** cover model training, deployment, inference, or evaluation.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Overview](#pipeline-overview)
- [Step 1: Start the Sandbox Server](#step-1-start-the-sandbox-server)
- [Step 2: Run QA Synthesis](#step-2-run-qa-synthesis)
- [Step 3: Inspect Outputs](#step-3-inspect-outputs)
- [Configuration Reference](#configuration-reference)
- [FAQ / Debugging](#faq--debugging)

---

## Overview

CodingAgent is a **local repository coding agent**. For each seed, AgentFlow creates a coding workspace by copying a local repository into a sandbox directory, then lets the agent inspect or modify that workspace only through `code-*` tools.

The Coding Backend in this repo exposes 6 core tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `code-read` | Read a text file with line numbers | `file_path`, `offset` (optional), `limit` (optional) |
| `code-glob` | Find files by glob pattern | `pattern`, `path` (optional) |
| `code-grep` | Search file contents with a regex | `pattern`, `path` (optional), `glob` (optional) |
| `code-bash` | Run a shell command inside the current workspace | `command` |
| `code-edit` | Replace an exact string in an existing file | `file_path`, `old_string`, `new_string`, `replace_all` (optional) |
| `code-write` | Write a full file, creating parent directories if needed | `file_path`, `content` |

Typical use cases:

- Synthesize QA pairs grounded in a real repository
- Test whether `code-*` tools work correctly on a copied workspace
- Debug session initialization, workspace copying, and tool execution behavior

---

## Prerequisites

### 1) Install AgentFlow

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

### 2) Configure LLM credentials

The default coding synthesis config uses an OpenAI-compatible endpoint.

```bash
export OPENROUTER_API_KEY="YOUR_KEY"
```

If you keep the default config values, the synthesis config will use:

- `model_name`: `deepseek/deepseek-v4-flash`
- `base_url`: `https://openrouter.ai/api/v1`

### 3) Configure workspace-related environment variables

The two most important paths are:

- `SOURCE_DIR`: the repository that will be copied into each coding workspace
- `CODE_WORKSPACE_ROOT`: the parent directory where sandbox workspaces are created

Example:

```bash
export SOURCE_DIR="/path/to/your/repository"
export CODE_WORKSPACE_ROOT="/tmp/agentflow_code"
```

### 4) Prepare a seed file

Coding synthesis still requires a JSONL seed file. Each line must contain at least `content` and `kwargs`.

Example:

```jsonl
{"content":"Inspect the repository and identify the main entrypoint used to run the project.", "kwargs": {}}
{"content":"Find how this repository installs dependencies and how its test suite is executed.", "kwargs": {}}
```

Default seed file:

- `seeds/coding/coding.jsonl`

Important: for the Coding Backend, the seed describes **what to explore**, but the actual repository source comes from `resource_init_configs.code.content.source_dir` in the synthesis config, not from the seed itself.

In the current pipeline, seeds are processed **sequentially**.

### 5) Relevant config files

- Sandbox config: `configs/sandbox-server/coding_config.json`
- Synthesis config: `configs/synthesis/coding.json`

---

## Pipeline Overview

The Coding Backend flow verified in this repo is:

```text
Sandbox Server -> Code Session Initialization -> Workspace Copy -> Trajectory Sampling -> QA + Trajectory Output
```

For each seed, the synthesis pipeline does the following:

1. Start or connect to the sandbox server
2. Create or reinitialize the `code` session
3. Copy `source_dir` into a workspace under `CODE_WORKSPACE_ROOT`
4. Let the agent explore that workspace using `code-*` tools
5. Save synthesized QA pairs and selected trajectories
6. On later seeds, reinitialize the `code` session for isolation; workspace removal happens later when that session is destroyed during cleanup

Important behavior:

- The workspace is recreated from `source_dir` when the `code` session is initialized or reinitialized
- The workspace is deleted when the corresponding `code` session is destroyed during cleanup
- Because the workspace is mutable state, **set `branching_factor=1` for Coding Backend runs**

---

## Step 1: Start the Sandbox Server

The sandbox server provides the execution environment for `code-read`, `code-glob`, `code-grep`, `code-bash`, `code-edit`, and `code-write`.

**Command:**

```bash
./start_sandbox_server.sh --config configs/sandbox-server/coding_config.json
```

> Note: `--host` and `--port` flags are ignored by `start_sandbox_server.sh`; use `server.url` and `server.port` in the config file instead.

**Config file** `configs/sandbox-server/coding_config.json`:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "session_ttl": 900
  },
  "resources": {
    "code": {
      "enabled": true,
      "description": "Local coding backend for symbolic checks, Lean/Coq validation, bib processing, and plotting",
      "backend_class": "sandbox.server.backends.resources.code.CodeBackend",
      "config": {
        "workspace_root": "${CODE_WORKSPACE_ROOT}"
      }
    }
  }
}
```

**Verification:**

```bash
curl http://127.0.0.1:18890/health
```

Expected result:

```json
{"status":"healthy"}
```

### Does Coding Backend need warmup?

Usually, **no special warmup is needed**.

Unlike heavy backends such as RAG or VM, the Coding Backend does not load a model or a global resource pool in `warmup()`. The important step is **session initialization**, where the backend creates the workspace and copies `source_dir` into it.

So for Coding Backend debugging, focus on:

- whether the server starts correctly
- whether the `code` session is created
- whether `source_dir` is copied into the workspace
- whether `code-*` tools can execute against that workspace

---

## Step 2: Run QA Synthesis

### Recommended config for pure Coding Backend

In `configs/synthesis/coding.json`, keep the run strictly code-only:

```json
{
  "available_tools": ["code-*"],
  "resource_types": ["code"],
  "sandbox_config_path": "configs/sandbox-server/coding_config.json"
}
```

Also set:

```json
{
  "branching_factor": 1
}
```

These are strong recommendations for Coding Backend debugging, not just tuning suggestions.

Reasons:

- `branching_factor > 1`: sibling branches in the current sampler are explored concurrently, while a single seed uses one `code` session and one mutable workspace. Different branches may read or write the same workspace and contaminate each other.

### Run from CLI

```bash
python3 synthesis/pipeline.py \
  --config configs/synthesis/coding.json \
  --seeds seeds/coding/coding.jsonl \
  --output-dir results/coding
```

If `seeds_file` and `output_dir` are already set in the config, the shorter form also works:

```bash
python3 synthesis/pipeline.py --config configs/synthesis/coding.json
```

### What you should see in logs

For a healthy pure coding run, logs usually include signals like:

- sandbox server started or connected successfully
- `Warming up backends: ['code']` or no meaningful warmup work
- `Session created: code -> ...`
- `Available tools: ['code-read', 'code-glob', 'code-grep', 'code-bash', 'code-edit', 'code-write']`
- tool execution logs for `code-*`

If you see tools such as `rag-search`, `web-search`, or `text2sql-execute`, your synthesis config is not pure coding.

---

## Step 3: Inspect Outputs

By default, synthesis writes two JSONL files into the output directory:

- `synthesized_qa.jsonl`
- `trajectories.jsonl`

Example:

```bash
ls results/coding
```

Expected files:

```text
synthesized_qa.jsonl
trajectories.jsonl
```

Use these files for two different debugging purposes:

- `synthesized_qa.jsonl`: check whether the final QA pairs are repository-grounded and realistic
- `trajectories.jsonl`: check the actual tool-use path, including which files were read, which commands were run, and whether code-edit/code-write changed the workspace

If you are debugging the backend itself, `trajectories.jsonl` is usually the more important file.

---

## Configuration Reference

### Coding synthesis config

File: `configs/synthesis/coding.json`

Key fields:

| Field | Description |
|-------|-------------|
| `model_name` | LLM used for trajectory sampling and QA synthesis |
| `api_key` | OpenAI-compatible API key |
| `base_url` | OpenAI-compatible API base URL |
| `available_tools` | For pure coding, use `["code-*"]` |
| `resource_types` | For pure coding, use `["code"]` |
| `sandbox_server_url` | Sandbox server address |
| `sandbox_auto_start` | Whether the synthesis worker auto-starts the sandbox server |
| `sandbox_config_path` | Sandbox server config path used when auto-starting |
| `branching_factor` | Strongly recommend `1` for Coding Backend |
| `resource_init_configs.code.content.source_dir` | Initial repository directory copied into each workspace |
| `seeds_file` | Seed JSONL path |
| `output_dir` | Output directory for QA and trajectories |

Recommended minimal shape:

```json
{
  "available_tools": ["code-*"],
  "resource_types": ["code"],
  "branching_factor": 1,
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": true,
  "sandbox_config_path": "configs/sandbox-server/coding_config.json",
  "resource_init_configs": {
    "code": {
      "content": {
        "source_dir": "${SOURCE_DIR}"
      }
    }
  }
}
```

### Coding sandbox config

File: `configs/sandbox-server/coding_config.json`

Key fields:

| Field | Description |
|-------|-------------|
| `server.url` | Sandbox listen address |
| `server.port` | Sandbox port |
| `server.session_ttl` | Session TTL in seconds |
| `resources.code.backend_class` | Backend implementation class |
| `resources.code.config.workspace_root` | Parent directory where workspaces are created |

Recommended minimal shape:

```json
{
  "server": {
    "url": "http://127.0.0.1:18890",
    "port": 18890,
    "session_ttl": 900
  },
  "resources": {
    "code": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.code.CodeBackend",
      "config": {
        "workspace_root": "${CODE_WORKSPACE_ROOT}"
      }
    }
  }
}
```

---

## FAQ / Debugging

### 1) Does each run create a fresh workspace?

Yes, for each seed the pipeline creates or reinitializes the `code` session, and the Coding Backend copies `source_dir` into the workspace again.

That means:

- if you rerun the pipeline, the workspace starts from `source_dir` again
- if you process multiple seeds, later seeds do not continue from earlier seed edits

### 2) Will the workspace be deleted after the run?

Not always immediately.

The Coding Backend deletes the workspace when `code` session cleanup runs. In the current pipeline path, intermediate seed workspaces are removed during `reinitialize()`, because the old `code` session is destroyed before the next one is created. However, the final workspace is not guaranteed to be deleted the moment the worker stops, because this pipeline currently closes the sandbox connection without always explicitly destroying the last per-seed session first.

So if you are checking final on-disk edits, remember:

- the workspace exists during the run
- earlier seed workspaces are typically removed when the next seed reinitializes `code` (that is, every seed use the same, brand-new workspace)
- the final workspace may remain until the session is explicitly destroyed or cleaned by session TTL expiry

### 3) Why is `branching_factor=1` strongly recommended?

Because the current Coding Backend uses one mutable workspace per worker/session for a given seed, while the sampler can explore sibling branches concurrently.

With `branching_factor > 1`, one branch may:

- edit files that another branch later reads
- overwrite files written by another branch
- make trajectories depend on sibling side effects

That makes trajectory data hard to interpret and unsafe for backend debugging. For Coding Backend runs, set:

```json
{
  "branching_factor": 1
}
```

### 4) How do I confirm the run is pure Coding Backend?

Check three places:

1. `configs/synthesis/coding.json`
   - `available_tools` should be `["code-*"]`
   - `resource_types` should be `["code"]`
2. runtime logs
   - available tools should all be `code-*`
3. sandbox config
   - `configs/sandbox-server/coding_config.json` should only enable the `code` resource

### 5) How are multiple seeds handled?

Seeds are processed sequentially in the current pipeline, not in parallel.

For Coding Backend runs, that means:

- each new seed reinitializes the `code` session
- each new seed recreates the workspace from `source_dir`
- later seeds do not continue from earlier seed edits

### 6) What if `source_dir` is wrong?

If `source_dir` does not exist or is not a directory, `code` session initialization will fail.

Typical checks:

```bash
echo "$SOURCE_DIR"
ls "$SOURCE_DIR"
```

### 7) What if `code-glob` or `code-read` returns nothing useful?

First verify that the workspace was actually copied from the expected repository.

Check:

- `SOURCE_DIR` points to the intended repository
- `resource_init_configs.code.content.source_dir` expands correctly
- `CODE_WORKSPACE_ROOT` is writable
- the run logs show successful `code` session creation

### 8) What if `code-bash` fails?

`code-bash` runs inside the copied workspace. If it fails, the most common causes are:

- the command itself exits non-zero
- the expected toolchain is not installed in the runtime environment
- the command assumes a different working directory layout than the copied repository

For debugging, start with lightweight commands such as:

```bash
pwd
ls
find . -maxdepth 2 -type f | head
```

### 9) What is the difference between seeds and `source_dir`?

They serve different purposes:

- `seed.content`: tells the agent what to investigate
- `source_dir`: tells the backend which repository to copy into the workspace

Changing seeds changes the exploration task. Changing `source_dir` changes the repository being explored.
