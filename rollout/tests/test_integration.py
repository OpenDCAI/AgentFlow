"""
Integration tests for Rollout pipeline

These tests verify the entire pipeline works correctly.
Note: Some tests require a running sandbox server.
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rollout import (
    RolloutConfig,
    RolloutPipeline,
    BenchmarkItem,
    load_config,
    load_tasks,
)
from rollout.core import load_benchmark_data


class TestDataLoading:
    """Test data loading functions"""

    def test_load_jsonl_data(self):
        """Test loading JSONL benchmark data"""
        data_path = Path(__file__).parent.parent.parent / "data" / "example_benchmark.jsonl"
        
        if data_path.exists():
            items = load_benchmark_data(str(data_path))
            
            assert len(items) > 0
            assert "id" in items[0] or "task_id" in items[0]
            assert "question" in items[0] or "query" in items[0]

    def test_load_tasks_from_file(self):
        """Test load_tasks function with file path"""
        data_path = Path(__file__).parent.parent.parent / "data" / "example_benchmark.jsonl"
        
        if data_path.exists():
            tasks = load_tasks(str(data_path))
            
            assert len(tasks) > 0
            assert isinstance(tasks[0], BenchmarkItem)
            assert tasks[0].id is not None

    def test_load_tasks_from_list(self):
        """Test load_tasks function with list"""
        task_list = [
            {"id": "1", "question": "Q1", "answer": "A1"},
            {"id": "2", "question": "Q2", "answer": "A2"},
        ]
        
        tasks = load_tasks(task_list)
        
        assert len(tasks) == 2
        assert tasks[0].id == "1"
        assert tasks[1].question == "Q2"


class TestConfigLoading:
    """Test configuration loading"""

    def test_load_json_config(self):
        """Test loading JSON config file"""
        config_path = Path(__file__).parent.parent.parent.parent / "configs" / "rollout" / "simple_config.json"
        
        if config_path.exists():
            config = load_config(str(config_path))
            
            assert isinstance(config, RolloutConfig)
            assert config.benchmark_name == "simple_test"

    def test_config_with_tools(self):
        """Test config with tool specifications"""
        config_dict = {
            "available_tools": ["web_search", "rag_search", "vm_*"],
            "resource_types": ["rag", "vm"],
        }
        
        config = RolloutConfig.from_dict(config_dict)
        
        assert "web_search" in config.available_tools
        assert "vm_*" in config.available_tools
        assert "rag" in config.resource_types


class TestPipelineSetup:
    """Test pipeline setup (no execution)"""

    def test_pipeline_creation(self):
        """Test creating pipeline"""
        config = RolloutConfig(
            benchmark_name="test",
            model_name="test-model",
            available_tools=["web_search"],
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RolloutPipeline(config, output_dir=tmpdir)
            
            assert pipeline.config == config
            assert pipeline.output_dir == tmpdir
            assert Path(tmpdir).exists()

    def test_pipeline_with_invalid_config(self):
        """Test pipeline rejects invalid config"""
        config = RolloutConfig(
            max_turns=0,  # Invalid
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                RolloutPipeline(config, output_dir=tmpdir)

    def test_pipeline_load_benchmark(self):
        """Test pipeline benchmark loading"""
        data_path = Path(__file__).parent.parent.parent / "data" / "example_benchmark.jsonl"
        
        if not data_path.exists():
            pytest.skip("Test data not found")
        
        config = RolloutConfig(
            benchmark_name="test",
            data_path=str(data_path),
            number_of_tasks=3,  # Limit to 3 tasks
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RolloutPipeline(config, output_dir=tmpdir)
            items = pipeline.load_benchmark()
            
            assert len(items) == 3


class TestUtilityFunctions:
    """Test utility functions"""

    def test_extract_final_answer(self):
        """Test answer extraction"""
        from rollout.core.utils import extract_final_answer
        
        # Test with "The answer is" pattern
        text1 = "After analyzing the data, the answer is 42."
        assert "42" in extract_final_answer(text1)
        
        # Test with explicit pattern
        text2 = "**Answer**: Paris"
        assert "Paris" in extract_final_answer(text2)

    def test_normalize_answer(self):
        """Test answer normalization"""
        from rollout.core.utils import normalize_answer
        
        assert normalize_answer("  Paris  ") == "paris"
        assert normalize_answer("The answer is Paris.") == "paris"
        assert normalize_answer("TOKYO") == "tokyo"

    def test_convert_tool_schema(self):
        """Test tool schema conversion"""
        from rollout.core.utils import convert_tool_schema_to_openai
        
        schema = {
            "name": "test:tool",
            "description": "A test tool",
            "parameters": [
                {"name": "query", "type": "string", "description": "Query string", "required": True},
                {"name": "limit", "type": "integer", "description": "Limit", "required": False}
            ]
        }
        
        openai_schema = convert_tool_schema_to_openai(schema)
        
        assert openai_schema["type"] == "function"
        assert openai_schema["function"]["name"] == "test:tool"
        assert "query" in openai_schema["function"]["parameters"]["properties"]
        assert "query" in openai_schema["function"]["parameters"]["required"]


class TestEndToEnd:
    """End-to-end tests (require mock or actual sandbox)"""

    @pytest.mark.skip(reason="Requires running sandbox server")
    def test_full_pipeline_run(self):
        """Test full pipeline execution"""
        config = RolloutConfig(
            benchmark_name="e2e_test",
            model_name="gpt-4.1-2025-04-14",
            available_tools=["web_search"],
            max_turns=5,
            number_of_tasks=1,
            evaluate_results=True,
            evaluation_metric="exact_match",
        )
        
        # Create test data
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test_data.jsonl"
            with open(data_file, 'w') as f:
                f.write('{"id": "1", "question": "What is 2+2?", "answer": "4"}\n')
            
            config.data_path = str(data_file)
            
            pipeline = RolloutPipeline(config, output_dir=tmpdir)
            summary = pipeline.run()
            
            assert summary.total_tasks == 1
            assert Path(pipeline.results_file).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
