"""
System Prompts for Different Environments and Action Spaces

This module contains all system prompts used by the AgentRunner.
Prompts are organized by environment type and action space mode.

=============================================================================
【开发指南 & 格式规范】(Development Guidelines)
=============================================================================

1. 核心必填项 (Mandatory Placeholders):
   - {tool_descriptions}: [必须] 框架会自动替换为当前环境注册的工具列表。
     位置建议放在 "## Available Tools" 标题下。

2. 推荐结构 (Recommended Structure):
   - [Role Definition]: 定义 Agent 的身份和目标。
   - [Available Tools]: 包含 {tool_descriptions}。
   - [Action Space/Strategy]: (可选) 定义动作格式或工具使用策略。
   - [Rules]: 定义执行规则和停止条件 (如 "Use DONE when complete")。

3. 自定义变量 (Custom Variables):
   - 支持自定义占位符，例如 {CLIENT_PASSWORD}, {CURRENT_DATE}。
   - 注意：使用自定义变量时，必须在对应的 Environment 子类中重写 
     `_replace_prompt_placeholders(self, prompt)` 方法来处理替换逻辑。

4. 动作空间描述 (Action Space):
   - 对于复杂环境 (如 OSWorld)，必须在 Prompt 中明确给出动作的 JSON Schema 
     或代码示例 (Few-Shot)，以确保 LLM 输出格式正确。

=============================================================================

Usage:
    from prompts.system_prompts import SYSTEM_PROMPTS

    # Get prompt for specific environment and action_space
    prompt = SYSTEM_PROMPTS.get("osworld_computer_13")
    prompt = SYSTEM_PROMPTS.get("math")
"""

# =============================================================================
# 1. Default / General
# =============================================================================

SYSTEM_PROMPT_DEFAULT = """... (Default system prompt content omitted) ..."""

# =============================================================================
# 2. OSWorld Environments
# =============================================================================

# OSWorld environment - computer_13 action space
SYSTEM_PROMPT_OSWORLD_COMPUTER13 = """... (OSWorld Computer13 prompt content with ACTION_SPACE definition omitted) ..."""

# OSWorld environment - pyautogui action space
SYSTEM_PROMPT_OSWORLD_PYAUTOGUI = """... (OSWorld PyAutoGUI prompt content with Python script examples omitted) ..."""

# =============================================================================
# 3. Specialized Environments (Math, Python, Web, RAG)
# =============================================================================

# Math Environment Prompt
SYSTEM_PROMPT_MATH = """... (Math environment prompt content omitted) ..."""

# Python Environment Prompt
SYSTEM_PROMPT_PYTHON = """... (Python environment prompt content omitted) ..."""

# Web Environment Prompt
SYSTEM_PROMPT_WEB = """... (Web environment prompt content omitted) ..."""

# RAG Environment Prompt
SYSTEM_PROMPT_RAG = """... (RAG environment prompt content omitted) ..."""

# =============================================================================
# 4. Mapping and Retrieval
# =============================================================================

# Mapping dictionary for easy lookup
# 核心逻辑：将环境模式 (mode) 映射到对应的 Prompt 变量
SYSTEM_PROMPTS = {
    "default": SYSTEM_PROMPT_DEFAULT,
    "osworld_computer_13": SYSTEM_PROMPT_OSWORLD_COMPUTER13,
    "osworld_pyautogui": SYSTEM_PROMPT_OSWORLD_PYAUTOGUI,
    # Registered new environments
    "math": SYSTEM_PROMPT_MATH,
    "python": SYSTEM_PROMPT_PYTHON,
    "web": SYSTEM_PROMPT_WEB,
    "rag": SYSTEM_PROMPT_RAG,
}


def get_system_prompt(environment_mode: str = "default", action_space: str = None) -> str:
    """
    Get system prompt based on environment mode and action space.

    Args:
        environment_mode: Environment mode (e.g., "osworld", "math", "web")
        action_space: Action space for the environment (e.g., "computer_13", "pyautogui")

    Returns:
        System prompt string template

    Examples:
        >>> get_system_prompt("osworld", "computer_13")
        SYSTEM_PROMPT_OSWORLD_COMPUTER13

        >>> get_system_prompt("math")
        SYSTEM_PROMPT_MATH
    """
    # Build prompt key
    if environment_mode == "osworld" and action_space:
        prompt_key = f"osworld_{action_space}"
    elif environment_mode and environment_mode != "default":
        # Direct mapping for simple modes: "math", "web", "rag", "python"
        prompt_key = environment_mode
    else:
        prompt_key = "default"

    # Fallback to default if key not found
    return SYSTEM_PROMPTS.get(prompt_key, SYSTEM_PROMPTS["default"])