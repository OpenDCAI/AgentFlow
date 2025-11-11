# GUI Agent 数据合成 - 快速开始

本文档提供GUI Agent（OSWorld）数据合成的快速入门指南。

## 5分钟快速开始

### 1. 准备VM环境

确保你有一个可用的VM镜像（VMware或VirtualBox）：

```bash
# 示例：VMware的Ubuntu镜像
VM_PATH="/home/user/VMs/ubuntu.vmx"
```

### 2. 修改配置文件

编辑 `configs/osworld_config.json`，只需修改VM路径：

```json
{
  "environment_kwargs": {
    "path_to_vm": "/home/user/VMs/ubuntu.vmx"  // 👈 修改这里
  }
}
```

### 3. 运行数据合成

**方式1: 使用脚本（推荐）**

```bash
cd /home/a1/sdb/tzw/AgentFlow/src/data_synthesis
./run_gui_synthesis.sh /home/user/VMs/ubuntu.vmx
```

**方式2: 直接运行Python**

```bash
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/gui
```

### 4. 查看结果

```bash
# 生成的QA对
cat synthesis_results/gui/synthesized_qa_osworld.jsonl | jq .

# 轨迹数据
cat synthesis_results/gui/trajectories_osworld.jsonl | jq .
```

## 目录结构

```
data_synthesis/
├── configs/
│   ├── osworld_config.json          # ✨ GUI Agent配置（新增）
│   ├── web_config.json              # WebAgent配置
│   └── ...
├── example_seed_gui_tasks.json      # ✨ GUI任务示例（新增）
├── synthesis_pipeline_multi.py      # ✅ 已支持OSWorld
├── synthesis_pipeline.py            # ✅ 已支持OSWorld
├── run_gui_synthesis.sh             # ✨ GUI合成脚本（新增）
├── README_GUI_SYNTHESIS.md          # ✨ GUI详细文档（新增）
└── QUICKSTART_GUI.md                # ✨ 本文档（新增）
```

## 核心修改说明

### 1. 环境支持（已完成）

**修改文件：**
- `synthesis_pipeline_multi.py`
- `synthesis_pipeline.py`

**修改内容：**
```python
def _create_environment(config: SynthesisConfig):
    # ...
    elif mode == "osworld" or mode == "gui":
        # OSWorld/GUI环境需要VM配置
        required_params = ['path_to_vm']
        missing = [p for p in required_params if p not in kwargs]
        if missing:
            raise ValueError(f"OSWorld环境需要提供以下参数: {', '.join(missing)}")
        from envs import OSWorldEnvironment
        return OSWorldEnvironment(**kwargs)
```

### 2. 配置文件（新增）

**文件：** `configs/osworld_config.json`

**关键配置：**
- `environment_mode`: "osworld"
- `path_to_vm`: VM镜像路径
- `action_space`: "computer_13"（12个操作工具 + 1个控制工具）
- `available_tools`: 鼠标、键盘、滚动、控制工具列表

### 3. Seeds示例（新增）

**文件：** `example_seed_gui_tasks.json`

**格式：** 简单的任务描述列表

```json
[
  "打开文本编辑器，创建一个新文档，输入标题和内容",
  "在文件浏览器中创建文件夹并移动文件",
  ...
]
```

## 与WebAgent的对比

| 特性 | WebAgent | GUI Agent (OSWorld) |
|------|----------|---------------------|
| **环境** | WebEnvironment | OSWorldEnvironment |
| **工具** | web_search, web_visit | mouse_*, keyboard_*, control |
| **观察** | HTML内容、搜索结果 | 截图 + 可访问性树 |
| **并行** | 支持多进程 | 建议串行（VM限制） |
| **Seeds** | 实体名称、URL | GUI任务描述 |
| **配置** | web_config.json | osworld_config.json |

## 工作流程

```
任务描述 (Seed)
    ↓
初始化OSWorldEnvironment
    ↓
连接VM并启动桌面环境
    ↓
[轨迹采样] 使用computer_13工具探索GUI操作
    ├─ 鼠标操作: 移动、点击、拖拽
    ├─ 键盘操作: 输入、按键、组合键
    ├─ 滚动操作
    └─ 控制信号: WAIT, DONE, FAIL
    ↓
[轨迹选择] 选择高质量的操作序列
    ↓
[QA合成] 基于操作轨迹生成推理问答
    ├─ 操作序列推理
    ├─ 界面元素定位
    ├─ 状态转换推理
    └─ 数量计算问题
    ↓
输出QA对 + 完整轨迹
```

## 配置调优建议

### 初次使用（推荐配置）

```json
{
  "max_depth": 6,           // 中等探索深度
  "branching_factor": 2,    // 每步2个分支
  "max_workers": 1,         // 串行处理
  "number_of_seed": 10      // 先测试10个seed
}
```

### 复杂任务

```json
{
  "max_depth": 8,           // 更深的探索
  "branching_factor": 2,    // 保持2个分支
  "max_workers": 1,         // 串行
  "number_of_seed": 100
}
```

### 快速测试

```json
{
  "max_depth": 4,           // 浅层探索
  "branching_factor": 2,
  "max_workers": 1,
  "number_of_seed": 3       // 只测试3个
}
```

## 常见问题速查

### VM无法连接
```bash
# 检查VM路径
ls -l /path/to/vm.vmx

# 检查provider_name
# VMware: "vmware"
# VirtualBox: "virtualbox"
```

### 操作太慢
```json
{
  "sleep_after_execution": 1.0,  // 减少等待时间
  "max_depth": 5                 // 减少探索深度
}
```

### 内存不足
```json
{
  "screen_width": 1280,    // 降低分辨率
  "screen_height": 720,
  "max_workers": 1         // 确保串行
}
```

## 输出示例

### QA对示例

```json
{
  "question": "在文本编辑器中打开第3个最近文件，在第2段插入表格，然后保存。需要多少次鼠标点击？",
  "answer": "7",
  "trajectory_id": "traj_0001",
  "source_id": "src_0001_a3b5c7d9",
  "reasoning_steps": [
    {"step": 1, "action": "mouse_click", "reasoning": "点击文件菜单"},
    {"step": 2, "action": "mouse_click", "reasoning": "选择最近文件"},
    {"step": 3, "action": "mouse_click", "reasoning": "点击第3个文件"},
    ...
  ]
}
```

### 轨迹示例

```json
{
  "trajectory_id": "traj_0001",
  "source_id": "src_0001_a3b5c7d9",
  "seed_data": "打开文本编辑器，创建文档，保存到桌面",
  "total_depth": 6,
  "nodes": [
    {
      "node_id": "d0_t0_b0",
      "observation": "桌面初始状态",
      "intent": "开始探索",
      "action": null,
      "depth": 0
    },
    {
      "node_id": "d1_t1_b0",
      "observation": "应用程序菜单打开",
      "intent": "查找文本编辑器",
      "action": {
        "tool_name": "mouse_click",
        "parameters": {"x": 50, "y": 50}
      },
      "depth": 1
    },
    ...
  ]
}
```

## 下一步

- 📖 阅读详细文档：`README_GUI_SYNTHESIS.md`
- 🔧 调整配置参数以适应你的任务
- 📊 分析生成的QA质量
- 🎯 根据结果优化sampling_tips和synthesis_tips

## 技术支持

- 问题反馈：提交Issue
- 详细文档：`README_GUI_SYNTHESIS.md`
- 架构文档：`README_DECOUPLING.md`
- 运行脚本：`../run_osworld.py`（单任务执行）

---

**快速开始完成！** 🎉

现在你可以开始为GUI Agent生成训练数据了。

