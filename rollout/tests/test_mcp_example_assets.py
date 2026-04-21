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
