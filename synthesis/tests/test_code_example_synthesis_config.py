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
