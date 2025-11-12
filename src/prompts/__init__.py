"""
Prompts package for AgentFlow.

This package contains all system prompts used across different environments.
"""

from .system_prompts import (
    SYSTEM_PROMPTS,
    SYSTEM_PROMPT_DEFAULT,
    SYSTEM_PROMPT_OSWORLD_COMPUTER13,
    SYSTEM_PROMPT_OSWORLD_PYAUTOGUI,
    get_system_prompt
)

__all__ = [
    "SYSTEM_PROMPTS",
    "SYSTEM_PROMPT_DEFAULT",
    "SYSTEM_PROMPT_OSWORLD_COMPUTER13",
    "SYSTEM_PROMPT_OSWORLD_PYAUTOGUI",
    "get_system_prompt"
]
