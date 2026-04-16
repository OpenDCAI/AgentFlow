"""
Configuration management for synthesis pipeline.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, fields


@dataclass
class SynthesisConfig:
    """Synthesis configuration"""

    # I/O paths
    seeds_file: Optional[str] = None
    output_dir: Optional[str] = None

    # Available tools
    available_tools: List[str] = field(default_factory=list)

    # QA examples for guidance
    qa_examples: List[Dict[str, str]] = field(default_factory=list)

    # Tips for each phase
    sampling_tips: str = ""
    selecting_tips: str = ""
    synthesis_tips: str = ""

    # Seed / task description
    seed_description: str = ""

    # Instruction markdown path (preferred: description_path; prompt_path kept for compatibility)
    prompt_path: Optional[str] = None
    description_path: Optional[str] = None

    # Skill integration settings
    # bool for quick on/off, or dict for advanced settings.
    skill: Union[bool, Dict[str, Any]] = False
    skills_root: Optional[str] = None
    skill_group: Optional[str] = None

    # Runtime-only information
    runtime: Dict[str, Any] = field(default_factory=dict)

    # Model configuration
    model_name: str = "gpt-4.1-2025-04-14"
    api_key: str = ""
    base_url: str = ""

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
        if "selecting_tips" in filtered:
            filtered["selecting_tips"] = _normalize_text_field(filtered.get("selecting_tips"))
        if "synthesis_tips" in filtered:
            filtered["synthesis_tips"] = _normalize_text_field(filtered.get("synthesis_tips"))

        cfg = cls(**filtered)
        return _apply_instruction_markdown(cfg)

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
            "selecting_tips": self.selecting_tips,
            "synthesis_tips": self.synthesis_tips,
            "seed_description": self.seed_description,
            "prompt_path": self.prompt_path,
            "description_path": self.description_path,
            "skill": self.skill,
            "skills_root": self.skills_root,
            "skill_group": self.skill_group,
            "seeds_file": self.seeds_file,
            "output_dir": self.output_dir,
            "model_name": self.model_name,
            "api_key": self.api_key,
            "base_url": self.base_url,
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

        if not self.model_name:
            errors.append("model_name must be provided in config")

        if not self.api_key:
            errors.append("api_key must be provided in config")

        if not self.base_url:
            errors.append("base_url must be provided in config")

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

    def skill_settings(self) -> Dict[str, Any]:
        """Normalize the skill field into a canonical settings dict."""
        if isinstance(self.skill, dict):
            out = dict(self.skill)
            out.setdefault("enabled", True)
        else:
            out = {"enabled": bool(self.skill)}

        out.setdefault("max_category_count", 2)
        out.setdefault("max_global_skills", 10)
        out.setdefault("min_global_skills", 5)
        out.setdefault("max_desc_chars", 800)
        out.setdefault("max_ref_chars", 3000)
        out.setdefault("max_skill_examples", 8)
        out.setdefault("max_total_qa_examples", 24)
        out.setdefault("temperature", 0.2)
        out.setdefault("include", [])
        out.setdefault("exclude", [])

        # Coerce numeric fields; None values in JSON config are handled by `or default`.
        out["max_category_count"] = max(1, int(out["max_category_count"] or 2))
        out["max_global_skills"] = max(1, int(out["max_global_skills"] or 10))
        out["min_global_skills"] = max(0, int(out["min_global_skills"] or 5))
        if out["min_global_skills"] > out["max_global_skills"]:
            out["min_global_skills"] = out["max_global_skills"]
        out["max_desc_chars"] = max(100, int(out["max_desc_chars"] or 800))
        out["max_ref_chars"] = max(200, int(out["max_ref_chars"] or 3000))
        out["max_skill_examples"] = max(0, int(out["max_skill_examples"] or 8))
        out["max_total_qa_examples"] = max(1, int(out["max_total_qa_examples"] or 24))
        out["temperature"] = float(out["temperature"] or 0.2)

        if not isinstance(out["include"], list):
            out["include"] = []
        if not isinstance(out["exclude"], list):
            out["exclude"] = []

        return out

    def skill_group_name(self) -> Optional[str]:
        """Resolve skill group by config or resource type."""
        if self.skill_group:
            return str(self.skill_group).strip() or None

        rts = [str(x).strip().lower() for x in (self.resource_types or []) if str(x).strip()]
        if not rts:
            return None

        primary = rts[0]
        mapping = {
            "rag": "rag",
            "web": "web",
            "doc": "doc",
            "sql": "sql",
            "vm": "gui",
            "gui": "gui",
            "ds": "data_analysis",
            "data": "data_analysis",
            "data_analysis": "data_analysis",
        }
        return mapping.get(primary, primary)


def _apply_instruction_markdown(cfg: SynthesisConfig) -> SynthesisConfig:
    """Apply instruction markdown from description_path/prompt_path."""
    md_path = str(cfg.description_path or cfg.prompt_path or "").strip()
    if not md_path:
        return cfg

    p = Path(md_path)
    if not p.is_absolute():
        project_root = Path(__file__).resolve().parents[2]
        p = project_root / p
    if not p.exists():
        raise FileNotFoundError(f"instruction markdown not found: {md_path}")

    text = p.read_text(encoding="utf-8")

    from .instruction import parse_qa_syn_instruction_md

    parsed = parse_qa_syn_instruction_md(text)
    required_keys = ("description", "sampling_tips", "selecting_tips", "synthesis_tips", "qa_examples")

    def _is_non_empty(k: str) -> bool:
        v = parsed.get(k)
        if k == "qa_examples":
            return isinstance(v, list) and len(v) > 0
        return bool(str(v).strip()) if v is not None else False

    missing_required = [k for k in required_keys if not _is_non_empty(k)]
    extracted_complete = len(missing_required) == 0

    cfg.runtime["instruction"] = {
        "path": str(p),
        "text": text,
        "parsed": parsed,
        "required_keys": list(required_keys),
        "missing_required": missing_required,
        "extracted_complete": extracted_complete,
    }

    # Share generic task description when available.
    if parsed.get("seed_description"):
        cfg.seed_description = str(parsed.get("seed_description")).strip()
    elif parsed.get("description"):
        cfg.seed_description = str(parsed.get("description")).strip()

    if parsed.get("qa_examples") and isinstance(parsed.get("qa_examples"), list):
        cfg.qa_examples = parsed.get("qa_examples")  # type: ignore[assignment]

    skill_enabled = bool(cfg.skill_settings().get("enabled", False))

    # Keep extracted stage tips if present. When skill is enabled, pipeline will
    # merge these with selected-skill injections per phase.
    if parsed.get("sampling_tips"):
        cfg.sampling_tips = str(parsed.get("sampling_tips")).strip()
    if parsed.get("selecting_tips"):
        cfg.selecting_tips = str(parsed.get("selecting_tips")).strip()
    if parsed.get("synthesis_tips"):
        cfg.synthesis_tips = str(parsed.get("synthesis_tips")).strip()

    # Skill disabled: extraction is required; fail fast if key blocks are missing.
    if not skill_enabled:
        if not extracted_complete:
            print(
                "⚠️ Instruction markdown parsing incomplete with skill disabled. "
                f"Missing required blocks: {', '.join(missing_required)}"
            )
            raise ValueError(
                "Skill disabled requires instruction markdown blocks: "
                "description, sampling_tips, selecting_tips, synthesis_tips, qa_examples. "
                f"Missing: {', '.join(missing_required)}"
            )
        return cfg

    # Skill enabled: extraction blocks are optional.
    if not extracted_complete:
        print(
            "⚠️ Instruction markdown parsing incomplete with skill enabled. "
            "Will fallback to raw markdown for global skill selection and continue."
        )

    return cfg
