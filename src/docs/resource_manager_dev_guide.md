## ResourceManager 开发指引

本指引总结了 `src/utils/resource_manager.py` 的关键结构，便于在并行 Rollout 与 VM 池相关的开发中快速定位扩展点。

### 模块分层
- `ResourceManager` / `HeavyResourceManager`：抽象接口，`ParallelOSWorldRolloutEnvironment` 仅依赖这些方法（`initialize`、`allocate`、`release`、`stop_all`）。实现新资源类型时只需遵守该接口。
- `VMPoolManager`：真正负责 VM 元数据与生命周期，运行在由 `BaseManager` 托管的独立进程，提供线程安全的 `initialize_pool`、`allocate_vm`、`release_vm` 等方法。
- `VMPoolResourceManager`：面向 Worker 的入口。内部自动：
  1. 标准化 `pool_config`（`_normalize_pool_config`）；
  2. 启动 `_VMPoolManagerBase` 进程并构造 `VMPoolManager`；
  3. 在 `allocate()` 中调用 `_build_desktop_env_params()`，实例化带 `remote_*` 参数的 `DesktopEnv`（Attach 模式）。

### 常用扩展点
1. **新增 Provider 字段**  
   - 在 `_normalize_pool_config` 的 `known_keys` 与返回字典中加入字段，并确保 `VMPoolManager.__init__` 接收该参数。
   - 如果该字段也需要透传给 DesktopEnv，在 `_build_desktop_env_params` 中同步处理。

2. **自定义 DesktopEnv 默认行为**  
   - `_build_desktop_env_params` 负责合并 VM 池提供的 config 与 `allocate()` 的 overrides，可在此集中处理布尔/路径等校验逻辑。

3. **调试 VM 分配流程**  
   - `VMPoolManager.get_stats()` 暴露池状态，`VMPoolResourceManager.get_status()` 直接返回该信息。建议在问题排查时日志输出 `json.dumps(get_status(), indent=2, ensure_ascii=False)`。
   - 需要快速定位占用来源，可查看 `vm_entry.allocated_to`（worker ID）以及 `worker_instance_events.jsonl`。

### 开发建议
- **保持单一入口**：外部调用统一使用 `VMPoolResourceManager`，切勿在 Worker 侧直接持有 `VMPoolManager` 引用，以防跨进程序列化问题。
- **善用 helper**：`_ensure_bool`、`_normalize_pool_config`、`_build_desktop_env_params` 将重复逻辑集中处理，新增配置时务必先考虑是否可以在 helper 中解决。
- **优雅关闭**：主进程的信号处理会调用 `stop_all()`，确保扩展逻辑中不要吞掉异常，否则 VM 进程可能残留。

通过以上分层思路和扩展指南，可以在保持核心接口稳定的前提下，快速迭代新的资源管理需求。***

