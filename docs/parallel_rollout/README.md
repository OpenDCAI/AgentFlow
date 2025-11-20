# 多进程并行运行框架文档

本目录包含多进程并行运行框架的完整文档。

## 文档列表

### 1. [使用指南](parallel_rollout_framework.md)
详细的使用说明和示例,包括:
- 架构概述
- 使用方式(OSWorld VM池模式、非VM池模式、其他环境)
- 参数说明
- 工作流程
- 性能优化建议
- 故障处理
- 使用示例

### 2. [设计说明](parallel_rollout_design.md)
框架的设计思路和实现细节,包括:
- 设计目标
- 架构设计(各组件职责)
- 运行流程
- 兼容性设计
- 关键实现细节
- 使用场景
- 未来扩展

## 快速开始

### OSWorld环境(VM池模式)

```bash
python src/run_parallel_rollout.py \
    --mode osworld \
    --data path/to/benchmark.jsonl \
    --num-rollouts 5 \
    --num-vms 3 \
    --use-vm-pool \
    --path-to-vm /path/to/vm.vmx \
    --provider-name vmware \
    --action-space computer_13
```

### 其他环境

```bash
python src/run_parallel_rollout.py \
    --mode math \
    --data path/to/benchmark.jsonl \
    --num-rollouts 5 \
    --model gpt-4.1-2025-04-14
```

## 相关代码文件

- `src/utils/resource_manager.py` - 资源管理抽象与 VM 池实现
- `src/utils/rollout_worker.py` - Rollout工作进程
- `src/run_parallel_rollout.py` - 主框架入口
- `src/envs/osworld_environment.py` - OSWorld环境(已扩展支持VM池)

## 架构图

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

## 更多信息

详细的使用说明请参考 [使用指南](parallel_rollout_framework.md),设计细节请参考 [设计说明](parallel_rollout_design.md)。

