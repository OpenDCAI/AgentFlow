# -*- coding: utf-8 -*-
"""
并行 Rollout 框架 - 支持重资产管理的并行任务执行

根据 FINAL_ARCHITECTURE_DOC.md 实现：
- 根据环境类型决定是否启用重资产
- 主干脚本加载 worker
- environment 根据是否需要重资产调用 manager
"""

import os
import sys
import json
import logging
import signal
from datetime import datetime
from multiprocessing import Manager, Process, current_process
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

import openai

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from benchmark import Benchmark
from utils.resource_manager import ResourceManager, NoResourceManager, VMPoolResourceManager, HeavyResourceManager
from envs.parallel_osworld_rollout_environment import ParallelOSWorldRolloutEnvironment
from envs.enviroment import Environment

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 预加载环境变量（如阿里云/AWS 等云厂商所需配置）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
# 如果 .env 文件存在，则加载环境变量；否则记录警告信息
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    logger.info(f"Loaded environment variables from {ENV_PATH}")
else:
    logger.warning(f".env file not found at {ENV_PATH}, skipping environment variable preload")

_MAIN_RESOURCE_MANAGER: Optional[ResourceManager] = None


def _register_main_signal_handlers(resource_manager: ResourceManager):
    """
    注册主进程信号处理，确保 Ctrl+C 时优雅关闭资源
    """
    global _MAIN_RESOURCE_MANAGER
    _MAIN_RESOURCE_MANAGER = resource_manager

    def handle_signal(signum, frame):
        """
        信号处理函数：当接收到 SIGINT 或 SIGTERM 信号时，清理资源并退出
        """
        logger.info(f"Main process received signal {signum}, cleaning up resources...")
        try:
            # 如果资源管理器已初始化，则停止所有资源
            if _MAIN_RESOURCE_MANAGER:
                _MAIN_RESOURCE_MANAGER.stop_all()
        except Exception as exc:
            # 捕获停止资源过程中的异常，记录错误但不阻止退出
            logger.error(f"Failed to stop resources during signal handling: {exc}")
        finally:
            # 无论成功与否，最终都退出进程
            sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)


@dataclass
class ParallelRolloutConfig:
    """并行 Rollout 配置"""
    num_rollouts: int = 5          # 并行度（Worker 数量）
    num_vms: int = 3               # VM 池大小（仅用于 OSWorld）
    env_mode: str = "osworld"      # 环境模式
    env_kwargs: Dict[str, Any] = field(default_factory=dict)  # 环境配置参数
    agent_config_dict: Dict[str, Any] = field(default_factory=dict)  # Agent 配置
    output_dir: str = "results"    # 输出目录
    use_resource_pool: bool = True  # 是否使用资源池（仅用于 OSWorld）


@dataclass
class AgentConfig:
    """Agent 执行配置，仅保留当前脚本实际使用的参数。"""
    model_name: str = "gpt-4.1-2025-04-14"
    max_turns: int = 3
    max_retries: int = 3


def _build_agent_config(agent_config_dict: Optional[Dict[str, Any]]) -> AgentConfig:
    """
    Merge来⾃配置和默认值，确保并⾏脚本获得完整的 AgentConfig。
    """
    base = AgentConfig()
    config_dict = agent_config_dict or {}
    # 合并配置：优先使用传入的配置值，如果不存在则使用默认值
    merged = AgentConfig(
        model_name=config_dict.get("model_name", base.model_name),
        max_turns=config_dict.get("max_turns", base.max_turns),
        max_retries=config_dict.get("max_retries", base.max_retries),
    )
    return merged


def _initialize_environment(
    env_mode: str,
    env_kwargs: Optional[Dict[str, Any]],
    resource_manager: Optional[HeavyResourceManager],
    parallel_degree: int,
) -> Environment:
    """
    创建环境实例（OSWorld 使用并行环境，其他模式使用基础 Environment）。
    """
    env_kwargs = env_kwargs or {}

    # 根据环境模式创建相应的环境实例
    if env_mode == "osworld":
        # 创建 OSWorld 并行环境实例
        environment = ParallelOSWorldRolloutEnvironment(
            resource_manager=resource_manager,
            parallel_degree=parallel_degree,
            **env_kwargs,
        )
        # 如果环境支持工具响应字典格式，则启用该功能
        enable_fn = getattr(environment, "enable_tool_response_dict", None)
        if callable(enable_fn):
            enable_fn(True)
        print(f"Environment setup complete. Available tools: {environment.list_tools()}")
        return environment

    # 不支持的环境模式，抛出异常
    raise NotImplementedError(f"Environment mode '{env_mode}' is not supported in parallel rollout.")


def _prepare_task_for_runner(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    统一 task 结构，确保 metadata 始终存在，并在必要时补齐 config/evaluator。
    """
    prepared = dict(task)
    metadata = prepared.get("metadata")
    # 确保 metadata 是一个字典类型
    if not isinstance(metadata, dict):
        metadata = {}
    prepared["metadata"] = metadata

    # 遍历需要从 metadata 中提取的键，如果主任务中没有该键，则从 metadata 中补充
    for key in ("config", "evaluator"):
        if key not in prepared and key in metadata:
            prepared[key] = metadata[key]

    return prepared


_OPENAI_CLIENT: Optional[openai.OpenAI] = None


def _get_openai_client() -> openai.OpenAI:
    """
    获取 OpenAI 客户端实例（单例模式）
    如果客户端未初始化，则从环境变量中读取配置并创建新实例
    """
    global _OPENAI_CLIENT
    # 如果客户端未初始化，则创建新实例
    if _OPENAI_CLIENT is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_API_URL") or os.environ.get("OPENAI_API_BASE")
        openai.api_key = api_key
        # 如果配置了自定义 base_url，则使用自定义 URL；否则使用默认 URL
        if base_url:
            openai.base_url = base_url
            _OPENAI_CLIENT = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            _OPENAI_CLIENT = openai.OpenAI(api_key=api_key)
    return _OPENAI_CLIENT


def _run_agent_task(
    environment: Environment,
    agent_config: AgentConfig,
    task: Dict[str, Any],
    output_dir: str,
    logger: logging.Logger,
) -> Dict[str, Any]:
    if not environment:
        raise ValueError("Environment not initialized")

    task_id = task.get("id", "unknown")
    question = task.get("question", "")

    # 如果环境支持任务输出目录功能，获取该任务的输出目录
    get_dir_fn = getattr(environment, "get_task_output_dir", None)
    task_output_dir = None
    if callable(get_dir_fn):
        task_output_dir = get_dir_fn(output_dir, task_id, agent_config.model_name)

    # 初始化任务环境，获取初始观察
    initial_obs = environment.env_task_init(task)

    # 执行对话，获取完整的消息列表
    messages = _run_conversation(environment, agent_config, question, initial_obs, logger)
    # 从消息中提取最终答案
    final_answer = _extract_final_answer(messages)

    # 构建任务结果字典
    result = {
        "task_id": task_id,
        "question": question,
        "answer": final_answer,
        "messages": messages,
        "success": True,
        "error": None,
    }

    # 如果环境支持内部评估，则执行评估并更新结果
    evaluation_score = None
    if getattr(environment, "has_internal_evaluation", lambda: False)():
        try:
            logger.info(f"Evaluating task {task_id} via environment evaluator...")
            eval_fn = getattr(environment, "evaluate", None)
            # 检查环境是否实现了评估方法
            if not callable(eval_fn):
                raise AttributeError("Environment does not implement evaluate()")
            evaluation_score = eval_fn()
            result["evaluation_score"] = evaluation_score
            result["answer"] = str(evaluation_score)
            # 如果任务输出目录存在，将评估结果写入文件
            if isinstance(task_output_dir, str):
                result_file = os.path.join(task_output_dir, "result.txt")
                with open(result_file, "w", encoding="utf-8") as f:
                    f.write(f"{evaluation_score}\n")
        except Exception as exc:
            # 评估失败不影响主流程，只记录警告
            logger.warning(f"Internal evaluation for task {task_id} failed: {exc}")

    # 调用环境的任务结束方法，进行清理和收尾工作
    try:
        end_fn = getattr(environment, "env_task_end")
        end_fn(task_id, task_output_dir if isinstance(task_output_dir, str) else None, result.get("answer"))
    except Exception as exc:
        # 任务结束处理失败不影响返回结果，只记录警告
        logger.warning(f"Failed to finalize task {task_id}: {exc}")

    # 如果任务输出目录存在，保存对话日志
    if isinstance(task_output_dir, str):
        _save_conversation_log(task_output_dir, task_id, question, agent_config.model_name, messages, result)

    return result


def _run_conversation(
    environment: Environment,
    agent_config: AgentConfig,
    question: str,
    initial_obs: Optional[Dict[str, Any]],
    logger: logging.Logger,
) -> List[Dict[str, Any]]:
    system_prompt = environment.get_system_prompt(question)
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
    ]

    # 构建用户消息内容，包含问题文本
    user_content: List[Dict[str, Any]] = [{"type": "text", "text": f"Question: {question}\n"}]
    # 如果环境支持格式化初始观察的功能，则将初始观察添加到消息中
    format_initial_fn = getattr(environment, "format_initial_observation_for_message", None)
    if callable(format_initial_fn) and initial_obs is not None:
        try:
            obs_content_parts = format_initial_fn(initial_obs)
            # 如果返回的是列表，则扩展用户内容；否则作为单个文本添加
            if isinstance(obs_content_parts, list):
                user_content.extend(obs_content_parts)
            else:
                user_content.append({"type": "text", "text": str(obs_content_parts)})
            logger.info("Initial observation added to conversation context")
        except Exception as exc:
            # 格式化失败不影响主流程，只记录警告
            logger.warning(f"Failed to format initial observation: {exc}")
    messages.append({"role": "user", "content": user_content})

    client = _get_openai_client()
    turn_count = 0
    step_idx = 0

    # 主对话循环：在最大轮次限制内进行多轮对话
    while turn_count < agent_config.max_turns:
        retry = 0
        # 重试循环：每次 API 调用失败后会重试，直到达到最大重试次数
        while retry < agent_config.max_retries:
            try:
                # 调用 OpenAI API 获取 LLM 响应
                response = client.chat.completions.create(  # type: ignore[arg-type]
                    model=agent_config.model_name,
                    messages=messages,  # type: ignore[arg-type]
                    tools=environment.get_tool_schemas(),  # type: ignore[arg-type]
                )
                # 验证 API 响应是否有效
                if not hasattr(response, "choices") or not response.choices:
                    raise ValueError("OpenAI API returned empty response")

                # 提取助手消息并添加到消息列表
                assistant_message = response.choices[0].message
                assistant_dict = _normalize_message(assistant_message)
                messages.append(assistant_dict)

                # 如果 LLM 返回了工具调用，则执行工具
                if assistant_message.tool_calls:
                    tool_call = assistant_message.tool_calls[0]
                    function_call = getattr(tool_call, "function", None)
                    # 验证工具调用是否包含函数信息
                    if not function_call:
                        raise ValueError("Tool call missing function payload")
                    tool_name = function_call.name
                    tool_args = json.loads(function_call.arguments)
                    logger.info(f"Turn {turn_count}: executing tool {tool_name}")

                    # 执行工具，获取执行结果
                    tool_result_raw = environment.execute_tool(tool_name, tool_args)
                    # 将工具结果转换为字典格式
                    if isinstance(tool_result_raw, dict):
                        tool_result = tool_result_raw
                    else:
                        try:
                            # 尝试将字符串解析为 JSON
                            tool_result = json.loads(tool_result_raw)
                        except json.JSONDecodeError:
                            # 解析失败则使用默认格式
                            tool_result = {"status": "unknown", "response": str(tool_result_raw), "observation": {}}

                    # 如果工具返回了观察结果，将其添加到轨迹中
                    observation = tool_result.get("observation") or {}
                    if observation:
                        step_idx += 1
                        add_step_fn = getattr(environment, "add_step_to_trajectory", None)
                        # 如果环境支持轨迹记录功能，则添加步骤
                        if callable(add_step_fn):
                            add_step_fn(observation, step_idx)

                    # 格式化工具响应内容，准备添加到消息中
                    content_payload = _format_tool_response_content(tool_result, observation)

                    # 将工具执行结果作为 tool 角色的消息添加到对话中
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": content_payload,
                        }
                    )
                    # 工具执行成功，跳出重试循环，进入下一轮对话
                    break

                else:
                    # LLM 返回了最终答案（没有工具调用），对话结束
                    logger.info(f"Turn {turn_count}: final answer produced")
                    return messages

            except Exception as exc:
                # API 调用或工具执行失败，进行重试
                retry += 1
                logger.warning(f"Retry {retry}/{agent_config.max_retries} due to error: {exc}")
                # 如果达到最大重试次数，则抛出异常
                if retry >= agent_config.max_retries:
                    raise

        # 完成一轮对话（可能包含多次重试），进入下一轮
        turn_count += 1

    # 达到最大轮次仍未获得最终答案，返回当前消息列表
    logger.warning("Max turns reached without final answer")
    return messages


def _format_tool_response_content(tool_result: Dict[str, Any], observation: Dict[str, Any]):
    content_parts: List[Dict[str, Any]] = []
    base_result = {
        "status": tool_result.get("status", "unknown"),
        "response": tool_result.get("response", ""),
    }
    # 添加工具执行的基础结果（状态和响应）
    content_parts.append({"type": "text", "text": f"Execution Result:\n{json.dumps(base_result, indent=2)}"})

    # 如果观察结果存在，添加观察内容（文本和/或图片）
    if observation:
        text_part = observation.get("text")
        image_part = observation.get("image")
        # 如果有文本观察，添加文本内容
        if text_part:
            content_parts.append({"type": "text", "text": f"\n--- Current Page State ---\n{text_part}"})
        # 如果有图片观察，添加图片内容（base64 编码）
        if image_part:
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_part}", "detail": "high"},
                }
            )

    # 如果只有一个内容部分，直接返回文本；否则返回内容列表
    if len(content_parts) == 1:
        return content_parts[0]["text"]
    return content_parts


def _extract_final_answer(messages: List[Dict[str, Any]]) -> str:
    """
    从消息列表中提取最终答案
    从后往前遍历消息，找到第一个没有工具调用的助手消息作为最终答案
    """
    # 从后往前遍历消息列表，查找最后一个不含工具调用的助手消息
    for message in reversed(messages):
        normalized = _normalize_message(message)
        # 如果是助手消息且没有工具调用，则认为是最终答案
        if normalized.get("role") == "assistant" and not normalized.get("tool_calls"):
            return normalized.get("content", "")
    # 如果找不到最终答案，返回默认消息
    return "No final answer found"


def _normalize_message(message: Any) -> Dict[str, Any]:
    """
    将消息对象标准化为字典格式
    如果消息对象有 model_dump 方法（如 Pydantic 模型），则调用该方法；否则直接返回原对象
    """
    # 如果消息对象是 Pydantic 模型，则使用 model_dump 方法转换为字典
    if hasattr(message, "model_dump"):
        return message.model_dump()
    # 否则直接返回原对象（假设已经是字典）
    return message


def _save_conversation_log(
    output_dir: str,
    task_id: str,
    question: str,
    model_name: str,
    messages: List[Dict[str, Any]],
    result: Dict[str, Any],
) -> None:
    # 将消息列表中的每个消息标准化为可序列化的字典格式
    serializable_messages = [_normalize_message(msg) for msg in messages]
    # 构建对话数据字典
    conversation_data = {
        "task_id": task_id,
        "question": question,
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "success": result.get("success", False),
        "evaluation_score": result.get("evaluation_score"),
        "messages": serializable_messages,
    }
    conversation_file = os.path.join(output_dir, "conversation.json")
    # 将对话数据写入 JSON 文件
    with open(conversation_file, "w", encoding="utf-8") as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)


def run_parallel_rollout(
    config: ParallelRolloutConfig,
    benchmark: Benchmark
):
    """
    运行并行 Rollout 框架
    
    流程：
    1. Benchmark 类已加载所有 Task（BenchmarkItem 格式）
    2. 创建资源管理器
    3. 启动 N 个 Worker 进程
    4. 每个 Worker 从任务队列获取 BenchmarkItem 格式的 Task
    5. Worker 执行任务并进行双重评测
    
    Args:
        config: 并行 Rollout 配置
        benchmark: Benchmark 实例（已加载任务）
    """
    logger.info("=" * 60)
    logger.info("Starting Parallel Rollout Framework")
    logger.info(f"  Num Rollouts: {config.num_rollouts}")
    logger.info(f"  Num VMs: {config.num_vms}")
    logger.info(f"  Env Mode: {config.env_mode}")
    logger.info(f"  Use Resource Pool: {config.use_resource_pool}")
    logger.info(f"  Benchmark Items: {len(benchmark.get_items())}")
    logger.info("=" * 60)
    
    # 1. 创建资源管理器
    resource_manager = _create_resource_manager(config)
    _register_main_signal_handlers(resource_manager)
    
    try:
        # 2. 创建跨进程共享的数据结构（任务队列、结果列表、映射字典、事件列表）
        with Manager() as manager:
            task_queue = manager.Queue()
            shared_results = manager.list()
            worker_instance_map = manager.dict()
            worker_instance_events = manager.list()
            
            # 将所有基准测试项转换为字典格式并放入任务队列
            for item in benchmark.get_items():
                task_dict = {
                    "id": item.id,
                    "question": item.question,
                    "answer": item.answer,
                    "metadata": item.metadata or {}
                }
                task_queue.put(task_dict)
            
            # 3. 启动指定数量的 Worker 进程，每个进程执行 run_rollout_worker 函数
            processes = []
            for i in range(config.num_rollouts):
                proc = Process(
                    target=run_rollout_worker,
                    args=(
                        f"worker-{i+1}",
                        task_queue,
                        config.env_mode,
                        config.env_kwargs,
                        config.agent_config_dict,
                        config.output_dir,
                        resource_manager,
                        config.num_rollouts,
                        shared_results,
                        worker_instance_map,
                        worker_instance_events,
                    )
                )
                proc.start()
                processes.append(proc)
                logger.info(f"Started worker process: worker-{i+1}")
            
            # 等待所有 Worker 进程执行完毕
            for proc in processes:
                proc.join()
            
            # 4. 收集所有 Worker 的执行结果并进行评测
            # 将共享结果列表转换为普通列表
            results = list(shared_results)
            # 将 worker 实例映射字典转换为普通字典（处理嵌套字典）
            worker_instance_snapshot = {k: dict(v) if isinstance(v, dict) else v for k, v in worker_instance_map.items()}
            # 将 worker 实例事件列表转换为普通列表
            worker_instance_events_log = list(worker_instance_events)
            
            logger.info(f"All workers completed. Total results: {len(results)}")
            
            # 从结果中提取成功的任务预测结果，用于 Benchmark 评测
            # 字典推导式：只包含成功执行的任务
            predictions = {
                result["task_id"]: result.get("answer", "")
                for result in results
                if result.get("success", False)
            }
            
            # 使用 Benchmark 类进行评测
            evaluation_metric = config.agent_config_dict.get("evaluation_metric", "exact_match")
            benchmark_results = benchmark.evaluate(
                predictions=predictions,
                metric=evaluation_metric
            )
            
            # 打印评测结果统计信息
            logger.info("=" * 60)
            logger.info("Benchmark Evaluation Results")
            logger.info(f"  Metric: {evaluation_metric}")
            logger.info(f"  Total Items: {len(benchmark_results)}")
            # 如果评测结果不为空，计算并打印平均分
            if benchmark_results:
                avg_score = sum(r.score for r in benchmark_results) / len(benchmark_results)
                logger.info(f"  Average Score: {avg_score:.4f}")
            logger.info("=" * 60)
            
            # 保存结果文件：创建输出目录
            os.makedirs(config.output_dir, exist_ok=True)
            # 保存 worker 实例映射关系到 JSON 文件
            mapping_file = os.path.join(config.output_dir, "worker_instance_map.json")
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(worker_instance_snapshot, f, indent=2, ensure_ascii=False)
            logger.info(f"Worker-instance mapping written to {mapping_file}")

            # 保存 worker 实例事件时间线到 JSONL 文件（每行一个 JSON 对象）
            events_file = os.path.join(config.output_dir, "worker_instance_events.jsonl")
            with open(events_file, "w", encoding="utf-8") as f:
                for event in worker_instance_events_log:
                    json.dump(event, f, ensure_ascii=False)
                    f.write("\n")
            logger.info(f"Worker-instance timeline written to {events_file}")

            # 返回结果字典，包含 Worker 执行结果和 Benchmark 评测结果
            return {
                "worker_results": results,
                "benchmark_evaluation": benchmark_results
            }
    finally:
        # 无论成功与否，都要停止所有资源（如 VM 池）
        try:
            logger.info("Stopping all resources...")
            resource_manager.stop_all()
        except Exception as exc:
            # 资源停止失败不影响主流程，只记录错误
            logger.error(f"Failed to stop resources: {exc}")


def _create_resource_manager(config: ParallelRolloutConfig) -> ResourceManager:
    """
    根据环境类型创建资源管理器
    
    在分布式架构中：
    - Manager 进程：管理 VM 池元数据（IP、端口等），不存储 DesktopEnv 对象
    - Worker 进程：通过 resource_manager.allocate() 获取连接信息，在本地实例化 DesktopEnv（Attach 模式）
    
    Args:
        config: 并行 Rollout 配置
    
    Returns:
        ResourceManager 实例（可以跨进程传递，因为包含 BaseManager 代理）
    """
    # 根据环境类型决定是否启用重资产：OSWorld 需要 VM 池，其他环境不需要
    if config.env_mode == "osworld" and config.use_resource_pool:
        logger.info("Initializing VM pool (Distributed Worker Architecture)...")
        pool_config = {
            "num_vms": config.num_vms,
            "provider_name": config.env_kwargs.get("provider_name", "vmware"),
            "path_to_vm": config.env_kwargs.get("path_to_vm"),
            "snapshot_name": config.env_kwargs.get("snapshot_name", "init_state"),
            "action_space": config.env_kwargs.get("action_space", "computer_13"),
            "screen_size": (
                config.env_kwargs.get("screen_width", 1920),
                config.env_kwargs.get("screen_height", 1080),
            ),
            "headless": config.env_kwargs.get("headless", False),
            "require_a11y_tree": config.env_kwargs.get("require_a11y_tree", True),
            "require_terminal": config.env_kwargs.get("require_terminal", False),
            "os_type": config.env_kwargs.get("os_type", "Ubuntu"),
            "client_password": config.env_kwargs.get("client_password", "password"),
        }
        resource_manager = VMPoolResourceManager(pool_config=pool_config)
        resource_manager.initialize()
        logger.info("VM pool initialized successfully (Distributed Worker Architecture)")
        return resource_manager
    else:
        # 其他环境或不使用资源池时，使用空资源管理器（不管理任何资源）
        logger.info("Using NoResourceManager (no heavy resources)")
        return NoResourceManager()


def run_rollout_worker(
    worker_id: str,
    task_queue,
    env_mode: str,
    env_kwargs: Dict[str, Any],
    agent_config_dict: Dict[str, Any],
    output_dir: str,
    resource_manager: ResourceManager,
    parallel_degree: int,
    shared_results,
    worker_instance_map=None,
    worker_instance_events=None,
):
    """
    Rollout Worker 进程函数
    
    在分布式架构中：
    - resource_manager 通过 multiprocessing.Process 的 args 传递（包含 BaseManager 代理）
    - environment.allocate_resource() 调用 resource_manager.allocate()
    - resource_manager.allocate() 从 Manager 获取连接信息，在 Worker 本地实例化 DesktopEnv（Attach 模式）
    - DesktopEnv 对象在 Worker 进程中创建，避免跨进程序列化问题
    
    Args:
        worker_id: Worker 标识符
        task_queue: 任务队列
        env_mode: 环境模式
        env_kwargs: 环境配置参数
        agent_config_dict: Agent 配置
        output_dir: 输出目录
        resource_manager: 资源管理器实例（包含 BaseManager 代理，可跨进程传递）
        parallel_degree: 并行度
        shared_results: 共享结果列表
        worker_instance_map: (可选) Manager dict，用于记录 worker-实例映射
        worker_instance_events: (可选) Manager list，记录实例申请/释放时间线
    """
    logger = logging.getLogger(f"worker.{worker_id}")
    environment: Optional[Environment] = None

    def worker_signal_handler(signum, frame):
        """
        Worker 进程信号处理函数：当接收到 SIGINT 或 SIGTERM 信号时，清理环境资源并退出
        """
        logger.info(f"Worker {worker_id} received signal {signum}. Cleaning up...")
        try:
            # 如果环境已初始化，则进行清理
            if environment:
                # 优先使用环境的 cleanup 方法，否则使用 env_close 方法
                cleanup_fn = getattr(environment, "cleanup", None)
                if callable(cleanup_fn):
                    cleanup_fn(worker_id)
                else:
                    environment.env_close()
        except Exception as e:
            # 清理失败不影响退出，只记录错误
            logger.error(f"Error during signal cleanup: {e}")
        # 无论清理成功与否，都退出进程
        sys.exit(0)

    signal.signal(signal.SIGINT, worker_signal_handler)
    signal.signal(signal.SIGTERM, worker_signal_handler)

    try:
        # 构建 Agent 配置对象
        agent_config = _build_agent_config(agent_config_dict)
        # 如果资源管理器是重型资源管理器，则传递给环境；否则传递 None
        heavy_manager = resource_manager if isinstance(resource_manager, HeavyResourceManager) else None
        # 初始化环境实例
        environment = _initialize_environment(
            env_mode=env_mode,
            env_kwargs=env_kwargs,
            resource_manager=heavy_manager,
            parallel_degree=parallel_degree,
        )

        # 启动环境，如果失败则记录警告但不影响后续流程
        try:
            environment.env_start() #这里的操作步骤没有获得desktopenv对象
        except Exception as exc:
            logger.warning(f"Worker {worker_id} env_start() failed: {exc}")

        # 如果环境支持初始化方法，则调用初始化
        init_fn = getattr(environment, "init", None)
        if callable(init_fn):
            try:
                init_fn()   #这里的操作步骤没有获得desktopenv对象
            except Exception as exc:
                # 初始化失败不影响主流程，只记录警告
                logger.warning(f"Worker {worker_id} environment init() failed: {exc}")

        logger.info(f"Worker {worker_id} started")

        # 检查环境支持的功能（任务配置、资源分配/释放、重型资源）
        task_config_fn = getattr(environment, "initialize_with_task_config", None)
        env_supports_task_config = callable(task_config_fn)
        allocate_fn = getattr(environment, "allocate_resource", None)
        release_fn = getattr(environment, "release_resource", None)
        env_has_heavy_resource = bool(getattr(environment, "has_heavy_resource", False) and callable(allocate_fn))

        # 主任务循环：从任务队列中获取任务并执行，直到队列为空或超时
        while True:
            try:
                # 从任务队列中获取任务，设置超时时间为 5 秒
                task = task_queue.get(timeout=5)
            except Exception:
                # 队列为空或超时，退出循环
                break

            task_id = task.get("id", "unknown")
            resource_allocated = False

            try:
                # 准备任务数据，统一任务格式
                prepared_task = _prepare_task_for_runner(task)

                # 如果环境支持任务配置，则使用任务的配置初始化环境
                if env_supports_task_config:
                    task_env_config = (
                        prepared_task.get("env_config")
                        or prepared_task.get("metadata", {}).get("env_config")
                    )
                    # 如果任务包含环境配置，则应用配置
                    if task_env_config:
                        task_config_fn(task_env_config)

                # 如果环境需要重型资源（如 VM），则从资源池中分配资源
                if env_has_heavy_resource:
                    logger.info(f"[worker {worker_id}] requesting VM from manager")
                    # 尝试分配资源，如果失败则抛出异常
                    if not allocate_fn or not allocate_fn(worker_id):
                        raise RuntimeError("Failed to allocate resource from pool")
                    resource_allocated = True
                    # 获取已分配的资源 ID（如 VM ID）
                    get_allocated_fn = getattr(environment, "get_allocated_resource_id", None)
                    current_vm_id = get_allocated_fn() if callable(get_allocated_fn) else None
                    if current_vm_id:
                        logger.info(f"[worker {worker_id}] acquired vm={current_vm_id}")
                        # 如果提供了映射字典，记录 worker 与实例的映射关系
                        if worker_instance_map is not None:
                            worker_instance_map[worker_id] = {
                                "instance_id": current_vm_id,
                                "task_id": task_id,
                                "assigned_time": datetime.now().isoformat(),
                            }
                        # 如果提供了事件列表，记录资源分配事件
                        if worker_instance_events is not None:
                            worker_instance_events.append(
                                {
                                    "timestamp": datetime.now().isoformat(),
                                    "worker_id": worker_id,
                                    "instance_id": current_vm_id,
                                    "task_id": task_id,
                                    "action": "allocate",
                                }
                            )

                # 执行 Agent 任务，获取执行结果
                result = _run_agent_task(environment, agent_config, prepared_task, output_dir, logger)

                # 将任务结果添加到共享结果列表
                if shared_results is not None:
                    shared_results.append(result)

                logger.info(f"Worker {worker_id} completed task {task_id}")

            except Exception as e:
                # 任务执行失败，记录错误并创建失败结果
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                failure_result = {
                    "task_id": task_id,
                    "question": task.get("question", ""),
                    "answer": "",
                    "messages": [],
                    "success": False,
                    "error": str(e),
                }
                # 将失败结果也添加到共享结果列表
                if shared_results is not None:
                    shared_results.append(failure_result)
            finally:
                # 无论任务成功或失败，都要释放已分配的资源
                if env_has_heavy_resource and resource_allocated and callable(release_fn):
                    current_vm_id = None
                    # 获取当前分配的实例 ID
                    get_allocated_fn = getattr(environment, "get_allocated_resource_id", None)
                    if callable(get_allocated_fn):
                        current_vm_id = get_allocated_fn()
                    if current_vm_id:
                        logger.info(f"[worker {worker_id}] releasing vm={current_vm_id}")
                    # 释放资源并重置环境
                    release_fn(worker_id, reset=True)
                    # 从映射字典中移除该 worker 的记录
                    if worker_instance_map is not None:
                        worker_instance_map.pop(worker_id, None)
                    # 记录资源释放事件
                    if worker_instance_events is not None:
                        worker_instance_events.append(
                            {
                                "timestamp": datetime.now().isoformat(),
                                "worker_id": worker_id,
                                "instance_id": current_vm_id,
                                "task_id": task_id,
                                "action": "release",
                            }
                        )

    finally:
        # Worker 退出时的清理工作
        # 从映射字典中移除该 worker 的记录（如果存在）
        if worker_instance_map is not None:
            worker_instance_map.pop(worker_id, None)
        # 记录 worker 退出事件
        if worker_instance_events is not None:
            worker_instance_events.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "worker_id": worker_id,
                    "instance_id": None,
                    "task_id": None,
                    "action": "worker_exit",
                }
            )

        # 如果环境已初始化，则清理环境资源
        if environment:
            try:
                # 优先使用环境的 cleanup 方法，否则使用 env_close 方法
                cleanup_fn = getattr(environment, "cleanup", None)
                if callable(cleanup_fn):
                    cleanup_fn(worker_id)
                else:
                    environment.env_close()
            except Exception as e:
                # 清理失败不影响退出，只记录错误
                logger.error(f"Cleanup failed: {e}")


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description="Run parallel rollout")
    parser.add_argument("--data_path", type=str, required=True, help="Path to benchmark data file")
    parser.add_argument("--num_rollouts", type=int, default=5, help="Number of parallel workers")
    parser.add_argument("--num_vms", type=int, default=3, help="Number of VMs in pool")
    parser.add_argument("--env_mode", type=str, default="osworld", help="Environment mode")
    parser.add_argument("--output_dir", type=str, default="results", help="Output directory")
    parser.add_argument("--use_resource_pool", action="store_true", help="Use resource pool")
    parser.add_argument("--provider", type=str, default=None, help="Override VM provider name (e.g., aliyun, aws)")
    parser.add_argument("--region", type=str, default=None, help="Override region for cloud providers")
    parser.add_argument("--headless", action="store_true", help="Run desktop environment in headless mode if supported")
    
    args = parser.parse_args()
    
    # 加载 Benchmark
    benchmark = Benchmark(data_path=args.data_path)
    
    # 基础环境配置
    env_kwargs: Dict[str, Any] = {
        "action_space": "computer_13",
        "observation_type": "screenshot_a11y_tree",
    }
    
    # 根据命令行参数更新环境配置
    # 如果指定了云提供商，则设置提供商名称
    if args.provider:
        env_kwargs["provider_name"] = args.provider
    # 如果指定了区域，则设置区域
    if args.region:
        env_kwargs["region"] = args.region
    # 如果指定了无头模式，则启用无头模式
    if args.headless:
        env_kwargs["headless"] = True
    
    # 创建配置
    config = ParallelRolloutConfig(
        num_rollouts=args.num_rollouts,
        num_vms=args.num_vms,
        env_mode=args.env_mode,
        output_dir=args.output_dir,
        use_resource_pool=args.use_resource_pool,
        env_kwargs=env_kwargs,
        agent_config_dict={
            "model_name": "gpt-4.1-2025-04-14",
            "evaluation_metric": "exact_match"
        }
    )
    
    # 运行并行 Rollout
    results = run_parallel_rollout(config, benchmark)
    
    logger.info("Parallel rollout completed successfully")

