"""
Rollout - Agent execution pipeline for benchmarks

A clean implementation for running agents on benchmark tasks using sandbox tools.
Supports JSON configuration, multiple evaluation metrics, and parallel execution.

Usage:
    # Simple API
    from rollout import rollout
    
    summary = rollout(
        config_path="configs/rollout/rag_benchmark.json",
        data_path="benchmark/benchmark.jsonl"
    )
    
    # Quick single question
    from rollout import quick_rollout
    
    result = quick_rollout(
        "What is the capital of France?",
        tools=["web:search", "web:visit"]
    )
    
    # Full control with Pipeline
    from rollout import RolloutPipeline, RolloutConfig
    
    config = RolloutConfig.from_json("config.json")
    pipeline = RolloutPipeline(config)
    summary = pipeline.run()
"""

__version__ = "1.0.0"
__author__ = "Rollout Team"

from .core import (
    # Config
    RolloutConfig,
    
    # Models
    BenchmarkItem,
    ToolCall,
    Message,
    Trajectory,
    TaskResult,
    EvaluationResult,
    RolloutSummary,
    
    # Evaluator
    Evaluator,
    evaluate_results,
    
    # Utils
    load_benchmark_data,
    get_timestamp,
)

from .api import load_config, load_tasks

# Lazy imports for heavy dependencies
def __getattr__(name):
    if name in ("AgentRunner", "SyncAgentRunner"):
        from .core.runner import AgentRunner, SyncAgentRunner
        return AgentRunner if name == "AgentRunner" else SyncAgentRunner
    if name == "RolloutPipeline":
        from .pipeline import RolloutPipeline
        return RolloutPipeline
    if name == "rollout":
        from .api import rollout
        return rollout
    if name == "quick_rollout":
        from .api import quick_rollout
        return quick_rollout
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Version
    "__version__",
    
    # Config
    "RolloutConfig",
    "load_config",
    
    # Models
    "BenchmarkItem",
    "ToolCall",
    "Message",
    "Trajectory",
    "TaskResult",
    "EvaluationResult",
    "RolloutSummary",
    
    # Core (lazy loaded)
    "AgentRunner",
    "SyncAgentRunner",
    "Evaluator",
    "evaluate_results",
    "RolloutPipeline",
    
    # API (lazy loaded)
    "rollout",
    "quick_rollout",
    "load_tasks",
    "load_benchmark_data",
    "get_timestamp",
]
