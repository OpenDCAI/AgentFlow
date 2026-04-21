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
