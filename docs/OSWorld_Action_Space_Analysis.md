# OSWorld 动作空间分析与设计建议

## 当前三种动作空间

### 1. `computer_13` - 结构化动作空间

**特点:**
- 13种预定义的高级动作类型
- 每个动作都有明确的参数schema
- 结构化的 JSON 格式

**动作列表:**
```python
ACTION_SPACE = [
    {"action_type": "MOVE_TO", "parameters": {"x": float, "y": float}},
    {"action_type": "CLICK", "parameters": {"button": str, "x": float, "y": float, "num_clicks": int}},
    {"action_type": "MOUSE_DOWN", "parameters": {"button": str}},
    {"action_type": "MOUSE_UP", "parameters": {"button": str}},
    {"action_type": "RIGHT_CLICK", "parameters": {"x": float, "y": float}},
    {"action_type": "DOUBLE_CLICK", "parameters": {"x": float, "y": float}},
    {"action_type": "DRAG_TO", "parameters": {"x": float, "y": float}},
    {"action_type": "SCROLL", "parameters": {"dx": int, "dy": int}},
    {"action_type": "TYPING", "parameters": {"text": str}},
    {"action_type": "PRESS", "parameters": {"key": str}},
    {"action_type": "HOTKEY", "parameters": {"keys": list[str]}},
    {"action_type": "WAIT", "parameters": {"duration": float}},
    {"action_type": "SCREENSHOT", "parameters": {}}
]
```

**使用方式:**
```python
# LLM 输出结构化 JSON
action = {
    "action_type": "CLICK",
    "parameters": {"x": 100, "y": 200, "button": "left"}
}

# DesktopEnv.step() 处理
if self.action_space == "computer_13":
    self.controller.execute_action(action)  # 转换为 pyautogui 命令
```

**优点:**
- ✅ 类型安全、参数明确
- ✅ 易于验证和错误处理
- ✅ LLM 更容易理解和生成
- ✅ 可以添加约束（如坐标范围）

**缺点:**
- ❌ 只支持13种预定义动作
- ❌ 扩展新动作需要修改 ACTION_SPACE
- ❌ 复杂操作需要多步骤组合

---

### 2. `pyautogui` - 原始命令空间

**特点:**
- 直接执行 PyAutoGUI Python 代码
- 完全灵活，支持所有 PyAutoGUI API
- 字符串格式

**使用方式:**
```python
# LLM 输出 Python 代码字符串
action = "pyautogui.click(100, 200)"
action = "pyautogui.typewrite('Hello World')"
action = "pyautogui.hotkey('ctrl', 'c')"

# DesktopEnv.step() 处理
if self.action_space == "pyautogui":
    if action in ['WAIT', 'FAIL', 'DONE']:
        self.controller.execute_action(action)  # 特殊控制命令
    else:
        fixed_command = _fix_pyautogui_less_than_bug(action)
        self.controller.execute_python_command(fixed_command)  # 直接执行
```

**优点:**
- ✅ 完全灵活，支持所有 PyAutoGUI 功能
- ✅ 可以执行复杂的Python表达式
- ✅ 不需要预定义动作集合

**缺点:**
- ❌ 安全风险（可以执行任意 Python 代码）
- ❌ 难以验证和约束
- ❌ LLM 容易生成错误代码
- ❌ 调试困难

---

### 3. `claude_computer_use` - Claude Computer Use API

**特点:**
- 针对 Claude 的 Computer Use API 优化
- 介于结构化和灵活之间
- 支持特殊控制命令

**使用方式:**
```python
# 与 pyautogui 相同，但针对 Claude API 优化
# 支持 WAIT/FAIL/DONE 控制命令
# 也支持 pyautogui 命令字符串
```

**执行逻辑:**
```python
if self.action_space == "claude_computer_use":
    if action in ['WAIT', 'FAIL', 'DONE']:
        self.controller.execute_action(action)
    elif isinstance(action, str):
        self.controller.execute_python_command(action)
    elif isinstance(action, dict):
        # 支持结构化格式: {"command": "pyautogui.click(100, 200)"}
        self.controller.execute_python_command(action['command'])
```

---

## 问题分析

### 当前设计的问题:

1. **混合格式**
   - `computer_13`: Dict 格式
   - `pyautogui`: String 格式
   - `claude_computer_use`: String/Dict 混合

2. **安全性**
   - `pyautogui` 和 `claude_computer_use` 可以执行任意代码
   - 缺少输入验证和沙箱

3. **可维护性**
   - 三种格式需要不同的处理逻辑
   - 代码中充满 if-else 判断

4. **LLM 使用复杂**
   - LLM 需要根据 action_space 生成不同格式
   - 容易混淆和出错

---

## 重新设计建议

### 方案: 统一使用结构化动作 + 扩展机制

**核心思想:**
- 基础层: 使用 `computer_13` 的结构化设计
- 扩展层: 支持自定义动作类型
- 安全层: 所有动作经过验证和转换

**新的动作空间设计:**

```python
# 1. 基础动作 (原 computer_13)
class BaseActions:
    CLICK = {"action_type": "CLICK", "params": {"x": int, "y": int}}
    TYPE = {"action_type": "TYPE", "params": {"text": str}}
    KEY = {"action_type": "KEY", "params": {"key": str}}
    HOTKEY = {"action_type": "HOTKEY", "params": {"keys": list}}
    SCROLL = {"action_type": "SCROLL", "params": {"clicks": int}}
    ...

# 2. 控制动作
class ControlActions:
    WAIT = {"action_type": "WAIT"}
    DONE = {"action_type": "DONE"}
    FAIL = {"action_type": "FAIL"}

# 3. 扩展动作 (高级功能)
class ExtendedActions:
    # 支持注册自定义动作
    CUSTOM = {"action_type": "CUSTOM", "params": {"command": str}}
```

**统一执行流程:**

```python
def step(self, action: Dict[str, Any], pause: float = 2):
    """
    统一的动作执行接口

    Args:
        action: 结构化动作字典
            {
                "action_type": "CLICK" | "TYPE" | "KEY" | ...,
                "params": {...}
            }
    """
    # 1. 验证动作类型
    if not self._validate_action(action):
        raise ValueError(f"Invalid action: {action}")

    # 2. 转换为 PyAutoGUI 命令
    command = self._action_to_command(action)

    # 3. 执行命令
    self.controller.execute_python_command(command)

    # 4. 返回观测
    return self._get_obs(), reward, done, info
```

**动作转换器:**

```python
class ActionConverter:
    """将结构化动作转换为 PyAutoGUI 命令"""

    @staticmethod
    def to_pyautogui(action: Dict[str, Any]) -> str:
        action_type = action["action_type"]
        params = action.get("params", {})

        if action_type == "CLICK":
            x, y = params["x"], params["y"]
            return f"pyautogui.click({x}, {y})"

        elif action_type == "TYPE":
            text = params["text"].replace('"', '\\"')
            return f'pyautogui.typewrite("{text}")'

        elif action_type == "KEY":
            key = params["key"]
            return f"pyautogui.press('{key}')"

        elif action_type == "HOTKEY":
            keys = ", ".join([f"'{k}'" for k in params["keys"]])
            return f"pyautogui.hotkey({keys})"

        elif action_type == "SCROLL":
            clicks = params["clicks"]
            return f"pyautogui.scroll({clicks})"

        # 控制命令
        elif action_type in ["WAIT", "DONE", "FAIL"]:
            return action_type

        # 自定义命令 (需要权限验证)
        elif action_type == "CUSTOM":
            if not self._is_safe_command(params["command"]):
                raise SecurityError("Unsafe custom command")
            return params["command"]

        else:
            raise ValueError(f"Unknown action_type: {action_type}")
```

---

## AgentFlow 工具层设计建议

基于上面的分析，建议 AgentFlow 的工具层采用以下设计:

### 选项A: 多工具方案 (推荐) ✅

**优点:**
- 每个工具对应一个动作类型
- 参数明确，类型安全
- LLM 容易理解和使用
- 易于扩展和维护

**实现:**
```python
# 6个专用工具
ClickTool(x, y, pause)
TypeTool(text, pause)
KeyTool(key/keys, pause)
ScrollTool(clicks, pause)
ControlTool(command: WAIT/DONE/FAIL, pause)
PyAutoGUITool(command, pause)  # Fallback
```

**底层统一:**
```python
# 工具层: 接收特定参数
ClickTool(x=100, y=200)

# ↓ 转换为统一格式
action = {"action_type": "CLICK", "params": {"x": 100, "y": 200}}

# ↓ 传递给环境
env.step(action)

# ↓ 环境转换为 PyAutoGUI
command = "pyautogui.click(100, 200)"

# ↓ 执行
controller.execute_python_command(command)
```

---

### 选项B: 单工具 + 类型区分

**保留单一工具，但改进参数结构:**

```python
class DesktopActionTool(Tool):
    parameters = [
        {
            "name": "action",
            "type": "object",
            "required": True,
            "description": "Action to execute",
            "oneOf": [
                {
                    "properties": {
                        "action_type": {"const": "CLICK"},
                        "x": {"type": "integer"},
                        "y": {"type": "integer"}
                    }
                },
                {
                    "properties": {
                        "action_type": {"const": "TYPE"},
                        "text": {"type": "string"}
                    }
                },
                # ...
            ]
        }
    ]
```

**缺点:**
- JSON Schema 的 oneOf 支持有限
- LLM 仍然容易混淆
- 不如多工具方案清晰

---

## 最终建议

### 推荐架构:

```
┌─────────────────────────────────────────┐
│         LLM (Agent)                     │
│  选择工具: desktop_click / desktop_type │
└──────────────┬──────────────────────────┘
               │
       ┌───────▼────────┐
       │  AgentFlow     │
       │  Tool Layer    │  6个专用工具
       │  (v2 design)   │  + 统一返回格式
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │   OSWorld      │
       │  Environment   │  统一动作接口
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │   DesktopEnv   │
       │  action_space  │  统一使用结构化动作
       │  = "unified"   │  (不再区分3种)
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ ActionConverter│  转换器
       │ to PyAutoGUI   │  Dict → String
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │  PyAutoGUI     │
       │  执行命令       │  execute_python_command()
       └────────────────┘
```

### 核心改进:

1. **工具层**: 使用 osworld_tools_v2.py (6个专用工具)
2. **返回值**: 返回完整观测数据，不做 summary
3. **动作格式**: 统一使用结构化 Dict 格式
4. **动作空间**: 废弃 `computer_13/pyautogui/claude_computer_use` 的区分
5. **转换层**: 在环境内部统一转换为 PyAutoGUI 命令

### 迁移路径:

1. ✅ 已完成: 设计 osworld_tools_v2.py
2. 待实现: 修改 OSWorldEnvironment._initialize_tools() 注册新工具
3. 待实现: 简化 DesktopEnv.step() 的动作空间判断
4. 待实现: 测试新工具的功能
5. 待实现: 更新 run_osworld.py 处理新返回格式
