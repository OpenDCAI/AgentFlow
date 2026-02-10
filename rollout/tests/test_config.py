"""
Tests for RolloutConfig
"""

import os
import json
import tempfile
import pytest
from pathlib import Path

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rollout.core import RolloutConfig


class TestRolloutConfig:
    """Test RolloutConfig class"""

    def test_default_config(self):
        """Test creating config with defaults"""
        config = RolloutConfig()
        
        assert config.model_name == "gpt-4.1-2025-04-14"
        assert config.max_turns == 100
        assert config.max_retries == 3
        assert config.evaluate_results == True
        assert config.evaluation_metric == "exact_match"

    def test_from_dict(self):
        """Test creating config from dictionary"""
        config_dict = {
            "model_name": "gpt-3.5-turbo",
            "max_turns": 50,
            "available_tools": ["web_search", "rag_search"],
            "evaluation_metric": "f1_score"
        }
        
        config = RolloutConfig.from_dict(config_dict)
        
        assert config.model_name == "gpt-3.5-turbo"
        assert config.max_turns == 50
        assert config.available_tools == ["web_search", "rag_search"]
        assert config.evaluation_metric == "f1_score"

    def test_from_json(self):
        """Test loading config from JSON file"""
        config_dict = {
            "model_name": "test-model",
            "max_turns": 30,
            "data_path": "test/data.jsonl"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            temp_path = f.name
        
        try:
            config = RolloutConfig.from_json(temp_path)
            assert config.model_name == "test-model"
            assert config.max_turns == 30
            assert config.data_path == "test/data.jsonl"
        finally:
            os.unlink(temp_path)

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = RolloutConfig(
            model_name="test-model",
            max_turns=25,
            available_tools=["web_search"]
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["model_name"] == "test-model"
        assert config_dict["max_turns"] == 25
        assert config_dict["available_tools"] == ["web_search"]

    def test_validate_valid_config(self):
        """Test validation of valid config"""
        config = RolloutConfig(
            max_turns=10,
            max_retries=3,
            max_workers=2,
            evaluation_metric="exact_match"
        )
        
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_config(self):
        """Test validation of invalid config"""
        config = RolloutConfig(
            max_turns=0,  # Invalid
            max_retries=-1,  # Invalid
            max_workers=0,  # Invalid
            evaluation_metric="invalid_metric"  # Invalid
        )
        
        errors = config.validate()
        assert len(errors) == 4

    def test_get_system_prompt_default(self):
        """Test getting default system prompt"""
        config = RolloutConfig()
        prompt = config.get_system_prompt()
        
        assert "helpful assistant" in prompt.lower()
        assert len(prompt) > 50

    def test_get_system_prompt_custom(self):
        """Test getting custom system prompt"""
        custom_prompt = "You are a custom assistant."
        config = RolloutConfig(system_prompt=custom_prompt)
        prompt = config.get_system_prompt()
        
        assert prompt == custom_prompt

    def test_system_prompt_from_list(self):
        """Test system prompt as list of strings"""
        config_dict = {
            "system_prompt": [
                "Line 1",
                "Line 2",
                "Line 3"
            ]
        }
        
        config = RolloutConfig.from_dict(config_dict)
        
        assert "Line 1\nLine 2\nLine 3" == config.system_prompt


class TestRolloutConfigIntegration:
    """Integration tests for config loading"""

    def test_load_existing_config(self):
        """Test loading an existing config file"""
        config_path = Path(__file__).parent.parent.parent.parent / "configs" / "rollout" / "simple_config.json"
        
        if config_path.exists():
            config = RolloutConfig.from_json(str(config_path))
            assert config.benchmark_name == "simple_test"
            assert "web_search" in config.available_tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
