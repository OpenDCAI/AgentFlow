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
