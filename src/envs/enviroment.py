# -*- coding: utf-8 -*-
"""
Environment Base Class & Development Guide

=============================================================================
【开发指南 (Development Guide)】
=============================================================================

1. 核心概念 (Core Concept):
   Environment 是 Agent 与外部世界交互的容器。它负责：
   - 注册和管理工具 (Tools)
   - 生成标准化的系统提示词 (System Prompts)
   - 定义 Agent 执行任务的具体逻辑 (run_task)
   - 管理环境资源 (如虚拟机、浏览器、API连接)

2. 继承规范 (Inheritance):
   新建环境必须继承自 `Environment` 类，并实现以下抽象接口：
   
   (1) @property mode(self) -> str:
       定义环境的唯一标识符 (如 'math', 'osworld', 'rag')。
       该标识符用于查找 System Prompt 和配置文件。

   (2) _initialize_tools(self):
       在此方法中实例化并注册所需工具。
       必须使用 `self.register_tool(tool_instance)`，以便框架自动生成 Schema。

   (3) run_task(self, task, agent_config, logger) -> Dict:
       定义 Agent 的核心执行循环 (Prompt -> LLM -> Tool -> Observation)。
       * 必须返回包含 'answer' 字段的字典，以便 Benchmark 进行自动评测。
       * 必须使用 `self.execute_tool()` 来调用工具，严禁直接调用 tool.call()。

3. 资源管理 (Resource Management) [可选]:
   对于需要重型资源 (如虚拟机、Docker) 的环境：
   - 重写 `@classmethod setup_global_resources(config)`: 在主进程初始化资源池。
   - 重写 `env_start()`: 在 Worker 进程开始时申请具体资源。
   - 重写 `env_close()`: 在任务结束或进程退出时释放资源。

4. 提示词定制 (Prompt Customization) [可选]:
   如果 System Prompt 中包含自定义占位符 (如 {CLIENT_PASSWORD}):
   - 重写 `_replace_prompt_placeholders(self, prompt)` 方法来注入动态信息。

=============================================================================
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

from prompts.system_prompts import get_system_prompt as load_system_prompt
from tools.tool import Tool
from utils.resource_manager import ResourceManager


class Environment(ABC):
    """
    Agent 环境基类 (精简版)
    
    职责：
    1. 定义环境接口规范 (Mode, Run Task)
    2. 提供基础工具管理 (Register, Execute, Schema)
    3. 提供资源管理接口 (Setup Global Resources)
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4.1-2025-04-14",
                 resource_manager: Optional['ResourceManager'] = None,
                 **kwargs):
        """
        基础初始化。
        
        Args:
            model_name: 默认模型名称
            resource_manager: 资源管理器实例 (由 setup_global_resources 创建)
            **kwargs: 其他配置参数 (保存至 self.config)
        """
        self.model_name = model_name
        self.config = kwargs
        
        # 工具管理
        self.tools: Dict[str, Tool] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        self.tool_descriptions: str = ""
        
        # 资源管理
        if resource_manager is None:
            from utils.resource_manager import NoResourceManager
            self._resource_manager: ResourceManager = NoResourceManager()
        else:
            self._resource_manager = resource_manager
            
        # 自动调用子类工具初始化
        self._initialize_tools()

    # =========================================================================
    # 1. 核心抽象接口 (开发者必须实现)
    # =========================================================================
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """返回环境模式名称 (如 'math', 'osworld')"""
        pass

    @abstractmethod
    def _initialize_tools(self):
        """在此方法中注册环境所需的工具"""
        pass

    @abstractmethod
    def run_task(self, task: Dict[str, Any], agent_config: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        """
        核心任务执行入口。
        必须封装完整的 Agent 闭环：Prompt -> LLM -> Tool Execution -> Result
        """
        raise NotImplementedError("Subclasses must implement run_task")

    # =========================================================================
    # 2. 资源管理接口 (主进程调用)
    # =========================================================================

    @classmethod
    def setup_global_resources(cls, config: Any) -> Optional['ResourceManager']:
        """
        类方法：初始化全局资源 (如 VM 池)。
        默认返回空管理器，需要重资产的环境(如 OSWorld)需重写此方法。
        """
        from utils.resource_manager import NoResourceManager, ResourceManager as BaseResourceManager

        manager: BaseResourceManager = NoResourceManager()
        return manager

    @property
    def resource_manager(self) -> 'ResourceManager':
        return self._resource_manager

    # =========================================================================
    # 3. 工具管理设施 (已实现，通常无需修改)
    # =========================================================================

    def register_tool(self, tool: Tool):
        """注册工具并自动更新 Schema"""
        self.tools[tool.name] = tool
        self._update_tool_metadata()

    def list_tools(self) -> List[str]:
        """列出当前环境可用工具名称"""
        return sorted(self.tools.keys())

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def execute_tool(self, tool_name: str, params: Union[str, dict], **kwargs) -> Union[str, Dict[str, Any]]:
        """执行工具的安全包装器"""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        try:
            return tool.call(params, **kwargs)
        except Exception as e:
            return f"Error executing '{tool_name}': {str(e)}"

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """获取用于 LLM API 的工具定义"""
        return self.tool_schemas

    def get_tool_descriptions(self) -> str:
        """获取用于 Prompt 的工具描述文本"""
        if not self.tool_descriptions:
            return "- No tools registered. 请先通过 register_tool() 注册工具。"
        return self.tool_descriptions

    def _update_tool_metadata(self):
        """(内部) 生成工具 Schema 和描述"""
        self.tool_schemas = [self._tool_to_schema(t) for t in self.tools.values()]
        self.tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])

    def _tool_to_schema(self, tool: Tool) -> Dict[str, Any]:
        """(内部) 将 Tool 转换为 OpenAI Schema 格式"""
        properties = {
            p['name']: {"type": p['type'], "description": p['description']}
            for p in tool.parameters
        }
        required = [p['name'] for p in tool.parameters if p.get('required', False)]
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    # =========================================================================
    # 4. 生命周期钩子 (可选覆盖)
    # =========================================================================

    def get_action_space(self) -> Optional[str]:
        """
        获取当前环境的动作空间描述（默认从配置中推断，可由子类覆盖）
        """
        mode_config = self.config.get(self.mode)
        if isinstance(mode_config, dict) and "action_space" in mode_config:
            return mode_config.get("action_space")
        return self.config.get("action_space")

    def get_system_prompt(
        self,
        task_question: Optional[str] = None,
        extra_context: Optional[str] = None,
        action_space: Optional[str] = None,
    ) -> str:
        """
        基于 prompts/system_prompts.py 生成系统提示词，并自动注入工具描述。
        """
        resolved_action_space = action_space or self.get_action_space()
        if resolved_action_space is None:
            prompt_template = load_system_prompt(environment_mode=self.mode)
        else:
            prompt_template = load_system_prompt(
                environment_mode=self.mode,
                action_space=resolved_action_space
            )

        prompt_with_tools = prompt_template.replace(
            "{tool_descriptions}",
            self.get_tool_descriptions()
        )

        prompt_with_placeholders = self._replace_prompt_placeholders(prompt_with_tools)

        suffix_parts: List[str] = []
        if task_question:
            suffix_parts.append(f"You are asked to complete the following task: {task_question}")
        if extra_context:
            suffix_parts.append(extra_context)

        if suffix_parts:
            prompt_with_placeholders = "\n".join([prompt_with_placeholders, *suffix_parts])

        return prompt_with_placeholders

    def _replace_prompt_placeholders(self, prompt: str) -> str:
        """子类可覆盖此方法以替换自定义占位符"""
        return prompt

    def env_start(self) -> None:
        """Benchmark 开始时调用 (可选初始化)"""
        pass

    def env_close(self) -> None:
        """Benchmark 结束时调用 (可选清理)"""
        pass

    # =========================================================================
    # 5. 配置管理钩子 (可选覆盖，供子类调用 super())
    # =========================================================================

    def _initialize_config(self) -> None:
        """初始化配置 (可选覆盖)"""
        pass

    def _validate_config(self) -> None:
        """验证配置 (可选覆盖)"""
        pass
