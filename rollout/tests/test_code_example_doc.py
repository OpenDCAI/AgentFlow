from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _get_section(content: str, heading: str, next_heading: str) -> str:
    start = content.index(heading)
    end = content.index(next_heading, start)
    return content[start:end]


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
        "3-Step Example Guide",
        "cd AgentFlow",
        "export OPENAI_API_KEY=",
        "export OPENAI_API_URL=",
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

    step_2_content = _get_section(
        content,
        "## Step 2: Synthesize QA Data",
        "## Step 3: Synthesize Trajectory Data",
    )

    step_2_requirements = [
        "configs/synthesis/code_config.json",
        "results/code",
        "results/ds_synthesized_qa/",
        "results/ds_synthesized_qa/synthesized_qa.jsonl",
        "results/ds_synthesized_qa/trajectories.jsonl",
        "> Note: in this repo, synthesis currently writes to the fixed aggregation directory `results/ds_synthesized_qa/`, even if you provide a different `--output-dir`.",
    ]
    for needle in step_2_requirements:
        assert needle in step_2_content

    expected_command = """python3 synthesis/pipeline.py \\
  --config configs/synthesis/code_config.json \\
  --seeds seeds/code/seeds.jsonl \\
  --output-dir results/code"""
    assert expected_command in step_2_content

    assert "### Output files" not in step_2_content

    assert "/home/a1/sdb/dxd/DataFlow" not in content
    assert "DataFlow" not in content
    assert "Step 4" not in content
    assert "Step 5" not in content
