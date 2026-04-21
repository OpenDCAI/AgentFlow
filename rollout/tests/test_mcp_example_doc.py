from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _get_section(content: str, heading: str, next_heading: str) -> str:
    start = content.index(heading)
    end = content.index(next_heading, start)
    return content[start:end]


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

    step_2_content = _get_section(
        content,
        "## Step 2: Synthesize QA Data",
        "## Step 3: Synthesize Trajectory Data",
    )

    step_2_requirements = [
        "configs/synthesis/mcp_canvas_config.json",
        "configs/synthesis/mcp_snowflake_config.json",
        "configs/synthesis/mcp_woocommerce_config.json",
        "configs/synthesis/mcp_yahoo_finance_config.json",
        "configs/synthesis/mcp_youtube_config.json",
        "configs/synthesis/mcp_train_config.json",
        "results/ds_synthesized_qa/",
        "results/ds_synthesized_qa/synthesized_qa.jsonl",
        "results/ds_synthesized_qa/trajectories.jsonl",
        "> Note: in this repo, synthesis currently writes to the fixed aggregation directory `results/ds_synthesized_qa/`, even if you provide a different `--output-dir`.",
    ]
    for needle in step_2_requirements:
        assert needle in step_2_content

    expected_commands = [
        """python3 synthesis/pipeline.py \\
  --config configs/synthesis/mcp_canvas_config.json \\
  --seeds seeds/mcp/canvas_seeds.jsonl \\
  --output-dir results/mcp_canvas""",
        """python3 synthesis/pipeline.py \\
  --config configs/synthesis/mcp_snowflake_config.json \\
  --seeds seeds/mcp/snowflake_seeds.jsonl \\
  --output-dir results/mcp_snowflake""",
        """python3 synthesis/pipeline.py \\
  --config configs/synthesis/mcp_woocommerce_config.json \\
  --seeds seeds/mcp/woocommerce_seeds.jsonl \\
  --output-dir results/mcp_woocommerce""",
        """python3 synthesis/pipeline.py \\
  --config configs/synthesis/mcp_yahoo_finance_config.json \\
  --seeds seeds/mcp/yahoo_finance_seeds.jsonl \\
  --output-dir results/mcp_yahoo_finance""",
        """python3 synthesis/pipeline.py \\
  --config configs/synthesis/mcp_youtube_config.json \\
  --seeds seeds/mcp/youtube_seeds.jsonl \\
  --output-dir results/mcp_youtube""",
        """python3 synthesis/pipeline.py \\
  --config configs/synthesis/mcp_train_config.json \\
  --seeds seeds/mcp/train_seeds.jsonl \\
  --output-dir results/mcp_train""",
    ]
    for command in expected_commands:
        assert command in step_2_content

    assert "### Output files" not in step_2_content

    lowered = content.lower()
    assert "/home/" not in content
    assert "training" in lowered
    assert "deployment" in lowered
    assert "infer" in lowered
    assert "not covered" in lowered
    assert "Step 4" not in content
    assert "Step 5" not in content
