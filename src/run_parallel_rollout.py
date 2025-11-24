# -*- coding: utf-8 -*-
"""
并行 Rollout 框架 - 支持重资产管理的并行任务执行

开发说明 (Development Guide):
---------------------------
1. 模块概述:
   本模块 (`src/run_parallel_rollout.py`) 实现了 AgentFlow 的并行任务执行框架，
   专门针对需要重型资源（如 OSWorld 的虚拟机）的环境进行了优化。
   它采用 "Manager-Worker" 架构，支持跨进程的资源分配、任务分发和结果收集。

2. 核心架构:
   - 主进程 (Main Process):
     - 负责加载 Benchmark 数据和任务配置。
     - 初始化全局资源管理器 (`ResourceManager`)，如 VM 池。
     - 启动 N 个 Worker 进程，并维护共享的任务队列 (`task_queue`) 和结果列表 (`shared_results`)。
     - 监听系统信号 (SIGINT/SIGTERM)，确保优雅退出和资源清理。
     - 最后收集所有结果，调用 Benchmark 进行评测，并保存结果。

   - Worker 进程 (`run_rollout_worker`):
     - 每个 Worker 是一个独立的进程。
     - 动态加载指定的环境类 (如 `ParallelOSWorldRolloutEnvironment`)。
     - 实现了 "控制反转" (IoC): Worker 负责通用的循环逻辑（取任务 -> 申请资源 -> 执行 -> 释放资源），
       具体的任务执行逻辑由环境类的 `run_task` 接口提供。
     - 通过 `allocate_resource` 向主进程的资源管理器申请资源（如 VM），
       并在本地实例化 `DesktopEnv` (Attach 模式)。

3. 关键类与函数:
   - `ParallelRolloutConfig`: 数据类，定义并行执行的配置参数（并发数、环境模式等）。
   - `run_parallel_rollout`: 主入口函数，协调整个并行执行流程。
   - `run_rollout_worker`: Worker 进程的执行体，包含资源申请、任务执行和异常处理逻辑。
   - `_register_main_signal_handlers`: 注册信号处理器，防止强制退出导致资源泄露（如 VM 未释放）。

4. 扩展与适配:
   - 新增环境: 只需继承 `Environment` 并实现 `setup_global_resources`, `allocate_resource` 等接口，
     即可接入此并行框架，无需修改本文件核心逻辑。
   - 资源管理: 通过 `global_resources` 对象（鸭子类型）与具体的资源管理器（如 `VMPoolResourceManager`）交互，
     支持扩展其他类型的重型资源。

5. 使用示例:
   python src/run_parallel_rollout.py --data_path data/tasks.jsonl --num_rollouts 4 --env_mode osworld

"""

import os
import sys
import json
import logging
import signal
from datetime import datetime
from multiprocessing import Manager, Process, current_process
from typing import Dict, List, Any, Optional, Tuple, Type
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from benchmark import Benchmark
from envs.enviroment import Environment
from envs.factory import get_environment_class

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

_MAIN_RESOURCE_MANAGER: Optional[Any] = None


def _register_main_signal_handlers(global_resources: Any):
    """
    注册主进程信号处理，确保 Ctrl+C 时优雅关闭资源
    
    使用鸭子类型检查资源对象是否有 stop_all 方法
    """
    global _MAIN_RESOURCE_MANAGER
    _MAIN_RESOURCE_MANAGER = global_resources

    def handle_signal(signum, frame):
        """
        信号处理函数：当接收到 SIGINT 或 SIGTERM 信号时，清理资源并退出
        """
        logger.info(f"Main process received signal {signum}, cleaning up resources...")
        try:
            # 使用鸭子类型检查是否有 stop_all 方法
            if _MAIN_RESOURCE_MANAGER and hasattr(_MAIN_RESOURCE_MANAGER, 'stop_all'):
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
    env_mode: str = "osworld"      # 环境模式
    env_kwargs: Dict[str, Any] = field(default_factory=dict)  # 环境配置参数
    agent_config_dict: Dict[str, Any] = field(default_factory=dict)  # Agent 配置
    output_dir: str = "results"    # 输出目录


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
    logger.info(f"  Env Mode: {config.env_mode}")
    logger.info(f"  Benchmark Items: {len(benchmark.get_items())}")
    logger.info("=" * 60)
    
    # 1. 根据 env_mode 动态获取环境类
    EnvClass = get_environment_class(config.env_mode)
    logger.info(f"Using environment class: {EnvClass.__name__}")
    
    # 2. 调用环境类的 setup_global_resources 方法初始化全局资源
    global_resources = EnvClass.setup_global_resources(config)
    _register_main_signal_handlers(global_resources)
    
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

            # [修改点] 添加哨兵值 (Poison Pill) 到队列末尾，每个 Worker 一个
            # 这确保了 Worker 在处理完所有任务后能立即收到停止信号
            for _ in range(config.num_rollouts):
                task_queue.put(None)
            
            # 3. 启动指定数量的 Worker 进程，每个进程执行 run_rollout_worker 函数
            # 将环境类传递给 worker（使用类的完全限定名，因为类对象不能直接序列化）
            env_class_name = EnvClass.__module__ + "." + EnvClass.__name__
            processes = []
            for i in range(config.num_rollouts):
                proc = Process(
                    target=run_rollout_worker,
                    args=(
                        f"worker-{i+1}",
                        task_queue,
                        env_class_name,  # 传递类名而不是类对象
                        config.env_kwargs,
                        config.agent_config_dict,
                        config.output_dir,
                        global_resources,  # 传递全局资源对象
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
        # 无论成功与否，都要停止所有资源（使用鸭子类型检查）
        try:
            if global_resources is not None and hasattr(global_resources, 'stop_all'):
                logger.info("Stopping all resources...")
                global_resources.stop_all()
        except Exception as exc:
            # 资源停止失败不影响主流程，只记录错误
            logger.error(f"Failed to stop resources: {exc}")


def run_rollout_worker(
    worker_id: str,
    task_queue,
    env_class_name: str,  # 环境类的完全限定名
    env_kwargs: Dict[str, Any],
    agent_config_dict: Dict[str, Any],
    output_dir: str,
    global_resources: Any,  # 全局资源对象（不透明对象，使用鸭子类型）
    parallel_degree: int,
    shared_results,
    worker_instance_map=None,
    worker_instance_events=None,
):
    """
    Rollout Worker 进程函数
    
    使用控制反转模式：Worker 只负责通用流程，具体执行逻辑由环境类提供。
    
    Args:
        worker_id: Worker 标识符
        task_queue: 任务队列
        env_class_name: 环境类的完全限定名（如 "envs.parallel_osworld_rollout_environment.ParallelOSWorldRolloutEnvironment"）
        env_kwargs: 环境配置参数
        agent_config_dict: Agent 配置字典（包含 model_name, max_turns, max_retries, output_dir 等）
        output_dir: 输出目录
        global_resources: 全局资源对象（不透明对象，由环境类管理，主脚本不关心具体类型）
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
        # 1. 从类名动态导入环境类
        module_name, class_name = env_class_name.rsplit(".", 1)
        env_module = __import__(module_name, fromlist=[class_name])
        EnvClass = getattr(env_module, class_name)
        
        # 2. 初始化环境实例，将全局资源对象传递给环境
        # 环境类负责判断是否需要使用该资源对象
        environment = EnvClass(
            resource_manager=global_resources,
            parallel_degree=parallel_degree,
            **env_kwargs,
        )
        
        if environment is None:
            raise RuntimeError(f"Failed to create environment instance: {env_class_name}")

        # 4. 启动环境，如果失败则记录警告但不影响后续流程
        try:
            environment.env_start()
        except Exception as exc:
            logger.warning(f"Worker {worker_id} env_start() failed: {exc}")

        # 如果环境支持初始化方法，则调用初始化
        init_fn = getattr(environment, "init", None)
        if callable(init_fn):
            try:
                init_fn()
            except Exception as exc:
                # 初始化失败不影响主流程，只记录警告
                logger.warning(f"Worker {worker_id} environment init() failed: {exc}")

        logger.info(f"Worker {worker_id} started")

        # 5. 检查环境支持的功能（任务配置、资源分配/释放、重型资源）
        task_config_fn = getattr(environment, "initialize_with_task_config", None)
        env_supports_task_config = callable(task_config_fn)
        allocate_fn = getattr(environment, "allocate_resource", None)
        release_fn = getattr(environment, "release_resource", None)
        env_has_heavy_resource = bool(getattr(environment, "has_heavy_resource", False) and callable(allocate_fn))

        # 6. 准备 Agent 配置（包含 output_dir）
        agent_config = dict(agent_config_dict)
        agent_config["output_dir"] = output_dir

        # 7. 主任务循环：从任务队列中获取任务并执行
        while True:
            try:
                
                task = task_queue.get()
                
                #  检查哨兵值 (Poison Pill)
                if task is None:
                    logger.info(f"Worker {worker_id} received sentinel. Stopping loop.")
                    break
            except Exception as e:
                # 仅处理队列异常（极少发生），如果发生则退出
                logger.error(f"Worker {worker_id} error getting task: {e}")
                break

            task_id = task.get("id", "unknown")
            resource_allocated = False
            current_resource_id = None

            try:
                # 确保 task 的 metadata 字段存在
                if "metadata" not in task or not isinstance(task.get("metadata"), dict):
                    task["metadata"] = task.get("metadata") or {}
                
                # 补充 metadata 中的字段到 task 主字典（向后兼容）
                metadata = task.get("metadata", {})
                for key in ("config", "evaluator"):
                    if key not in task and key in metadata:
                        task[key] = metadata[key]

                # 如果环境支持任务配置，则使用任务的配置初始化环境
                if env_supports_task_config:
                    task_env_config = (
                        task.get("env_config")
                        or task.get("metadata", {}).get("env_config")
                    )
                    # 如果任务包含环境配置，则应用配置
                    if task_env_config:
                        task_config_fn(task_env_config)

                # 如果环境需要重型资源，则从资源池中分配资源
                if env_has_heavy_resource:
                    logger.info(f"[worker {worker_id}] requesting resource from manager")
                    # 尝试分配资源，如果失败则抛出异常
                    if not allocate_fn or not allocate_fn(worker_id):
                        raise RuntimeError("Failed to allocate resource from pool")
                    resource_allocated = True
                    # 获取已分配的资源 ID
                    get_allocated_fn = getattr(environment, "get_allocated_resource_id", None)
                    current_resource_id = get_allocated_fn() if callable(get_allocated_fn) else None
                    if current_resource_id:
                        logger.info(f"[worker {worker_id}] acquired resource={current_resource_id}")
                        # 如果提供了映射字典，记录 worker 与实例的映射关系
                        if worker_instance_map is not None:
                            worker_instance_map[worker_id] = {
                                "instance_id": current_resource_id,
                                "task_id": task_id,
                                "assigned_time": datetime.now().isoformat(),
                            }
                        # 如果提供了事件列表，记录资源分配事件
                        if worker_instance_events is not None:
                            worker_instance_events.append(
                                {
                                    "timestamp": datetime.now().isoformat(),
                                    "worker_id": worker_id,
                                    "instance_id": current_resource_id,
                                    "task_id": task_id,
                                    "action": "allocate",
                                }
                            )

                # 8. 调用环境的 run_task 方法执行任务（控制反转核心）
                result = environment.run_task(task, agent_config, logger)

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
                    if current_resource_id:
                        logger.info(f"[worker {worker_id}] releasing resource={current_resource_id}")
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
                                "instance_id": current_resource_id,
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
    parser.add_argument("--env_mode", type=str, default="osworld_parallel", help="Environment mode")
    parser.add_argument("--output_dir", type=str, default="results", help="Output directory")
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
        env_mode=args.env_mode,
        output_dir=args.output_dir,
        env_kwargs=env_kwargs,
        agent_config_dict={
            "model_name": "gpt-4.1-2025-04-14",
            "evaluation_metric": "exact_match"
        }
    )
    
    # 运行并行 Rollout
    results = run_parallel_rollout(config, benchmark)
    
    logger.info("Parallel rollout completed successfully")