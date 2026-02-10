"""
Rollout Core Module

Core components for running agents on benchmarks.
"""

from .config import RolloutConfig
from .models import (
    BenchmarkItem,
    ToolCall,
    Message,
    Trajectory,
    TaskResult,
    EvaluationResult,
    RolloutSummary
)
from .evaluator import Evaluator, evaluate_results
from .utils import (
    create_openai_client,
    chat_completion,
    async_chat_completion,
    load_benchmark_data,
    extract_final_answer,
    normalize_answer,
    get_timestamp
)

# Lazy import for runner (requires sandbox which has heavy dependencies)
def __getattr__(name):
    if name in ("AgentRunner", "SyncAgentRunner"):
        from .runner import AgentRunner, SyncAgentRunner
        return AgentRunner if name == "AgentRunner" else SyncAgentRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Config
    "RolloutConfig",
    
    # Models
    "BenchmarkItem",
    "ToolCall",
    "Message",
    "Trajectory",
    "TaskResult",
    "EvaluationResult",
    "RolloutSummary",
    
    # Runner (lazy loaded)
    "AgentRunner",
    "SyncAgentRunner",
    
    # Evaluator
    "Evaluator",
    "evaluate_results",
    
    # Utils
    "create_openai_client",
    "chat_completion",
    "async_chat_completion",
    "load_benchmark_data",
    "extract_final_answer",
    "normalize_answer",
    "get_timestamp",
]
