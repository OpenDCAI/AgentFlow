import json
from pathlib import Path

from synthesis.core.config import SynthesisConfig

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_code_synthesis_config_contract_expands_repo_root_when_set(monkeypatch):
    config_path = REPO_ROOT / "configs" / "synthesis" / "code_config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    monkeypatch.setenv("AGENTFLOW_REPO_ROOT", str(REPO_ROOT))
    config = SynthesisConfig.from_json(str(config_path))

    assert config.sandbox_config_path == "configs/sandbox-server/code_config.json"
    assert config.sandbox_auto_start is False
    assert config.resource_types == ["code"]
    assert config.resource_init_configs == {
        "code": {
            "content": {
                "source_dir": f"{REPO_ROOT}/seeds/code/seed/demo_repo"
            }
        }
    }
    assert config.available_tools == ["code-*"]
    assert config.seeds_file == "seeds/code/seeds.jsonl"
    assert raw["seed_description"] == "Coding demo repository prompts"
    assert len(config.qa_examples) >= 2
    assert config.sampling_tips.strip()
    assert config.synthesis_tips.strip()


def test_code_synthesis_config_preserves_placeholder_when_repo_root_unset(monkeypatch):
    config_path = REPO_ROOT / "configs" / "synthesis" / "code_config.json"
    monkeypatch.delenv("AGENTFLOW_REPO_ROOT", raising=False)

    config = SynthesisConfig.from_json(str(config_path))

    assert config.resource_init_configs == {
        "code": {
            "content": {
                "source_dir": "${AGENTFLOW_REPO_ROOT}/seeds/code/seed/demo_repo"
            }
        }
    }


def test_synthesis_config_from_dict_expands_nested_env_values(monkeypatch):
    monkeypatch.setenv("CODE_ROOT", "/tmp/demo")
    monkeypatch.delenv("UNSET_VALUE", raising=False)

    config = SynthesisConfig.from_dict(
        {
            "resource_init_configs": {
                "code": {
                    "content": {
                        "source_dir": "${CODE_ROOT}/repo",
                        "fallback_dir": "${UNSET_VALUE:-/tmp/fallback}",
                        "preserved_dir": "${UNSET_VALUE}/repo",
                        "artifacts": [
                            "${CODE_ROOT}/one",
                            "${UNSET_VALUE:-/tmp/two}",
                            "${UNSET_VALUE}/three",
                        ],
                    }
                }
            }
        }
    )

    content = config.resource_init_configs["code"]["content"]
    assert content["source_dir"] == "/tmp/demo/repo"
    assert content["fallback_dir"] == "/tmp/fallback"
    assert content["preserved_dir"] == "${UNSET_VALUE}/repo"
    assert content["artifacts"] == [
        "/tmp/demo/one",
        "/tmp/two",
        "${UNSET_VALUE}/three",
    ]
