"""
Configuration management for Rollout pipeline

Supports loading from JSON/YAML files with comprehensive validation.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, fields

# Optional yaml support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class RolloutConfig:
    """Rollout configuration for agent execution on benchmarks"""

    # I/O paths
    data_path: Optional[str] = None  # Benchmark data file path (jsonl)
    output_dir: Optional[str] = None  # Output directory for results

    # Model configuration
    model_name: str = "gpt-4.1-2025-04-14"
    
    # Agent execution configuration
    max_turns: int = 100  # Maximum conversation turns per task
    max_retries: int = 3  # Maximum retries per LLM call
    max_workers: int = 1  # Maximum parallel workers

    # Available tools (list of tool names or prefixed tools like "vm:screenshot")
    available_tools: List[str] = field(default_factory=list)

    # System prompt customization
    system_prompt: str = ""
    system_prompt_file: Optional[str] = None  # Load from file if provided

    # Evaluation configuration
    evaluate_results: bool = True
    evaluation_metric: str = "exact_match"  # exact_match, f1_score, contains_answer, numeric_match, llm_judgement

    # Resource configuration (for sandbox)
    resource_types: List[str] = field(default_factory=list)
    resource_init_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Sandbox configuration
    sandbox_server_url: str = "http://127.0.0.1:18890"
    sandbox_auto_start: bool = True
    sandbox_config_path: Optional[str] = None
    sandbox_timeout: int = 120

    # Benchmark configuration
    benchmark_name: Optional[str] = None
    number_of_tasks: Optional[int] = None  # Limit number of tasks (for testing)
    task_ids: Optional[List[str]] = None  # Specific task IDs to run
    
    # Parallel execution
    parallel: bool = False

    # Result saving
    save_results: bool = True
    save_trajectories: bool = True  # Save full conversation trajectories

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RolloutConfig':
        """Create configuration from dictionary"""
        if not isinstance(config_dict, dict):
            raise TypeError(f"config_dict must be dict, got: {type(config_dict).__name__}")

        valid_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in config_dict.items() if k in valid_fields}

        # Normalize text fields (allow list[str] for easier editing)
        def _normalize_text_field(v: Any) -> str:
            if v is None:
                return ""
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                return "\n".join("" if x is None else str(x) for x in v)
            return str(v)

        if "system_prompt" in filtered:
            filtered["system_prompt"] = _normalize_text_field(filtered.get("system_prompt"))

        return cls(**filtered)

    @classmethod
    def from_json(cls, json_path: str) -> 'RolloutConfig':
        """Load configuration from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'RolloutConfig':
        """Load configuration from YAML file"""
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "data_path": self.data_path,
            "output_dir": self.output_dir,
            "model_name": self.model_name,
            "max_turns": self.max_turns,
            "max_retries": self.max_retries,
            "max_workers": self.max_workers,
            "available_tools": self.available_tools,
            "system_prompt": self.system_prompt,
            "system_prompt_file": self.system_prompt_file,
            "evaluate_results": self.evaluate_results,
            "evaluation_metric": self.evaluation_metric,
            "resource_types": self.resource_types,
            "resource_init_configs": self.resource_init_configs,
            "sandbox_server_url": self.sandbox_server_url,
            "sandbox_auto_start": self.sandbox_auto_start,
            "sandbox_config_path": self.sandbox_config_path,
            "sandbox_timeout": self.sandbox_timeout,
            "benchmark_name": self.benchmark_name,
            "number_of_tasks": self.number_of_tasks,
            "task_ids": self.task_ids,
            "parallel": self.parallel,
            "save_results": self.save_results,
            "save_trajectories": self.save_trajectories,
        }

    def to_json(self, json_path: str):
        """Save as JSON file"""
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def to_yaml(self, yaml_path: str):
        """Save as YAML file"""
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)

    def get_system_prompt(self) -> str:
        """Get system prompt, loading from file if specified"""
        if self.system_prompt_file:
            try:
                with open(self.system_prompt_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                print(f"Warning: system_prompt_file not found: {self.system_prompt_file}")
        return self.system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        """Default system prompt for agent"""
        return """You are a helpful assistant. You need to use tools to solve the problem.

## Tool Usage Strategy

**For Multi-Step Analysis:**
1. Break complex problems into logical steps
2. Use ONE tool at a time to gather information
3. Verify findings through different approaches when possible
4. When you have enough information, provide the final answer

**Important:**
- Always explain your reasoning before using a tool
- If a tool call fails, try an alternative approach
- Provide clear, concise answers based on the gathered information
"""

    def validate(self) -> List[str]:
        """Validate configuration, return list of errors"""
        errors = []

        if self.max_turns < 1:
            errors.append("max_turns must be greater than 0")

        if self.max_retries < 0:
            errors.append("max_retries cannot be negative")

        if self.max_workers < 1:
            errors.append("max_workers must be greater than 0")

        valid_metrics = ["exact_match", "f1_score", "similarity", "contains_answer", "numeric_match", "llm_judgement"]
        if self.evaluation_metric not in valid_metrics:
            errors.append(f"evaluation_metric must be one of {valid_metrics}")

        return errors
