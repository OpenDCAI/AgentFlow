# AgentFlow 运行框架架构说明

## 目录
- [概述](#概述)
- [运行流程](#运行流程)
- [核心模块详解](#核心模块详解)
- [Environment 生命周期方法](#environment-生命周期方法)
- [模块间交互流程](#模块间交互流程)
- [扩展指南](#扩展指南)

---

## 概述

AgentFlow 是一个通用的智能体运行框架，支持在不同环境（Environment）下执行基准测试（Benchmark）任务。框架采用环境抽象设计，通过统一的生命周期接口实现对不同类型环境的支持。

### 核心设计原则

1. **环境抽象**：所有环境特定逻辑封装在 Environment 类中
2. **统一接口**：Runner 通过统一的生命周期方法与 Environment 交互
3. **职责分离**：
   - **Runner**：流程控制、对话管理、结果保存
   - **Environment**：环境管理、工具注册、观察获取
   - **Benchmark**：任务数据加载和组织

---

## 运行流程

### 整体流程图

```
AgentRunner.run_benchmark()
│
├─> env.env_start()                          # [1] 环境启动（一次）
│   └─> OSWorld: 初始化 DesktopEnv
│
├─> for each task in tasks:                  # [2] 遍历所有任务
│   │
│   ├─> run_single_task(task)                # [3] 单任务执行
│   │   │
│   │   ├─> env.get_task_output_dir()        # [3.1] 获取任务输出目录
│   │   │   └─> OSWorld: "results/osworld/{task_id}/{model_name}"
│   │   │
│   │   ├─> env.env_task_init(task)          # [3.2] 任务初始化
│   │   │   └─> OSWorld:
│   │   │       ├─> reset(task)              # 重置环境
│   │   │       ├─> start_recording()        # 开始录屏
│   │   │       ├─> 清空轨迹存储
│   │   │       └─> 返回 {'text': a11y_tree, 'image': screenshot}
│   │   │
│   │   ├─> _run_conversation(question, initial_obs)  # [3.3] 多轮对话
│   │   │   │
│   │   │   ├─> env.get_system_prompt(question)      # 获取系统提示词
│   │   │   │   └─> 从 prompts 模块选择提示词模板
│   │   │   │       根据 env.mode 和 env.get_action_space()
│   │   │   │
│   │   │   ├─> 构建初始消息（包含 initial_obs）      # 添加初始观察
│   │   │   │   └─> 格式化为 LLM 消息格式
│   │   │   │
│   │   │   └─> while turn < max_turns:              # 对话循环
│   │   │       │
│   │   │       ├─> LLM 生成响应
│   │   │       │
│   │   │       ├─> if tool_calls:                   # 工具调用
│   │   │       │   │
│   │   │       │   ├─> env.execute_tool(name, args) # 执行工具
│   │   │       │   │   └─> OSWorld: 调用 Desktop Action Tool
│   │   │       │   │       返回 {'status', 'response', 'observation'}
│   │   │       │   │
│   │   │       │   ├─> if observation exists:       # 处理观察数据
│   │   │       │   │   ├─> env.add_step_to_trajectory(obs, step_idx)
│   │   │       │   │   │   └─> OSWorld: 存储到 _current_trajectory
│   │   │       │   │   │
│   │   │       │   │   └─> 格式化 obs 并添加到消息
│   │   │       │   │       {'text': a11y, 'image': screenshot}
│   │   │       │   │
│   │   │       │   └─> 继续下一轮
│   │   │       │
│   │   │       └─> else: 对话结束
│   │   │
│   │   ├─> 保存对话和轨迹                            # [3.4] 保存结果
│   │   │   └─> _save_conversation_and_trajectory()
│   │   │
│   │   └─> finally: env.env_task_end(task_id, output_dir)  # [3.5] 任务清理
│   │       └─> OSWorld:
│   │           ├─> end_recording()                  # 结束录屏
│   │           ├─> _save_trajectory_to_files()      # 保存轨迹
│   │           │   ├─> step_0.png, step_0_accessibility_tree.txt
│   │           │   ├─> step_1.png, step_1_accessibility_tree.txt
│   │           │   └─> ...
│   │           ├─> evaluate()                       # 评估任务
│   │           └─> 保存 result.txt
│   │
│   └─> 返回任务结果
│
└─> finally: env.env_close()                 # [4] 环境关闭（一次）
    └─> OSWorld: 关闭 DesktopEnv
```

### 流程说明

#### 阶段 1: 环境启动（Benchmark 级别）
- **触发点**：`run_benchmark()` 开始
- **调用方法**：`env.env_start()`
- **OSWorld 行为**：初始化 DesktopEnv（虚拟机连接）
- **其他环境**：通常为空操作

#### 阶段 2-3: 任务循环（Task 级别）
每个任务执行以下步骤：

**3.1 获取输出目录**
- **调用**：`env.get_task_output_dir(output_dir, task_id, model_name)`
- **返回**：任务专属目录路径或 None

**3.2 任务初始化**
- **调用**：`initial_obs = env.env_task_init(task)`
- **返回**：初始观察（observation）或 None
- **OSWorld 执行**：
  1. `reset(task)` - 重置虚拟机到任务初始状态
  2. `start_recording()` - 开始屏幕录制
  3. 清空 `_current_trajectory` 列表
  4. `get_obs()` - 获取截图和可访问性树
  5. 格式化并存储到轨迹
  6. 返回 `{'text': linearized_a11y_tree, 'image': base64_screenshot}`

**3.3 多轮对话**
- **系统提示词**：
  - 调用 `env.get_system_prompt(question)`
  - 根据 `env.mode` 和 `env.get_action_space()` 选择模板
  - OSWorld computer_13: 结构化动作工具提示词
  - OSWorld pyautogui: Python 脚本执行提示词

- **初始消息构建**：
  - 如果 `initial_obs` 不为 None，转换为 LLM 消息格式
  - 添加文本部分（可访问性树）
  - 添加图像部分（base64 截图）

- **对话循环**：
  - LLM 生成工具调用
  - 执行工具：`env.execute_tool(tool_name, tool_args)`
  - 处理返回的 observation：
    - 调用 `env.add_step_to_trajectory(obs, step_idx)` 存储
    - 格式化为消息内容并添加到对话

**3.4 保存结果**
- 保存完整对话历史（conversation.json）
- 保存轨迹摘要（trajectory.json, trajectory.txt）

**3.5 任务清理**
- **调用**：`env.env_task_end(task_id, task_output_dir)`
- **OSWorld 执行**：
  1. `end_recording(path)` - 停止录屏并保存视频
  2. `_save_trajectory_to_files(output_dir)` - 保存轨迹
     - 遍历 `_current_trajectory`
     - 保存每个 step 的截图和可访问性树
  3. `evaluate()` - 评估任务结果
  4. 保存 result.txt
  5. 清空 `_current_trajectory` 和 `_current_task_id`

#### 阶段 4: 环境关闭（Benchmark 级别）
- **触发点**：`run_benchmark()` 结束（finally 块）
- **调用方法**：`env.env_close()`
- **OSWorld 行为**：关闭 DesktopEnv 并释放资源

---

## 核心模块详解

### 1. AgentRunner（src/run_osworld.py）

#### 职责
- 流程控制器，协调 Environment 和 Benchmark
- 管理对话流程和 LLM 交互
- 保存结果和轨迹数据

#### 关键方法

**`run_benchmark(parallel, output_dir)`**
```python
def run_benchmark(self, parallel: bool = False, output_dir: str = "results"):
    """运行整个基准测试"""

    # [引用 Environment] 启动环境
    self.environment.env_start()

    try:
        # 准备任务列表
        tasks = [...]

        # 执行所有任务
        for task in tasks:
            result = self.run_single_task(task, output_dir)

    finally:
        # [引用 Environment] 关闭环境
        self.environment.env_close()
```

**引用的 Environment 方法**：
- `env_start()` - 环境初始化
- `env_close()` - 环境清理

---

**`run_single_task(task, output_dir)`**
```python
def run_single_task(self, task: Dict[str, Any], output_dir: str):
    """执行单个任务"""

    # [引用 Environment] 获取输出目录
    task_output_dir = self.environment.get_task_output_dir(
        output_dir, task_id, self.config.model_name
    )

    # [引用 Environment] 初始化任务，获取初始观察
    initial_obs = self.environment.env_task_init(task)
    # 返回: {'text': str, 'image': str} 或 None

    try:
        # [传递 initial_obs] 运行对话
        messages = self._run_conversation(
            question, task_id, initial_obs=initial_obs
        )

        # 提取答案和保存结果
        final_answer = self._extract_final_answer(messages)
        self._save_conversation_and_trajectory(...)

    finally:
        # [引用 Environment] 结束任务，保存轨迹和评估
        self.environment.env_task_end(task_id, task_output_dir)
```

**引用的 Environment 方法**：
- `get_task_output_dir(base_dir, task_id, model_name)` - 获取任务输出路径
- `env_task_init(task)` - 任务初始化，返回初始观察
- `env_task_end(task_id, output_dir)` - 任务清理和评估

---

**`_run_conversation(question, task_id, initial_obs, ...)`**
```python
def _run_conversation(self, question, task_id, initial_obs=None, ...):
    """多轮对话主循环"""

    # [引用 Environment] 获取系统提示词
    system_prompt = self.environment.get_system_prompt(question)
    # 内部调用:
    #   - env.mode (属性)
    #   - env.get_action_space() (OSWorld 专用)
    #   - prompts.get_system_prompt(mode, action_space)
    #   - env._replace_prompt_placeholders(prompt) (OSWorld 替换密码)

    messages = [{"role": "system", "content": system_prompt}]

    # 构建初始消息（包含 initial_obs）
    user_content = [{"type": "text", "text": f"Question: {question}"}]

    if initial_obs is not None:
        # initial_obs 格式: {'text': str, 'image': str}
        user_content.append({
            "type": "text",
            "text": f"Accessibility tree:\n{initial_obs['text']}"
        })
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{initial_obs['image']}"}
        })

    messages.append({"role": "user", "content": user_content})

    # 对话循环
    step_idx = 0
    while turn_count < max_turns:
        # 调用 LLM
        response = client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            tools=self.environment.get_tool_schemas()  # [引用 Environment]
        )

        if tool_calls:
            for tool_call in tool_calls:
                # [引用 Environment] 执行工具
                tool_result = self.environment.execute_tool(
                    tool_name, tool_args
                )
                # 返回: JSON字符串 {'status', 'response', 'observation'}

                # 处理观察数据（如果存在）
                observation = tool_result.get('observation', {})
                if observation:
                    step_idx += 1

                    # [引用 Environment] 添加到轨迹存储
                    if hasattr(self.environment, 'add_step_to_trajectory'):
                        self.environment.add_step_to_trajectory(
                            observation, step_idx
                        )

                    # 格式化观察数据为消息内容
                    obs_parts = []
                    if observation.get('text'):
                        obs_parts.append({
                            "type": "text",
                            "text": f"Current State:\n{observation['text']}"
                        })
                    if observation.get('image'):
                        obs_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{observation['image']}"
                            }
                        })

                    # 添加到工具响应消息
                    messages.append({
                        "role": "tool",
                        "content": [execution_result] + obs_parts
                    })
        else:
            # 对话结束
            break

    return messages
```

**引用的 Environment 方法**：
- `get_system_prompt(question)` - 获取系统提示词
  - 内部调用 `mode` 属性
  - 内部调用 `get_action_space()` (OSWorld)
  - 内部调用 `_replace_prompt_placeholders()` (OSWorld)
- `get_tool_schemas()` - 获取工具定义
- `execute_tool(tool_name, args)` - 执行工具
- `add_step_to_trajectory(obs, step)` - 添加观察到轨迹（OSWorld 专用）

---

### 2. Environment 基类（src/envs/enviroment.py）

#### 职责
- 定义环境抽象接口
- 管理工具注册和执行
- 提供默认的生命周期实现

#### 核心方法

**系统提示词相关**

```python
def get_system_prompt(self, task_question: str) -> str:
    """获取完整的系统提示词"""
    from prompts import get_system_prompt as get_prompt_template

    # 获取环境模式和动作空间
    environment_mode = self.mode  # 子类实现
    action_space = self.get_action_space()  # 子类可重写

    # 从 prompts 模块获取模板
    system_prompt_template = get_prompt_template(environment_mode, action_space)

    # 替换工具描述占位符
    system_prompt = system_prompt_template.replace(
        "{tool_descriptions}",
        self.get_tool_descriptions()
    )

    # 替换环境特定占位符（子类可重写）
    system_prompt = self._replace_prompt_placeholders(system_prompt)

    # 添加任务问题
    system_prompt += f"\nYou are asked to complete the following task: {task_question}"

    return system_prompt

def get_action_space(self) -> Optional[str]:
    """获取动作空间类型（子类可重写）"""
    return None

def _replace_prompt_placeholders(self, prompt: str) -> str:
    """替换环境特定占位符（子类可重写）"""
    return prompt
```

**使用流程**：
1. Runner 调用 `env.get_system_prompt(question)`
2. 读取 `env.mode` 和 `env.get_action_space()`
3. 从 `prompts` 模块选择模板
4. 替换 `{tool_descriptions}`
5. 调用 `_replace_prompt_placeholders()` 进行环境特定替换
6. 添加任务问题

---

**生命周期方法**

```python
def env_task_init(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    任务初始化（子类重写）

    返回:
        初始观察 {'text': str, 'image': str} 或 None
    """
    return None

def env_task_end(self, task_id: str, task_output_dir: Optional[str] = None) -> None:
    """任务清理（子类重写）"""
    pass

def env_start(self) -> None:
    """环境启动（子类重写）"""
    pass

def env_close(self) -> None:
    """环境关闭（子类重写）"""
    pass
```

**工具管理**

```python
def get_tool_schemas(self) -> List[Dict[str, Any]]:
    """获取所有工具的 OpenAI function calling schema"""
    return self.tool_schemas

def execute_tool(self, tool_name: str, params: Union[str, dict], **kwargs) -> str:
    """执行工具并返回结果（JSON 字符串）"""
    tool = self.get_tool(tool_name)
    if not tool:
        return f"Tool '{tool_name}' not found"

    try:
        return tool.call(params, **kwargs)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
```

---

### 3. OSWorldEnvironment（src/envs/osworld_environment.py）

#### 职责
- OSWorld 桌面自动化环境实现
- 管理虚拟机（DesktopEnv）生命周期
- 处理截图、可访问性树等观察数据
- 存储和保存任务执行轨迹

#### 实例变量

```python
class OSWorldEnvironment(Environment):
    def __init__(self, **kwargs):
        self._desktop_env: Optional[DesktopEnv] = None  # 桌面环境实例

        # 轨迹存储
        self._current_trajectory: List[Dict[str, Any]] = []  # 当前任务轨迹
        self._current_task_id: Optional[str] = None         # 当前任务 ID
```

#### 核心方法实现

**1. 环境属性**

```python
@property
def mode(self) -> str:
    """环境模式标识"""
    return "osworld"

def get_action_space(self) -> str:
    """获取动作空间类型"""
    return self.config.get("osworld", {}).get("action_space", "computer_13")
    # 返回: "computer_13" 或 "pyautogui"
```

**Runner 调用链**：
```
runner._run_conversation()
  └─> env.get_system_prompt(question)
      ├─> env.mode  # 返回 "osworld"
      └─> env.get_action_space()  # 返回 "computer_13" 或 "pyautogui"
          └─> prompts.get_system_prompt("osworld", "computer_13")
              └─> 返回对应的提示词模板
```

---

**2. 提示词占位符替换**

```python
def _replace_prompt_placeholders(self, prompt: str) -> str:
    """替换 {CLIENT_PASSWORD} 占位符"""
    if "{CLIENT_PASSWORD}" in prompt:
        client_password = self.config.get("osworld", {}).get(
            "client_password", "password"
        )
        prompt = prompt.replace("{CLIENT_PASSWORD}", client_password)
    return prompt
```

**Runner 调用链**：
```
runner._run_conversation()
  └─> env.get_system_prompt(question)
      └─> env._replace_prompt_placeholders(prompt)
          └─> 替换提示词中的 {CLIENT_PASSWORD}
```

---

**3. 任务初始化**

```python
def env_task_init(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    初始化 OSWorld 任务

    执行步骤:
    1. 存储任务 ID
    2. 重置虚拟机环境
    3. 开始屏幕录制
    4. 清空轨迹存储
    5. 获取初始观察
    6. 存储到轨迹
    7. 返回格式化的观察
    """
    task_id = task.get('id', 'unknown')
    self._current_task_id = task_id

    # 重置环境
    self.reset(task)  # 调用 DesktopEnv.reset()

    # 开始录屏
    self.start_recording()  # 调用 DesktopEnv.controller.start_recording()

    # 清空轨迹
    self._current_trajectory = []

    # 获取初始观察
    raw_obs = self.get_obs()  # 调用 DesktopEnv.observation()
    # 返回: {'screenshot': bytes, 'accessibility_tree': dict}

    if not raw_obs:
        return None

    # 格式化观察
    formatted_obs = self._format_observation_for_llm(raw_obs)
    # 返回: {'screenshot': base64_str, 'a11y_tree': linearized_str}

    # 存储到轨迹
    self._current_trajectory.append({
        'step': 0,
        'type': 'initial_observation',
        'text': formatted_obs.get('a11y_tree', ''),
        'image': formatted_obs.get('screenshot', '')
    })

    # 返回给 Runner
    return {
        'text': formatted_obs.get('a11y_tree', ''),
        'image': formatted_obs.get('screenshot', '')
    }
```

**Runner 调用链**：
```
runner.run_single_task(task)
  └─> initial_obs = env.env_task_init(task)
      ├─> env.reset(task)
      │   └─> DesktopEnv.reset(task)
      ├─> env.start_recording()
      │   └─> DesktopEnv.controller.start_recording()
      ├─> env.get_obs()
      │   └─> DesktopEnv.observation()
      │       └─> 返回 {'screenshot': bytes, 'accessibility_tree': dict}
      └─> env._format_observation_for_llm(raw_obs)
          ├─> env._linearize_accessibility_tree()
          ├─> env._trim_accessibility_tree()
          └─> env._encode_image()
              └─> 返回 {'text': a11y_tree, 'image': base64_screenshot}
```

---

**4. 添加步骤到轨迹**

```python
def add_step_to_trajectory(self, observation: Dict[str, Any], step_number: int):
    """添加工具执行后的观察到轨迹"""
    self._current_trajectory.append({
        'step': step_number,
        'type': 'action_observation',
        'text': observation.get('text', ''),
        'image': observation.get('image', '')
    })
```

**Runner 调用链**：
```
runner._run_conversation()
  └─> 工具执行后
      └─> if observation exists:
          └─> env.add_step_to_trajectory(observation, step_idx)
              └─> 添加到 self._current_trajectory 列表
```

---

**5. 任务结束**

```python
def env_task_end(self, task_id: str, task_output_dir: Optional[str] = None):
    """
    结束 OSWorld 任务

    执行步骤:
    1. 结束屏幕录制并保存视频
    2. 保存轨迹文件（截图 + 可访问性树）
    3. 评估任务结果
    4. 保存评估分数到 result.txt
    5. 清空轨迹存储
    """
    # 结束录屏
    if task_output_dir:
        recording_path = os.path.join(task_output_dir, f"task_{task_id}.mp4")
        self.end_recording(recording_path)  # 调用 DesktopEnv.controller.end_recording()

    # 保存轨迹文件
    if task_output_dir and self._current_trajectory:
        self._save_trajectory_to_files(task_output_dir)
        # 为每个 step 保存:
        #   - step_N.png (base64 解码的截图)
        #   - step_N_accessibility_tree.txt (可访问性树文本)

    # 评估任务
    score = self.evaluate()  # 调用 DesktopEnv.evaluate()

    # 保存评估结果
    if task_output_dir:
        result_file = os.path.join(task_output_dir, "result.txt")
        with open(result_file, "w") as f:
            f.write(f"{score}\n")

    # 清空轨迹
    self._current_trajectory = []
    self._current_task_id = None
```

**Runner 调用链**：
```
runner.run_single_task(task)
  └─> finally:
      └─> env.env_task_end(task_id, task_output_dir)
          ├─> env.end_recording(path)
          │   └─> DesktopEnv.controller.end_recording()
          ├─> env._save_trajectory_to_files(output_dir)
          │   └─> for each step in _current_trajectory:
          │       ├─> 保存 step_N.png
          │       └─> 保存 step_N_accessibility_tree.txt
          ├─> env.evaluate()
          │   └─> DesktopEnv.evaluate()
          └─> 保存 result.txt
```

---

**6. 环境启动和关闭**

```python
def env_start(self) -> None:
    """启动 OSWorld 环境（Benchmark 开始时调用一次）"""
    if self._desktop_env is None:
        self.setup()  # 初始化 DesktopEnv（连接虚拟机）

def env_close(self) -> None:
    """关闭 OSWorld 环境（Benchmark 结束时调用一次）"""
    if self._desktop_env:
        self._desktop_env.close()  # 关闭虚拟机连接
        self._desktop_env = None
```

**Runner 调用链**：
```
runner.run_benchmark()
  ├─> env.env_start()
  │   └─> env.setup()
  │       └─> self._desktop_env = DesktopEnv(...)
  │
  └─> finally:
      └─> env.env_close()
          └─> DesktopEnv.close()
```

---

**7. 工具执行**

```python
# 工具已在 _initialize_tools() 中注册
def _initialize_tools(self):
    """注册 OSWorld 工具"""
    # 根据 action_space 注册不同的工具
    action_space = self.config.get("osworld", {}).get("action_space", "computer_13")

    if action_space == "computer_13":
        # 注册结构化动作工具
        self.register_tool(MouseTool(...))
        self.register_tool(KeyboardTool(...))
    elif action_space == "pyautogui":
        # 注册 Python 脚本工具
        self.register_tool(PyAutoGUIScriptTool(...))

    # 共享的控制工具
    self.register_tool(ControlTool(...))
```

**Runner 调用链**：
```
runner._run_conversation()
  └─> env.execute_tool(tool_name, args)
      └─> tool.call(args)
          └─> DesktopActionTool.call()
              ├─> env.step(action)  # 执行动作
              │   └─> DesktopEnv.step(action)
              └─> env.get_obs()  # 获取新观察
                  └─> DesktopEnv.observation()
                      └─> 返回 {'screenshot': bytes, 'accessibility_tree': dict}

              └─> 返回 ToolResponse JSON:
                  {
                    'status': 'success',
                    'response': '动作执行成功',
                    'observation': {
                      'text': linearized_a11y_tree,
                      'image': base64_screenshot
                    }
                  }
```

---

### 4. Prompts 模块（src/prompts/system_prompts.py）

#### 职责
- 管理所有系统提示词模板
- 根据环境模式和动作空间选择提示词

#### 提示词映射

```python
SYSTEM_PROMPTS = {
    "default": SYSTEM_PROMPT_DEFAULT,
    "osworld_computer_13": SYSTEM_PROMPT_OSWORLD_COMPUTER13,
    "osworld_pyautogui": SYSTEM_PROMPT_OSWORLD_PYAUTOGUI,
    # 可扩展其他环境...
}

def get_system_prompt(environment_mode: str = "default",
                      action_space: str = None) -> str:
    """
    根据环境模式和动作空间选择提示词

    示例:
        get_system_prompt("osworld", "computer_13")
        -> SYSTEM_PROMPTS["osworld_computer_13"]

        get_system_prompt("osworld", "pyautogui")
        -> SYSTEM_PROMPTS["osworld_pyautogui"]

        get_system_prompt("math")
        -> SYSTEM_PROMPTS["math"] or SYSTEM_PROMPTS["default"]
    """
    if environment_mode == "osworld" and action_space:
        prompt_key = f"osworld_{action_space}"
    elif environment_mode and environment_mode != "default":
        prompt_key = environment_mode
    else:
        prompt_key = "default"

    return SYSTEM_PROMPTS.get(prompt_key, SYSTEM_PROMPTS["default"])
```

**调用链**：
```
Environment.get_system_prompt(question)
  └─> prompts.get_system_prompt(env.mode, env.get_action_space())
      └─> 返回对应的提示词模板字符串
```

---

## Environment 生命周期方法

### 方法分类

#### Benchmark 级别（整个测试执行一次）

| 方法 | 调用时机 | OSWorld 行为 | 其他环境 |
|------|---------|-------------|---------|
| `env_start()` | Benchmark 开始 | 初始化 DesktopEnv（连接虚拟机） | 通常为空 |
| `env_close()` | Benchmark 结束（finally） | 关闭 DesktopEnv（断开虚拟机） | 通常为空 |

#### Task 级别（每个任务执行一次）

| 方法 | 调用时机 | 返回值 | OSWorld 行为 |
|------|---------|-------|-------------|
| `get_task_output_dir()` | 任务开始前 | 输出目录路径 | `results/osworld/{task_id}/{model_name}` |
| `env_task_init(task)` | 任务开始 | 初始观察 | 重置环境→开始录屏→获取初始obs |
| `env_task_end(task_id, dir)` | 任务结束（finally） | 无 | 结束录屏→保存轨迹→评估→清理 |

#### 对话过程中（多次调用）

| 方法 | 调用时机 | 参数/返回 | 说明 |
|------|---------|----------|------|
| `get_system_prompt(question)` | 对话开始 | 返回提示词字符串 | 选择模板→替换占位符→添加任务 |
| `get_tool_schemas()` | 每轮 LLM 调用 | 返回工具定义列表 | 供 LLM function calling 使用 |
| `execute_tool(name, args)` | LLM 返回工具调用时 | 返回 JSON 字符串 | 执行工具→返回结果和观察 |
| `add_step_to_trajectory(obs, step)` | 工具返回观察时 | 无 | 添加到轨迹存储（OSWorld 专用） |

---

### 数据流转

#### 初始观察流转

```
env_task_init(task)
  └─> 返回 {'text': str, 'image': str}
      └─> runner.run_single_task() 接收
          └─> 传递给 _run_conversation(initial_obs=...)
              └─> 构建初始消息
                  ├─> 添加文本部分（可访问性树）
                  └─> 添加图像部分（base64 截图）
```

#### 工具观察流转

```
execute_tool(name, args)
  └─> 返回 JSON: {'status', 'response', 'observation': {'text', 'image'}}
      └─> runner._run_conversation() 解析
          ├─> 提取 observation
          │   └─> 调用 env.add_step_to_trajectory(obs, step)
          │       └─> OSWorld 存储到 _current_trajectory
          │
          └─> 格式化 observation 为消息内容
              ├─> 文本部分: "Current State:\n{text}"
              └─> 图像部分: base64 编码
```

#### 轨迹保存流转

```
env_task_end(task_id, output_dir)
  └─> OSWorld._save_trajectory_to_files(output_dir)
      └─> for each step in _current_trajectory:
          ├─> base64.b64decode(step['image'])
          │   └─> 保存 step_{N}.png
          │
          └─> step['text']
              └─> 保存 step_{N}_accessibility_tree.txt
```

---

## 模块间交互流程

### 完整交互时序图

```
用户启动 Benchmark
    │
    ├──────────────────────────────────────────────────────────┐
    │                  AgentRunner.run_benchmark()              │
    │──────────────────────────────────────────────────────────│
    │
    │  [1] 环境启动
    ├─> Environment.env_start()
    │      └─> OSWorld: 初始化 DesktopEnv
    │
    │  [2] 遍历任务
    ├─> for task in tasks:
    │   │
    │   ├──────────────────────────────────────────────────┐
    │   │         AgentRunner.run_single_task(task)        │
    │   ├──────────────────────────────────────────────────│
    │   │
    │   │  [2.1] 获取输出目录
    │   ├─> Environment.get_task_output_dir(...)
    │   │      └─> OSWorld: 返回 "results/osworld/{task_id}/{model}"
    │   │
    │   │  [2.2] 任务初始化
    │   ├─> initial_obs = Environment.env_task_init(task)
    │   │      │
    │   │      ├─> OSWorld.reset(task)
    │   │      │      └─> DesktopEnv.reset()
    │   │      │
    │   │      ├─> OSWorld.start_recording()
    │   │      │      └─> DesktopEnv.controller.start_recording()
    │   │      │
    │   │      ├─> OSWorld.get_obs()
    │   │      │      └─> DesktopEnv.observation()
    │   │      │          └─> {'screenshot': bytes, 'a11y_tree': dict}
    │   │      │
    │   │      └─> 返回 {'text': a11y_str, 'image': base64_str}
    │   │
    │   │  [2.3] 多轮对话
    │   ├─────────────────────────────────────────────────┐
    │   │       AgentRunner._run_conversation()           │
    │   ├─────────────────────────────────────────────────│
    │   │
    │   │  [2.3.1] 获取系统提示词
    │   ├─> Environment.get_system_prompt(question)
    │   │      │
    │   │      ├─> env.mode (属性)
    │   │      │      └─> OSWorld: "osworld"
    │   │      │
    │   │      ├─> Environment.get_action_space()
    │   │      │      └─> OSWorld: "computer_13" 或 "pyautogui"
    │   │      │
    │   │      ├─> prompts.get_system_prompt(mode, action_space)
    │   │      │      └─> 返回提示词模板
    │   │      │
    │   │      ├─> Environment._replace_prompt_placeholders(prompt)
    │   │      │      └─> OSWorld: 替换 {CLIENT_PASSWORD}
    │   │      │
    │   │      └─> 返回完整提示词
    │   │
    │   │  [2.3.2] 构建初始消息
    │   ├─> 如果 initial_obs 不为 None:
    │   │      ├─> 添加文本: "Accessibility tree:\n{text}"
    │   │      └─> 添加图像: "data:image/png;base64,{image}"
    │   │
    │   │  [2.3.3] 对话循环
    │   ├─> while turn < max_turns:
    │   │   │
    │   │   │  [2.3.3.1] LLM 调用
    │   │   ├─> OpenAI.chat.completions.create(
    │   │   │      messages=messages,
    │   │   │      tools=Environment.get_tool_schemas()  <─┐
    │   │   │   )                                          │
    │   │   │                                              │
    │   │   │  [2.3.3.2] 如果有工具调用                    │
    │   │   ├─> if tool_calls:                            │
    │   │   │   │                                          │
    │   │   │   │  [2.3.3.2.1] 执行工具                   │
    │   │   │   ├─> result_json = Environment.execute_tool(name, args)
    │   │   │   │      │                                   │
    │   │   │   │      └─> Tool.call(args)                │
    │   │   │   │          │                               │
    │   │   │   │          ├─> OSWorld.step(action)       │
    │   │   │   │          │      └─> DesktopEnv.step()   │
    │   │   │   │          │                               │
    │   │   │   │          ├─> OSWorld.get_obs()          │
    │   │   │   │          │      └─> DesktopEnv.observation()
    │   │   │   │          │          └─> {'screenshot', 'a11y_tree'}
    │   │   │   │          │                               │
    │   │   │   │          └─> 返回 JSON:                 │
    │   │   │   │              {                           │
    │   │   │   │                'status': 'success',      │
    │   │   │   │                'response': '...',        │
    │   │   │   │                'observation': {          │
    │   │   │   │                  'text': a11y_str,       │
    │   │   │   │                  'image': base64_str     │
    │   │   │   │                }                         │
    │   │   │   │              }                           │
    │   │   │   │                                          │
    │   │   │   │  [2.3.3.2.2] 处理观察                   │
    │   │   │   ├─> if observation exists:                │
    │   │   │   │   │                                      │
    │   │   │   │   ├─> Environment.add_step_to_trajectory(obs, step)
    │   │   │   │   │      └─> OSWorld: 添加到 _current_trajectory
    │   │   │   │   │                                      │
    │   │   │   │   └─> 格式化 obs 并添加到 messages      │
    │   │   │   │                                          │
    │   │   │   └─> 继续下一轮                            │
    │   │   │                                              │
    │   │   └─> else: 对话结束                            │
    │   │                                                  │
    │   ├─> 返回 messages                                 │
    │   └─────────────────────────────────────────────────┘
    │   │
    │   │  [2.4] 保存对话和轨迹
    │   ├─> _save_conversation_and_trajectory(...)
    │   │      ├─> 保存 conversation.json
    │   │      ├─> 保存 trajectory.json
    │   │      └─> 保存 trajectory.txt
    │   │
    │   │  [2.5] 任务清理
    │   └─> finally: Environment.env_task_end(task_id, output_dir)
    │          │
    │          ├─> OSWorld.end_recording(path)
    │          │      └─> DesktopEnv.controller.end_recording()
    │          │          └─> 保存 task_{id}.mp4
    │          │
    │          ├─> OSWorld._save_trajectory_to_files(output_dir)
    │          │      └─> for each step in _current_trajectory:
    │          │          ├─> 保存 step_{N}.png
    │          │          └─> 保存 step_{N}_accessibility_tree.txt
    │          │
    │          ├─> OSWorld.evaluate()
    │          │      └─> DesktopEnv.evaluate()
    │          │          └─> 返回评分
    │          │
    │          └─> 保存 result.txt
    │
    │  [3] 环境关闭
    └─> finally: Environment.env_close()
           └─> OSWorld: 关闭 DesktopEnv
```

---

### 关键交互点详解

#### 交互点 1: 系统提示词生成

```
调用路径:
AgentRunner._run_conversation()
  └─> Environment.get_system_prompt(question)
      └─> [内部调用链]
          ├─> self.mode  (读取环境模式)
          ├─> self.get_action_space()  (读取动作空间，OSWorld 专用)
          ├─> prompts.get_system_prompt(mode, action_space)
          ├─> self.get_tool_descriptions()  (获取工具描述)
          ├─> self._replace_prompt_placeholders(prompt)  (替换占位符)
          └─> 拼接任务问题

涉及模块:
- AgentRunner: 发起调用
- Environment 基类: 协调流程
- OSWorldEnvironment: 提供 mode、action_space、占位符替换
- Prompts 模块: 提供提示词模板
```

#### 交互点 2: 初始观察获取

```
调用路径:
AgentRunner.run_single_task(task)
  └─> Environment.env_task_init(task)
      └─> [OSWorld 内部调用链]
          ├─> self.reset(task)
          │   └─> DesktopEnv.reset()
          ├─> self.start_recording()
          │   └─> DesktopEnv.controller.start_recording()
          ├─> self.get_obs()
          │   └─> DesktopEnv.observation()
          ├─> self._format_observation_for_llm(raw_obs)
          │   ├─> self._linearize_accessibility_tree()
          │   ├─> self._trim_accessibility_tree()
          │   └─> self._encode_image()
          └─> 存储到 self._current_trajectory
              返回 {'text': str, 'image': str}

涉及模块:
- AgentRunner: 发起调用，接收返回值
- OSWorldEnvironment: 实现完整初始化逻辑
- DesktopEnv: 提供底层虚拟机操作
```

#### 交互点 3: 工具执行

```
调用路径:
AgentRunner._run_conversation()
  └─> Environment.execute_tool(tool_name, args)
      └─> Tool.call(args)
          └─> [OSWorld Tool 内部调用链]
              ├─> self.environment.step(action)
              │   └─> DesktopEnv.step(action)
              ├─> self.environment.get_obs()
              │   └─> DesktopEnv.observation()
              └─> self.environment._format_observation_for_llm(obs)
                  └─> 返回 ToolResponse JSON

返回给 Runner:
  └─> JSON 字符串解析
      └─> 如果有 observation:
          └─> Environment.add_step_to_trajectory(obs, step)
              └─> OSWorld: 添加到 _current_trajectory

涉及模块:
- AgentRunner: 发起调用，处理返回值
- Environment 基类: 工具管理和执行
- OSWorld Tools: 实现具体动作
- OSWorldEnvironment: 提供 step() 和 get_obs()
- DesktopEnv: 底层执行
```

#### 交互点 4: 轨迹保存

```
调用路径:
AgentRunner.run_single_task()
  └─> finally: Environment.env_task_end(task_id, output_dir)
      └─> [OSWorld 内部调用链]
          ├─> self.end_recording(path)
          │   └─> DesktopEnv.controller.end_recording()
          │
          ├─> self._save_trajectory_to_files(output_dir)
          │   └─> for step in self._current_trajectory:
          │       ├─> base64.b64decode(step['image'])
          │       │   └─> 保存 PNG 文件
          │       └─> step['text']
          │           └─> 保存 TXT 文件
          │
          └─> self.evaluate()
              └─> DesktopEnv.evaluate()

涉及模块:
- AgentRunner: 在 finally 块中调用
- OSWorldEnvironment: 实现完整清理逻辑
- DesktopEnv: 提供录屏和评估
```

---

## 扩展指南

### 添加新环境

要添加新的环境类型（如 WebBrowserEnvironment），需要：

#### 1. 创建环境类

```python
# src/envs/web_environment.py
from envs.enviroment import Environment

class WebBrowserEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "webbrowser"

    def _initialize_tools(self):
        """注册 Web 浏览器工具"""
        self.register_tool(NavigateTool())
        self.register_tool(ClickTool())
        # ...

    # 根据需要重写生命周期方法
    def env_task_init(self, task):
        """如果需要初始观察，返回 {'text': str, 'image': str}"""
        # 打开浏览器，导航到起始页
        # 获取页面截图和 DOM 树
        return {'text': dom_tree, 'image': screenshot}

    def env_task_end(self, task_id, output_dir):
        """清理浏览器会话，保存历史记录"""
        pass
```

#### 2. 添加系统提示词

```python
# src/prompts/system_prompts.py
SYSTEM_PROMPT_WEBBROWSER = """
You are a web browsing agent...

Available tools:
{tool_descriptions}

Your task: {task_question}
"""

SYSTEM_PROMPTS = {
    "default": SYSTEM_PROMPT_DEFAULT,
    "osworld_computer_13": SYSTEM_PROMPT_OSWORLD_COMPUTER13,
    "osworld_pyautogui": SYSTEM_PROMPT_OSWORLD_PYAUTOGUI,
    "webbrowser": SYSTEM_PROMPT_WEBBROWSER,  # 添加新提示词
}
```

#### 3. 使用新环境

```python
from envs.web_environment import WebBrowserEnvironment

env = WebBrowserEnvironment(
    browser="chrome",
    headless=False
)

runner = AgentRunner(environment=env)
runner.load_benchmark("web_tasks.json")
runner.run_benchmark()
```

**无需修改 Runner 代码！** 所有环境特定逻辑都封装在环境类中。

---

### 常见扩展场景

#### 场景 1: 添加新的动作空间

如果 OSWorld 需要支持新的动作空间（如 "selenium"）：

1. 在 `osworld_environment.py` 中更新 `_initialize_tools()`：
```python
def _initialize_tools(self):
    action_space = self.get_action_space()
    if action_space == "selenium":
        self.register_tool(SeleniumScriptTool(self))
    # ...
```

2. 在 `system_prompts.py` 中添加新提示词：
```python
SYSTEM_PROMPT_OSWORLD_SELENIUM = """..."""
SYSTEM_PROMPTS["osworld_selenium"] = SYSTEM_PROMPT_OSWORLD_SELENIUM
```

#### 场景 2: 支持不同的观察格式

如果环境返回不同格式的观察（如音频、视频）：

```python
def env_task_init(self, task):
    # 返回自定义格式
    return {
        'text': transcript,
        'audio': base64_audio,
        'video': base64_video
    }
```

在 `_run_conversation` 中处理：
```python
if initial_obs is not None:
    if initial_obs.get('audio'):
        # 添加音频内容
        pass
    if initial_obs.get('video'):
        # 添加视频内容
        pass
```

#### 场景 3: 自定义轨迹格式

重写 `env_task_end` 来保存自定义格式的轨迹：

```python
def env_task_end(self, task_id, output_dir):
    # 保存为 HTML 报告
    html = self._generate_html_report(self._current_trajectory)
    with open(f"{output_dir}/report.html", "w") as f:
        f.write(html)
```

---

## 总结

### 核心优势

1. **环境无关的 Runner**：
   - Runner 只通过统一接口与 Environment 交互
   - 添加新环境无需修改 Runner 代码

2. **清晰的职责划分**：
   - **Runner**：流程控制、对话管理
   - **Environment**：环境管理、工具执行、观察获取
   - **Prompts**：提示词模板管理

3. **灵活的扩展性**：
   - 通过继承 Environment 添加新环境
   - 通过重写方法自定义行为
   - 通过添加提示词支持新模式

4. **完整的生命周期管理**：
   - Benchmark 级别：`env_start()` / `env_close()`
   - Task 级别：`env_task_init()` / `env_task_end()`
   - 对话过程：`get_system_prompt()` / `execute_tool()`

### 数据流总览

```
Benchmark 启动
  └─> env_start()
      └─> 初始化资源

Task 循环
  └─> env_task_init(task)
      └─> 返回 initial_obs {'text', 'image'}
          └─> 构建初始消息

对话循环
  ├─> get_system_prompt(question)
  │   └─> 返回完整提示词
  │
  ├─> execute_tool(name, args)
  │   └─> 返回 {'status', 'response', 'observation'}
  │       └─> add_step_to_trajectory(obs, step)
  │
  └─> 对话结束

Task 清理
  └─> env_task_end(task_id, output_dir)
      ├─> 保存录屏视频
      ├─> 保存轨迹文件
      ├─> 评估结果
      └─> 保存评分

Benchmark 结束
  └─> env_close()
      └─> 释放资源
```

这个架构确保了代码的可维护性、可扩展性和可测试性。
