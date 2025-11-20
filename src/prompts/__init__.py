"""
Prompts package for AgentFlow.

This package contains all system prompts used across different environments.
"""

from .system_prompts import (
    SYSTEM_PROMPTS,
    SYSTEM_PROMPT_DEFAULT,
    SYSTEM_PROMPT_OSWORLD_COMPUTER13,
    SYSTEM_PROMPT_OSWORLD_PYAUTOGUI,
    # New environment prompts
    SYSTEM_PROMPT_MATH,
    SYSTEM_PROMPT_PYTHON,
    SYSTEM_PROMPT_WEB,
    SYSTEM_PROMPT_RAG,
    get_system_prompt
)

__all__ = [
    "SYSTEM_PROMPTS",
    "SYSTEM_PROMPT_DEFAULT",
    "SYSTEM_PROMPT_OSWORLD_COMPUTER13",
    "SYSTEM_PROMPT_OSWORLD_PYAUTOGUI",
    "SYSTEM_PROMPT_MATH",
    "SYSTEM_PROMPT_PYTHON",
    "SYSTEM_PROMPT_WEB",
    "SYSTEM_PROMPT_RAG",
    "get_system_prompt"
]