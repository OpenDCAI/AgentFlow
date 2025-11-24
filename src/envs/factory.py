# -*- coding: utf-8 -*-
"""
Environment Factory - Centralized environment creation and registration.

This module provides a factory pattern for creating environments,
eliminating hard-coded if-elif chains in AgentRunner.
"""

from typing import Type, Dict, Optional
from .enviroment import Environment

# Environment registry - maps mode names to environment classes
_ENVIRONMENT_REGISTRY: Dict[str, Type[Environment]] = {}


def register_environment(mode: str, env_class: Type[Environment]) -> None:
    """
    Register an environment class for a given mode.
    
    Args:
        mode: Environment mode name (e.g., "math", "osworld")
        env_class: Environment class to register
    
    Example:
        >>> register_environment("custom", CustomEnvironment)
    """
    if not issubclass(env_class, Environment):
        raise TypeError(f"{env_class} must be a subclass of Environment")
    _ENVIRONMENT_REGISTRY[mode] = env_class


def unregister_environment(mode: str) -> None:
    """
    Unregister an environment class.
    
    Args:
        mode: Environment mode name to unregister
    """
    _ENVIRONMENT_REGISTRY.pop(mode, None)


def list_registered_environments() -> list:
    """
    List all registered environment modes.
    
    Returns:
        List of registered mode names
    """
    return list(_ENVIRONMENT_REGISTRY.keys())


def is_registered(mode: str) -> bool:
    """
    Check if an environment mode is registered.
    
    Args:
        mode: Environment mode name
    
    Returns:
        True if registered, False otherwise
    """
    return mode in _ENVIRONMENT_REGISTRY


def get_environment_class(mode: str) -> Type[Environment]:
    """
    Get the environment class for a given mode.
    
    Args:
        mode: Environment mode name
    
    Returns:
        Environment class (not an instance)
    
    Raises:
        ValueError: If mode is not registered
    
    Example:
        >>> EnvClass = get_environment_class("osworld")
        >>> resource_manager = EnvClass.setup_global_resources(config)
    """
    if mode not in _ENVIRONMENT_REGISTRY:
        available_modes = ", ".join(sorted(_ENVIRONMENT_REGISTRY.keys()))
        raise ValueError(
            f"Unknown environment mode: '{mode}'. "
            f"Available modes: {available_modes}. "
            f"Use register_environment() to add new modes."
        )
    
    return _ENVIRONMENT_REGISTRY[mode]


def create_environment(mode: str, **kwargs) -> Environment:
    """
    Create an environment instance using the factory pattern.
    
    Args:
        mode: Environment mode name
        **kwargs: Environment initialization parameters
    
    Returns:
        Environment instance
    
    Raises:
        ValueError: If mode is not registered
    
    Example:
        >>> env = create_environment("math", model_name="gpt-4")
        >>> env = create_environment("osworld", provider_name="aliyun", path_to_vm="...")
    """
    if mode not in _ENVIRONMENT_REGISTRY:
        available_modes = ", ".join(sorted(_ENVIRONMENT_REGISTRY.keys()))
        raise ValueError(
            f"Unknown environment mode: '{mode}'. "
            f"Available modes: {available_modes}. "
            f"Use register_environment() to add new modes."
        )
    
    env_class = _ENVIRONMENT_REGISTRY[mode]
    return env_class(**kwargs)


class EnvironmentFactory:
    """
    Environment factory class for centralized environment creation.
    
    This class provides a clean interface for creating environments
    and managing the environment registry.
    """
    
    def __init__(self):
        """Initialize the factory."""
        self._registry = _ENVIRONMENT_REGISTRY
    
    def register(self, mode: str, env_class: Type[Environment]) -> None:
        """Register an environment class."""
        register_environment(mode, env_class)
    
    def create(self, mode: str, **kwargs) -> Environment:
        """Create an environment instance."""
        return create_environment(mode, **kwargs)
    
    def list_modes(self) -> list:
        """List all registered modes."""
        return list_registered_environments()
    
    def is_available(self, mode: str) -> bool:
        """Check if a mode is available."""
        return is_registered(mode)


# Auto-register built-in environments on import
def _auto_register_builtin_environments():
    """Auto-register all built-in environment classes."""
    try:
        from .math_environment import MathEnvironment
        register_environment("math", MathEnvironment)
    except ImportError:
        pass
    
    try:
        from .python_environment import PythonEnvironment
        register_environment("py", PythonEnvironment)
    except ImportError:
        pass
    
    try:
        from .rag_environment import RAGEnvironment
        register_environment("rag", RAGEnvironment)
    except ImportError:
        pass
    
    try:
        from .web_environment import WebEnvironment
        register_environment("web", WebEnvironment)
    except ImportError:
        pass
    
    try:
        from .tbench_environment import TBenchEnvironment
        register_environment("tbench", TBenchEnvironment)
    except ImportError:
        pass
    # Register parallel rollout environment (for parallel execution)
    try:
        from .parallel_osworld_rollout_environment import ParallelOSWorldRolloutEnvironment
        # Use "osworld_parallel" mode for parallel rollout, but fallback to "osworld" if needed
        # In practice, parallel rollout should use the parallel environment class
        register_environment("osworld_parallel", ParallelOSWorldRolloutEnvironment)
    except ImportError:
        pass


# Auto-register on module import
_auto_register_builtin_environments()

