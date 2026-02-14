"""
Lightweight public API for running synthesis with minimal code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, cast

from .core import SynthesisConfig
from .pipeline import SynthesisPipeline


def load_config(config_path: str) -> SynthesisConfig:
    """Load synthesis config from json/yaml."""
    if config_path.endswith(".json"):
        return SynthesisConfig.from_json(config_path)
    if config_path.endswith(".yaml") or config_path.endswith(".yml"):
        return SynthesisConfig.from_yaml(config_path)
    raise ValueError("config_path must end with .json/.yaml/.yml")


def load_seeds(seeds_or_path: Union[str, List[str], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Load seeds from a list or a jsonl file path.
    If a string is not a file path, treat it as a single seed.
    Returns a list of dicts with 'content' and 'kwargs' fields.
    """
    # If already a list of dicts, return as-is
    if isinstance(seeds_or_path, list):
        if seeds_or_path and isinstance(seeds_or_path[0], dict):
            return cast(List[Dict[str, Any]], seeds_or_path)
        # If list of strings, convert to dict format
        return [{"content": seed, "kwargs": {}} for seed in seeds_or_path]

    candidate = Path(seeds_or_path)
    if candidate.exists() and candidate.is_file():
        # Load JSONL format
        seeds = []
        with candidate.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    seed = json.loads(line)
                    # Ensure seed has required fields
                    if isinstance(seed, dict):
                        if "content" not in seed:
                            raise ValueError(f"Seed missing 'content' field: {seed}")
                        if "kwargs" not in seed:
                            seed["kwargs"] = {}
                        seeds.append(seed)
                    else:
                        raise ValueError(f"Each seed must be a dict with 'content' and 'kwargs' fields, got: {type(seed)}")
        return seeds
    else:
        # Single string seed
        return [{"content": seeds_or_path, "kwargs": {}}]


def synthesize(
    *,
    config_path: str,
    seeds: Optional[Union[str, List[str], List[Dict[str, Any]]]] = None,
) -> None:
    """
    One-call wrapper to run synthesis.
    """
    config = load_config(config_path)

    seeds_path = config.seeds_file or os.environ.get("SEEDS_FILE")
    if seeds is None and not seeds_path:
        raise ValueError("Missing seeds: provide seeds or set seeds_file in config")

    if seeds is None:
        seeds = seeds_path  # type: ignore[assignment]
    if seeds is None:
        raise ValueError("Missing seeds: provide seeds or set seeds_file in config")

    output_dir = config.output_dir or os.environ.get("OUTPUT_DIR") or "synthesis_results"

    pipeline = SynthesisPipeline(config=config, output_dir=output_dir)
    pipeline.run(load_seeds(seeds))
