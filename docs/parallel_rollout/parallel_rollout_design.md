# 多进程并行运行框架设计说明

## 设计目标

基于已有的`desktop_env`类和各种`Environment`环境,设计一个多进程并行运行框架,实现:

1. **N-rollout架构**: N个Rollout进程,每个包含Agent+Env
2. **VM-Manager**: 中央VM池管理器,管理M个VM实例
3. **M-VM**: M个虚拟机实例,由VM-Manager统一管理
4. **兼容性**: 与OSWorldEnvironment以及其他Environment兼容

## 架构设计

### 1. VMPoolManager (VM池管理器)

**位置**: `src/utils/resource_manager.py`

**职责**:
- 管理M个VM实例的池
- 提供VM的分配和回收接口
- 支持VM的生命周期管理(init, step, reset, stop)
- 线程安全的VM池操作

**核心方法**:
- `initialize_pool()`: 初始化M个VM实例
- `allocate_vm(worker_id)`: 为worker分配VM
- `release_vm(vm_id, worker_id)`: 释放VM回池
- `reset_vm(vm_id)`: 重置VM到快照
- `stop_vm(vm_id)`: 停止VM

**设计要点**:
- 使用`Queue`管理空闲VM
- 使用`threading.RLock`保证线程安全
- 支持VM状态跟踪(空闲/占用/错误/停止)
- 支持VM分配超时机制

### 2. RolloutWorker (Rollout工作进程)

**位置**: `src/utils/rollout_worker.py`

**职责**:
- 封装Agent+Env的组合
- 对于OSWorld环境,从VM池获取VM
- 对于其他环境,直接使用Env
- 执行任务并返回结果

**核心方法**:
- `initialize()`: 初始化Environment
- `run_task(task, output_dir)`: 执行单个任务
- `cleanup()`: 清理资源

**设计要点**:
- 支持VM池模式和非VM池模式
- 对于OSWorld+VM池: 从VMPoolManager分配VM,注入到OSWorldEnvironment
- 对于其他环境: 使用标准初始化流程
- 任务完成后自动释放VM

### 3. OSWorldEnvironment扩展

**位置**: `src/envs/osworld_environment.py`

**新增方法**:
- `_register_tools_without_desktop_env()`: 注册工具但不创建新的DesktopEnv(用于VM池模式)

**设计要点**:
- 支持外部DesktopEnv注入
- 保持向后兼容(默认行为不变)
- VM池模式下,DesktopEnv由VMPoolManager管理

### 4. Parallel Rollout Framework (主框架)

**位置**: `src/run_parallel_rollout.py`

**职责**:
- 初始化VM池(如果使用VM池模式)
- 启动N个Rollout进程
- 管理任务队列和结果收集
- 处理进程生命周期和信号

**核心流程**:
1. 解析配置参数
2. 加载任务列表
3. 初始化VM池(OSWorld+VM池模式)
4. 创建任务队列和结果列表
5. 启动N个Rollout进程
6. 等待所有任务完成
7. 清理资源(停止VM池)

## 运行流程

### OSWorld环境(VM池模式)

```
主进程
  ├─ 初始化VMPoolManager
  │   └─ 创建M个DesktopEnv实例
  │
  ├─ 启动N个Rollout进程
  │   ├─ Rollout-1: 从VM池分配VM → 初始化OSWorldEnvironment → 执行任务 → 释放VM
  │   ├─ Rollout-2: 从VM池分配VM → 初始化OSWorldEnvironment → 执行任务 → 释放VM
  │   └─ ...
  │
  └─ 等待所有任务完成 → 停止VM池
```

### OSWorld环境(非VM池模式)

```
主进程
  ├─ 启动N个Rollout进程
  │   ├─ Rollout-1: 创建DesktopEnv → 初始化OSWorldEnvironment → 执行任务
  │   ├─ Rollout-2: 创建DesktopEnv → 初始化OSWorldEnvironment → 执行任务
  │   └─ ...
  │
  └─ 等待所有任务完成
```

### 其他环境(math, web, rag等)

```
主进程
  ├─ 启动N个Rollout进程
  │   ├─ Rollout-1: 初始化MathEnvironment → 执行任务
  │   ├─ Rollout-2: 初始化WebEnvironment → 执行任务
  │   └─ ...
  │
  └─ 等待所有任务完成
```

## 兼容性设计

### 与现有代码的兼容性

1. **OSWorldEnvironment**: 
   - 保持原有接口不变
   - 新增VM池模式支持(可选)
   - 向后兼容

2. **其他Environment**:
   - 完全兼容,无需修改
   - 每个进程独立管理自己的环境

3. **AgentRunner**:
   - 复用现有的`run_osworld.py`中的AgentRunner
   - 通过动态导入避免循环依赖

### 设计原则

1. **最小侵入**: 尽量不修改现有代码
2. **可选功能**: VM池模式是可选的,默认行为不变
3. **统一接口**: 所有环境使用相同的RolloutWorker接口
4. **资源管理**: 自动管理VM生命周期,避免资源泄漏

## 关键实现细节

### 1. VM池分配机制

- 使用`Queue`实现FIFO分配
- 支持超时等待(避免无限阻塞)
- 线程安全的分配和释放

### 2. DesktopEnv注入

- VM池模式下,DesktopEnv由VMPoolManager创建
- 通过直接设置`OSWorldEnvironment._desktop_env`注入
- 跳过DesktopEnv的创建步骤,只注册工具

### 3. 进程间通信

- 使用`multiprocessing.Manager`创建共享队列和列表
- 任务队列: `manager.Queue()`
- 结果列表: `manager.list()`

### 4. 信号处理

- 主进程和子进程都注册信号处理函数
- 优雅关闭: 先发送SIGTERM,等待2秒后发送SIGKILL
- 确保VM正确释放和停止

## 使用场景

### 场景1: OSWorld大规模并行

- **需求**: 处理大量OSWorld任务,需要高并发
- **配置**: `num_rollouts=10`, `num_vms=5`, `use_vm_pool=True`
- **优势**: VM复用,提高资源利用率

### 场景2: OSWorld小规模测试

- **需求**: 快速测试少量任务
- **配置**: `num_rollouts=2`, `num_vms=1`, `use_vm_pool=False`
- **优势**: 简单直接,无需VM池管理

### 场景3: 混合环境

- **需求**: 同时处理多种环境任务
- **配置**: 分别运行不同环境的Rollout
- **优势**: 统一框架,易于管理

## 未来扩展

1. **动态VM池**: 根据负载动态调整VM数量
2. **VM健康检查**: 定期检查VM状态,自动恢复错误VM
3. **负载均衡**: 根据VM负载智能分配任务
4. **监控和统计**: 添加详细的性能监控和统计信息

