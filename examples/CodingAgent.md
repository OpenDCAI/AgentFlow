# CodingAgent: Repository QA / Edit Agent - Data Synthesis Guide (No Training/Deployment)

This guide explains how to use AgentFlow's CodingAgent example to synthesize QA data and trajectory data for a small repository workflow.

CodingAgent uses the `code` backend's six tools through `code-*`, so the same setup covers repository inspection, search, shell validation, and small file edits.

## Overview

CodingAgent is a repository-grounded coding agent example. It works against a local code workspace and uses six code tools exposed through `code-*`:

- `code-read`
- `code-glob`
- `code-grep`
- `code-bash`
- `code-edit`
- `code-write`

The bundled example is intentionally small and example-oriented. It includes both a read-only question style and an edit-task style based on the committed demo repository, so you can synthesize data for repository inspection and minimal bug-fix workflows from the same assets.

## Prerequisites

Install and enter the repository:

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

Configure model access and the repo-root contract used by the committed code example configs:

```bash
export OPENAI_API_KEY=YOUR_KEY
export OPENAI_API_URL=https://openrouter.ai/api/v1
export AGENTFLOW_REPO_ROOT=$(pwd)
```

The default committed repository for this example lives at `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`.

Seed prompts are stored in `seeds/code/seeds.jsonl`. If you want to run the same pipeline on your own repository instead of the bundled demo repo, replace `resource_init_configs.code.content.source_dir` with your own repository path.

## Pipeline Overview

This CodingAgent example uses a simple three-step flow:

```text
Step 1 Sandbox Server -> Step 2 QA Synthesis -> Step 3 Trajectory Data
```

The assets in this repo are already aligned for that flow:

- Sandbox config: `configs/sandbox-server/code_config.json`
- QA synthesis config: `configs/synthesis/code_config.json`
- Trajectory rollout config: `configs/trajectory/code_trajectory.json`
- Benchmark file: `benchmark/code_benchmark.jsonl`

The benchmark mixes a bundled read-only plus edit-task example style. One task asks the agent to inspect the repo and answer a question; another asks it to make a minimal fix and verify it with `python tests/smoke_test.py`.

## Step 1: Start the Sandbox Server

Start the sandbox server before synthesis or rollout:

```bash
./start_sandbox_server.sh --config configs/sandbox-server/code_config.json
```

This launches the code resource backend and prepares per-run workspaces under the sandbox workspace root.

## Step 2: Synthesize QA Data

Use the committed synthesis config to generate repository-grounded QA from the coding seeds:

```bash
python3 synthesis/pipeline.py \
  --config configs/synthesis/code_config.json \
  --seeds seeds/code/seeds.jsonl \
  --output-dir results/code
```

By default, the synthesis config initializes the code resource from `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo` through `resource_init_configs.code.content.source_dir`.

The committed prompts are designed around the bundled demo repository and support both repository-reading questions and a lightweight edit-validation workflow.

## Step 3: Synthesize Trajectory Data

Use rollout to generate trajectory-only records with the committed benchmark:

```bash
python -m rollout.pipeline \
  --config configs/trajectory/code_trajectory.json \
  --output-dir trajectory_results/code
```

This config reads tasks from `benchmark/code_benchmark.jsonl` and keeps the same default repo-root contract via `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`.

One bundled task explicitly validates the edit workflow by asking the agent to run `python tests/smoke_test.py` after making a minimal fix.

## Configuration Reference

### Sandbox config

`configs/sandbox-server/code_config.json` enables the `code` resource and points the sandbox to a temporary workspace root.

### Synthesis config

`configs/synthesis/code_config.json` defines:

- `available_tools` as `code-*`
- `seeds_file` as `seeds/code/seeds.jsonl`
- `resource_init_configs.code.content.source_dir` as `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`

If you want to use a different repository, update `source_dir` to your own path while keeping the rest of the pipeline structure the same.

### Trajectory config

`configs/trajectory/code_trajectory.json` defines:

- `available_tools` as `code-*`
- `data_path` as `benchmark/code_benchmark.jsonl`
- `resource_init_configs.code.content.source_dir` as `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`

## FAQ

### What repository does the example use by default?

The committed default is `seeds/code/seed/demo_repo`, resolved in config as `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`.

### Can I point the example at my own repository?

Yes. Replace `resource_init_configs.code.content.source_dir` with your own repo path in the synthesis or trajectory config you want to run.

### Does this guide cover training or deployment?

No. Later training / deployment / infer are not covered yet, so this guide stops after QA synthesis and trajectory generation.
