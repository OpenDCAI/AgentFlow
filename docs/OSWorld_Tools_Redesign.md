# OSWorld Tools 重新设计方案

## 问题分析

### 问题1: 单一工具过于复杂

**旧设计 (osworld_tools.py):**
```python
class DesktopActionTool:
    parameters = [
        {"name": "action_type", ...},  # click/type/key/hotkey/scroll/pyautogui/WAIT/DONE/FAIL
        {"name": "coordinate", ...},   # 仅 click 需要
        {"name": "text", ...},         # 仅 type 需要
        {"name": "key", ...},          # 仅 key 需要
        {"name": "keys", ...},         # 仅 hotkey 需要
        {"name": "clicks", ...},       # 仅 scroll 需要
        {"name": "command", ...},      # 仅 pyautogui 需要
    ]
```

**问题:**
- 所有动作类型的参数混在一起
- 参数之间有互斥关系，但 schema 无法表达
- LLM 容易混淆不同动作所需的参数
- 代码中需要大量 if-else 来判断和转换

### 问题2: 返回值被过度 summary

**旧设计:**
```python
def call(self, params, **kwargs) -> str:
    obs, reward, done, info = env.step(action, pause)

    # ❌ 在工具内部 summary 观测
    summary = self._summarize_obs(obs)  # 只保留前10行 a11y，不返回完整数据

    meta = {
        "done": done,
        "reward": reward,
        "info": info,
        "obs_summary": {  # ❌ 只是 summary，不是完整数据
            "a11y_head": summary['a11y_head'],  # 只有前10行
            "screenshot_file": png_filename,     # 只有文件名，没有实际数据
            "step_num": step_num
        }
    }

    # 返回 JSON + 人类可读文本
    return json.dumps(meta) + "\n" + human_text
```

**问题:**
- 截图数据被保存到文件，但不在返回值中
- a11y tree 只返回前10行，调用者拿不到完整数据
- 调用者如果需要完整观测，还需要再次调用 `env.get_obs()`
- 返回格式复杂（JSON + 文本），不利于程序处理

---

## 新设计方案

### 方案: 拆分为多个专用工具

#### 工具列表:

1. **ClickTool** (`desktop_click`)
   - 参数: `x`, `y`, `pause`
   - 用途: 点击指定坐标

2. **TypeTool** (`desktop_type`)
   - 参数: `text`, `pause`
   - 用途: 输入文本

3. **KeyPressTool** (`desktop_key`)
   - 参数: `key` 或 `keys`, `pause`
   - 用途: 按单个键或组合键

4. **ScrollTool** (`desktop_scroll`)
   - 参数: `clicks`, `pause`
   - 用途: 滚动

5. **ControlTool** (`desktop_control`)
   - 参数: `command` (WAIT/DONE/FAIL), `pause`
   - 用途: 控制命令

6. **PyAutoGUITool** (`desktop_pyautogui`)
   - 参数: `command`, `pause`
   - 用途: 原始 PyAutoGUI 命令（fallback）

#### 优点:

✅ **参数清晰**: 每个工具只有自己需要的参数
✅ **类型安全**: 不会出现参数混淆
✅ **易于理解**: LLM 更容易选择正确的工具
✅ **易于维护**: 每个工具职责单一

### 返回值重新设计

**新设计:**
```python
def call(self, params, **kwargs) -> str:
    # 执行动作
    observation, reward, done, info = env.step(action, pause)

    # ✅ 返回完整数据，不做 summary
    result = {
        'observation': observation or {},  # ✅ 完整观测，包含完整 screenshot 和 a11y tree
        'reward': float(reward),
        'done': bool(done),
        'info': info or {},
        'metadata': {                      # ✅ 元数据单独分组
            'step_num': step_num,
            'timestamp': timestamp,
            'screenshot_file': png_filename,
            'action': action
        }
    }

    # ✅ 纯 JSON 返回，方便程序处理
    return json.dumps(result, ensure_ascii=False)
```

**返回值结构:**
```json
{
  "observation": {
    "screenshot": "<base64 bytes>",           // ✅ 完整截图数据
    "accessibility_tree": "<full a11y tree>"  // ✅ 完整 a11y 树
  },
  "reward": 0.0,
  "done": false,
  "info": {},
  "metadata": {
    "step_num": 1,
    "timestamp": "20250105@123456",
    "screenshot_file": "step_1_20250105@123456.png",
    "action": "pyautogui.click(100, 200)"
  }
}
```

#### 优点:

✅ **数据完整**: 调用者可以获取完整的观测数据
✅ **灵活处理**: 调用者可以自行决定如何 summary 或使用数据
✅ **避免重复**: 不需要再次调用 `get_obs()` 获取完整观测
✅ **格式统一**: 纯 JSON，易于解析和处理
✅ **元数据分离**: 记录信息和观测数据清晰分开

---

## 实现细节

### BaseDesktopTool

所有工具共享的基类，提供:
- `_execute_and_record()`: 统一的执行和记录逻辑
- 自动保存截图到文件
- 自动追加 trajectory JSONL
- 返回完整观测数据

```python
class BaseDesktopTool(ABC):
    def _execute_and_record(self, action: str, step_num: int, pause: float = None):
        # 1. 执行动作
        observation, reward, done, info = env.step(action, pause)

        # 2. 保存截图
        # 3. 追加轨迹
        # 4. 返回完整结果
        return {
            'observation': observation,  # 完整数据
            'reward': reward,
            'done': done,
            'info': info,
            'metadata': {...}
        }
```

### 具体工具示例

```python
class ClickTool(BaseDesktopTool, Tool):
    @property
    def parameters(self):
        return [
            {"name": "x", "type": "integer", "required": True},
            {"name": "y", "type": "integer", "required": True},
            {"name": "pause", "type": "number", "required": False}
        ]

    def call(self, params, **kwargs):
        x, y = params['x'], params['y']
        action = f"pyautogui.click({x}, {y})"
        result = self._execute_and_record(action, step_num, pause)
        return json.dumps(result, ensure_ascii=False)
```

---

## 迁移建议

### 环境文件修改

需要在 `OSWorldEnvironment._initialize_tools()` 中注册所有新工具:

```python
def _initialize_tools(self):
    from tools.osworld_tools_v2 import (
        ClickTool, TypeTool, KeyPressTool,
        ScrollTool, ControlTool, PyAutoGUITool
    )

    # 注册所有工具
    self.register_tool(ClickTool(self))
    self.register_tool(TypeTool(self))
    self.register_tool(KeyPressTool(self))
    self.register_tool(ScrollTool(self))
    self.register_tool(ControlTool(self))
    self.register_tool(PyAutoGUITool(self))
```

### Runner 修改

Runner 需要修改返回值处理逻辑:

```python
# 旧代码
tool_result = env.execute_tool('desktop_action', args, step_num=turn+1)
first_line = tool_result.splitlines()[0]
meta = json.loads(first_line)  # ❌ 需要解析首行

# 新代码
tool_result = env.execute_tool('desktop_click', args, step_num=turn+1)
result = json.loads(tool_result)  # ✅ 直接解析 JSON
observation = result['observation']  # ✅ 获取完整观测
done = result['done']
```

---

## 总结

### 改进点:

1. ✅ **工具拆分**: 从1个复杂工具拆分为6个简单工具
2. ✅ **参数清晰**: 每个工具参数独立，无互斥关系
3. ✅ **返回完整**: 返回完整观测数据，不做 summary
4. ✅ **格式统一**: 纯 JSON 返回，易于处理
5. ✅ **职责分离**: 工具负责执行，调用者负责处理数据

### 下一步:

1. 修改 `osworld_environment.py` 的 `_initialize_tools()` 方法
2. 测试新工具的功能
3. 修改 `run_osworld.py` 的返回值处理逻辑
4. 考虑是否保留旧工具作为向后兼容
