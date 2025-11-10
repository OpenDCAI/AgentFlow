# OSWorld Tools Parameter Validation Specification

本文档详细说明了OSWorld工具的参数验证规则，严格基于 `desktop_env/controllers/python.py` 中的 `execute_action()` 函数实现。

## 总览

所有工具（除Control工具外）生成以下格式的动作：

```python
{
    "action_type": "ACTION_NAME",
    "parameters": {...}
}
```

Control工具生成纯字符串：`"WAIT"`, `"DONE"`, `"FAIL"`

---

## 1. MOVE_TO (MouseMoveTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{}` (空) | `pyautogui.moveTo()` | 移动到默认位置 |
| 2 | `{x, y}` | `pyautogui.moveTo(x, y, duration, mode)` | 移动到指定位置 |

### 验证规则

1. **必须同时提供x和y，或者都不提供**
   - ✅ Valid: `{}`, `{x: 100, y: 200}`
   - ❌ Invalid: `{x: 100}`, `{y: 200}`

2. **错误处理**
   - 如果只提供x或只提供y → 返回错误: "MOVE_TO requires both 'x' and 'y' parameters"

### Tool实现

```python
# Tool定义x和y都是REQUIRED
parameters = [
    {"name": "x", "type": "number", "required": True},
    {"name": "y", "type": "number", "required": True}
]

# 验证逻辑
if 'x' not in params or 'y' not in params:
    return error("MOVE_TO requires both 'x' and 'y' parameters")
```

---

## 2. CLICK (MouseClickTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{}` | `pyautogui.click()` | 当前位置，左键，单击 |
| 2a | `{button, x, y}` | `pyautogui.click(button=b, x=x, y=y)` | 指定位置和按钮 |
| 2b | `{button, x, y, num_clicks}` | `pyautogui.click(button=b, x=x, y=y, clicks=n)` | 指定位置、按钮、次数 |
| 3a | `{button}` | `pyautogui.click(button=b)` | 当前位置，指定按钮 |
| 3b | `{button, num_clicks}` | `pyautogui.click(button=b, clicks=n)` | 当前位置，指定按钮和次数 |
| 4a | `{x, y}` | `pyautogui.click(x=x, y=y)` | 指定位置，左键 |
| 4b | `{x, y, num_clicks}` | `pyautogui.click(x=x, y=y, clicks=n)` | 指定位置和次数 |

### 验证规则

1. **x和y必须同时出现或同时缺失**
   - ✅ Valid: `{}`, `{x: 100, y: 200}`, `{button: 'left'}`
   - ❌ Invalid: `{x: 100}`, `{y: 200}`, `{x: 100, button: 'left'}`

2. **button值必须在 ['left', 'right', 'middle'] 中**
   - ✅ Valid: `{button: 'left'}`, `{button: 'right'}`, `{button: 'middle'}`
   - ❌ Invalid: `{button: 'center'}`, `{button: 'LEFT'}`

3. **num_clicks值必须在 [1, 2, 3] 中**
   - ✅ Valid: `{num_clicks: 1}`, `{num_clicks: 2}`, `{num_clicks: 3}`
   - ❌ Invalid: `{num_clicks: 0}`, `{num_clicks: 4}`, `{num_clicks: 1.5}`

4. **错误处理**
   - x和y不匹配 → "If 'x' is provided, 'y' must also be provided, and vice versa."
   - 无效button → "Invalid button '{value}'. Must be 'left', 'right', or 'middle'."
   - 无效num_clicks → "Invalid num_clicks '{value}'. Must be 1, 2, or 3."

### Tool实现

```python
# 所有参数都是可选的
parameters = [
    {"name": "x", "type": "number", "required": False},
    {"name": "y", "type": "number", "required": False},
    {"name": "button", "type": "string", "required": False},
    {"name": "num_clicks", "type": "integer", "required": False}
]

# 验证逻辑
if has_x != has_y:
    return error("x and y must both be present or both absent")
if has_button and params['button'] not in ['left', 'right', 'middle']:
    return error("Invalid button")
if has_num_clicks and params['num_clicks'] not in [1, 2, 3]:
    return error("Invalid num_clicks")
```

---

## 3. MOUSE_DOWN / MOUSE_UP (MouseButtonTool)

### 有效参数组合

| Action | Parameters | PyAutoGUI Command | 说明 |
|--------|-----------|------------------|------|
| down | `{}` | `pyautogui.mouseDown()` | 按下左键 |
| down | `{button}` | `pyautogui.mouseDown(button=b)` | 按下指定键 |
| up | `{}` | `pyautogui.mouseUp()` | 释放左键 |
| up | `{button}` | `pyautogui.mouseUp(button=b)` | 释放指定键 |

### 验证规则

1. **action参数必须提供，值为 'down' 或 'up'**
   - ✅ Valid: `{action: 'down'}`, `{action: 'up'}`
   - ❌ Invalid: `{action: 'press'}`, 缺少action

2. **button值必须在 ['left', 'right', 'middle'] 中（可选）**
   - ✅ Valid: `{action: 'down'}`, `{action: 'down', button: 'left'}`
   - ❌ Invalid: `{action: 'down', button: 'center'}`

3. **不允许其他参数（如x, y）**

4. **错误处理**
   - 缺少action → "'action' parameter is required"
   - 无效action → "Invalid action '{value}'. Must be 'down' or 'up'."
   - 无效button → "Invalid button '{value}'. Must be 'left', 'right', or 'middle'."

### Tool实现

```python
# action必须，button可选
parameters = [
    {"name": "action", "type": "string", "required": True},  # 'down' or 'up'
    {"name": "button", "type": "string", "required": False}
]

# 验证逻辑
if 'action' not in params:
    return error("'action' parameter is required")
if params['action'].upper() not in ['DOWN', 'UP']:
    return error("Invalid action")
if has_button and params['button'] not in ['left', 'right', 'middle']:
    return error("Invalid button")

# 生成动作类型
action_type = f"MOUSE_{params['action'].upper()}"  # MOUSE_DOWN or MOUSE_UP
```

---

## 4. RIGHT_CLICK (MouseRightClickTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{}` | `pyautogui.rightClick()` | 当前位置右键 |
| 2 | `{x, y}` | `pyautogui.rightClick(x, y)` | 指定位置右键 |

### 验证规则

1. **x和y必须同时出现或同时缺失**
   - ✅ Valid: `{}`, `{x: 100, y: 200}`
   - ❌ Invalid: `{x: 100}`, `{y: 200}`

2. **错误处理**
   - x和y不匹配 → "RIGHT_CLICK requires both 'x' and 'y', or neither."

### Tool实现

```python
parameters = [
    {"name": "x", "type": "number", "required": False},
    {"name": "y", "type": "number", "required": False}
]

# 验证逻辑
if has_x != has_y:
    return error("RIGHT_CLICK requires both 'x' and 'y', or neither.")
```

---

## 5. DOUBLE_CLICK (MouseDoubleClickTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{}` | `pyautogui.doubleClick()` | 当前位置双击 |
| 2 | `{x, y}` | `pyautogui.doubleClick(x, y)` | 指定位置双击 |

### 验证规则

1. **x和y必须同时出现或同时缺失**
   - ✅ Valid: `{}`, `{x: 100, y: 200}`
   - ❌ Invalid: `{x: 100}`, `{y: 200}`

2. **错误处理**
   - x和y不匹配 → "DOUBLE_CLICK requires both 'x' and 'y', or neither."

### Tool实现

```python
parameters = [
    {"name": "x", "type": "number", "required": False},
    {"name": "y", "type": "number", "required": False}
]

# 验证逻辑
if has_x != has_y:
    return error("DOUBLE_CLICK requires both 'x' and 'y', or neither.")
```

---

## 6. DRAG_TO (MouseDragTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{x, y}` | `pyautogui.dragTo(x, y, duration=1.0, button='left', mouseDownUp=True)` | 拖拽到指定位置 |

### 验证规则

1. **x和y都是必需的**（没有空参数的情况）
   - ✅ Valid: `{x: 100, y: 200}`
   - ❌ Invalid: `{}`, `{x: 100}`, `{y: 200}`

2. **错误处理**
   - 缺少x或y → "DRAG_TO requires both 'x' and 'y' parameters"

### Tool实现

```python
parameters = [
    {"name": "x", "type": "number", "required": True},
    {"name": "y", "type": "number", "required": True}
]

# 验证逻辑
if 'x' not in params or 'y' not in params:
    return error("DRAG_TO requires both 'x' and 'y' parameters")
```

---

## 7. SCROLL (ScrollTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Commands | 说明 |
|------|-----------|-------------------|------|
| 1 | `{dx, dy}` | `pyautogui.hscroll(dx) + pyautogui.vscroll(dy)` | 水平+垂直滚动 |
| 2 | `{dx}` | `pyautogui.hscroll(dx)` | 仅水平滚动 |
| 3 | `{dy}` | `pyautogui.vscroll(dy)` | 仅垂直滚动 |

### 验证规则

1. **至少需要dx或dy之一**
   - ✅ Valid: `{dx: 5}`, `{dy: -3}`, `{dx: 5, dy: -3}`
   - ❌ Invalid: `{}`

2. **dx和dy是整数（int）**
   - 正数dx：向右滚动
   - 负数dx：向左滚动
   - 正数dy：向上滚动
   - 负数dy：向下滚动

3. **错误处理**
   - 两者都缺失 → "SCROLL requires at least one of 'dx' or 'dy'"

### Tool实现

```python
parameters = [
    {"name": "dx", "type": "integer", "required": False},
    {"name": "dy", "type": "integer", "required": False}
]

# 验证逻辑
if not has_dx and not has_dy:
    return error("SCROLL requires at least one of 'dx' or 'dy'")
```

---

## 8. TYPING (TypeTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{text}` | `pyautogui.typewrite(repr(text))` | 输入文本 |

### 验证规则

1. **text参数必须提供**
   - ✅ Valid: `{text: 'hello'}`, `{text: ''}`
   - ❌ Invalid: `{}`

2. **text是字符串**
   - 特殊字符会被自动转义处理（使用repr()）

3. **错误处理**
   - 缺少text → "TYPING requires 'text' parameter"

### Tool实现

```python
parameters = [
    {"name": "text", "type": "string", "required": True}
]

# 验证逻辑
if 'text' not in params:
    return error("TYPING requires 'text' parameter")
```

---

## 9. PRESS (KeyPressTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{key}` | `pyautogui.press(key)` | 按下并释放按键 |

### 验证规则

1. **key参数必须提供**
   - ✅ Valid: `{key: 'enter'}`, `{key: 'a'}`
   - ❌ Invalid: `{}`

2. **key必须在KEYBOARD_KEYS列表中**
   - 验证时转换为小写：`key.lower() in KEYBOARD_KEYS`
   - KEYBOARD_KEYS包含：字母、数字、特殊字符、功能键等

3. **错误处理**
   - 缺少key → "PRESS requires 'key' parameter"
   - 无效key → "Invalid key '{key}'. Must be one of the valid keyboard keys."

### Tool实现

```python
parameters = [
    {"name": "key", "type": "string", "required": True}
]

# 验证逻辑
if 'key' not in params:
    return error("PRESS requires 'key' parameter")
if params['key'].lower() not in KEYBOARD_KEYS:
    return error("Invalid key")
```

---

## 10. KEY_DOWN / KEY_UP (KeyHoldTool)

### 有效参数组合

| Action | Parameters | PyAutoGUI Command | 说明 |
|--------|-----------|------------------|------|
| down | `{key}` | `pyautogui.keyDown(key)` | 按下按键 |
| up | `{key}` | `pyautogui.keyUp(key)` | 释放按键 |

### 验证规则

1. **action参数必须提供，值为 'down' 或 'up'**
   - ✅ Valid: `{action: 'down', key: 'ctrl'}`
   - ❌ Invalid: `{action: 'press', key: 'ctrl'}`

2. **key参数必须提供**
   - ✅ Valid: `{action: 'down', key: 'shift'}`
   - ❌ Invalid: `{action: 'down'}`

3. **key必须在KEYBOARD_KEYS列表中**
   - 验证时转换为小写：`key.lower() in KEYBOARD_KEYS`

4. **错误处理**
   - 缺少action → "'action' parameter is required"
   - 无效action → "Invalid action '{value}'. Must be 'down' or 'up'."
   - 缺少key → "'key' parameter is required"
   - 无效key → "Invalid key '{key}'. Must be one of the valid keyboard keys."

### Tool实现

```python
parameters = [
    {"name": "action", "type": "string", "required": True},  # 'down' or 'up'
    {"name": "key", "type": "string", "required": True}
]

# 验证逻辑
if 'action' not in params:
    return error("'action' parameter is required")
if params['action'].upper() not in ['DOWN', 'UP']:
    return error("Invalid action")
if 'key' not in params:
    return error("'key' parameter is required")
if params['key'].lower() not in KEYBOARD_KEYS:
    return error("Invalid key")

# 生成动作类型
action_type = f"KEY_{params['action'].upper()}"  # KEY_DOWN or KEY_UP
```

---

## 11. HOTKEY (HotkeyTool)

### 有效参数组合

| Case | Parameters | PyAutoGUI Command | 说明 |
|------|-----------|------------------|------|
| 1 | `{keys: [k1, k2, ...]}` | `pyautogui.hotkey('k1', 'k2', ...)` | 按下组合键 |

### 验证规则

1. **keys参数必须提供**
   - ✅ Valid: `{keys: ['ctrl', 'c']}`
   - ❌ Invalid: `{}`

2. **keys必须是列表（list）**
   - ✅ Valid: `{keys: ['ctrl', 'c']}`
   - ❌ Invalid: `{keys: 'ctrl'}`, `{keys: ('ctrl', 'c')}`

3. **列表中的每个key都必须在KEYBOARD_KEYS中**
   - ✅ Valid: `{keys: ['ctrl', 'shift', 't']}`
   - ❌ Invalid: `{keys: ['ctrl', 'invalid_key']}`

4. **错误处理**
   - 缺少keys → "HOTKEY requires 'keys' parameter"
   - keys不是列表 → "'keys' must be a list, got {type}"
   - 包含无效key → "Invalid key '{key}' in keys list. All keys must be valid keyboard keys."

### Tool实现

```python
parameters = [
    {"name": "keys", "type": "array", "required": True}
]

# 验证逻辑
if 'keys' not in params:
    return error("HOTKEY requires 'keys' parameter")
if not isinstance(params['keys'], list):
    return error("'keys' must be a list")
for key in params['keys']:
    if key.lower() not in KEYBOARD_KEYS:
        return error(f"Invalid key '{key}' in keys list")
```

---

## 12. WAIT / DONE / FAIL (ControlTool)

### 有效参数组合

| Action | Format | execute_action处理 | 说明 |
|--------|--------|------------------|------|
| wait | 字符串 `"WAIT"` | 直接返回（pass） | 等待 |
| done | 字符串 `"DONE"` | 直接返回（pass） | 任务完成 |
| fail | 字符串 `"FAIL"` | 直接返回（pass） | 任务失败 |

### 验证规则

1. **action参数必须提供，值为 'wait', 'done', 或 'fail'**
   - ✅ Valid: `{action: 'wait'}`, `{action: 'done'}`, `{action: 'fail'}`
   - ❌ Invalid: `{action: 'pause'}`, 缺少action

2. **这些是特殊的字符串动作，不是字典格式**
   - 生成的action是字符串：`"WAIT"`, `"DONE"`, `"FAIL"`
   - 不是：`{"action_type": "WAIT", "parameters": {}}`

3. **错误处理**
   - 缺少action → "'action' parameter is required"
   - 无效action → "Invalid action '{value}'. Must be 'wait', 'done', or 'fail'."

### Tool实现

```python
parameters = [
    {"name": "action", "type": "string", "required": True}  # 'wait', 'done', or 'fail'
]

# 验证逻辑
if 'action' not in params:
    return error("'action' parameter is required")
if params['action'].upper() not in ['WAIT', 'DONE', 'FAIL']:
    return error("Invalid action")

# 生成动作（字符串，不是字典！）
action = params['action'].upper()  # "WAIT", "DONE", or "FAIL"
```

---

## 错误返回格式

所有验证失败都返回统一的错误格式：

```json
{
    "observation": {},
    "reward": 0.0,
    "done": false,
    "info": {
        "error": "具体的错误信息"
    },
    "metadata": {
        "step_num": 0,
        "timestamp": "2025-01-XX...",
        "screenshot_file": null,
        "action": null,
        "validation_failed": true
    }
}
```

这样LLM可以从返回的`info.error`字段中看到具体的验证错误，并修正参数。

---

## KEYBOARD_KEYS 完整列表

```python
KEYBOARD_KEYS = [
    # 特殊字符
    '\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+',
    ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^',
    '_', '`', '{', '|', '}', '~',

    # 数字
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',

    # 字母
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',

    # 功能键
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute',

    # F键
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24',

    # 其他
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert',
    'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright',
    'yen', 'command', 'option', 'optionleft', 'optionright'
]
```

---

## 工具总览表

| Tool Name | Action Type(s) | Required Params | Optional Params | 特殊验证 |
|-----------|---------------|----------------|----------------|---------|
| `desktop_mouse_move` | MOVE_TO | x, y | pause | x和y必须同时出现 |
| `desktop_mouse_click` | CLICK | - | x, y, button, num_clicks, pause | x/y同时出现；button∈{left,right,middle}；num_clicks∈{1,2,3} |
| `desktop_mouse_button` | MOUSE_DOWN, MOUSE_UP | action | button, pause | action∈{down,up}；button∈{left,right,middle} |
| `desktop_mouse_right_click` | RIGHT_CLICK | - | x, y, pause | x和y必须同时出现或同时缺失 |
| `desktop_mouse_double_click` | DOUBLE_CLICK | - | x, y, pause | x和y必须同时出现或同时缺失 |
| `desktop_mouse_drag` | DRAG_TO | x, y | pause | x和y都必须 |
| `desktop_scroll` | SCROLL | dx或dy至少一个 | dx, dy, pause | 至少提供dx或dy |
| `desktop_type` | TYPING | text | pause | text必须 |
| `desktop_key_press` | PRESS | key | pause | key必须在KEYBOARD_KEYS中 |
| `desktop_key_hold` | KEY_DOWN, KEY_UP | action, key | pause | action∈{down,up}；key在KEYBOARD_KEYS中 |
| `desktop_hotkey` | HOTKEY | keys (list) | pause | keys是列表；每个key在KEYBOARD_KEYS中 |
| `desktop_control` | WAIT, DONE, FAIL | action | pause | action∈{wait,done,fail}；生成字符串而非字典 |

---

## 实现验证的关键要点

1. **参数存在性检查**：必需参数缺失立即返回错误
2. **参数值域检查**：枚举值（button, num_clicks等）必须在允许范围内
3. **参数组合检查**：某些参数必须同时出现（如x和y）
4. **参数类型检查**：列表必须是list类型（如keys）
5. **特殊字符处理**：text参数使用repr()转义
6. **键盘键验证**：所有键名转小写后检查
7. **控制动作特殊处理**：WAIT/DONE/FAIL生成字符串而非字典
8. **错误信息清晰**：明确指出哪个参数有问题，如何修正

---

## 使用示例

### ✅ 正确用法

```python
# MOVE_TO
{"x": 100, "y": 200}

# CLICK - 多种组合
{}                                              # 当前位置左键单击
{"x": 100, "y": 200}                           # 指定位置左键单击
{"button": "right"}                             # 当前位置右键单击
{"x": 100, "y": 200, "button": "middle"}       # 指定位置中键单击
{"x": 100, "y": 200, "num_clicks": 2}          # 指定位置双击

# MOUSE_BUTTON
{"action": "down"}                              # 按下左键
{"action": "down", "button": "right"}          # 按下右键
{"action": "up", "button": "left"}             # 释放左键

# SCROLL
{"dy": -5}                                      # 向下滚动
{"dx": 3, "dy": -2}                            # 水平+垂直滚动

# TYPING
{"text": "Hello World!"}

# PRESS
{"key": "enter"}

# KEY_HOLD
{"action": "down", "key": "ctrl"}
{"action": "up", "key": "shift"}

# HOTKEY
{"keys": ["ctrl", "c"]}
{"keys": ["ctrl", "shift", "t"]}

# CONTROL
{"action": "wait"}
{"action": "done"}
{"action": "fail"}
```

### ❌ 错误用法

```python
# MOVE_TO - 只提供x或y
{"x": 100}                                      # ❌ 缺少y

# CLICK - x和y不匹配
{"x": 100, "button": "left"}                   # ❌ 有x没有y

# CLICK - 无效button
{"button": "center"}                            # ❌ button不在允许值中

# CLICK - 无效num_clicks
{"num_clicks": 5}                               # ❌ num_clicks必须是1,2,3

# MOUSE_BUTTON - 缺少action
{"button": "left"}                              # ❌ action是必需的

# SCROLL - 两个都缺失
{}                                              # ❌ 至少需要dx或dy

# TYPING - 缺少text
{}                                              # ❌ text是必需的

# PRESS - 无效key
{"key": "invalid_key"}                          # ❌ key不在KEYBOARD_KEYS中

# KEY_HOLD - 缺少参数
{"action": "down"}                              # ❌ 缺少key

# HOTKEY - keys不是列表
{"keys": "ctrl"}                                # ❌ keys必须是列表

# HOTKEY - 列表中有无效key
{"keys": ["ctrl", "invalid"]}                   # ❌ invalid不在KEYBOARD_KEYS中

# CONTROL - 无效action
{"action": "pause"}                             # ❌ action必须是wait/done/fail
```
