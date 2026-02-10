"""
Configuration management for RAG synthesis pipeline
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, fields


@dataclass
class SynthesisConfig:
    """RAG synthesis configuration"""

    # I/O paths
    seeds_file: Optional[str] = None
    output_dir: Optional[str] = None

    # Available tools
    available_tools: List[str] = field(default_factory=list)

    # QA examples for guidance
    qa_examples: List[Dict[str, str]] = field(default_factory=list)

    # Sampling tips (guidance for agent exploration)
    sampling_tips: str = ""

    # Synthesis tips (guidance for QA generation)
    synthesis_tips: str = ""

    # Seed description
    seed_description: str = ""

    # Model configuration
    model_name: str = "gpt-4.1-2025-04-14"

    # Trajectory sampling configuration
    max_depth: int = 5
    branching_factor: int = 2
    depth_threshold: int = 3

    # Trajectory selection configuration
    min_depth: int = 2
    max_selected_traj: int = 3
    path_similarity_threshold: float = 0.7

    # Seed processing limit
    number_of_seed: Optional[int] = None

    # Resource configuration (for sandbox)
    resource_types: List[str] = field(default_factory=list)
    resource_init_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Sandbox configuration
    sandbox_server_url: str = "http://127.0.0.1:18890"
    sandbox_auto_start: bool = True
    sandbox_config_path: Optional[str] = None
    sandbox_timeout: int = 120

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SynthesisConfig':
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

        if "sampling_tips" in filtered:
            filtered["sampling_tips"] = _normalize_text_field(filtered.get("sampling_tips"))
        if "synthesis_tips" in filtered:
            filtered["synthesis_tips"] = _normalize_text_field(filtered.get("synthesis_tips"))

        return cls(**filtered)

    @classmethod
    def from_json(cls, json_path: str) -> 'SynthesisConfig':
        """Load configuration from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'SynthesisConfig':
        """Load configuration from YAML file"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "available_tools": self.available_tools,
            "qa_examples": self.qa_examples,
            "sampling_tips": self.sampling_tips,
            "synthesis_tips": self.synthesis_tips,
            "seed_description": self.seed_description,
            "seeds_file": self.seeds_file,
            "output_dir": self.output_dir,
            "model_name": self.model_name,
            "max_depth": self.max_depth,
            "branching_factor": self.branching_factor,
            "depth_threshold": self.depth_threshold,
            "min_depth": self.min_depth,
            "max_selected_traj": self.max_selected_traj,
            "number_of_seed": self.number_of_seed,
            "path_similarity_threshold": self.path_similarity_threshold,
            "resource_types": self.resource_types,
            "resource_init_configs": self.resource_init_configs,
            "sandbox_server_url": self.sandbox_server_url,
            "sandbox_auto_start": self.sandbox_auto_start,
            "sandbox_config_path": self.sandbox_config_path,
            "sandbox_timeout": self.sandbox_timeout,
        }

    def to_json(self, json_path: str):
        """Save as JSON file"""
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def to_yaml(self, yaml_path: str):
        """Save as YAML file"""
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)

    def validate(self) -> List[str]:
        """Validate configuration, return list of errors"""
        errors = []

        if self.max_depth < 1:
            errors.append("max_depth must be greater than 0")

        if self.branching_factor < 1:
            errors.append("branching_factor must be greater than 0")

        if self.max_selected_traj < 1:
            errors.append("max_selected_traj must be greater than 0")

        if self.min_depth < 1:
            errors.append("min_depth must be greater than 0")

        if self.min_depth > self.max_depth:
            errors.append("min_depth cannot be greater than max_depth")

        return errors
