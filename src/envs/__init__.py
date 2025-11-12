"""
Environment package for AgentFlow.
"""

# Import data models from data_models module (no dependencies)
from .data_models import (
    Observation,
    TrajectoryStep,
    TaskTrajectory
)

# Import base classes from enviroment module (no dependencies)
from .enviroment import (
    Environment,
    Tool
)

# Lazy imports for concrete environments to avoid tool dependency issues at import time
# These will only be imported when actually used
def __getattr__(name):
    """Lazy import for environment classes."""
    if name == "MathEnvironment":
        from .math_environment import MathEnvironment
        return MathEnvironment
    elif name == "create_math_environment":
        from .math_environment import create_math_environment
        return create_math_environment
    elif name == "PythonEnvironment":
        from .python_environment import PythonEnvironment
        return PythonEnvironment
    elif name == "create_python_environment":
        from .python_environment import create_python_environment
        return create_python_environment
    elif name == "RAGEnvironment":
        from .rag_environment import RAGEnvironment
        return RAGEnvironment
    elif name == "create_rag_environment":
        from .rag_environment import create_rag_environment
        return create_rag_environment
    elif name == "WebEnvironment":
        from .web_environment import WebEnvironment
        return WebEnvironment
    elif name == "create_web_environment":
        from .web_environment import create_web_environment
        return create_web_environment
    elif name == "TBenchEnvironment":
        from .tbench_environment import TBenchEnvironment
        return TBenchEnvironment
    elif name == "OSWorldEnvironment":
        from .osworld_environment import OSWorldEnvironment
        return OSWorldEnvironment
    elif name == "create_osworld_environment":
        from .osworld_environment import create_osworld_environment
        return create_osworld_environment
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Data models
    "Observation",
    "TrajectoryStep",
    "TaskTrajectory",
    # Base classes
    "Environment",
    "Tool",
    # Environments (lazy loaded)
    "MathEnvironment",
    "PythonEnvironment",
    "RAGEnvironment",
    "WebEnvironment",
    "TBenchEnvironment",
    "OSWorldEnvironment",
    # Factory functions (lazy loaded)
    "create_math_environment",
    "create_python_environment",
    "create_rag_environment",
    "create_web_environment",
    "create_osworld_environment"
]
