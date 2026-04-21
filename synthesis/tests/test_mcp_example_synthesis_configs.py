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
