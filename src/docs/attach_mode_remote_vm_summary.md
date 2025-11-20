## Attach 模式远程 VM 连接综述

### 背景
- 并行 rollout 采用分布式 Worker 架构：Manager 仅维护 VM 元数据；Worker 负责真实交互。
- `ParallelOSWorldRolloutEnvironment` 通过 `_desktop_env` 与 VM 交互；在 Attach 模式下，该对象在 Worker 本地实例化，但连接远程 VM。

### 关键组件
- `VMPoolManager`：初始化/维护 VM 池，记录 IP、端口、快照等，只存储元数据。
- `VMPoolResourceManager.allocate()`：向池请求 `vm_id` 与连接信息，然后用这些信息初始化 `DesktopEnv`（Attach 参数 `remote_*`）。
- `DesktopEnv`：检测到 `remote_ip` 时触发 `_attach_to_remote_vm()`，直接连远端控制器，跳过本地启动；`close()` 仅断开本地控制器，不会关机。
- `ParallelOSWorldRolloutEnvironment._set_desktop_env()`：写入 `_desktop_env`、注册工具、更新状态。

### Attach 模式工作流
1. Worker 调 `allocate_resource()` → `resource_manager.allocate()`。
2. `VMPoolManager` 从空闲队列取 VM，返回 `(vm_id, connection_info)`。
3. Worker 使用连接信息实例化 `DesktopEnv(remote_ip=..., remote_port=...)`。
4. `_set_desktop_env()` 注入环境，工具注册后即可 `reset/step/get_obs`。
5. `release_resource()`：先 `DesktopEnv.close()`（释放本地连接），再通知 VM 池重置+归还。

### 手动注入场景
- 若未使用资源池，可自行创建 `DesktopEnv(remote_ip=..., remote_port=...)` 后调用 `env.attach_desktop_env(desktop_env, vm_id="external")`，同样触发工具注册。

### 常见注意事项
- Worker 进程必须在成功 `allocate_resource()` 后才能调用 `reset/step`，否则 `_desktop_env` 仍为 `None`。
- Attach 模式不负责 VM 生命周期，真正的快照恢复/停机由 VM 池完成。
- 释放 VM 前务必关闭本地 `DesktopEnv`，避免句柄泄漏；即便关闭失败也要继续归还 VM，以免占用。
- 若远端 VM 重置导致 IP 改变，`DesktopEnv.reset()` 会检测并重新配置控制器，必要时重新拉取端口信息。

### 故障排查提示
- `_desktop_env is None`：确认 `allocate_resource()` 是否成功以及 `resource_manager.allocate()` 是否返回。
- 无法连接远程 VM：检查 VM 池记录的 IP/端口是否可达，或确认防火墙/安全组配置。
- 释放失败：日志关注 `release_resource` 流程，确保 `vm_id` 与 `worker_id` 匹配；必要时查看 `worker_instance_events.jsonl`。

