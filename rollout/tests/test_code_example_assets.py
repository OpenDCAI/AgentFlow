import json
import shutil
import subprocess
import sys
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


def test_code_demo_repo_smoke_test_runtime_contract(tmp_path):
    source_repo = REPO_ROOT / "seeds" / "code" / "seed" / "demo_repo"
    repo_copy = tmp_path / "demo_repo"
    shutil.copytree(source_repo, repo_copy)

    pre_fix = subprocess.run(
        [sys.executable, "tests/smoke_test.py"],
        cwd=repo_copy,
        capture_output=True,
        text=True,
        check=False,
    )

    assert pre_fix.returncode != 0
    assert "AssertionError: Hello, AgentFlow?" in pre_fix.stderr
    assert "ModuleNotFoundError" not in pre_fix.stderr

    app_path = repo_copy / "app.py"
    app_text = app_path.read_text(encoding="utf-8")
    app_path.write_text(
        app_text.replace('render_greeting(config["default_name"], "?")', 'render_greeting(config["default_name"], "!")'),
        encoding="utf-8",
    )

    post_fix = subprocess.run(
        [sys.executable, "tests/smoke_test.py"],
        cwd=repo_copy,
        capture_output=True,
        text=True,
        check=False,
    )

    assert post_fix.returncode == 0, post_fix.stderr
    assert post_fix.stdout.strip() == "SMOKE_OK"
