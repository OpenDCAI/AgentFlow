# OSWorld 工具名称修复总结

## 问题描述

`self.tool_descriptions` 为空字符串，导致探索采样器无法正常工作。

## 根本原因

配置文件中的工具名称与实际注册的工具名称不匹配：

### 错误的工具名称（配置文件中）
```json
"available_tools": [
  "mouse_move",
  "mouse_click",
  "mouse_right_click",
  ...
]
```

### 正确的工具名称（实际注册的）
```json
"available_tools": [
  "desktop_mouse_move",
  "desktop_mouse_click",
  "desktop_mouse_right_click",
  ...
]
```

**关键发现**：所有 OSWorld 工具名称都有 `desktop_` 前缀！

## 修复内容

### 1. 更新 `osworld_exploration_config.json`

**文件**: `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/configs/osworld_exploration_config.json`

**修改前**:
```json
"available_tools": [
  "mouse_move",
  "mouse_click",
  "mouse_right_click",
  "mouse_double_click",
  "scroll",
  "type",
  "key_press",
  "hotkey",
  "control"
]
```

**修改后**:
```json
"available_tools": [
  "desktop_mouse_move",
  "desktop_mouse_click",
  "desktop_mouse_right_click",
  "desktop_mouse_double_click",
  "desktop_mouse_drag",
  "desktop_scroll",
  "desktop_type",
  "desktop_key_press",
  "desktop_hotkey",
  "desktop_control"
]
```

### 2. 更新 `osworld_config.json`

**文件**: `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/configs/osworld_config.json`

**修改前**:
```json
"available_tools": [
  "mouse_move",
  "mouse_click",
  "mouse_right_click",
  "mouse_double_click",
  "mouse_button",
  "mouse_drag",
  "scroll",
  "type",
  "key_press",
  "key_hold",
  "hotkey",
  "control"
]
```

**修改后**:
```json
"available_tools": [
  "desktop_mouse_move",
  "desktop_mouse_click",
  "desktop_mouse_right_click",
  "desktop_mouse_double_click",
  "desktop_mouse_button",
  "desktop_mouse_drag",
  "desktop_scroll",
  "desktop_type",
  "desktop_key_press",
  "desktop_key_hold",
  "desktop_hotkey",
  "desktop_control"
]
```

### 3. 改进 `exploration_sampler.py` 的错误处理

**文件**: `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/exploration_sampler.py`

**改进点**:

#### (1) 增强 `_get_available_tools()` 方法
- ✅ 添加日志输出，显示工具加载过程
- ✅ 检测并报告未找到的工具
- ✅ 显示所有已注册的工具列表（用于诊断）
- ✅ 提供有用的提示信息

```python
def _get_available_tools(self) -> List[Dict[str, Any]]:
    """获取可用工具信息"""
    tools = []
    
    if self.config.available_tools:
        tool_names = self.config.available_tools
        print(f"📋 从配置获取工具列表: {len(tool_names)} 个工具")
    else:
        tool_names = self.environment.list_tools()
        print(f"📋 从环境获取工具列表: {len(tool_names)} 个工具")
    
    # 获取所有已注册的工具（用于诊断）
    all_registered_tools = self.environment.list_tools()
    
    not_found_tools = []
    for tool_name in tool_names:
        tool = self.environment.get_tool(tool_name)
        if tool:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        else:
            not_found_tools.append(tool_name)
    
    # 报告结果
    if tools:
        print(f"✅ 成功加载 {len(tools)} 个工具")
    else:
        print(f"❌ 警告：没有找到任何可用工具！")
    
    if not_found_tools:
        print(f"⚠️  以下工具未找到: {not_found_tools}")
        print(f"💡 可用的工具列表: {all_registered_tools}")
        print(f"💡 提示：OSWorld工具名称通常以 'desktop_' 开头")
    
    return tools
```

#### (2) 增强 `_generate_tool_descriptions()` 方法
- ✅ 添加空列表检查
- ✅ 返回有用的错误提示

```python
def _generate_tool_descriptions(self) -> str:
    """生成工具描述文本"""
    if not self.available_tools:
        return "⚠️ 没有可用的工具。请检查配置文件中的 available_tools 列表。"
    
    # ... 原有逻辑 ...
```

## OSWorld 完整工具列表

### computer_13 动作空间（结构化工具）

| 工具名称 | 说明 | 对应动作类型 |
|---------|------|-------------|
| `desktop_mouse_move` | 移动鼠标 | MOVE_TO |
| `desktop_mouse_click` | 鼠标点击 | CLICK |
| `desktop_mouse_right_click` | 鼠标右键点击 | RIGHT_CLICK |
| `desktop_mouse_double_click` | 鼠标双击 | DOUBLE_CLICK |
| `desktop_mouse_button` | 鼠标按下/释放 | MOUSE_DOWN, MOUSE_UP |
| `desktop_mouse_drag` | 鼠标拖拽 | DRAG_TO |
| `desktop_scroll` | 滚轮滚动 | SCROLL |
| `desktop_type` | 输入文本 | TYPING |
| `desktop_key_press` | 按键 | PRESS |
| `desktop_key_hold` | 按住/释放按键 | KEY_DOWN, KEY_UP |
| `desktop_hotkey` | 快捷键组合 | HOTKEY |
| `desktop_control` | 控制指令 | WAIT, DONE, FAIL |

### pyautogui 动作空间（脚本执行）

| 工具名称 | 说明 |
|---------|------|
| `desktop_execute_python_script` | 执行 Python 脚本 |
| `desktop_control` | 控制指令 |

## 如何查找工具名称

### 方法1：查看工具定义
查看 `/home/a1/sdb/tzw/AgentFlow/src/tools/osworld_tools.py` 中每个工具类的 `name` 属性：

```python
class MouseMoveTool(BaseDesktopTool, Tool):
    @property
    def name(self) -> str:
        return "desktop_mouse_move"  # 这是工具名称
```

### 方法2：通过环境获取
```python
from envs import OSWorldEnvironment

env = OSWorldEnvironment(...)
tool_names = env.list_tools()
print(tool_names)
```

### 方法3：查看日志输出
运行探索采样器时，现在会输出：
```
📋 从配置获取工具列表: 10 个工具
✅ 成功加载 10 个工具
```

如果工具名称错误：
```
⚠️  以下工具未找到: ['mouse_move', 'mouse_click', ...]
💡 可用的工具列表: ['desktop_mouse_move', 'desktop_mouse_click', ...]
💡 提示：OSWorld工具名称通常以 'desktop_' 开头
```

## 调试技巧

### 1. 快速验证工具名称
```python
from envs import OSWorldEnvironment

env = OSWorldEnvironment(path_to_vm="...")
print("所有已注册的工具：")
for tool_name in env.list_tools():
    tool = env.get_tool(tool_name)
    print(f"  - {tool_name}: {tool.description}")
```

### 2. 检查配置文件
确保配置文件中的 `available_tools` 列表中的工具名称与实际注册的工具名称完全匹配。

### 3. 使用改进的错误日志
新版本的 `exploration_sampler.py` 会自动报告未找到的工具和可用的工具列表。

## 常见错误

### ❌ 错误1：缺少 `desktop_` 前缀
```json
// 错误
"available_tools": ["mouse_move"]

// 正确
"available_tools": ["desktop_mouse_move"]
```

### ❌ 错误2：工具名称拼写错误
```json
// 错误
"available_tools": ["desktop_mouse_moves"]  // 多了一个 's'

// 正确
"available_tools": ["desktop_mouse_move"]
```

### ❌ 错误3：使用了不存在的工具
```json
// 错误（computer_13 动作空间没有这个工具）
"available_tools": ["desktop_execute_python_script"]

// 提示：desktop_execute_python_script 只在 pyautogui 动作空间中可用
```

## 验证修复

运行探索式数据合成，应该看到：

```
初始化 OSWorld Environment（探索模式）...
📋 从配置获取工具列表: 10 个工具
✅ 成功加载 10 个工具
```

而不是：
```
❌ 警告：没有找到任何可用工具！
⚠️  以下工具未找到: [...]
```

## 参考资源

- **工具定义**：`/home/a1/sdb/tzw/AgentFlow/src/tools/osworld_tools.py`
- **环境基类**：`/home/a1/sdb/tzw/AgentFlow/src/envs/enviroment.py`
- **OSWorld环境**：`/home/a1/sdb/tzw/AgentFlow/src/envs/osworld_environment.py`
- **配置示例**：`/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/configs/osworld_*_config.json`

---

**修复时间**: 2025-11-10  
**修复内容**: 工具名称映射错误  
**影响范围**: 所有使用 OSWorld 环境的数据合成配置

