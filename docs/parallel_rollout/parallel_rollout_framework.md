# 多进程并行运行框架使用指南

## 架构概述

本框架实现了 **N-rollout -> VM-Manager -> M-VM** 架构:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Rollout-1   │     │ Rollout-2   │ ... │ Rollout-N   │
│ Agent+Env   │     │ Agent+Env   │     │ Agent+Env   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                     │
       └───────────────────┴─────────────────────┘
                          │
                  ┌────────▼────────┐
                  │   VM-Manager    │
                  │  (VMPoolManager)│
                  └────────┬────────┘
                          │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐      ┌────▼────┐
   │  VM-1   │        │  VM-2   │ ...  │  VM-M   │
   └─────────┘        └─────────┘      └─────────┘
```

### 核心组件

1. **VMPoolManager** (`src/utils/resource_manager.py`)
   - 管理M个VM实例的池
   - 支持VM的初始化、分配、回收、重置和停止
   - 线程安全的VM池管理

2. **RolloutWorker** (`src/utils/rollout_worker.py`)
   - 封装Agent+Env的组合
   - 对于OSWorld环境,从VM池获取VM
   - 对于其他环境,直接使用Env

3. **Parallel Rollout Framework** (`src/run_parallel_rollout.py`)
   - 主框架,协调N个Rollout进程
   - 管理任务队列和结果收集

## 使用方式

### 1. OSWorld环境(使用VM池)

```bash
python src/run_parallel_rollout.py \
    --mode osworld \
    --data path/to/benchmark.jsonl \
    --num-rollouts 5 \
    --num-vms 3 \
    --use-vm-pool \
    --path-to-vm /path/to/vm.vmx \
    --provider-name vmware \
    --action-space computer_13 \
    --screen-width 1920 \
    --screen-height 1080 \
    --model gpt-4.1-2025-04-14 \
    --output-dir results
```

**特点:**
- N=5个Rollout进程共享M=3个VM
- 每个Rollout进程从VM池获取VM,执行任务后释放
- VM在释放前会重置到快照状态

### 2. OSWorld环境(非VM池模式)

```bash
python src/run_parallel_rollout.py \
    --mode osworld \
    --data path/to/benchmark.jsonl \
    --num-rollouts 5 \
    --path-to-vm /path/to/vm.vmx \
    --provider-name vmware \
    --model gpt-4.1-2025-04-14 \
    --output-dir results
```

**特点:**
- 每个Rollout进程独立管理自己的VM
- 不共享VM池

### 3. 其他环境(math, web, rag等)

```bash
python src/run_parallel_rollout.py \
    --mode math \
    --data path/to/benchmark.jsonl \
    --num-rollouts 5 \
    --model gpt-4.1-2025-04-14 \
    --output-dir results
```

**特点:**
- 不涉及VM池
- 每个Rollout进程独立管理自己的环境

## 参数说明

### 基本参数

- `--mode`: 环境模式 (`osworld`, `math`, `py`, `rag`, `web`)
- `--data`: 基准测试数据路径 (JSON或JSONL格式)
- `--num-rollouts`: Rollout进程数量 (N, 默认5)
- `--num-vms`: VM池大小 (M, 仅OSWorld, 默认3)
- `--use-vm-pool`: 使用VM池模式 (仅OSWorld)
- `--output-dir`: 输出目录 (默认 `results`)

### Agent配置

- `--model`: OpenAI模型名称 (默认 `gpt-4.1-2025-04-14`)
- `--max-turns`: 最大对话轮数 (默认 100)
- `--max-retries`: 每轮最大重试次数 (默认 3)

### OSWorld参数

- `--path-to-vm`: VM镜像路径 (OSWorld必需)
- `--provider-name`: VM提供商 (`vmware`, `virtualbox`, `aws`, etc.)
- `--action-space`: 动作空间 (`computer_13`, `pyautogui`)
- `--screen-width`: 屏幕宽度 (默认 1920)
- `--screen-height`: 屏幕高度 (默认 1080)
- `--headless`: 无头模式
- `--snapshot-name`: VM快照名称
- `--client-password`: VM客户端密码 (默认 `password`)

## 工作流程

### VM池模式工作流程

1. **初始化阶段**
   - 创建VMPoolManager
   - 初始化M个VM实例
   - 将VM放入空闲队列

2. **Rollout进程启动**
   - 启动N个Rollout进程
   - 每个进程从VM池分配VM
   - 如果VM池为空,等待直到有VM可用

3. **任务执行**
   - Rollout进程从任务队列获取任务
   - 使用分配的VM执行任务
   - 任务完成后释放VM回池

4. **VM回收**
   - VM释放前重置到快照状态
   - 放回空闲队列供其他进程使用

5. **清理阶段**
   - 所有任务完成后停止所有VM
   - 清理资源

### 非VM池模式工作流程

1. **Rollout进程启动**
   - 启动N个Rollout进程
   - 每个进程独立初始化自己的环境

2. **任务执行**
   - Rollout进程从任务队列获取任务
   - 使用自己的环境执行任务

3. **清理阶段**
   - 所有任务完成后关闭环境
   - 清理资源

## 兼容性说明

### OSWorld环境

- **VM池模式**: 多个Rollout进程共享VM池,提高资源利用率
- **非VM池模式**: 每个进程独立VM,与原有`run_osworld.py`行为一致

### 其他环境

- **完全兼容**: math, web, rag等环境无需修改
- **独立运行**: 每个Rollout进程独立管理自己的环境
- **无VM依赖**: 不涉及VM池管理

## 性能优化建议

1. **VM池大小**: 建议 `num_vms < num_rollouts`, 通过VM复用提高利用率
2. **Rollout数量**: 根据CPU核心数和任务数量调整
3. **快照管理**: 使用快照可以快速重置VM状态,提高任务切换效率

## 故障处理

1. **VM分配失败**: 如果VM池中所有VM都被占用,进程会等待直到有VM可用
2. **VM错误**: 如果VM进入错误状态,会被标记为不可用,不影响其他VM
3. **进程崩溃**: 主进程会监控子进程状态,如果进程崩溃会记录日志

## 示例

### 示例1: OSWorld小规模并行

```bash
# 3个Rollout进程共享2个VM
python src/run_parallel_rollout.py \
    --mode osworld \
    --data benchmarks/osworld_tasks.jsonl \
    --num-rollouts 3 \
    --num-vms 2 \
    --use-vm-pool \
    --path-to-vm /vms/ubuntu.vmx \
    --provider-name vmware \
    --action-space computer_13
```

### 示例2: 大规模并行(非OSWorld)

```bash
# 10个Rollout进程并行处理数学任务
python src/run_parallel_rollout.py \
    --mode math \
    --data benchmarks/math_tasks.jsonl \
    --num-rollouts 10 \
    --model gpt-4.1-2025-04-14
```

## 注意事项

1. **VM池模式仅适用于OSWorld**: 其他环境不支持VM池
2. **快照要求**: 使用VM池模式时,建议配置快照以便快速重置
3. **资源限制**: 注意系统资源限制(内存、CPU、VM数量)
4. **网络配置**: 如果使用云服务提供商,注意网络配置和区域设置

