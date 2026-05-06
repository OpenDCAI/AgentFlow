import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from synthesis.core.config import SynthesisConfig
from synthesis.pipeline import SynthesisPipeline


def test_synthesis_pipeline_respects_caller_output_dir(tmp_path):
    output_dir = tmp_path / "custom-output"
    config = SynthesisConfig(
        api_key="test-key",
        base_url="http://example.com",
    )

    pipeline = SynthesisPipeline(config=config, output_dir=str(output_dir))

    assert pipeline.output_dir == str(output_dir)
    assert output_dir.is_dir()
    assert pipeline.qa_file_path == str(output_dir / "synthesized_qa.jsonl")
    assert pipeline.traj_file_path == str(output_dir / "trajectories.jsonl")


def test_synthesis_config_from_dict_expands_env_vars(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    config = SynthesisConfig.from_dict(
        {
            "api_key": "${OPENROUTER_API_KEY}",
            "base_url": "${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}",
            "resource_init_configs": {
                "canvas": {
                    "token": "${OPENROUTER_API_KEY}",
                }
            },
        }
    )

    assert config.api_key == "test-key"
    assert config.base_url == "https://openrouter.ai/api/v1"
    assert config.resource_init_configs == {"canvas": {"token": "test-key"}}


def test_synthesis_config_from_json_expands_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    config_path = tmp_path / "synthesis-config.json"
    config_path.write_text(
        json.dumps(
            {
                "api_key": "${OPENROUTER_API_KEY}",
                "base_url": "https://openrouter.ai/api/v1",
            }
        ),
        encoding="utf-8",
    )

    config = SynthesisConfig.from_json(str(config_path))

    assert config.api_key == "test-key"


def test_synthesis_config_from_yaml_expands_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    config_path = tmp_path / "synthesis-config.yaml"
    config_path.write_text(
        """
api_key: ${OPENROUTER_API_KEY}
base_url: ${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}
""".strip(),
        encoding="utf-8",
    )

    config = SynthesisConfig.from_yaml(str(config_path))

    assert config.api_key == "test-key"
    assert config.base_url == "https://openrouter.ai/api/v1"
