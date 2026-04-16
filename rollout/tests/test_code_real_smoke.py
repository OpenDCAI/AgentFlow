import json

import pytest

from rollout import RolloutConfig, RolloutPipeline


pytestmark = pytest.mark.code_real


def _canonical_tool_name(name):
    for separator in (".", "_", "-"):
        if separator in name:
            prefix, suffix = name.split(separator, 1)
            return f"{prefix}:{suffix}"
    return name


def test_code_real_smoke_reads_token_via_real_tools(
    tmp_path,
    real_api_key,
    real_base_url,
    real_model,
):
    fixture_repo = tmp_path / "fixture_repo"
    nested_dir = fixture_repo / "nested"
    nested_dir.mkdir(parents=True)

    token = f"token-{tmp_path.name}"
    (nested_dir / "TOKEN.txt").write_text(token + "\n", encoding="utf-8")

    benchmark_path = tmp_path / "benchmark.jsonl"
    prompt = (
        "Use code tools to inspect the repository and read nested/TOKEN.txt. "
        "Reply with only the exact token and nothing else."
    )
    benchmark_path.write_text(
        json.dumps(
            {
                "id": "code-real-smoke",
                "question": prompt,
                "answer": token,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "rollout_output"
    config = RolloutConfig(
        benchmark_name="code_real_smoke",
        data_path=str(benchmark_path),
        model_name=real_model,
        api_key=real_api_key,
        base_url=real_base_url,
        available_tools=["code-*"],
        resource_types=["code"],
        resource_init_configs={
            "code": {"content": {"source_dir": str(fixture_repo)}}
        },
        sandbox_config_path="configs/sandbox-server/code_config.json",
        sandbox_auto_start=True,
        evaluate_results=False,
        save_trajectories=True,
        number_of_tasks=1,
    )

    summary = RolloutPipeline(config, output_dir=str(output_dir)).run()

    assert summary.total_tasks == 1
    assert summary.successful_tasks == 1
    assert summary.failed_tasks == 0

    result_files = sorted(output_dir.glob("results_code_real_smoke_*.jsonl"))
    assert result_files

    payload = json.loads(result_files[-1].read_text(encoding="utf-8").strip())
    trajectory = payload["trajectory"]
    tool_calls = trajectory["tool_calls"]
    tool_messages = [
        message for message in trajectory["messages"] if message["role"] == "tool"
    ]

    assert any(
        _canonical_tool_name(call["tool_name"]).startswith("code:")
        for call in tool_calls
    )
    assert payload["predicted_answer"] == token
    assert trajectory["final_answer"] == token
    assert any(
        token in json.dumps(message, ensure_ascii=False) for message in tool_messages
    )
