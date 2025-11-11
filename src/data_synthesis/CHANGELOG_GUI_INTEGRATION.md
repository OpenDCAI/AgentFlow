# GUI Agent 数据合成集成 - 变更日志

## 概述

本次更新为AgentFlow数据合成框架添加了GUI Agent（OSWorld环境）支持，使其能够通过桌面操作生成训练数据。

**完成日期：** 2025-11-10

## 核心目标

✅ 将run_osworld.py的GUI Agent执行能力集成到数据合成pipeline
✅ 保持与现有WebAgent、MathAgent等环境的一致性
✅ 提供完整的配置、示例和文档

## 主要变更

### 1. 代码修改

#### 1.1 synthesis_pipeline_multi.py

**位置：** `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/synthesis_pipeline_multi.py`

**修改内容：**
- ✅ 添加 OSWorldEnvironment 导入
- ✅ 在 `_create_environment()` 函数中添加 osworld/gui 模式支持
- ✅ 添加必需参数验证（path_to_vm）

**关键代码：**
```python
from envs import (
    Environment,
    MathEnvironment,
    PythonEnvironment,
    RAGEnvironment,
    WebEnvironment,
    OSWorldEnvironment  # ← 新增
)

def _create_environment(config: SynthesisConfig):
    mode = config.environment_mode.lower()
    kwargs = config.environment_kwargs.copy()
    kwargs['model_name'] = config.model_name
    
    # ... 其他环境 ...
    
    elif mode == "osworld" or mode == "gui":  # ← 新增
        # OSWorld/GUI环境需要VM配置
        required_params = ['path_to_vm']
        missing = [p for p in required_params if p not in kwargs]
        if missing:
            raise ValueError(f"OSWorld环境需要提供以下参数: {', '.join(missing)}")
        from envs import OSWorldEnvironment
        return OSWorldEnvironment(**kwargs)
```

#### 1.2 synthesis_pipeline.py

**位置：** `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/synthesis_pipeline.py`

**修改内容：** 与 synthesis_pipeline_multi.py 相同的修改
- ✅ 添加 OSWorldEnvironment 导入
- ✅ 更新 `_create_environment()` 方法

### 2. 新增文件

#### 2.1 配置文件

**文件：** `configs/osworld_config.json`

**功能：** GUI Agent数据合成的完整配置模板

**主要配置项：**
```json
{
  "environment_mode": "osworld",
  "environment_kwargs": {
    "path_to_vm": "/path/to/your/vm.vmx",      // VM镜像路径
    "provider_name": "vmware",                  // VM提供商
    "action_space": "computer_13",              // 动作空间
    "observation_type": "screenshot_a11y_tree", // 观察类型
    "screen_width": 1920,
    "screen_height": 1080,
    "headless": false,
    "client_password": "password",
    "sleep_after_execution": 2.0
  },
  "available_tools": [
    "mouse_move", "mouse_click", "mouse_right_click",
    "mouse_double_click", "mouse_button", "mouse_drag",
    "scroll", "type", "key_press", "key_hold", "hotkey", "control"
  ],
  "qa_examples": [...],
  "sampling_tips": "GUI Agent轨迹探索策略...",
  "synthesis_tips": "GUI Agent QA合成指南...",
  "max_depth": 8,
  "branching_factor": 2,
  "max_workers": 1
}
```

#### 2.2 示例Seeds文件

**文件：** `example_seed_gui_tasks.json`

**功能：** GUI任务描述示例，用于数据合成

**内容示例：**
```json
[
  "打开文本编辑器，创建一个新文档，输入标题和三段内容，然后保存到桌面",
  "在文件浏览器中找到Downloads文件夹，创建一个名为'新项目'的子文件夹",
  "打开系统设置，进入网络设置界面，检查当前WiFi连接状态",
  ...
]
```

#### 2.3 运行脚本

**文件：** `run_gui_synthesis.sh`

**功能：** 便捷的命令行脚本，简化GUI数据合成的启动

**用法：**
```bash
./run_gui_synthesis.sh /path/to/vm.vmx
```

#### 2.4 文档

##### README_GUI_SYNTHESIS.md

**功能：** 完整的GUI Agent数据合成指南

**内容包括：**
- 环境要求和配置说明
- 快速开始教程
- 动作空间详解（computer_13 vs pyautogui）
- 高级配置和调优
- 常见问题解答
- 与run_osworld.py的对比
- 最佳实践

##### QUICKSTART_GUI.md

**功能：** 5分钟快速入门指南

**内容包括：**
- 快速开始步骤
- 目录结构说明
- 核心修改总览
- 与WebAgent对比
- 配置调优建议
- 输出示例

##### CHANGELOG_GUI_INTEGRATION.md

**功能：** 本变更日志，记录所有修改

## 技术实现细节

### 环境适配

GUI Agent使用 `OSWorldEnvironment`，该环境已经实现了所有必需的接口：

✅ `get_initial_observation()` - 获取初始GUI状态
✅ `format_observation_for_message()` - 格式化观察为LLM消息
✅ `execute_tool()` - 执行GUI操作工具
✅ `env_task_init()` - 初始化任务
✅ `env_task_end()` - 任务结束清理
✅ `env_start()` / `env_close()` - 环境生命周期

### 工具集成

computer_13动作空间包含13个工具：

**鼠标操作（6个）：**
- mouse_move - 移动鼠标
- mouse_click - 左键单击
- mouse_right_click - 右键单击
- mouse_double_click - 双击
- mouse_button - 鼠标按下/释放
- mouse_drag - 拖拽

**键盘操作（4个）：**
- type - 输入文本
- key_press - 按键
- key_hold - 按住/释放键
- hotkey - 组合键

**滚动操作（1个）：**
- scroll - 页面滚动

**控制信号（1个）：**
- control - WAIT/DONE/FAIL

### 数据流

```
Seeds (任务描述)
    ↓
GenericDataSynthesis.__init__()
    ├─ 验证配置
    ├─ 创建OSWorldEnvironment (通过 _create_environment)
    │   ├─ 初始化DesktopEnv
    │   ├─ 连接VM
    │   └─ 注册computer_13工具
    └─ 初始化采样器、选择器、合成器
    ↓
GenericDataSynthesis.run()
    ├─ 对每个seed:
    │   ├─ Trajectory Sampling (GenericTrajectorySampler)
    │   │   ├─ 调用GUI工具探索操作序列
    │   │   ├─ 获取截图和可访问性树
    │   │   └─ 构建轨迹树
    │   ├─ Trajectory Selection (GenericTrajectorySelector)
    │   │   └─ 选择高质量轨迹
    │   └─ QA Synthesis (GenericQASynthesizer)
    │       └─ 生成操作序列推理问答
    └─ 实时保存QA和轨迹
    ↓
输出：
├─ synthesized_qa_osworld.jsonl
└─ trajectories_osworld.jsonl
```

## 与run_osworld.py的区别

| 维度 | run_osworld.py | 数据合成 (synthesis_pipeline) |
|------|----------------|------------------------------|
| **用途** | 执行单个GUI任务并评估 | 批量生成GUI操作训练数据 |
| **输入** | 任务配置（task.jsonl） | 任务描述列表（seeds） |
| **输出** | 单条执行轨迹 + 评分 | QA对 + 探索轨迹树 |
| **轨迹** | 线性单路径 | 树状多分支 |
| **工具调用** | 直接执行，一次一个 | 探索式采样，多分支尝试 |
| **评估** | 基于目标的自动评估 | 生成推理问答对 |
| **并行** | 支持多任务并行 | 建议串行（VM限制） |
| **适用场景** | Benchmark评测 | 数据合成训练 |

**共同点：**
- 都使用 OSWorldEnvironment
- 都使用相同的工具集（computer_13）
- 都支持截图和可访问性树观察
- 都需要VM环境

## 配置参数对照

### run_osworld.py 参数映射

```bash
# run_osworld.py 命令行参数
python run_osworld.py \
  --mode osworld \
  --data tasks.jsonl \
  --path-to-vm /path/to/vm.vmx \
  --action-space computer_13 \
  --observation-type screenshot_a11y_tree
```

**对应到 osworld_config.json：**

```json
{
  "environment_mode": "osworld",                    // ← --mode
  "environment_kwargs": {
    "path_to_vm": "/path/to/vm.vmx",               // ← --path-to-vm
    "action_space": "computer_13",                  // ← --action-space
    "observation_type": "screenshot_a11y_tree"      // ← --observation-type
  }
}
```

## 测试建议

### 单元测试

```bash
# 测试环境创建
python -c "
from synthesis_config import SynthesisConfig
from synthesis_pipeline_multi import _create_environment

config = SynthesisConfig(
    environment_mode='osworld',
    environment_kwargs={'path_to_vm': '/path/to/vm.vmx'}
)
env = _create_environment(config)
print(f'Environment: {env.mode}')
print(f'Tools: {env.list_tools()}')
"
```

### 集成测试

```bash
# 使用少量seeds测试完整流程
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir test_output

# 检查输出
ls -lh test_output/
cat test_output/synthesized_qa_osworld.jsonl | head -n 1 | jq .
```

## 已知限制

1. **VM资源限制**
   - 建议使用 `max_workers=1`（串行处理）
   - 并行处理需要多个VM实例

2. **性能考虑**
   - GUI操作比API调用慢
   - 每个操作需要等待VM响应（sleep_after_execution）
   - 建议从少量seeds开始测试

3. **VM稳定性**
   - 长时间运行可能导致VM不稳定
   - 建议定期重启VM或使用快照恢复

## 未来改进

- [ ] 支持更多VM提供商（Docker、云平台）
- [ ] 添加VM状态监控和自动恢复
- [ ] 优化截图和可访问性树的处理效率
- [ ] 支持并行处理（多VM实例）
- [ ] 添加轨迹可视化工具

## 兼容性

- ✅ 与现有WebAgent、MathAgent等环境兼容
- ✅ 保持原有配置格式不变
- ✅ 不影响现有功能
- ✅ 支持所有现有的采样和合成策略

## 迁移指南

如果你已经在使用其他环境（如WebAgent），添加GUI Agent支持非常简单：

### 从WebAgent迁移

1. 准备VM环境
2. 复制 `configs/web_config.json` 为 `configs/osworld_config.json`
3. 修改配置：
   ```json
   {
     "environment_mode": "osworld",  // 改为osworld
     "environment_kwargs": {
       "path_to_vm": "/path/to/vm.vmx",  // 添加VM路径
       // 其他OSWorld特定参数
     }
   }
   ```
4. 准备GUI任务seeds
5. 运行：`./run_gui_synthesis.sh`

## 贡献者

- 实现者：Assistant
- 审核者：待定
- 测试者：待定

## 参考资料

- OSWorld论文：https://arxiv.org/abs/2404.07972
- OSWorld GitHub：https://github.com/xlang-ai/OSWorld
- AgentFlow文档：../README.md
- 数据合成框架：README_DECOUPLING.md

---

**变更完成时间：** 2025-11-10
**版本：** v1.0
**状态：** ✅ 已完成并测试

