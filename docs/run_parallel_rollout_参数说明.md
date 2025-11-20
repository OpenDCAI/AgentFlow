# run_parallel_rollout.py 参数说明

本文档详细说明 `run_parallel_rollout.py` 脚本支持的所有运行参数及其含义。

## 目录

1. [命令行参数](#命令行参数)
2. [配置类参数](#配置类参数)
3. [环境配置参数 (env_kwargs)](#环境配置参数-env_kwargs)
4. [Agent 配置参数 (agent_config_dict)](#agent-配置参数-agent_config_dict)
5. [使用示例](#使用示例)

---

## 命令行参数

通过 `argparse` 定义的命令行参数：

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--data_path` | str | ✅ 是 | - | 基准测试数据文件路径（JSONL 或 JSON 格式） |
| `--num_rollouts` | int | ❌ 否 | 5 | 并行 Worker 进程数量（并行度） |
| `--num_vms` | int | ❌ 否 | 3 | VM 池大小（仅用于 OSWorld 环境） |
| `--env_mode` | str | ❌ 否 | "osworld" | 环境模式（如 "osworld", "math", "web" 等） |
| `--output_dir` | str | ❌ 否 | "results" | 结果输出目录 |
| `--use_resource_pool` | flag | ❌ 否 | False | 是否使用资源池（仅用于 OSWorld） |

### 命令行参数详细说明

#### `--data_path`
- **类型**: 字符串
- **必需**: 是
- **说明**: 指向基准测试数据文件的路径，支持 JSONL 或 JSON 格式
- **示例**: `--data_path data/osworld_examples.jsonl`

#### `--num_rollouts`
- **类型**: 整数
- **必需**: 否
- **默认值**: 5
- **说明**: 并行执行的 Worker 进程数量。建议配置为 VM 数量的 2-3 倍以获得最佳性能
- **推荐值**: 
  - 成本优先: `num_rollouts = 5-10 × num_vms`
  - 均衡配置: `num_rollouts = 2-3 × num_vms`
  - 性能优先: `num_rollouts = num_vms` (1:1 比例)
- **示例**: `--num_rollouts 10`

#### `--num_vms`
- **类型**: 整数
- **必需**: 否
- **默认值**: 3
- **说明**: VM 池中虚拟机的数量（仅用于 OSWorld 环境）。每个 VM 可以被多个 Worker 共享
- **示例**: `--num_vms 5`

#### `--env_mode`
- **类型**: 字符串
- **必需**: 否
- **默认值**: "osworld"
- **说明**: 指定环境类型。不同环境类型决定是否启用重资产管理：
  - `"osworld"`: 桌面自动化环境（需要 VM 池）
  - `"math"`: 数学计算环境（无需重资产）
  - `"web"`: 网络搜索环境（无需重资产）
  - `"rag"`: RAG 检索环境（无需重资产）
- **示例**: `--env_mode osworld`

#### `--output_dir`
- **类型**: 字符串
- **必需**: 否
- **默认值**: "results"
- **说明**: 任务执行结果、轨迹数据、录屏视频等的输出目录
- **示例**: `--output_dir results/parallel_rollout_20240101`

#### `--use_resource_pool`
- **类型**: 标志（布尔值）
- **必需**: 否
- **默认值**: False
- **说明**: 是否启用资源池模式。当设置为 True 时，OSWorld 环境会使用 VM 池管理多个 VM 实例，实现资源共享
- **注意**: 仅对 OSWorld 环境有效
- **示例**: `--use_resource_pool`

---

## 配置类参数

`ParallelRolloutConfig` 数据类中的配置项（可通过代码直接设置）：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `num_rollouts` | int | 5 | 并行度（Worker 数量） |
| `num_vms` | int | 3 | VM 池大小（仅用于 OSWorld） |
| `env_mode` | str | "osworld" | 环境模式 |
| `env_kwargs` | Dict[str, Any] | {} | 环境配置参数字典（见下文） |
| `agent_config_dict` | Dict[str, Any] | {} | Agent 配置参数字典（见下文） |
| `output_dir` | str | "results" | 输出目录 |
| `use_resource_pool` | bool | True | 是否使用资源池 |

---

## 环境配置参数 (env_kwargs)

这些参数通过 `env_kwargs` 字典传递给环境初始化。对于 OSWorld 环境，以下参数会被用于创建 VM 池：

### OSWorld 环境参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `provider_name` | str | "vmware" | VM 提供商名称。可选值: `"vmware"`, `"virtualbox"`, `"aws"`, `"gcp"`, `"azure"`, `"aliyun"`, `"volcengine"`, `"docker"` |
| `path_to_vm` | str | None | VM 镜像路径。如果为 None，将根据 provider 自动分配 |
| `snapshot_name` | str | "init_state" | VM 快照名称（用于重置 VM 状态） |
| `action_space` | str | "computer_13" | 动作空间类型。可选值: `"computer_13"`, `"pyautogui"`, `"claude_computer_use"` |
| `screen_width` | int | 1920 | 屏幕宽度（像素） |
| `screen_height` | int | 1080 | 屏幕高度（像素） |
| `headless` | bool | False | 是否以无头模式运行（不显示 GUI） |
| `require_a11y_tree` | bool | True | 是否需要辅助功能树（accessibility tree） |
| `require_terminal` | bool | False | 是否需要终端访问 |
| `os_type` | str | "Ubuntu" | 操作系统类型。可选值: `"Ubuntu"`, `"Windows"` 等 |
| `client_password` | str | "password" | VM 客户端密码（用于 sudo 操作） |
| `region` | str | None | 区域（用于云服务提供商，如 AWS、Azure 等） |
| `observation_type` | str | "screenshot_a11y_tree" | 观察类型。可选值: `"screenshot"`, `"a11y_tree"`, `"screenshot_a11y_tree"`, `"som"` |
| `sleep_after_execution` | float | 2.0 | 每次动作执行后的等待时间（秒） |
| `enable_recording` | bool | True | 是否启用屏幕录制 |

### 参数详细说明

#### `provider_name`
- **说明**: VM 提供商，决定使用哪种虚拟化技术
- **vmware**: 本地 VMware Workstation/Player
- **virtualbox**: 本地 VirtualBox
- **aws/gcp/azure/aliyun/volcengine**: 云服务提供商
- **docker**: Docker 容器

#### `action_space`
- **computer_13**: 结构化动作空间（13 种动作类型：鼠标移动、点击、键盘输入等）
- **pyautogui**: Python 脚本执行模式（直接执行 pyautogui 命令）
- **claude_computer_use**: Claude Computer Use 格式

#### `observation_type`
- **screenshot**: 仅截图
- **a11y_tree**: 仅辅助功能树
- **screenshot_a11y_tree**: 截图 + 辅助功能树（推荐）
- **som**: Screen Object Model

---

## Agent 配置参数 (agent_config_dict)

这些参数通过 `agent_config_dict` 字典传递给 Agent 配置：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_name` | str | "gpt-4" | LLM 模型名称（如 "gpt-4", "gpt-3.5-turbo" 等） |
| `evaluation_metric` | str | "exact_match" | Benchmark 评测指标。可选值: `"exact_match"`, `"f1_score"`, `"similarity"`, `"contains_answer"`, `"numeric_match"`, `"llm_judgement"` |
| `max_turns` | int | 50 | Agent 最大对话轮数 |
| `max_retries` | int | 3 | 工具调用失败时的最大重试次数 |
| `save_results` | bool | True | 是否保存结果到文件 |
| `evaluate_results` | bool | True | 是否执行结果评估 |

### 评测指标说明

#### `evaluation_metric`
- **exact_match**: 精确匹配（字符串完全相等）
- **f1_score**: F1 分数（用于文本相似度）
- **similarity**: 字符串相似度（基于编辑距离等）
- **contains_answer**: 包含答案检查（预测是否包含标准答案）
- **numeric_match**: 数值匹配（提取数值进行比较）
- **llm_judgement**: LLM 判断（使用 LLM 评估答案正确性）

---

## 使用示例

### 示例 1: 基本用法

```bash
python src/run_parallel_rollout.py \
    --data_path data/osworld_examples.jsonl \
    --num_rollouts 10 \
    --num_vms 5 \
    --use_resource_pool
```

### 示例 2: 自定义环境配置（通过代码）

```python
from src.run_parallel_rollout import run_parallel_rollout, ParallelRolloutConfig
from benchmark import Benchmark

# 加载 Benchmark
benchmark = Benchmark(data_path="data/osworld_examples.jsonl")

# 创建配置
config = ParallelRolloutConfig(
    num_rollouts=10,
    num_vms=5,
    env_mode="osworld",
    output_dir="results/custom_run",
    use_resource_pool=True,
    env_kwargs={
        # VM 配置
        "provider_name": "vmware",
        "path_to_vm": "/path/to/vm.vmx",
        "snapshot_name": "clean_desktop",
        "action_space": "computer_13",
        "observation_type": "screenshot_a11y_tree",
        "screen_width": 1920,
        "screen_height": 1080,
        "headless": False,
        "require_a11y_tree": True,
        "os_type": "Ubuntu",
        "client_password": "your_password",
        
        # 运行时配置
        "sleep_after_execution": 2.0,
        "enable_recording": True,
    },
    agent_config_dict={
        "model_name": "gpt-4",
        "evaluation_metric": "exact_match",
        "max_turns": 50,
        "max_retries": 3,
    }
)

# 运行
results = run_parallel_rollout(config, benchmark)
```

### 示例 3: 成本优先配置

```bash
python src/run_parallel_rollout.py \
    --data_path data/large_dataset.jsonl \
    --num_rollouts 20 \
    --num_vms 2 \
    --use_resource_pool
```

**说明**: Worker 数量是 VM 数量的 10 倍，最大化 VM 利用率，降低成本。

### 示例 4: 性能优先配置

```bash
python src/run_parallel_rollout.py \
    --data_path data/critical_tasks.jsonl \
    --num_rollouts 10 \
    --num_vms 10 \
    --use_resource_pool
```

**说明**: Worker 和 VM 数量 1:1，零分配延迟，适合关键实时任务。

### 示例 5: 均衡配置（推荐）

```bash
python src/run_parallel_rollout.py \
    --data_path data/standard_tasks.jsonl \
    --num_rollouts 15 \
    --num_vms 5 \
    --use_resource_pool
```

**说明**: Worker 数量是 VM 数量的 3 倍，平衡成本和性能。

---

## 配置建议

### Worker 与 VM 比例

根据任务需求选择合适的比例：

1. **成本优先**: `num_rollouts = 5-10 × num_vms`
   - 最小化 VM 成本
   - 分配延迟较大（30-60秒）
   - VM 利用率极高（95-99%）

2. **均衡配置**: `num_rollouts = 2-3 × num_vms`（推荐）
   - 成本和性能平衡
   - 分配延迟可接受（10-20秒）
   - VM 利用率高（80-90%）

3. **性能优先**: `num_rollouts = num_vms` (1:1)
   - 零分配延迟
   - 资源利用率中等（40-60%）
   - 成本较高

### 资源分配超时

资源分配超时时间建议：
- **推荐**: 60-120 秒
- **计算公式**: `timeout = task_duration × (num_rollouts / num_vms)`

---

## 注意事项

1. **环境类型决定重资产**: 只有 `env_mode="osworld"` 时才会创建 VM 池，其他环境使用 `NoResourceManager`
2. **Task 级别的配置**: 某些配置（如 `snapshot`, `proxy`, `fixed_ip`）可以在 Task 的 `env_config` 中设置，覆盖默认值
3. **启动时参数**: `action_space` 和 `observation_type` 是启动时参数，所有任务共享，不能在 Task 中单独设置
4. **资源释放**: 确保 Worker 进程正确释放资源，避免资源泄漏

---

## 相关文档

- [FINAL_ARCHITECTURE_DOC.md](../src/todo/FINAL_ARCHITECTURE_DOC.md) - 完整架构文档
- [task_config_fields_flow.md](./task_config_fields_flow.md) - Task 配置字段流向说明

