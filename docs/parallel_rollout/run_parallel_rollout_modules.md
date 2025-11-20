# `run_parallel_rollout.py` 模块与依赖解析

## 脚本定位
- 负责从 `Benchmark` 加载任务、构建资源池、启动多进程 Worker，并协调并行 OSWorld Rollout 的完整生命周期。
- 通过 CLI 接口提供数据路径、并行度、VM 配置、资源池开关等外部参数。

## 引入模块与职责
| 模块类别 | 具体引用 | 核心职责 |
| --- | --- | --- |
| Python 标准库 | `os`, `sys`, `json`, `logging`, `signal`, `datetime`, `multiprocessing`(`Manager`, `Process`, `current_process`), `typing`, `dataclasses` | 文件/路径管理、序列化、日志与信号处理、时间戳、多进程通信、类型声明与配置结构体 |
| 第三方 | `openai`, `dotenv.load_dotenv` | OpenAI Chat Completions、加载 `.env` 配置 |
| 项目内 | `benchmark.Benchmark`, `utils.resource_manager` 系列（`ResourceManager`, `NoResourceManager`, `VMPoolResourceManager`, `HeavyResourceManager`, `VMPoolManager`）、`envs.parallel_osworld_rollout_environment.ParallelOSWorldRolloutEnvironment`, `envs.enviroment.Environment` | Benchmark 任务与评测、资源池抽象/实现、VM 池启动、并行 OSWorld 环境封装 |

## 核心结构
1. **配置结构体**：`ParallelRolloutConfig`、`AgentConfig` + `_build_agent_config` 提供 worker 端一致的 Agent 参数。
2. **信号管理**：`_register_main_signal_handlers` 记住主进程 `ResourceManager`，确保 Ctrl+C 可调用 `stop_all` 释放 VM。
3. **环境构建**：`_initialize_environment` 依据 `env_mode` 创建 `ParallelOSWorldRolloutEnvironment`，并可启用工具响应字典、列出可用工具。
4. **资源池**：`_create_resource_manager` 判断是否启用 VM 池；由整合后的 `VMPoolResourceManager` 内部启动 BaseManager 进程并托管 `VMPoolManager`，向外暴露申请/释放接口。
5. **主控流程**：`run_parallel_rollout` 完成任务入队、worker 启动与收尾评测：
   - `Benchmark.get_items()` → 转换成字典任务放入 `Manager().Queue()`
   - `Process(target=run_rollout_worker, ...)` 启动 N 个 worker
   - 汇总 `shared_results`，根据 `evaluation_metric` 调 `benchmark.evaluate`
6. **Worker 流程**：`run_rollout_worker` 主要动作：
   - 初始化环境与资源能力探测（是否支持 `initialize_with_task_config`、`allocate_resource`, `release_resource`）
   - 循环从任务队列取任务，必要时注入 task-specific env config
   - 若环境声明需要重资源，则申请 VM，执行 `_run_agent_task`，并在 finally 中归还
   - 捕获异常并写入失败结果，确保 `cleanup`/`env_close`
7. **Agent 对话链**：
   - `_run_agent_task` 负责 `env_task_init`、调用 `_run_conversation`、触发环境内评测(`evaluate`)、调用 `env_task_end`、保存对话日志。
   - `_run_conversation` 构建系统 & 用户消息，附带初始观察；循环调用 `_get_openai_client().chat.completions.create()`；若 Assistant 返回 tool call，则通过 `environment.execute_tool` 执行并记录轨迹，否则返回最终答案。
   - `_format_tool_response_content` 将工具执行结果（含文本/截图）整理成多模态消息，`_extract_final_answer` 在消息列表中回溯最终助手文本，`_save_conversation_log` 将对话 JSON 写入任务输出目录。
8. **CLI 入口**：解析 `--data_path` 等参数 → 构造 `ParallelRolloutConfig` → 调用 `run_parallel_rollout` 并记录收尾日志。

## 引用关系概览
```
Benchmark -> run_parallel_rollout -> Manager.Queue -> run_rollout_worker
run_parallel_rollout -> _create_resource_manager -> (NoResourceManager | VMPoolResourceManager)
run_rollout_worker -> _initialize_environment -> ParallelOSWorldRolloutEnvironment
run_rollout_worker -> _run_agent_task -> _run_conversation -> OpenAI API & environment.execute_tool
run_parallel_rollout -> benchmark.evaluate (使用 worker 汇总结果)
```

以上结构展示了脚本从任务加载、资源分配、环境交互到评测归档的完整依赖链，便于日后扩展新的环境模式或替换资源管理策略。
