# MCP and Coding Examples Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add official MCP and Coding example docs, configs, seeds, demo assets, and validation coverage so both backends have runnable three-step examples aligned with the existing `examples/` set.

**Architecture:** Implement the work in four isolated chunks. Chunk 1 locks the shared MCP sandbox template contract so the example path has a stable server subset and `mcp_servers_path` behavior. Chunk 2 adds the six-domain MCP example assets and doc with MCP-specific tests. Chunk 3 adds the Coding example assets, bundled demo repo, and doc with Coding-specific tests. Chunk 4 runs the final combined verification suite plus optional real-environment dry runs without expanding scope to training or infer.

**Tech Stack:** Python, pytest, JSON, JSONL, Markdown, AgentFlow sandbox config loader, synthesis config loader, rollout config loader, Toolathlon-GYM MCP backend, Code backend

---

**Assumptions and Guardrails**

- The approved spec at `docs/superpowers/specs/2026-04-20-mcp-and-coding-examples-design.md` remains the source of truth.
- Keep `examples/MCPAgent.md` and `examples/CodingAgent.md` at the same granularity as `examples/DSAgent.md`: Overview, Prerequisites, Pipeline Overview, Step 1, Step 2, Step 3, Configuration Reference, FAQ.
- Official committed docs and configs must stay generic. Do not mention `/home/a1/sdb/dxd/DataFlow` or any other machine-local absolute path in committed example assets.
- MCP examples assume a local `toolathlon_gym` checkout is already initialized and running before AgentFlow starts. AgentFlow does not bootstrap Toolathlon-GYM services in this task.
- Coding examples use a committed demo repo by default through `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`, but the docs must also say `source_dir` can be overridden to point at a user-provided repo.
- Both new docs must explicitly stop at Step 3 and explain that training / deployment / infer are not covered yet, matching the DS-style scope the user approved.
- If the current synthesis pipeline still writes to the repo’s shared aggregation directory instead of respecting per-config `output_dir`, document the actual observed behavior in the new example docs rather than broadening this task into a synthesis pipeline refactor.

## File Map

### Shared MCP sandbox contract

- Modify: `configs/sandbox-server/mcp_config.json`
  Responsibility: official MCP sandbox entry point for the example path; declare `mcp_servers_path`, the approved MCP server subset, localhost-style env defaults, and warmup settings.
- Modify: `sandbox/tests/test_sandbox_config_loading.py`
  Responsibility: verify `${TOOLATHLON_GYM_ROOT}/local_servers` survives env expansion when the env var is unset.
- Modify: `sandbox/tests/test_mcp_backend.py`
  Responsibility: verify the checked-in MCP sandbox template exposes the exact approved config contract, including warmup.
- Modify: `sandbox/tests/test_mcp_client.py`
  Responsibility: verify MCP YAML resolution still maps `${local_servers_paths}` to the JSON config’s `mcp_servers_path`.

### MCP example validation and assets

- Create: `synthesis/tests/test_mcp_example_synthesis_configs.py`
  Responsibility: validate all six MCP synthesis configs, tool exposure, seed references, and empty `resource_init_configs`.
- Create: `rollout/tests/test_mcp_example_assets.py`
  Responsibility: validate all six MCP rollout configs plus the MCP seeds and benchmark files.
- Create: `rollout/tests/test_mcp_example_doc.py`
  Responsibility: validate `examples/MCPAgent.md` has the DS-style structure and the exact prerequisite/config references the user approved.
- Create: `examples/MCPAgent.md`
- Create: `configs/synthesis/mcp_canvas_config.json`
- Create: `configs/synthesis/mcp_snowflake_config.json`
- Create: `configs/synthesis/mcp_woocommerce_config.json`
- Create: `configs/synthesis/mcp_yahoo_finance_config.json`
- Create: `configs/synthesis/mcp_youtube_config.json`
- Create: `configs/synthesis/mcp_train_config.json`
- Create: `configs/trajectory/mcp_canvas_trajectory.json`
- Create: `configs/trajectory/mcp_snowflake_trajectory.json`
- Create: `configs/trajectory/mcp_woocommerce_trajectory.json`
- Create: `configs/trajectory/mcp_yahoo_finance_trajectory.json`
- Create: `configs/trajectory/mcp_youtube_trajectory.json`
- Create: `configs/trajectory/mcp_train_trajectory.json`
- Create: `seeds/mcp/canvas_seeds.jsonl`
- Create: `seeds/mcp/snowflake_seeds.jsonl`
- Create: `seeds/mcp/woocommerce_seeds.jsonl`
- Create: `seeds/mcp/yahoo_finance_seeds.jsonl`
- Create: `seeds/mcp/youtube_seeds.jsonl`
- Create: `seeds/mcp/train_seeds.jsonl`
- Create: `benchmark/mcp_canvas_benchmark.jsonl`
- Create: `benchmark/mcp_snowflake_benchmark.jsonl`
- Create: `benchmark/mcp_woocommerce_benchmark.jsonl`
- Create: `benchmark/mcp_yahoo_finance_benchmark.jsonl`
- Create: `benchmark/mcp_youtube_benchmark.jsonl`
- Create: `benchmark/mcp_train_benchmark.jsonl`

### Coding example validation and assets

- Create: `synthesis/tests/test_code_example_synthesis_config.py`
  Responsibility: validate the Coding synthesis config, `code-*` tool exposure, and repo-local `source_dir` contract.
- Create: `rollout/tests/test_code_example_assets.py`
  Responsibility: validate the Coding rollout config, bundled demo repo, seed data, and mixed read/edit benchmark tasks.
- Create: `rollout/tests/test_code_example_doc.py`
  Responsibility: validate `examples/CodingAgent.md` has the DS-style structure, exact `AGENTFLOW_REPO_ROOT` setup steps, and no machine-local path leakage.
- Create: `examples/CodingAgent.md`
- Create: `configs/synthesis/code_config.json`
- Create: `configs/trajectory/code_trajectory.json`
- Create: `seeds/code/seeds.jsonl`
- Create: `seeds/code/seed/demo_repo/README.md`
- Create: `seeds/code/seed/demo_repo/app.py`
- Create: `seeds/code/seed/demo_repo/config/app_config.json`
- Create: `seeds/code/seed/demo_repo/lib/helpers.py`
- Create: `seeds/code/seed/demo_repo/tests/smoke_test.py`
- Create: `benchmark/code_benchmark.jsonl`

## Chunk 1: Shared MCP Sandbox Contract

### Task 1: Lock the official MCP sandbox template

**Files:**
- Modify: `configs/sandbox-server/mcp_config.json`
- Modify: `sandbox/tests/test_sandbox_config_loading.py`
- Modify: `sandbox/tests/test_mcp_backend.py`
- Modify: `sandbox/tests/test_mcp_client.py`

- [ ] **Step 1: Add the failing MCP contract tests**

Add these exact assertions.

In `sandbox/tests/test_sandbox_config_loading.py`, add:

```python
def test_load_server_config_keeps_required_mcp_servers_path_placeholder_when_env_missing(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("TOOLATHLON_GYM_ROOT", raising=False)

    config_path = tmp_path / "mcp_config.json"
    raw_config = {
        "resources": {
            "mcp": {
                "enabled": True,
                "config": {
                    "mcp_servers_path": "${TOOLATHLON_GYM_ROOT}/local_servers"
                },
            }
        }
    }
    config_path.write_text(json.dumps(raw_config), encoding="utf-8")

    sandbox = Sandbox(config=SandboxConfig(server_config_path=str(config_path)))
    loaded = sandbox._load_server_config()

    assert (
        loaded["resources"]["mcp"]["config"]["mcp_servers_path"]
        == "${TOOLATHLON_GYM_ROOT}/local_servers"
    )
```

In `sandbox/tests/test_mcp_backend.py`, replace the current lightweight template parse check with:

```python
def test_mcp_config_template_declares_example_server_subset(monkeypatch):
    monkeypatch.delenv("TOOLATHLON_GYM_ROOT", raising=False)
    monkeypatch.delenv("PGHOST", raising=False)
    monkeypatch.delenv("PGPORT", raising=False)
    monkeypatch.delenv("PGUSER", raising=False)
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.delenv("PGDATABASE", raising=False)
    monkeypatch.delenv("CANVAS_DOMAIN", raising=False)
    monkeypatch.delenv("WORDPRESS_SITE_URL", raising=False)

    loader = ConfigLoader()
    config_path = (
        Path(__file__).resolve().parents[2]
        / "configs"
        / "sandbox-server"
        / "mcp_config.json"
    )

    config = loader.load(str(config_path))
    mcp_resource = config.resources["mcp"]
    mcp_config = mcp_resource.config

    assert mcp_resource.backend_class == (
        "sandbox.server.backends.resources.mcp.toolathlon_gym.ToolathlonGymBackend"
    )
    assert mcp_config["mcp_servers_path"] == "${TOOLATHLON_GYM_ROOT}/local_servers"
    assert mcp_config["enabled_mcp_servers"] == [
        "canvas",
        "snowflake",
        "woocommerce",
        "yahoo-finance",
        "youtube",
        "youtube-transcript",
        "rail_12306",
        "filesystem",
    ]
    assert mcp_config["env_overrides"] == {
        "PGHOST": "localhost",
        "PGPORT": "5432",
        "PGUSER": "eigent",
        "PGPASSWORD": "camel",
        "PGDATABASE": "toolathlon_gym",
        "CANVAS_DOMAIN": "localhost:8080",
        "WORDPRESS_SITE_URL": "http://localhost:8081",
    }
    assert config.warmup.enabled is True
    assert config.warmup.resources == ["mcp"]
```

In `sandbox/tests/test_mcp_client.py`, add:

```python
def test_load_mcp_process_config_resolves_toolathlon_local_servers_path(tmp_path):
    module = load_mcp_client_module()
    config_dir = tmp_path / "configs" / "mcp_servers"
    config_dir.mkdir(parents=True)
    (config_dir / "filesystem.yaml").write_text(
        """
type: stdio
name: filesystem
params:
  command: node
  args:
    - ${local_servers_paths}/filesystem/environment/dist/index.js
    - ${agent_workspace}
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    config = module.load_mcp_process_config(
        server_name="filesystem",
        agent_workspace="/tmp/agentflow-worker",
        mcp_servers_path="/tmp/toolathlon/local_servers",
        config_dir=config_dir,
    )

    assert config.command == "node"
    assert config.args == [
        "/tmp/toolathlon/local_servers/filesystem/environment/dist/index.js",
        "/tmp/agentflow-worker",
    ]
```

- [ ] **Step 2: Run the MCP contract tests and confirm they fail**

Run:

```bash
pytest \
  sandbox/tests/test_sandbox_config_loading.py::test_load_server_config_keeps_required_mcp_servers_path_placeholder_when_env_missing \
  sandbox/tests/test_mcp_backend.py::test_mcp_config_template_declares_example_server_subset \
  sandbox/tests/test_mcp_client.py::test_load_mcp_process_config_resolves_toolathlon_local_servers_path \
  -v
```

Expected: the suite should fail before the template update; likely causes are the missing `mcp_servers_path`, the old server subset, or the old `PGHOST` default, but the exact failing assertion may vary slightly if the branch state drifts.

- [ ] **Step 3: Update `configs/sandbox-server/mcp_config.json` to match the approved example contract**

Make `resources.mcp.config` match this exact shape:

```json
{
  "mcp_servers_path": "${TOOLATHLON_GYM_ROOT}/local_servers",
  "enabled_mcp_servers": [
    "canvas",
    "snowflake",
    "woocommerce",
    "yahoo-finance",
    "youtube",
    "youtube-transcript",
    "rail_12306",
    "filesystem"
  ],
  "workspace_root": "${TOOLATHLON_WORKSPACE_ROOT:-/tmp/agentflow_mcp}",
  "env_overrides": {
    "PGHOST": "${PGHOST:-localhost}",
    "PGPORT": "${PGPORT:-5432}",
    "PGUSER": "${PGUSER:-eigent}",
    "PGPASSWORD": "${PGPASSWORD:-camel}",
    "PGDATABASE": "${PGDATABASE:-toolathlon_gym}",
    "CANVAS_DOMAIN": "${CANVAS_DOMAIN:-localhost:8080}",
    "WORDPRESS_SITE_URL": "${WORDPRESS_SITE_URL:-http://localhost:8081}"
  }
}
```

Keep:

```json
"warmup": {
  "enabled": true,
  "resources": ["mcp"]
}
```

Do not add `terminal` back into the official example template.

- [ ] **Step 4: Re-run the MCP contract tests and verify they pass**

Run the same pytest command from Step 2.

Expected: PASS for all three tests.

- [ ] **Step 5: Commit the MCP sandbox contract change**

```bash
git add \
  configs/sandbox-server/mcp_config.json \
  sandbox/tests/test_sandbox_config_loading.py \
  sandbox/tests/test_mcp_backend.py \
  sandbox/tests/test_mcp_client.py
git commit -m "test: lock MCP example sandbox contract"
```

## Chunk 2: MCP Example Assets and Guide

### Task 2: Add MCP config and asset tests first

**Files:**
- Create: `synthesis/tests/test_mcp_example_synthesis_configs.py`
- Create: `rollout/tests/test_mcp_example_assets.py`

- [ ] **Step 1: Write the failing synthesis-config test file**

Create `synthesis/tests/test_mcp_example_synthesis_configs.py` with:

```python
import json
from pathlib import Path

import pytest

from synthesis.core.config import SynthesisConfig

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "canvas": {
        "tools": ["mcp:canvas.*", "mcp:filesystem.*"],
        "seeds_file": "seeds/mcp/canvas_seeds.jsonl",
        "seed_description": "Canvas MCP prompts",
    },
    "snowflake": {
        "tools": ["mcp:snowflake.*", "mcp:filesystem.*"],
        "seeds_file": "seeds/mcp/snowflake_seeds.jsonl",
        "seed_description": "Snowflake MCP prompts",
    },
    "woocommerce": {
        "tools": ["mcp:woocommerce.*", "mcp:filesystem.*"],
        "seeds_file": "seeds/mcp/woocommerce_seeds.jsonl",
        "seed_description": "WooCommerce MCP prompts",
    },
    "yahoo_finance": {
        "tools": ["mcp:yahoo-finance.*", "mcp:filesystem.*"],
        "seeds_file": "seeds/mcp/yahoo_finance_seeds.jsonl",
        "seed_description": "Yahoo Finance MCP prompts",
    },
    "youtube": {
        "tools": [
            "mcp:youtube.*",
            "mcp:youtube-transcript.*",
            "mcp:filesystem.*",
        ],
        "seeds_file": "seeds/mcp/youtube_seeds.jsonl",
        "seed_description": "YouTube MCP prompts",
    },
    "train": {
        "tools": ["mcp:rail_12306.*", "mcp:filesystem.*"],
        "seeds_file": "seeds/mcp/train_seeds.jsonl",
        "seed_description": "Train MCP prompts",
    },
}


@pytest.mark.parametrize("domain", sorted(EXPECTED))
def test_mcp_synthesis_config_contract(domain):
    expected = EXPECTED[domain]
    config_path = REPO_ROOT / "configs" / "synthesis" / f"mcp_{domain}_config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    config = SynthesisConfig.from_json(str(config_path))
    raw_init = raw.get("resource_init_configs", {})

    assert config.sandbox_config_path == "configs/sandbox-server/mcp_config.json"
    assert config.sandbox_auto_start is False
    assert config.resource_types == ["mcp"]
    assert raw_init in ({}, {"mcp": {"content": {}}})
    assert config.resource_init_configs in ({}, {"mcp": {"content": {}}})
    assert config.model_name == "openai/gpt-oss-120b"
    assert config.api_key == "${OPENAI_API_KEY}"
    assert config.base_url == "${OPENAI_API_URL}"
    assert config.max_depth == 12
    assert config.branching_factor == 2
    assert config.depth_threshold == 2
    assert config.min_depth == 2
    assert config.max_selected_traj == 1
    assert config.path_similarity_threshold == 0.7
    assert config.available_tools == expected["tools"]
    assert config.seeds_file == expected["seeds_file"]
    assert config.output_dir == f"results/mcp_{domain}"
    assert raw["seed_description"] == expected["seed_description"]
    assert len(config.qa_examples) >= 2
    assert config.sampling_tips.strip()
    assert config.synthesis_tips.strip()
```

- [ ] **Step 2: Write the failing rollout-asset test file**

Create `rollout/tests/test_mcp_example_assets.py` with:

```python
import json
from pathlib import Path

import pytest

from rollout.core.config import RolloutConfig

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "canvas": {
        "tools": ["mcp:canvas.*", "mcp:filesystem.*"],
        "benchmark": "benchmark/mcp_canvas_benchmark.jsonl",
        "benchmark_name": "mcp_canvas_trajectory",
    },
    "snowflake": {
        "tools": ["mcp:snowflake.*", "mcp:filesystem.*"],
        "benchmark": "benchmark/mcp_snowflake_benchmark.jsonl",
        "benchmark_name": "mcp_snowflake_trajectory",
    },
    "woocommerce": {
        "tools": ["mcp:woocommerce.*", "mcp:filesystem.*"],
        "benchmark": "benchmark/mcp_woocommerce_benchmark.jsonl",
        "benchmark_name": "mcp_woocommerce_trajectory",
    },
    "yahoo_finance": {
        "tools": ["mcp:yahoo-finance.*", "mcp:filesystem.*"],
        "benchmark": "benchmark/mcp_yahoo_finance_benchmark.jsonl",
        "benchmark_name": "mcp_yahoo_finance_trajectory",
    },
    "youtube": {
        "tools": [
            "mcp:youtube.*",
            "mcp:youtube-transcript.*",
            "mcp:filesystem.*",
        ],
        "benchmark": "benchmark/mcp_youtube_benchmark.jsonl",
        "benchmark_name": "mcp_youtube_trajectory",
    },
    "train": {
        "tools": ["mcp:rail_12306.*", "mcp:filesystem.*"],
        "benchmark": "benchmark/mcp_train_benchmark.jsonl",
        "benchmark_name": "mcp_train_trajectory",
    },
}


def _read_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.parametrize("domain", sorted(EXPECTED))
def test_mcp_rollout_config_contract(domain):
    expected = EXPECTED[domain]
    config_path = REPO_ROOT / "configs" / "trajectory" / f"mcp_{domain}_trajectory.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    config = RolloutConfig.from_json(str(config_path))
    raw_init = raw.get("resource_init_configs", {})

    assert config.benchmark_name == expected["benchmark_name"]
    assert config.data_path == expected["benchmark"]
    assert config.model_name == "openai/gpt-oss-120b"
    assert config.api_key == "${OPENAI_API_KEY}"
    assert config.base_url == "${OPENAI_API_URL}"
    assert config.max_turns == 20
    assert config.available_tools == expected["tools"]
    assert config.sandbox_config_path == "configs/sandbox-server/mcp_config.json"
    assert config.sandbox_auto_start is False
    assert config.resource_types == ["mcp"]
    assert raw_init in ({}, {"mcp": {"content": {}}})
    assert config.resource_init_configs in ({}, {"mcp": {"content": {}}})
    assert "MCP domain assistant" in config.system_prompt
    assert "Use only the available MCP tools" in config.system_prompt
    assert "Reply with the final answer only" in config.system_prompt
    assert config.evaluate_results is False
    assert config.output_dir == f"trajectory_results/mcp_{domain}"
    assert config.save_results is True
    assert config.trajectory_only is True
    assert config.save_trajectories is True


@pytest.mark.parametrize("domain", sorted(EXPECTED))
def test_mcp_seed_files_are_two_row_jsonl(domain):
    seed_path = REPO_ROOT / "seeds" / "mcp" / f"{domain}_seeds.jsonl"
    rows = _read_jsonl(seed_path)

    assert len(rows) == 2
    assert all(set(row.keys()) == {"content", "kwargs"} for row in rows)
    assert all(isinstance(row["content"], str) and row["content"].strip() for row in rows)
    assert all(row["kwargs"] == {} for row in rows)


@pytest.mark.parametrize("domain", sorted(EXPECTED))
def test_mcp_benchmark_files_have_two_row_jsonl_contract(domain):
    benchmark_path = REPO_ROOT / "benchmark" / f"mcp_{domain}_benchmark.jsonl"
    rows = _read_jsonl(benchmark_path)

    assert len(rows) == 2
    assert all(set(row.keys()) == {"id", "question", "answer"} for row in rows)
    assert all(isinstance(row["question"], str) and row["question"].strip() for row in rows)
    assert all(isinstance(row["answer"], str) for row in rows)
```

- [ ] **Step 3: Run the new MCP tests and verify they fail because the assets do not exist yet**

Run:

```bash
pytest \
  synthesis/tests/test_mcp_example_synthesis_configs.py \
  rollout/tests/test_mcp_example_assets.py \
  -v
```

Expected: FAIL with missing-file errors for the new MCP configs, seeds, and benchmarks.

### Task 3: Create the six-domain MCP seeds, benchmarks, and configs

**Files:**
- Create: `configs/synthesis/mcp_canvas_config.json`
- Create: `configs/synthesis/mcp_snowflake_config.json`
- Create: `configs/synthesis/mcp_woocommerce_config.json`
- Create: `configs/synthesis/mcp_yahoo_finance_config.json`
- Create: `configs/synthesis/mcp_youtube_config.json`
- Create: `configs/synthesis/mcp_train_config.json`
- Create: `configs/trajectory/mcp_canvas_trajectory.json`
- Create: `configs/trajectory/mcp_snowflake_trajectory.json`
- Create: `configs/trajectory/mcp_woocommerce_trajectory.json`
- Create: `configs/trajectory/mcp_yahoo_finance_trajectory.json`
- Create: `configs/trajectory/mcp_youtube_trajectory.json`
- Create: `configs/trajectory/mcp_train_trajectory.json`
- Create: `seeds/mcp/canvas_seeds.jsonl`
- Create: `seeds/mcp/snowflake_seeds.jsonl`
- Create: `seeds/mcp/woocommerce_seeds.jsonl`
- Create: `seeds/mcp/yahoo_finance_seeds.jsonl`
- Create: `seeds/mcp/youtube_seeds.jsonl`
- Create: `seeds/mcp/train_seeds.jsonl`
- Create: `benchmark/mcp_canvas_benchmark.jsonl`
- Create: `benchmark/mcp_snowflake_benchmark.jsonl`
- Create: `benchmark/mcp_woocommerce_benchmark.jsonl`
- Create: `benchmark/mcp_yahoo_finance_benchmark.jsonl`
- Create: `benchmark/mcp_youtube_benchmark.jsonl`
- Create: `benchmark/mcp_train_benchmark.jsonl`

- [ ] **Step 1: Create the six MCP seed files**

Use exactly two rows per file, each shaped as `{"content": "...", "kwargs": {}}`.

Seed rows:

- `seeds/mcp/canvas_seeds.jsonl`
  - `Use the available Canvas MCP tools to inspect courses, assignments, and enrollment information.`
  - `Find a small Canvas reporting task that can be answered from the mock data and save intermediate notes with filesystem tools if helpful.`
- `seeds/mcp/snowflake_seeds.jsonl`
  - `Use the available Snowflake MCP tools to inspect schemas, tables, and small analytical queries in the mock warehouse.`
  - `Find one compact warehouse reporting question that can be answered from the available Snowflake tools.`
- `seeds/mcp/woocommerce_seeds.jsonl`
  - `Use the WooCommerce MCP tools to inspect customers, products, and orders in the mock store.`
  - `Find one small sales or operations question that can be answered from the WooCommerce mock data.`
- `seeds/mcp/yahoo_finance_seeds.jsonl`
  - `Use the Yahoo Finance MCP tools to inspect the mock ticker and market data available locally.`
  - `Find one small finance lookup or comparison question that can be answered directly from the available tools.`
- `seeds/mcp/youtube_seeds.jsonl`
  - `Use the YouTube and YouTube Transcript MCP tools to inspect mock video metadata and transcript data.`
  - `Find one small content-discovery or transcript lookup question that can be answered from the local mock data.`
- `seeds/mcp/train_seeds.jsonl`
  - `Use the rail_12306 MCP tools to inspect mock train, station, and route information.`
  - `Find one small travel-planning or route lookup question that can be answered from the available railway tools.`

- [ ] **Step 2: Create the six MCP benchmark files**

Use exactly two rows per file with schema `{"id": "...", "question": "...", "answer": "..."}`.

Questions:

- `benchmark/mcp_canvas_benchmark.jsonl`
  - `{"id": "mcp_canvas_001", "question": "Use Canvas MCP tools to list the first three course names in alphabetical order. Reply as a comma-separated list only.", "answer": ""}`
  - `{"id": "mcp_canvas_002", "question": "Use Canvas MCP tools to find one course and report its course code plus enrollment count as code=<code>, enrolled=<int>.", "answer": ""}`
- `benchmark/mcp_snowflake_benchmark.jsonl`
  - `{"id": "mcp_snowflake_001", "question": "Use Snowflake MCP tools to list the first three tables visible in the default schema in alphabetical order. Reply as a comma-separated list only.", "answer": ""}`
  - `{"id": "mcp_snowflake_002", "question": "Use Snowflake MCP tools to compute one small aggregate from a mock table and reply as key=value.", "answer": ""}`
- `benchmark/mcp_woocommerce_benchmark.jsonl`
  - `{"id": "mcp_woocommerce_001", "question": "Use WooCommerce MCP tools to list the first three product names in alphabetical order. Reply as a comma-separated list only.", "answer": ""}`
  - `{"id": "mcp_woocommerce_002", "question": "Use WooCommerce MCP tools to identify one customer email and that customer's order count. Reply as email=<email>, orders=<int>.", "answer": ""}`
- `benchmark/mcp_yahoo_finance_benchmark.jsonl`
  - `{"id": "mcp_yahoo_finance_001", "question": "Use Yahoo Finance MCP tools to list the first three ticker symbols available in the mock dataset in alphabetical order. Reply as a comma-separated list only.", "answer": ""}`
  - `{"id": "mcp_yahoo_finance_002", "question": "Use Yahoo Finance MCP tools to compare two available mock tickers and reply with the one that has the larger price as symbol=<ticker>.", "answer": ""}`
- `benchmark/mcp_youtube_benchmark.jsonl`
  - `{"id": "mcp_youtube_001", "question": "Use YouTube MCP tools to list the first three video titles returned by the local mock dataset in alphabetical order. Reply as a comma-separated list only.", "answer": ""}`
  - `{"id": "mcp_youtube_002", "question": "Use YouTube Transcript MCP tools to find one video and report the video id plus transcript language as video=<id>, language=<lang>.", "answer": ""}`
- `benchmark/mcp_train_benchmark.jsonl`
  - `{"id": "mcp_train_001", "question": "Use rail_12306 MCP tools to list the first three station names available in the local mock dataset in alphabetical order. Reply as a comma-separated list only.", "answer": ""}`
  - `{"id": "mcp_train_002", "question": "Use rail_12306 MCP tools to find one route and reply with departure=<station>, arrival=<station>.", "answer": ""}`

During Chunk 2, keep all twelve `answer` fields as empty strings. Do not guess or invent answers here; Chunk 4 Task 9 is the required live grounding step that will fill them from the prepared mock environment.

- [ ] **Step 3: Create the six MCP synthesis configs**

Use `configs/synthesis/ds_config.json` for field ordering, but make each MCP file follow this exact contract:

```json
{
  "model_name": "openai/gpt-oss-120b",
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "${OPENAI_API_URL}",
  "max_depth": 12,
  "branching_factor": 2,
  "depth_threshold": 2,
  "min_depth": 2,
  "max_selected_traj": 1,
  "path_similarity_threshold": 0.7,
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": false,
  "sandbox_config_path": "configs/sandbox-server/mcp_config.json",
  "resource_types": ["mcp"],
  "resource_init_configs": {},
  "available_tools": ["mcp:<server>.*", "mcp:filesystem.*"],
  "sampling_tips": [
    "Domain-specific MCP exploration guidance",
    "Prefer using filesystem tools only for scratch notes or short saved artifacts."
  ],
  "synthesis_tips": [
    "Generate domain-grounded factual QA only.",
    "Keep answers short and directly verifiable from tool outputs."
  ],
  "qa_examples": [
    {"question": "Example question 1", "answer": "Example answer 1"},
    {"question": "Example question 2", "answer": "Example answer 2"}
  ],
  "seed_description": "Domain-specific MCP prompts",
  "seeds_file": "seeds/mcp/<domain>_seeds.jsonl",
  "output_dir": "results/mcp_<domain>"
}
```

Exact tool mappings:

- `canvas`: `["mcp:canvas.*", "mcp:filesystem.*"]`
- `snowflake`: `["mcp:snowflake.*", "mcp:filesystem.*"]`
- `woocommerce`: `["mcp:woocommerce.*", "mcp:filesystem.*"]`
- `yahoo_finance`: `["mcp:yahoo-finance.*", "mcp:filesystem.*"]`
- `youtube`: `["mcp:youtube.*", "mcp:youtube-transcript.*", "mcp:filesystem.*"]`
- `train`: `["mcp:rail_12306.*", "mcp:filesystem.*"]`

Exact `seed_description` strings:

- `Canvas MCP prompts`
- `Snowflake MCP prompts`
- `WooCommerce MCP prompts`
- `Yahoo Finance MCP prompts`
- `YouTube MCP prompts`
- `Train MCP prompts`

Each file must use 2-3 domain-specific `qa_examples`. Keep them domain-grounded and format-focused, but do not invent benchmark answers that depend on live mock data.

For `resource_init_configs`, the committed files should prefer:

```json
"resource_init_configs": {}
```

but the tests must also accept:

```json
"resource_init_configs": {
  "mcp": {
    "content": {}
  }
}
```

because the approved spec allows MCP init content to be omitted or explicitly empty.

- [ ] **Step 4: Create the six MCP rollout configs**

Use `configs/trajectory/ds_trajectory.json` for field ordering, but make each MCP rollout config follow this exact contract:

```json
{
  "benchmark_name": "mcp_<domain>_trajectory",
  "model_name": "openai/gpt-oss-120b",
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "${OPENAI_API_URL}",
  "max_turns": 20,
  "available_tools": ["mcp:<server>.*", "mcp:filesystem.*"],
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": false,
  "sandbox_config_path": "configs/sandbox-server/mcp_config.json",
  "resource_types": ["mcp"],
  "resource_init_configs": {},
  "system_prompt": [
    "You are an MCP domain assistant.",
    "Use only the available MCP tools to answer the question.",
    "Reply with the final answer only unless the question explicitly asks for another format."
  ],
  "evaluate_results": false,
  "data_path": "benchmark/mcp_<domain>_benchmark.jsonl",
  "output_dir": "trajectory_results/mcp_<domain>",
  "save_results": true,
  "save_trajectories": true,
  "trajectory_only": true
}
```

For `youtube`, the `available_tools` list must include both `mcp:youtube.*` and `mcp:youtube-transcript.*`.

As in Step 3, prefer `"resource_init_configs": {}` in the committed files, but keep the tests permissive enough to allow the spec-approved explicit-empty MCP init form.

- [ ] **Step 5: Run the MCP synthesis-config and rollout-asset tests and make them pass**

Run:

```bash
pytest \
  synthesis/tests/test_mcp_example_synthesis_configs.py \
  rollout/tests/test_mcp_example_assets.py \
  -v
```

Expected: PASS.

- [ ] **Step 6: Defer MCP benchmark answer grounding to Chunk 4**

Keep this chunk deterministic. Do not block Chunk 2 on external MCP services or LLM credentials. The required live answer-grounding step for MCP benchmarks happens later in Chunk 4 Task 9.

- [ ] **Step 7: Commit the MCP assets and configs**

```bash
git add \
  synthesis/tests/test_mcp_example_synthesis_configs.py \
  rollout/tests/test_mcp_example_assets.py \
  configs/synthesis/mcp_*.json \
  configs/trajectory/mcp_*.json \
  seeds/mcp \
  benchmark/mcp_*.jsonl
git commit -m "feat: add MCP example assets"
```

### Task 4: Add the MCP guide and lock the doc contract

**Files:**
- Create: `rollout/tests/test_mcp_example_doc.py`
- Create: `examples/MCPAgent.md`

- [ ] **Step 1: Write the failing MCP doc contract test**

Create `rollout/tests/test_mcp_example_doc.py` with:

```python
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_mcp_example_doc_has_required_sections_and_exact_prerequisite_contract():
    content = (REPO_ROOT / "examples" / "MCPAgent.md").read_text(encoding="utf-8")

    required_sections = [
        "## Overview",
        "## Prerequisites",
        "## Pipeline Overview",
        "## Step 1: Start the Sandbox Server",
        "## Step 2: Synthesize QA Data",
        "## Step 3: Synthesize Trajectory Data",
        "## Configuration Reference",
        "## FAQ",
    ]
    for section in required_sections:
        assert section in content

    required_strings = [
        "configs/sandbox-server/mcp_config.json",
        "configs/synthesis/mcp_canvas_config.json",
        "configs/synthesis/mcp_snowflake_config.json",
        "configs/synthesis/mcp_woocommerce_config.json",
        "configs/synthesis/mcp_yahoo_finance_config.json",
        "configs/synthesis/mcp_youtube_config.json",
        "configs/synthesis/mcp_train_config.json",
        "configs/trajectory/mcp_canvas_trajectory.json",
        "configs/trajectory/mcp_snowflake_trajectory.json",
        "configs/trajectory/mcp_woocommerce_trajectory.json",
        "configs/trajectory/mcp_yahoo_finance_trajectory.json",
        "configs/trajectory/mcp_youtube_trajectory.json",
        "configs/trajectory/mcp_train_trajectory.json",
        "export TOOLATHLON_GYM_ROOT=",
        "${TOOLATHLON_GYM_ROOT}/local_servers",
        "./start_sandbox_server.sh --config configs/sandbox-server/mcp_config.json",
        "node",
        "uv",
        "PGHOST",
        "PGPORT",
        "PGUSER",
        "PGPASSWORD",
        "PGDATABASE",
        "CANVAS_DOMAIN",
        "WORDPRESS_SITE_URL",
    ]
    for needle in required_strings:
        assert needle in content

    lowered = content.lower()
    assert "/home/" not in content
    assert "training" in lowered
    assert "deployment" in lowered
    assert "infer" in lowered
    assert "not covered" in lowered
    assert "Step 4" not in content
    assert "Step 5" not in content
```

- [ ] **Step 2: Run the doc contract test and confirm it fails**

Run:

```bash
pytest rollout/tests/test_mcp_example_doc.py -v
```

Expected: FAIL because `examples/MCPAgent.md` does not exist yet.

- [ ] **Step 3: Write `examples/MCPAgent.md` in DS-style structure**

The guide must:

- open with a DS-style three-step title, not a five-step title
- cover the six domains: `canvas`, `snowflake`, `woocommerce`, `yahoo_finance`, `youtube`, `train`
- explain that the example uses `configs/sandbox-server/mcp_config.json`
- include prerequisites for:
  - `cd AgentFlow`
  - `export OPENAI_API_KEY=...`
  - `export OPENAI_API_URL=...`
  - `export TOOLATHLON_GYM_ROOT=/path/to/toolathlon_gym`
  - an already prepared and already running Toolathlon-GYM environment
  - `node` and `uv`
- mention that the MCP server bundle is resolved from `${TOOLATHLON_GYM_ROOT}/local_servers`
- list the env override fields surfaced by `mcp_config.json`
- give one Step 1 command:

```bash
./start_sandbox_server.sh --config configs/sandbox-server/mcp_config.json
```

- give Step 2 commands for all six synthesis configs
- give Step 3 commands for all six rollout configs
- explicitly say later training / deployment / infer are not covered yet
- keep explanations short and example-oriented; do not add internal orchestration advice about restarting sandboxes between domains

- [ ] **Step 4: Run the MCP doc test and a targeted MCP suite**

Run:

```bash
pytest \
  rollout/tests/test_mcp_example_doc.py \
  synthesis/tests/test_mcp_example_synthesis_configs.py \
  rollout/tests/test_mcp_example_assets.py \
  -v
```

Expected: PASS.

- [ ] **Step 5: Commit the MCP guide**

```bash
git add rollout/tests/test_mcp_example_doc.py examples/MCPAgent.md
git commit -m "docs: add MCP example guide"
```

## Chunk 3: Coding Example Assets and Guide

### Task 5: Add Coding config and asset tests first

**Files:**
- Create: `synthesis/tests/test_code_example_synthesis_config.py`
- Create: `rollout/tests/test_code_example_assets.py`

- [ ] **Step 1: Write the failing Coding synthesis-config test**

Create `synthesis/tests/test_code_example_synthesis_config.py` with:

```python
import json
from pathlib import Path

from synthesis.core.config import SynthesisConfig

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_code_synthesis_config_contract():
    config_path = REPO_ROOT / "configs" / "synthesis" / "code_config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    config = SynthesisConfig.from_json(str(config_path))

    assert config.sandbox_config_path == "configs/sandbox-server/code_config.json"
    assert config.sandbox_auto_start is False
    assert config.resource_types == ["code"]
    assert config.resource_init_configs == {
        "code": {
            "content": {
                "source_dir": "${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo"
            }
        }
    }
    assert config.available_tools == ["code-*"]
    assert config.seeds_file == "seeds/code/seeds.jsonl"
    assert raw["seed_description"] == "Coding demo repository prompts"
    assert len(config.qa_examples) >= 2
    assert config.sampling_tips.strip()
    assert config.synthesis_tips.strip()
```

- [ ] **Step 2: Write the failing Coding rollout-asset test**

Create `rollout/tests/test_code_example_assets.py` with:

```python
import json
from pathlib import Path

from rollout.core.config import RolloutConfig

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_code_rollout_config_contract():
    config_path = REPO_ROOT / "configs" / "trajectory" / "code_trajectory.json"
    config = RolloutConfig.from_json(str(config_path))

    assert config.benchmark_name == "code_trajectory"
    assert config.data_path == "benchmark/code_benchmark.jsonl"
    assert config.available_tools == ["code-*"]
    assert config.sandbox_config_path == "configs/sandbox-server/code_config.json"
    assert config.sandbox_auto_start is False
    assert config.resource_types == ["code"]
    assert config.resource_init_configs == {
        "code": {
            "content": {
                "source_dir": "${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo"
            }
        }
    }
    assert config.evaluate_results is False
    assert config.trajectory_only is True
    assert config.save_trajectories is True
    assert config.save_summary is False


def test_code_seed_file_contract():
    rows = _read_jsonl(REPO_ROOT / "seeds" / "code" / "seeds.jsonl")

    assert len(rows) == 2
    assert all(set(row.keys()) == {"content", "kwargs"} for row in rows)
    assert all(isinstance(row["content"], str) and row["content"].strip() for row in rows)
    assert all(row["kwargs"] == {} for row in rows)


def test_code_benchmark_contract():
    rows = _read_jsonl(REPO_ROOT / "benchmark" / "code_benchmark.jsonl")

    assert len(rows) == 2
    assert all({"id", "question", "answer"} <= set(row.keys()) for row in rows)
    assert rows[0]["id"] == "code_read_001"
    assert "metadata" not in rows[0]
    assert rows[1]["id"] == "code_edit_001"
    assert "tests/smoke_test.py" in rows[1]["question"]
    assert rows[1]["answer"] == "smoke test passed"
    assert rows[1]["metadata"] == {
        "target_files": ["app.py"],
        "check_command": "python tests/smoke_test.py",
    }
    assert all("/home/" not in json.dumps(row, ensure_ascii=False) for row in rows)
    assert all("DataFlow" not in json.dumps(row, ensure_ascii=False) for row in rows)


def test_code_demo_repo_contract():
    repo_root = REPO_ROOT / "seeds" / "code" / "seed" / "demo_repo"

    required_paths = [
        repo_root / "README.md",
        repo_root / "app.py",
        repo_root / "config" / "app_config.json",
        repo_root / "lib" / "helpers.py",
        repo_root / "tests" / "smoke_test.py",
    ]
    for path in required_paths:
        assert path.exists(), path

    smoke_test = (repo_root / "tests" / "smoke_test.py").read_text(encoding="utf-8")
    assert "build_message" in smoke_test
    assert "SMOKE_OK" in smoke_test
```

- [ ] **Step 3: Run the new Coding tests and verify they fail because the assets do not exist yet**

Run:

```bash
pytest \
  synthesis/tests/test_code_example_synthesis_config.py \
  rollout/tests/test_code_example_assets.py \
  -v
```

Expected: FAIL with missing-file errors for the new Coding config, seed, benchmark, and demo repo files.

### Task 6: Create the Coding demo repo, seeds, benchmark, and configs

**Files:**
- Create: `configs/synthesis/code_config.json`
- Create: `configs/trajectory/code_trajectory.json`
- Create: `seeds/code/seeds.jsonl`
- Create: `seeds/code/seed/demo_repo/README.md`
- Create: `seeds/code/seed/demo_repo/app.py`
- Create: `seeds/code/seed/demo_repo/config/app_config.json`
- Create: `seeds/code/seed/demo_repo/lib/helpers.py`
- Create: `seeds/code/seed/demo_repo/tests/smoke_test.py`
- Create: `benchmark/code_benchmark.jsonl`

- [ ] **Step 1: Create the committed demo repo contents**

Use these exact file contents.

`seeds/code/seed/demo_repo/README.md`

```md
# Coding Example Demo Repo

This tiny repository is bundled for AgentFlow's CodingAgent example.

- `app.py` builds a greeting string.
- `config/app_config.json` stores the expected name and suffix.
- `lib/helpers.py` contains the formatting helper.
- `tests/smoke_test.py` is the verification command used by the rollout example.
```

`seeds/code/seed/demo_repo/config/app_config.json`

```json
{
  "default_name": "AgentFlow",
  "suffix": "!"
}
```

`seeds/code/seed/demo_repo/lib/helpers.py`

```python
def render_greeting(name: str, suffix: str) -> str:
    return f"Hello, {name}{suffix}"
```

`seeds/code/seed/demo_repo/app.py`

```python
import json
from pathlib import Path

from lib.helpers import render_greeting


CONFIG_PATH = Path(__file__).parent / "config" / "app_config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def build_message() -> str:
    config = load_config()
    return render_greeting(config["default_name"], "?")


if __name__ == "__main__":
    print(build_message())
```

`seeds/code/seed/demo_repo/tests/smoke_test.py`

```python
from app import build_message


def main() -> None:
    message = build_message()
    assert message == "Hello, AgentFlow!", message
    print("SMOKE_OK")


if __name__ == "__main__":
    main()
```

Keep the `app.py` / `smoke_test.py` mismatch intentional here: the hard-coded `"?"` is the planned edit-task bug that the bundled Coding benchmark will exercise later.

- [ ] **Step 2: Create the Coding seed and benchmark files**

`seeds/code/seeds.jsonl` must contain exactly:

```jsonl
{"content": "Inspect the demo repository and trace how the greeting is assembled from config and helper code.", "kwargs": {}}
{"content": "Look for a small repository bug that can be fixed with a minimal edit and validated with the committed smoke test.", "kwargs": {}}
```

`benchmark/code_benchmark.jsonl` must contain exactly two rows:

```jsonl
{"id": "code_read_001", "question": "Use code tools to inspect the demo repository. What default name does the app greet? Reply with the name only.", "answer": "AgentFlow"}
{"id": "code_edit_001", "question": "Update the demo repository so `python tests/smoke_test.py` succeeds. Preserve the config-driven greeting behavior, verify the fix with that command, then reply with exactly `smoke test passed`.", "answer": "smoke test passed", "metadata": {"target_files": ["app.py"], "check_command": "python tests/smoke_test.py"}}
```

- [ ] **Step 3: Create the Coding synthesis config**

Create `configs/synthesis/code_config.json` with this exact contract:

```json
{
  "model_name": "openai/gpt-oss-120b",
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "${OPENAI_API_URL}",
  "max_depth": 10,
  "branching_factor": 2,
  "depth_threshold": 2,
  "min_depth": 2,
  "max_selected_traj": 1,
  "path_similarity_threshold": 0.7,
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": false,
  "sandbox_config_path": "configs/sandbox-server/code_config.json",
  "resource_types": ["code"],
  "resource_init_configs": {
    "code": {
      "content": {
        "source_dir": "${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo"
      }
    }
  },
  "available_tools": ["code-*"],
  "sampling_tips": [
    "Inspect the repository before proposing edits.",
    "Use code-bash only for lightweight checks that fit the bundled demo repo."
  ],
  "synthesis_tips": [
    "Generate repo-grounded QA only.",
    "Prefer file-path, function-behavior, and small edit-validation questions over open-ended design prompts."
  ],
  "qa_examples": [
    {
      "question": "Which file stores the greeting suffix used by the demo app? Reply with the relative file path only.",
      "answer": "config/app_config.json"
    },
    {
      "question": "What string does `build_message()` return before any edits? Reply with the exact string only.",
      "answer": "Hello, AgentFlow?"
    }
  ],
  "seed_description": "Coding demo repository prompts",
  "seeds_file": "seeds/code/seeds.jsonl",
  "output_dir": "results/code"
}
```

- [ ] **Step 4: Create the Coding rollout config**

Create `configs/trajectory/code_trajectory.json` with this exact contract:

```json
{
  "benchmark_name": "code_trajectory",
  "model_name": "openai/gpt-oss-120b",
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "${OPENAI_API_URL}",
  "max_turns": 12,
  "available_tools": ["code-*"],
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": false,
  "sandbox_config_path": "configs/sandbox-server/code_config.json",
  "resource_types": ["code"],
  "resource_init_configs": {
    "code": {
      "content": {
        "source_dir": "${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo"
      }
    }
  },
  "system_prompt": [
    "You are a coding assistant working inside a small repository.",
    "Inspect files before editing them.",
    "When a task asks for verification, run the requested command inside the coding workspace before giving the final answer."
  ],
  "evaluate_results": false,
  "data_path": "benchmark/code_benchmark.jsonl",
  "output_dir": "trajectory_results/code",
  "save_results": true,
  "save_trajectories": true,
  "trajectory_only": true,
  "save_summary": false
}
```

- [ ] **Step 5: Run the Coding config and asset tests plus deterministic backend coverage**

Run:

```bash
pytest \
  synthesis/tests/test_code_example_synthesis_config.py \
  rollout/tests/test_code_example_assets.py \
  sandbox/tests/test_code_backend.py \
  sandbox/tests/test_code_tool_schemas.py \
  -v
```

Expected: PASS.

- [ ] **Step 6: Defer the credential-dependent live Coding rollout to Chunk 4**

Do not block this chunk on external credentials or a running sandbox. The required gate for Chunk 3 is the deterministic pytest suite from Step 5. Perform the representative live Coding rollout later using Chunk 4 Task 10.

- [ ] **Step 7: Commit the Coding assets**

```bash
git add \
  synthesis/tests/test_code_example_synthesis_config.py \
  rollout/tests/test_code_example_assets.py \
  configs/synthesis/code_config.json \
  configs/trajectory/code_trajectory.json \
  seeds/code \
  benchmark/code_benchmark.jsonl
git commit -m "feat: add Coding example assets"
```

### Task 7: Add the Coding guide and lock the doc contract

**Files:**
- Create: `rollout/tests/test_code_example_doc.py`
- Create: `examples/CodingAgent.md`

- [ ] **Step 1: Write the failing Coding doc contract test**

Create `rollout/tests/test_code_example_doc.py` with:

```python
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_coding_example_doc_has_required_sections_and_repo_root_contract():
    content = (REPO_ROOT / "examples" / "CodingAgent.md").read_text(encoding="utf-8")

    required_sections = [
        "## Overview",
        "## Prerequisites",
        "## Pipeline Overview",
        "## Step 1: Start the Sandbox Server",
        "## Step 2: Synthesize QA Data",
        "## Step 3: Synthesize Trajectory Data",
        "## Configuration Reference",
        "## FAQ",
    ]
    for section in required_sections:
        assert section in content

    required_strings = [
        "cd AgentFlow",
        "export AGENTFLOW_REPO_ROOT=$(pwd)",
        "code-*",
        "configs/sandbox-server/code_config.json",
        "configs/synthesis/code_config.json",
        "configs/trajectory/code_trajectory.json",
        "benchmark/code_benchmark.jsonl",
        "seeds/code/seeds.jsonl",
        "seeds/code/seed/demo_repo",
        "${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo",
        "source_dir",
        "./start_sandbox_server.sh --config configs/sandbox-server/code_config.json",
        "python tests/smoke_test.py",
        "training / deployment / infer are not covered yet",
    ]
    for needle in required_strings:
        assert needle in content

    assert "/home/a1/sdb/dxd/DataFlow" not in content
    assert "DataFlow" not in content
    assert "Step 4" not in content
    assert "Step 5" not in content
```

- [ ] **Step 2: Run the Coding doc test and confirm it fails**

Run:

```bash
pytest rollout/tests/test_code_example_doc.py -v
```

Expected: FAIL because `examples/CodingAgent.md` does not exist yet.

- [ ] **Step 3: Write `examples/CodingAgent.md` in DS-style structure**

The guide must:

- use a DS-style three-step title
- explain that CodingAgent uses the `code` backend’s six tools through `code-*`
- include prerequisites for:
  - `cd AgentFlow`
  - `export OPENAI_API_KEY=...`
  - `export OPENAI_API_URL=...`
  - `export AGENTFLOW_REPO_ROOT=$(pwd)`
- document the default committed repo path `${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo`
- say users can replace `resource_init_configs.code.content.source_dir` with their own repo path if desired
- use `configs/sandbox-server/code_config.json` for Step 1
- use `configs/synthesis/code_config.json` for Step 2
- use `configs/trajectory/code_trajectory.json` for Step 3
- mention `benchmark/code_benchmark.jsonl`
- mention the bundled read-only plus edit-task example style
- explicitly say later training / deployment / infer are not covered yet
- keep the explanation example-oriented; do not mention the user’s local DataFlow path

- [ ] **Step 4: Run the Coding doc test and the targeted Coding suite**

Run:

```bash
pytest \
  rollout/tests/test_code_example_doc.py \
  synthesis/tests/test_code_example_synthesis_config.py \
  rollout/tests/test_code_example_assets.py \
  sandbox/tests/test_code_backend.py \
  sandbox/tests/test_code_tool_schemas.py \
  -v
```

Expected: PASS.

- [ ] **Step 5: Commit the Coding guide**

```bash
git add rollout/tests/test_code_example_doc.py examples/CodingAgent.md
git commit -m "docs: add Coding example guide"
```

## Chunk 4: Final Verification and Local Dry Runs

### Task 8: Run the required deterministic verification suite

**Files:**
- No planned file changes. If any failures appear here, fix them in the owning chunk and create a normal corrective commit before reporting completion.

- [ ] **Step 1: Run the full targeted example suite**

Run:

```bash
pytest \
  sandbox/tests/test_sandbox_config_loading.py \
  sandbox/tests/test_mcp_backend.py \
  sandbox/tests/test_mcp_client.py \
  sandbox/tests/test_code_backend.py \
  sandbox/tests/test_code_tool_schemas.py \
  synthesis/tests/test_mcp_example_synthesis_configs.py \
  synthesis/tests/test_code_example_synthesis_config.py \
  rollout/tests/test_mcp_example_assets.py \
  rollout/tests/test_mcp_example_doc.py \
  rollout/tests/test_code_example_assets.py \
  rollout/tests/test_code_example_doc.py \
  -v
```

Expected: PASS.

- [ ] **Step 2: Record final status without creating a verification-only commit**

If Step 1 is green, continue to Task 9 to finalize the MCP benchmark answers. If a verification failure requires code or doc fixes, make the fix in the owning chunk, rerun the affected tests, and create a normal corrective commit rather than a “verification only” commit.

### Task 9: Finalize MCP benchmark answers against the prepared Toolathlon-GYM environment

**Files:**
- Modify: `benchmark/mcp_canvas_benchmark.jsonl`
- Modify: `benchmark/mcp_snowflake_benchmark.jsonl`
- Modify: `benchmark/mcp_woocommerce_benchmark.jsonl`
- Modify: `benchmark/mcp_yahoo_finance_benchmark.jsonl`
- Modify: `benchmark/mcp_youtube_benchmark.jsonl`
- Modify: `benchmark/mcp_train_benchmark.jsonl`

This task is required to convert the placeholder MCP benchmark answers from Chunk 2 into real benchmark answers. If `OPENAI_API_KEY`, `OPENAI_API_URL`, or the prepared Toolathlon-GYM environment are unavailable, stop here and report a blocker instead of inventing answers.

- [ ] **Step 1: Start the MCP sandbox server**

Run in a dedicated terminal from the AgentFlow repo root:

```bash
export TOOLATHLON_GYM_ROOT=/path/to/toolathlon_gym
./start_sandbox_server.sh --config configs/sandbox-server/mcp_config.json
```

Expected: the MCP sandbox stays running while Step 2 and Step 3 execute.

- [ ] **Step 2: Run one MCP synthesis smoke check**

Run:

```bash
export TOOLATHLON_GYM_ROOT=/path/to/toolathlon_gym
export OPENAI_API_KEY=...
export OPENAI_API_URL=...
python synthesis/pipeline.py \
  --config configs/synthesis/mcp_canvas_config.json \
  --seeds seeds/mcp/canvas_seeds.jsonl \
  --output-dir /tmp/agentflow-mcp-canvas-synth
```

Expected: the command starts successfully with the checked-in MCP config. If the current synthesis pipeline still writes to the repo’s shared aggregation directory, confirm that new QA / trajectory rows appear there; otherwise confirm output appears under `/tmp/agentflow-mcp-canvas-synth/`.

- [ ] **Step 3: Run the six MCP rollout configs and transcribe grounded answers**

Run:

```bash
export TOOLATHLON_GYM_ROOT=/path/to/toolathlon_gym
export OPENAI_API_KEY=...
export OPENAI_API_URL=...
python -m rollout.pipeline --config configs/trajectory/mcp_canvas_trajectory.json --output-dir /tmp/agentflow-mcp-canvas-check
python -m rollout.pipeline --config configs/trajectory/mcp_snowflake_trajectory.json --output-dir /tmp/agentflow-mcp-snowflake-check
python -m rollout.pipeline --config configs/trajectory/mcp_woocommerce_trajectory.json --output-dir /tmp/agentflow-mcp-woocommerce-check
python -m rollout.pipeline --config configs/trajectory/mcp_yahoo_finance_trajectory.json --output-dir /tmp/agentflow-mcp-yahoo-finance-check
python -m rollout.pipeline --config configs/trajectory/mcp_youtube_trajectory.json --output-dir /tmp/agentflow-mcp-youtube-check
python -m rollout.pipeline --config configs/trajectory/mcp_train_trajectory.json --output-dir /tmp/agentflow-mcp-train-check
```

For each domain:

- open the newest results JSONL under the matching `/tmp/agentflow-mcp-<domain>-check/` directory
- for each task, verify the candidate answer against the saved trajectory’s MCP tool output (`trajectory.messages` tool entries and/or `trajectory.tool_calls[*].result`) rather than trusting only `predicted_answer`
- copy the tool-supported final textual answers into the corresponding two rows in `benchmark/mcp_<domain>_benchmark.jsonl`

Expected: all six rollout commands start successfully, each output directory contains a results JSONL file, and every committed MCP benchmark answer is backed by observed tool output.

- [ ] **Step 4: Validate that all MCP benchmark answers are now populated**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path

for path in sorted(Path("benchmark").glob("mcp_*_benchmark.jsonl")):
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows, path
    assert all(isinstance(row["answer"], str) and row["answer"].strip() for row in rows), path
print("MCP benchmark answers verified")
PY
```

Expected: the script prints `MCP benchmark answers verified`.

- [ ] **Step 5: Re-run the MCP asset contract test after editing the benchmark files**

Run:

```bash
pytest rollout/tests/test_mcp_example_assets.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit the grounded MCP benchmark answers**

```bash
git add \
  benchmark/mcp_canvas_benchmark.jsonl \
  benchmark/mcp_snowflake_benchmark.jsonl \
  benchmark/mcp_woocommerce_benchmark.jsonl \
  benchmark/mcp_yahoo_finance_benchmark.jsonl \
  benchmark/mcp_youtube_benchmark.jsonl \
  benchmark/mcp_train_benchmark.jsonl
git commit -m "test: ground MCP benchmark answers"
```

### Task 10: Run optional Coding live smoke checks when LLM credentials are available

**Files:**
- No planned file changes. Skip this task if `OPENAI_API_KEY` or `OPENAI_API_URL` are unavailable. Record the skip reason in the execution report.

- [ ] **Step 1: Start the Code sandbox server**

Run in a dedicated terminal from the AgentFlow repo root:

```bash
./start_sandbox_server.sh --config configs/sandbox-server/code_config.json
```

Expected: the Code sandbox stays running while Step 2-4 execute.

- [ ] **Step 2: Run one Coding synthesis smoke check with the bundled repo**

Run:

```bash
# from the AgentFlow repo root
export OPENAI_API_KEY=...
export OPENAI_API_URL=...
export AGENTFLOW_REPO_ROOT=$(pwd)
python synthesis/pipeline.py \
  --config configs/synthesis/code_config.json \
  --seeds seeds/code/seeds.jsonl \
  --output-dir /tmp/agentflow-code-synth-check
```

Expected: the command starts successfully with the checked-in Coding synthesis config. If the current synthesis pipeline still writes to the repo’s shared aggregation directory, confirm that new QA / trajectory rows appear there; otherwise confirm output appears under `/tmp/agentflow-code-synth-check/`.

- [ ] **Step 3: Run one Coding rollout smoke check with the bundled repo**

Run:

```bash
# from the AgentFlow repo root
export OPENAI_API_KEY=...
export OPENAI_API_URL=...
export AGENTFLOW_REPO_ROOT=$(pwd)
python -m rollout.pipeline \
  --config configs/trajectory/code_trajectory.json \
  --task-ids code_edit_001 \
  --output-dir /tmp/agentflow-code-final-check
```

Expected: the rollout starts successfully, copies the bundled demo repo into the code workspace, and writes results JSONL under `/tmp/agentflow-code-final-check/`.

- [ ] **Step 4: Optionally prove the documented `source_dir` override path works with another local repo**

Run:

```bash
# from the AgentFlow repo root
export OPENAI_API_KEY=...
export OPENAI_API_URL=...
export AGENTFLOW_REPO_ROOT=$(pwd)
export LOCAL_CODE_REPO=/abs/path/to/local/repo
python - <<'PY'
import json
import os
from pathlib import Path

src = Path("configs/trajectory/code_trajectory.json")
dst = Path("/tmp/code_trajectory_local_repo.json")
payload = json.loads(src.read_text(encoding="utf-8"))
payload["resource_init_configs"]["code"]["content"]["source_dir"] = os.environ["LOCAL_CODE_REPO"]
payload["data_path"] = "/tmp/code_override_benchmark.jsonl"
dst.write_text(json.dumps(payload, indent=2), encoding="utf-8")
Path("/tmp/code_override_benchmark.jsonl").write_text(
    json.dumps(
        {
            "id": "code_override_read_001",
            "question": "Use code tools to inspect the repository and reply with the relative path of any one file located at the repository root.",
        }
    )
    + "\n",
    encoding="utf-8",
)
print(dst)
PY
python -m rollout.pipeline \
  --config /tmp/code_trajectory_local_repo.json \
  --max-tasks 1 \
  --output-dir /tmp/agentflow-code-local-repo-check
```

Expected: the override-repo rollout starts successfully against the temporary generic benchmark and writes a result file, proving the documented `source_dir` override works without hard-coding any machine-local repo path into committed assets.

Plan complete and saved to `docs/superpowers/plans/2026-04-20-mcp-and-coding-examples-implementation.md`. Ready to execute?
