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

5. 共享数据结构 (Shared Data Models):
   所有环境在记录/返回观测与轨迹时，应复用 `envs.data_models` 中的
   `Observation`, `TrajectoryStep`, `TaskTrajectory` 数据类，从而保证与
   data_synthesis 管线的数据格式一致。本文档通过导入并导出这些类型，
   方便开发者直接复用。

=============================================================================
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

from envs.data_models import Observation, TrajectoryStep, TaskTrajectory
from prompts.system_prompts import get_system_prompt as load_system_prompt
from tools.tool import Tool
from utils.resource_manager import ResourceManager
import openai
import os
import json

__all__ = [
    "Environment",
    "Observation",
    "TrajectoryStep",
    "TaskTrajectory",
]


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


    def run_task(self, task: Dict[str, Any], agent_config: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        """
        执行完整的 Agent 任务循环
        
        封装从任务初始化到结果返回的完整流程，包括：
        - 任务初始化（env_task_init）
        - Agent 对话循环（LLM -> Tool -> Env）
        - 评估（如果支持）
        - 任务清理（env_task_end）
        
        Args:
            task: 任务字典，包含 id, question, metadata 等字段
            agent_config: Agent 配置字典，包含 model_name, max_turns, max_retries 等
            logger: 日志记录器
        
        Returns:
            包含 task_id, question, answer, messages, success 等字段的结果字典
        """
        task_id = task.get("id", "unknown")
        question = task.get("question", "")
        
        # 获取 Agent 配置参数
        model_name = agent_config.get("model_name", "gpt-4.1-2025-04-14")
        max_turns = agent_config.get("max_turns", 3)
        max_retries = agent_config.get("max_retries", 3)

        # 获取任务输出目录（如果环境支持）
        task_output_dir = None
        if hasattr(self, "get_task_output_dir") and callable(self.get_task_output_dir):
            task_output_dir = self.get_task_output_dir(
                agent_config.get("output_dir", "results"),
                task_id,
                model_name
            )

        # 执行对话，获取完整的消息列表
        messages = self._run_conversation(question, model_name, max_turns, max_retries, logger)
        
        # 从消息中提取最终答案
        final_answer = self._extract_final_answer(messages)

        # 构建任务结果字典
        result = {
            "task_id": task_id,
            "question": question,
            "answer": final_answer,
            "messages": messages,
            "success": True,
            "error": None,
        }

        # 如果任务输出目录存在，保存对话日志
        if task_output_dir:
            self._save_conversation_log(
                task_output_dir,
                task_id,
                question,
                model_name,
                messages,
                result
            )

        return result

    def _run_conversation(
        self,
        question: str,
        model_name: str,
        max_turns: int,
        max_retries: int,
        logger: logging.Logger,
    ) -> List[Dict[str, Any]]:
        """
        执行 Agent 对话循环
        
        Args:
            question: 任务问题
            initial_obs: 初始观察结果
            model_name: LLM 模型名称
            max_turns: 最大对话轮数
            max_retries: 每次调用的最大重试次数
            logger: 日志记录器
        
        Returns:
            完整的消息列表
        """
        system_prompt = self.get_system_prompt(question)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]

        # 构建用户消息内容，包含问题文本
        user_content: List[Dict[str, Any]] = [{"type": "text", "text": f"Question: {question}\n"}]
        # 如果环境支持格式化初始观察的功能，则将初始观察添加到消息中

        messages.append({"role": "user", "content": user_content})

        client = self._get_openai_client()
        turn_count = 0
        step_idx = 0

        # 主对话循环：在最大轮次限制内进行多轮对话
        while turn_count < max_turns:
            retry = 0
            # 重试循环：每次 API 调用失败后会重试，直到达到最大重试次数
            while retry < max_retries:
                try:
                    # 调用 OpenAI API 获取 LLM 响应
                    # exit()
                    print(f"Messages: {messages}")
                    response = client.chat.completions.create(  # type: ignore[arg-type]
                        model=model_name,
                        messages=messages,  # type: ignore[arg-type]
                        tools=self.get_tool_schemas(),  # type: ignore[arg-type]
                    )
                    # 验证 API 响应是否有效
                    if not hasattr(response, "choices") or not response.choices:
                        raise ValueError("OpenAI API returned empty response")

                    # 提取助手消息并添加到消息列表
                    assistant_message = response.choices[0].message
                    print(f"Assistant message: {assistant_message}")
                    messages.append(assistant_message.model_dump())

                    # 如果 LLM 返回了工具调用，则执行工具
                    if assistant_message.tool_calls:
                        print(f"Messages: {messages[-1]['content']}")
                        if messages[-1]['content'] == "":
                            tc = messages[-1].tool_calls[0].model_dump()['function']
                            messages[-1]['content'] = tc
                        for tool_call in assistant_message.tool_calls[:1]:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            print(f"Round {turn_count}: 🔧 Using tool: {tool_name}")
                            print(f"Round {turn_count}:    Arguments: {tool_args}")
                            
                            # Execute tool
                            tool_result = self.execute_tool(
                                tool_name, 
                                tool_args
                            )
                            
                            print(f"Round {turn_count}:    Result: {tool_result[:100]}...")
                            
                            # Add tool result to conversation
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result
                            })
                        
                    else:
                        logger.info(f"Turn {turn_count}: final answer produced")
                        return messagess
                except Exception as exc:
                    # API 调用或工具执行失败，进行重试
                    retry += 1
                    logger.warning(f"Retry {retry}/{max_retries} due to error: {exc}")
                    # 如果达到最大重试次数，则抛出异常
                    if retry >= max_retries:
                        raise
            turn_count += 1
        logger.warning("Max turns reached without final answer")
        return messages
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
        required_params = [param['name'] for param in tool.parameters if param.get('required', False)]
        properties = {}
        
        for param in tool.parameters:
            properties[param['name']] = {
                "type": param['type'],
                "description": param['description']
            }
            if param['type'] == 'array':
                properties[param['name']]['items'] = {
                    "type": param['array_type']
                }
        
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_params
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

    def _get_openai_client(self) -> openai.OpenAI:
        """
        获取 OpenAI 客户端实例（单例模式）
        如果客户端未初始化，则从环境变量或配置中读取配置并创建新实例
        """
        if not hasattr(self, '_openai_client') or self._openai_client is None:
            import openai
            api_key = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
            base_url = self.config.get("openai_api_url") or os.environ.get("OPENAI_API_URL") or os.environ.get("OPENAI_API_BASE")
            
            openai.api_key = api_key
            # 如果配置了自定义 base_url，则使用自定义 URL；否则使用默认 URL
            if base_url:
                openai.base_url = base_url
                self._openai_client = openai.OpenAI(api_key=api_key, base_url=base_url)
            else:
                self._openai_client = openai.OpenAI(api_key=api_key)
        return self._openai_client