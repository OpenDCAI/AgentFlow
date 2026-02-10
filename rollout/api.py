"""
Lightweight public API for running rollout with minimal code.

Usage:
    from rollout import rollout
    
    rollout(
        config_path="configs/rollout/rag_benchmark.json",
        data_path="benchmark/benchmark.jsonl"
    )
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, TYPE_CHECKING

from .core.config import RolloutConfig
from .core.models import BenchmarkItem
from .core.utils import load_benchmark_data

if TYPE_CHECKING:
    from .pipeline import RolloutPipeline


def load_config(config_path: str) -> RolloutConfig:
    """Load rollout config from json/yaml."""
    if config_path.endswith(".json"):
        return RolloutConfig.from_json(config_path)
    if config_path.endswith(".yaml") or config_path.endswith(".yml"):
        return RolloutConfig.from_yaml(config_path)
    raise ValueError("config_path must end with .json/.yaml/.yml")


def load_tasks(tasks_or_path: Union[str, List[Dict[str, Any]]]) -> List[BenchmarkItem]:
    """
    Load benchmark tasks from a list or file path.
    
    Args:
        tasks_or_path: Either a file path (jsonl/json) or a list of task dicts
        
    Returns:
        List of BenchmarkItem objects
    """
    if isinstance(tasks_or_path, list):
        return [BenchmarkItem.from_dict(task) for task in tasks_or_path]
    
    # Load from file
    raw_data = load_benchmark_data(tasks_or_path)
    return [BenchmarkItem.from_dict(item) for item in raw_data]


def rollout(
    *,
    config_path: str,
    data_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    model_name: Optional[str] = None,
    use_env_model: bool = True,
    max_tasks: Optional[int] = None,
    task_ids: Optional[List[str]] = None,
    evaluate: bool = True,
    metric: Optional[str] = None,
) -> Dict[str, Any]:
    """
    One-call wrapper to run rollout.
    
    Args:
        config_path: Path to configuration file
        data_path: Override benchmark data path
        output_dir: Override output directory
        model_name: Override model name
        use_env_model: Use LLM_MODEL_NAME from environment if set
        max_tasks: Limit number of tasks
        task_ids: Specific task IDs to run
        evaluate: Whether to evaluate results
        metric: Evaluation metric override
        
    Returns:
        Summary dictionary with run results
    """
    # Load config
    config = load_config(config_path)
    
    # Apply overrides
    if data_path:
        config.data_path = data_path
    
    if model_name:
        config.model_name = model_name
    elif use_env_model:
        env_model = os.environ.get("LLM_MODEL_NAME")
        if env_model:
            config.model_name = env_model
    
    if max_tasks is not None:
        config.number_of_tasks = max_tasks
    
    if task_ids:
        config.task_ids = task_ids
    
    config.evaluate_results = evaluate
    
    if metric:
        config.evaluation_metric = metric
    
    # Determine output directory
    final_output_dir = output_dir or config.output_dir or os.environ.get("OUTPUT_DIR") or "rollout_results"
    
    # Run pipeline (lazy import to avoid heavy dependencies)
    from .pipeline import RolloutPipeline
    pipeline = RolloutPipeline(config=config, output_dir=final_output_dir)
    summary = pipeline.run()
    
    return summary.to_dict()


def quick_rollout(
    question: str,
    *,
    tools: Optional[List[str]] = None,
    model_name: str = "gpt-4.1-2025-04-14",
    max_turns: int = 10,
    sandbox_url: str = "http://127.0.0.1:18890",
) -> Dict[str, Any]:
    """
    Quick rollout for a single question.
    
    Args:
        question: The question to answer
        tools: List of tools to use
        model_name: Model name
        max_turns: Maximum conversation turns
        sandbox_url: Sandbox server URL
        
    Returns:
        Result dictionary with answer and trajectory
    """
    import asyncio
    from .core.runner import AgentRunner
    from .core.models import BenchmarkItem
    
    # Create minimal config
    config = RolloutConfig(
        model_name=model_name,
        max_turns=max_turns,
        available_tools=tools or [],
        sandbox_server_url=sandbox_url,
        sandbox_auto_start=True,
        save_trajectories=True
    )
    
    # Determine resource types from tools
    if tools:
        resource_types = set()
        for tool in tools:
            if ":" in tool:
                resource_types.add(tool.split(":")[0])
        config.resource_types = list(resource_types)
    
    async def _run():
        runner = AgentRunner(config, worker_id="quick_runner")
        
        try:
            await runner.start()
            
            task = BenchmarkItem(
                id="quick_task",
                question=question
            )
            
            result = await runner.run_task(task)
            
            return {
                "question": question,
                "answer": result.predicted_answer,
                "success": result.success,
                "error": result.error,
                "trajectory": result.trajectory.to_dict() if result.trajectory else None
            }
            
        finally:
            await runner.stop()
    
    return asyncio.run(_run())


# Convenience aliases
run = rollout
quick = quick_rollout
