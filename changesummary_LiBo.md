# AgentFlow Environment Architecture Refactoring

## 概述

本次更新对 AgentFlow 的架构进行了重大重构,将 system prompt 生成和初始 observation 获取逻辑从 runner 层移到 Environment 层,实现了更好的封装和抽象。主要改进包括:

1. **System Prompt 模块化**: 创建独立的 prompts 模块管理所有 system prompts
2. **Environment 封装增强**: Environment 类负责生成完整的 system prompt 和初始 observation
3. **通用化 Runner**: `_run_conversation` 方法不再包含环境特定逻辑,可以通用地处理所有环境类型

## 架构设计理念

### 关注点分离 (Separation of Concerns)

```
┌─────────────────────────────────────────────┐
│          Runner Layer (run_osworld.py)       │
│  - 通用的对话流程控制                          │
│  - 不包含环境特定逻辑                          │
│  - 调用 environment 的统一接口                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Environment Layer (Environment类)       │
│  - 负责 system prompt 生成                    │
│  - 负责初始 observation 获取和格式化           │
│  - 负责工具管理                               │
│  - 负责环境特定配置                           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     Prompts Module (prompts/system_prompts)  │
│  - 集中管理所有 system prompts                │
│  - 提供 prompt 选择函数                       │
└─────────────────────────────────────────────┘
```

## 主要改动

### 1. 新增 `prompts/` 模块

**文件结构:**
```
src/prompts/
├── __init__.py                  # 模块导出
└── system_prompts.py            # 所有 system prompts 定义
```

**主要内容:**
- `SYSTEM_PROMPT_DEFAULT`: 通用 prompt (用于 math, web, rag 等环境)
- `SYSTEM_PROMPT_OSWORLD_COMPUTER13`: OSWorld computer_13 模式 prompt
- `SYSTEM_PROMPT_OSWORLD_PYAUTOGUI`: OSWorld pyautogui 模式 prompt
- `get_system_prompt(mode, action_space)`: 动态 prompt 选择函数

### 2. 修改 `envs/enviroment.py` (Environment 基类)

**新增方法:**

```python
def get_action_space(self) -> Optional[str]:
    """获取环境的 action space (如果适用)。

    子类可以覆盖此方法来返回特定的 action space。
    默认返回 None。
    """
    return None

def get_system_prompt(self, task_question: str) -> str:
    """获取完整的 system prompt。

    此方法:
    1. 根据 mode 和 action_space 选择 prompt 模板
    2. 替换占位符 (tool_descriptions, CLIENT_PASSWORD 等)
    3. 添加任务问题

    返回可直接使用的 system prompt 字符串。
    """
    # 实现细节见代码

def _replace_prompt_placeholders(self, prompt: str) -> str:
    """替换环境特定的占位符。

    子类可以覆盖此方法来处理特定的占位符。
    默认实现不做任何处理。
    """
    return prompt

def get_initial_observation(self, task_question: str) -> Optional[Dict[str, Any]]:
    """获取任务的初始 observation (如果适用)。

    返回原始 observation 数据,或 None (如果不需要)。
    子类应覆盖此方法来提供初始 observation。
    """
    return None

def format_observation_for_message(self, observation: Any) -> List[Dict[str, Any]]:
    """将 observation 格式化为 LLM 消息内容部分。

    返回消息内容部分列表 (文本、图像等)。
    子类应覆盖此方法来格式化特定的 observation 类型。
    """
    return []
```

### 3. 修改 `envs/osworld_environment.py`

**新增/覆盖方法:**

```python
def get_action_space(self) -> str:
    """获取 OSWorld 环境的 action space 模式。

    Returns:
        "computer_13" 或 "pyautogui"
    """
    return self.config.get("osworld", {}).get("action_space", "computer_13")

def _replace_prompt_placeholders(self, prompt: str) -> str:
    """替换 OSWorld 特定的占位符。

    处理 {CLIENT_PASSWORD} 占位符。
    """
    if "{CLIENT_PASSWORD}" in prompt:
        client_password = self.config.get("osworld", {}).get("client_password", "password")
        prompt = prompt.replace("{CLIENT_PASSWORD}", client_password)
    return prompt

def get_initial_observation(self, task_question: str) -> Optional[Dict[str, Any]]:
    """获取 OSWorld 任务的初始 observation。

    返回包含 screenshot 和 accessibility_tree 的字典。
    """
    if not self._desktop_env:
        return None
    return self.get_obs()

def format_observation_for_message(self, observation: Any) -> List[Dict[str, Any]]:
    """将 OSWorld observation 格式化为消息内容部分。

    返回:
        [
            {"type": "text", "text": "..."},
            {"type": "text", "text": "Accessibility tree:\n..."},
            {"type": "image_url", "image_url": {...}}
        ]
    """
    # 实现细节见代码
```

### 4. 重构 `run_osworld.py` 的 `_run_conversation` 方法

**重构前:**
```python
# 大量环境特定逻辑
if is_osworld:
    # 获取 observation
    # 格式化 observation
    # 添加到消息
```

**重构后:**
```python
# Step 1: Get system prompt from environment
system_prompt = self.environment.get_system_prompt(question)

# Step 2: Get initial observation from environment (if applicable)
initial_observation = self.environment.get_initial_observation(question)

# Format and add to messages
if initial_observation is not None:
    obs_content_parts = self.environment.format_observation_for_message(initial_observation)
    user_content.extend(obs_content_parts)
```

**关键改进:**
- ✅ 移除了 `if is_osworld:` 等环境特定判断
- ✅ 移除了 `get_system_prompt` 导入 (现在由 Environment 内部处理)
- ✅ 简化了 prompt 构建逻辑 (完全交给 Environment)
- ✅ 简化了 observation 处理逻辑 (完全交给 Environment)
- ✅ `_run_conversation` 现在是完全通用的

## 架构优势

### 1. **更好的封装**
- System prompt 生成逻辑完全封装在 Environment 类中
- Initial observation 获取和格式化逻辑完全封装在 Environment 类中
- Runner 不需要知道环境的内部细节

### 2. **更高的可维护性**
- 环境特定逻辑集中在环境类中,便于维护
- Prompt 模板集中管理,便于更新和版本控制
- 每个层次职责清晰,修改更安全

### 3. **更强的可扩展性**
- 添加新环境只需:
  1. 继承 Environment 类
  2. 实现 `mode` 属性
  3. (可选) 覆盖 `get_action_space()`
  4. (可选) 覆盖 `_replace_prompt_placeholders()`
  5. (可选) 覆盖 `get_initial_observation()` 和 `format_observation_for_message()`
- 添加新 prompt 只需在 `prompts/system_prompts.py` 中注册
- Runner 层完全不需要修改

### 4. **更好的测试性**
- 每个方法职责单一,易于单元测试
- Environment 的 prompt 生成逻辑可以独立测试
- Observation 格式化逻辑可以独立测试

### 5. **配置驱动**
- 基于 environment 的 `mode` 和 `action_space` 自动选择
- 无需手动判断环境类型
- 支持未来扩展到其他环境

## 使用示例

### OSWorld Computer_13 模式

```python
runner = AgentRunner(config)
runner.setup_environment(
    mode="osworld",
    path_to_vm="/path/to/vm",
    action_space="computer_13"  # 使用结构化工具
)
# Environment 自动:
# 1. 选择 SYSTEM_PROMPT_OSWORLD_COMPUTER13
# 2. 注册 computer_13 工具集
# 3. 准备初始 observation 获取逻辑
```

### OSWorld Pyautogui 模式

```python
runner = AgentRunner(config)
runner.setup_environment(
    mode="osworld",
    path_to_vm="/path/to/vm",
    action_space="pyautogui"  # 使用 Python 脚本
)
# Environment 自动:
# 1. 选择 SYSTEM_PROMPT_OSWORLD_PYAUTOGUI
# 2. 注册 pyautogui 工具集
# 3. 准备初始 observation 获取逻辑
```

### 其他环境 (默认 prompt)

```python
runner = AgentRunner(config)
runner.setup_environment(mode="math")  # 或 "web", "rag", "py"
# Environment 自动:
# 1. 选择 SYSTEM_PROMPT_DEFAULT
# 2. get_initial_observation() 返回 None (无需初始 observation)
```

## Prompt 映射规则

| Environment Mode | Action Space | 使用的 Prompt | 初始 Observation |
|------------------|--------------|---------------|------------------|
| `osworld` | `computer_13` | `SYSTEM_PROMPT_OSWORLD_COMPUTER13` | ✅ Screenshot + A11y Tree |
| `osworld` | `pyautogui` | `SYSTEM_PROMPT_OSWORLD_PYAUTOGUI` | ✅ Screenshot + A11y Tree |
| `math` | `None` | `SYSTEM_PROMPT_DEFAULT` | ❌ None |
| `web` | `None` | `SYSTEM_PROMPT_DEFAULT` | ❌ None |
| `rag` | `None` | `SYSTEM_PROMPT_DEFAULT` | ❌ None |
| `py` | `None` | `SYSTEM_PROMPT_DEFAULT` | ❌ None |

## 工具区分

### Computer_13 模式工具列表
1. `desktop_mouse_move` - 鼠标移动
2. `desktop_mouse_click` - 鼠标点击
3. `desktop_mouse_right_click` - 右键点击
4. `desktop_mouse_double_click` - 双击
5. `desktop_mouse_button` - 鼠标按钮按下/释放
6. `desktop_mouse_drag` - 拖拽
7. `desktop_scroll` - 滚动
8. `desktop_type` - 输入文本
9. `desktop_key_press` - 按键
10. `desktop_key_hold` - 按住/释放按键
11. `desktop_hotkey` - 组合键
12. `desktop_control` - 控制信号 (WAIT/DONE/FAIL)

### Pyautogui 模式工具列表
1. `desktop_execute_python_script` - 执行 Python 脚本
2. `desktop_control` - 控制信号 (WAIT/DONE/FAIL)

两种模式共享三个控制工具:
- `WAIT` - 等待下一个操作
- `DONE` - 标记任务完成
- `FAIL` - 标记任务失败

## 未来扩展示例

添加新环境非常简单:

```python
# 1. 在 prompts/system_prompts.py 中添加 prompt
SYSTEM_PROMPT_NEW_ENV = """..."""

SYSTEM_PROMPTS = {
    ...
    "new_env": SYSTEM_PROMPT_NEW_ENV,
}

# 2. 创建新环境类
class NewEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "new_env"

    # 如果需要初始 observation,覆盖这些方法
    def get_initial_observation(self, task_question: str):
        # 返回初始状态数据
        return {"state": "..."}

    def format_observation_for_message(self, observation):
        # 格式化为消息内容
        return [{"type": "text", "text": f"State: {observation['state']}"}]

# 3. Runner 无需任何修改!
runner = AgentRunner(config)
runner.setup_environment(mode="new_env")
# 自动工作!
```

## 测试建议

### 单元测试
1. 测试 `Environment.get_system_prompt()` 能否正确生成 prompt
2. 测试 `OSWorldEnvironment._replace_prompt_placeholders()` 能否正确替换密码
3. 测试 `OSWorldEnvironment.get_initial_observation()` 能否获取 observation
4. 测试 `OSWorldEnvironment.format_observation_for_message()` 能否正确格式化

### 集成测试
1. 测试 computer_13 模式的完整流程
2. 测试 pyautogui 模式的完整流程
3. 测试其他环境 (math/web/rag) 的流程
4. 验证 trajectory 保存功能

### 验证点
- ✅ {CLIENT_PASSWORD} 占位符正确替换
- ✅ {tool_descriptions} 占位符正确替换
- ✅ 初始 observation 正确添加到消息
- ✅ 不同 action_space 使用正确的 prompt
- ✅ Runner 层不包含环境特定逻辑

## 相关文件清单

### 新增文件
- ✅ `src/prompts/__init__.py` - Prompts 模块初始化
- ✅ `src/prompts/system_prompts.py` - 所有 system prompts 定义

### 修改文件
- ✅ `src/envs/enviroment.py` - 添加 4 个新方法到基类
  - `get_action_space()`
  - `get_system_prompt()`
  - `_replace_prompt_placeholders()`
  - `get_initial_observation()`
  - `format_observation_for_message()`

- ✅ `src/envs/osworld_environment.py` - 实现/覆盖新方法
  - `get_action_space()` - 返回 action_space
  - `_replace_prompt_placeholders()` - 处理 {CLIENT_PASSWORD}
  - `get_initial_observation()` - 获取桌面状态
  - `format_observation_for_message()` - 格式化为消息内容

- ✅ `src/run_osworld.py` - 重构 `_run_conversation()`
  - 移除环境特定判断 (`if is_osworld:`)
  - 移除 `from prompts import get_system_prompt` 导入
  - 使用 `environment.get_system_prompt()`
  - 使用 `environment.get_initial_observation()`
  - 使用 `environment.format_observation_for_message()`

## 向后兼容性

- ✅ 配置参数完全不变
- ✅ 工具注册机制不变
- ✅ 外部 API 接口不变
- ✅ 现有环境类 (Math, Web, RAG, Python) 无需修改即可工作
- ⚠️  `run_osworld.py` 中的 `_run_conversation` 方法已重构

## 迁移指南

如果其他代码也在使用类似的模式,可以参考以下步骤迁移:

1. **不要直接调用 `get_system_prompt()` 函数**
   ```python
   # ❌ 旧方式
   from prompts import get_system_prompt
   prompt = get_system_prompt(mode, action_space)

   # ✅ 新方式
   prompt = environment.get_system_prompt(question)
   ```

2. **不要直接获取和格式化 observation**
   ```python
   # ❌ 旧方式
   if is_osworld:
       obs = environment.get_obs()
       formatted = environment.format_observation_for_message(obs)

   # ✅ 新方式
   obs = environment.get_initial_observation(question)
   if obs is not None:
       formatted = environment.format_observation_for_message(obs)
   ```

3. **不要做环境类型判断**
   ```python
   # ❌ 旧方式
   if environment.mode == "osworld":
       # OSWorld 特定逻辑

   # ✅ 新方式
   # 让 environment 自己处理,调用统一接口
   ```

## 总结

这次重构实现了真正的关注点分离:

- **Prompts 模块**: 只负责存储 prompt 模板
- **Environment 类**: 负责生成完整 prompt 和处理 observation
- **Runner 类**: 只负责通用的对话流程控制

这种架构使得代码更加模块化、可维护、可扩展,并且更容易测试。
