# OSWorld AgentFlow 集成完整实施方案

**版本**: v1.0
**日期**: 2025-11-05
**目标**: 提供从数据输入到结果保存的全生命周期实施方案，确保架构清晰、职责分离

---

## 目录

1. [数据格式与示例](#1-数据格式与示例)
2. [数据输入与参数传递](#2-数据输入与参数传递)
3. [环境设置与工具注册](#3-环境设置与工具注册)
4. [任务执行与多轮交互](#4-任务执行与多轮交互)
5. [轨迹与结果保存](#5-轨迹与结果保存)
6. [完整代码实现](#6-完整代码实现)
7. [执行流程图](#7-执行流程图)
8. [关键设计决策](#8-关键设计决策)

---

## 1. 数据格式与示例

### 1.1 输入数据格式 (osworld_examples.jsonl)

每行一个 JSON 对象，包含任务的完整信息：

```json
{
  "id": "0d0f5ee2-7621-41f7-a4bc-c9b985ce5c14",
  "instruction": "I want to install the comic sans font. Find the font file, download it, and install it on my system.",
  "config": [
    {
      "type": "execute",
      "command": "rm -rf ~/.local/share/fonts/comic_sans.ttf"
    }
  ],
  "related_apps": ["os"],
  "evaluator": {
    "func": "is_file_exist",
    "result": {
      "type": "vm_file",
      "path": "~/.local/share/fonts/comic_sans.ttf",
      "dest": "comic_sans.ttf"
    },
    "expected": {
      "type": "rule",
      "rules": {
        "include": ["comic"]
      }
    }
  },
  "snapshot": "os_0",
  "max_steps": 15
}
```

**字段说明**:
- `id`: 任务唯一标识符
- `instruction`: 自然语言任务描述（给 Agent 的指令）
- `config`: 环境初始化配置，包含 setup 步骤（如删除文件、准备环境等）
- `related_apps`: 相关应用列表，用于组织结果目录
- `evaluator`: 评估器配置，定义如何判断任务是否成功
- `snapshot`: VM 快照名称
- `max_steps`: 最大步数（可选，覆盖全局配置）

### 1.2 输出数据格式

#### 1.2.1 轨迹文件 (traj.jsonl)

每个任务生成一个轨迹文件，记录每一步的执行：

```json
{"step_num": 0, "action_timestamp": "20251105@143022", "action": "__init__", "reward": 0.0, "done": false, "info": {}, "screenshot_file": "step_0_20251105@143022.png", "instruction": "I want to install..."}
{"step_num": 1, "action_timestamp": "20251105@143035", "action": "pyautogui.click(100, 200)", "reward": 0.0, "done": false, "info": {}, "screenshot_file": "step_1_20251105@143035.png", "instruction": "I want to install..."}
{"step_num": 2, "action_timestamp": "20251105@143048", "action": "DONE", "reward": 1.0, "done": true, "info": {"success": true}, "screenshot_file": "step_2_20251105@143048.png", "instruction": "I want to install..."}
```

#### 1.2.2 结果文件 (result.txt)

单行文本，记录评估分数：

```
1.0
```

#### 1.2.3 汇总结果 (results_summary.jsonl)

所有任务的汇总，每行一个任务结果：

```json
{"task_id": "0d0f5ee2-7621-41f7-a4bc-c9b985ce5c14", "instruction": "I want to install...", "score": 1.0, "steps": 2, "success": true, "error": null, "result_dir": "results/pyautogui/screenshot_a11y_tree/gpt-4.1-2025-04-14/os/0d0f5ee2-7621-41f7-a4bc-c9b985ce5c14"}
```

#### 1.2.4 配置文件 (args.json)

保存本次运行的所有配置参数：

```json
{
  "model_name": "gpt-4.1-2025-04-14",
  "max_turns": 15,
  "max_retries": 3,
  "initial_wait": 60,
  "settle_wait": 20,
  "pause": 0.5,
  "result_root": "results",
  "action_space": "pyautogui",
  "observation_type": "screenshot_a11y_tree",
  "save_results": true
}
```

---

## 2. 数据输入与参数传递

### 2.1 数据流架构

```
CLI Args → OSWorldConfig (dataclass) → OSWorldRunner
                ↓
        OSWorldEnvironment (with config dict)
                ↓
        DesktopActionTool (reads from env.config)
```

### 2.2 参数传递层次

#### 层次 1: CLI 参数 → OSWorldConfig

```python
# CLI 参数解析
args = parser.parse_args()

# 创建配置对象（全局配置）
config = OSWorldConfig(
    model_name=args.model,
    max_turns=args.max_turns,
    max_retries=args.max_retries,
    initial_wait=args.initial_wait,
    settle_wait=args.settle_wait,
    pause=args.pause,
    result_root=args.result_root,
    action_space=args.action_space,
    observation_type=args.observation_type,
    save_results=not args.no_save
)
```

**设计原因**: 使用 dataclass 统一管理全局配置，便于传递和修改，类型安全。

#### 层次 2: OSWorldConfig → Runner → Environment

```python
# Runner 初始化时保存配置
class OSWorldRunner:
    def __init__(self, config: OSWorldConfig):
        self.config = config  # 全局配置

# Environment 初始化时设置环境相关配置
def setup_environment(self, **env_kwargs) -> OSWorldEnvironment:
    env = OSWorldEnvironment(**env_kwargs)  # VM 相关配置

    # 将 Runner 配置同步到 Environment
    env.update_config(
        action_space=self.config.action_space,
        observation_type=self.config.observation_type,
        pause=self.config.pause,
    )
```

**设计原因**:
- `env_kwargs` 包含 VM 底层配置（provider, vm_path, snapshot 等）
- `update_config` 将运行时配置同步到环境的 config 字典
- 分离关注点：底层配置 vs 运行时配置

#### 层次 3: 任务级配置注入

```python
def run_single_task(self, example: Dict[str, Any]) -> Dict[str, Any]:
    # 为每个任务设置专属配置
    result_dir = self._get_result_dir(example)

    env.update_config(
        current_result_dir=result_dir,      # 当前任务结果目录
        instruction=example['instruction'],  # 当前任务指令
        current_task_id=example['id']       # 当前任务 ID
    )
```

**设计原因**:
- 每个任务有独立的结果目录和指令
- 通过 `env.config` 传递，工具可以访问
- 避免函数参数传递链过长

#### 层次 4: Tool 读取配置

```python
class DesktopActionTool:
    def call(self, params: Union[str, dict], **kwargs) -> str:
        env = self.osworld_env

        # 从环境配置读取
        result_dir = env.get_config('current_result_dir')
        instruction = env.get_config('instruction')
        pause = env.get_config('pause', 0.5)  # 默认值

        # 从 kwargs 读取步数（由 _run_conversation 传入）
        step_num = kwargs.get('step_num', 0)
```

**设计原因**:
- Tool 不需要知道全局配置，只需要当前任务相关信息
- `env.config` 作为共享状态容器
- `kwargs` 用于传递调用时的动态参数（如 step_num）

### 2.3 完整参数传递示意图

```
main()
  ↓
  args (CLI parsed)
  ↓
OSWorldConfig(dataclass) ──┐
  ↓                        │
OSWorldRunner              │
  ├─ self.config ←─────────┘
  │
  ├─ setup_environment(**env_kwargs)
  │    ↓
  │  OSWorldEnvironment
  │    ├─ __init__(**env_kwargs)  # VM 配置
  │    ├─ update_config(...)       # 运行时配置
  │    └─ self.config = {          # 统一配置字典
  │          'action_space': 'pyautogui',
  │          'pause': 0.5,
  │          'current_result_dir': None,  # 动态设置
  │          'instruction': None,          # 动态设置
  │        }
  │
  └─ run_single_task(example)
       ↓
       env.update_config(
           current_result_dir=...,
           instruction=example['instruction']
       )
       ↓
       _run_conversation(example)
           ↓
           env.execute_tool('desktop_action', args, step_num=1)
               ↓
               DesktopActionTool.call(args, step_num=1)
                   ├─ result_dir = env.get_config('current_result_dir')
                   └─ step_num = kwargs['step_num']
```

---

## 3. 环境设置与工具注册

### 3.1 环境初始化流程

```python
class OSWorldEnvironment(Environment):
    def __init__(self, **kwargs):
        """
        参数:
            provider_name: VM 提供商 (vmware/virtualbox)
            path_to_vm: VM 镜像路径
            snapshot_name: 快照名称
            screen_size: 屏幕尺寸 (width, height)
            headless: 是否无头模式
            require_a11y_tree: 是否需要辅助功能树
            require_terminal: 是否需要终端
            os_type: 操作系统类型
        """
        super().__init__(**kwargs)
        self._desktop_env: Optional[DesktopEnv] = None

        # 注意: 不在 __init__ 中初始化 DesktopEnv
        # 等待 _initialize_tools 调用

    @property
    def mode(self) -> str:
        return "osworld"

    def _initialize_tools(self):
        """
        由父类 Environment.__init__ 自动调用
        在这里初始化 DesktopEnv 并注册工具
        """
        # 1. 初始化底层 DesktopEnv
        self._init_desktop_env_from_config()

        # 2. 注册 DesktopActionTool
        from tools.osworld_tools import DesktopActionTool
        self.register_tool(DesktopActionTool(self))

    def _init_desktop_env_from_config(self):
        """从 self.config 读取参数并创建 DesktopEnv"""
        provider_name = self.config.get("provider_name", "vmware")
        path_to_vm = self.config.get("path_to_vm")
        snapshot_name = self.config.get("snapshot_name", "init_state")
        action_space = self.config.get("action_space", "pyautogui")
        screen_size = self.config.get("screen_size", (1920, 1080))
        headless = self.config.get("headless", False)
        require_a11y_tree = self.config.get("require_a11y_tree", True)
        require_terminal = self.config.get("require_terminal", False)
        os_type = self.config.get("os_type", "Ubuntu")

        # 创建底层 DesktopEnv 实例
        self._desktop_env = DesktopEnv(
            provider_name=provider_name,
            path_to_vm=path_to_vm,
            snapshot_name=snapshot_name,
            action_space=action_space,
            screen_size=screen_size,
            headless=headless,
            require_a11y_tree=require_a11y_tree,
            require_terminal=require_terminal,
            os_type=os_type,
        )
```

**设计原因**:
1. **延迟初始化**: 在 `_initialize_tools` 中初始化 `DesktopEnv`，确保 `self.config` 已正确设置
2. **封装性**: 只有 `OSWorldEnvironment` 直接访问 `DesktopEnv`，其他模块通过封装方法访问
3. **配置驱动**: 所有参数从 `self.config` 读取，统一管理

### 3.2 工具注册机制

```python
class OSWorldEnvironment(Environment):
    def _initialize_tools(self):
        # 延迟导入避免循环依赖
        from tools.osworld_tools import DesktopActionTool

        # 先初始化环境
        self._init_desktop_env_from_config()

        # 注册工具（传入 self 引用）
        self.register_tool(DesktopActionTool(self))

        # register_tool 由父类 Environment 提供
        # 会将工具添加到 self._tools 列表
        # 并生成 OpenAI function calling schema

class DesktopActionTool(Tool):
    def __init__(self, osworld_env: OSWorldEnvironment):
        """
        参数:
            osworld_env: OSWorldEnvironment 实例引用
        """
        self.osworld_env = osworld_env

    @property
    def name(self) -> str:
        return "desktop_action"

    @property
    def description(self) -> str:
        return (
            "Execute desktop actions via DesktopEnv. "
            "Supports: click, type, key, hotkey, scroll, pyautogui, WAIT, DONE, FAIL."
        )

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        """定义工具参数 schema（用于 OpenAI function calling）"""
        return [
            {
                "name": "action_type",
                "type": "string",
                "required": True,
                "description": "Action type: click/type/key/hotkey/scroll/pyautogui/WAIT/DONE/FAIL"
            },
            {
                "name": "coordinate",
                "type": "array",
                "items": {"type": "number"},
                "required": False,
                "description": "[x, y] coordinates for click action"
            },
            {
                "name": "text",
                "type": "string",
                "required": False,
                "description": "Text to type"
            },
            {
                "name": "key",
                "type": "string",
                "required": False,
                "description": "Single key to press (e.g., 'enter', 'tab')"
            },
            {
                "name": "keys",
                "type": "array",
                "items": {"type": "string"},
                "required": False,
                "description": "Multiple keys for hotkey (e.g., ['ctrl', 'c'])"
            },
            {
                "name": "clicks",
                "type": "integer",
                "required": False,
                "description": "Number of scroll clicks (positive=up, negative=down)"
            },
            {
                "name": "command",
                "type": "string",
                "required": False,
                "description": "Raw pyautogui command string"
            }
        ]
```

**设计原因**:
1. **工具持有环境引用**: `DesktopActionTool(self)` 将环境实例传入，工具可调用环境方法
2. **Schema 自动生成**: `parameters` 属性定义参数结构，父类自动转换为 OpenAI schema
3. **单一职责**: Tool 只负责动作转换和执行，环境负责状态管理

### 3.3 环境封装方法

```python
class OSWorldEnvironment(Environment):
    """
    封装 DesktopEnv 的所有访问方法
    外部模块（Runner, Tool）只能通过这些方法访问底层环境
    """

    def reset(self, task_config: Dict[str, Any]):
        """
        重置环境到初始状态

        参数:
            task_config: 任务配置（example 字典）
                - config: setup 步骤列表
                - evaluator: 评估器配置
        """
        return self._desktop_env.reset(task_config=task_config)

    def step(self, action: str, pause: float = 0.5):
        """
        执行一个动作

        参数:
            action: 动作字符串（pyautogui 命令或 WAIT/DONE/FAIL）
            pause: 执行后暂停时间

        返回:
            (observation, reward, done, info)
        """
        return self._desktop_env.step(action, pause=pause)

    def get_obs(self) -> Dict[str, Any]:
        """
        获取当前观测

        返回:
            {
                'screenshot': bytes,           # PNG 图片字节
                'accessibility_tree': str,     # a11y 树文本
                'som': ...,                    # 其他观测
            }
        """
        return self._desktop_env._get_obs() or {}

    def evaluate(self) -> float:
        """
        评估当前状态

        返回:
            score: 0.0-1.0 分数
        """
        return float(self._desktop_env.evaluate())

    def start_recording(self):
        """开始屏幕录制"""
        self._desktop_env.controller.start_recording()

    def end_recording(self, out_path: str):
        """
        结束屏幕录制并保存

        参数:
            out_path: 输出视频路径
        """
        self._desktop_env.controller.end_recording(out_path)

    def close(self):
        """关闭环境（关闭 VM 连接等）"""
        if self._desktop_env:
            self._desktop_env.close()
```

**设计原因**:
1. **封装隔离**: 外部不直接访问 `_desktop_env`，通过封装方法访问
2. **接口稳定**: 即使底层 `DesktopEnv` 实现变化，接口保持稳定
3. **便于测试**: 可以 mock `OSWorldEnvironment` 而不需要真实 VM

---

## 4. 任务执行与多轮交互

### 4.1 职责重新划分

基于您的建议，重新设计 `run_single_task` 和 `_run_conversation` 的职责：

#### 4.1.1 run_single_task: 任务级生命周期管理

**职责**:
- 任务配置设置（result_dir, instruction）
- 环境重置（reset）
- 录制控制（start_recording, end_recording）
- 评估与结果保存（evaluate, save result.txt）
- 异常处理

**不负责**:
- 初始观测获取和保存 → 移到 `_run_conversation`
- 等待时间控制 → 移到 `_run_conversation`
- 轨迹写入 → 移到 `_run_conversation` 和 Tool

#### 4.1.2 _run_conversation: 对话级交互管理

**职责**:
- 初始等待（initial_wait）
- 获取初始观测并保存 step_0
- 写入轨迹首条记录
- 构建 messages（system + user with initial obs）
- 多轮工具调用循环
- 解析 done 标志
- Settle 等待（settle_wait）

**不负责**:
- 环境重置
- 录制控制
- 最终评估

### 4.2 完整执行流程

```python
class OSWorldRunner:
    def run_single_task(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        任务级生命周期管理

        流程:
        1. 配置设置
        2. 环境重置
        3. 开始录制
        4. 调用 _run_conversation（核心交互）
        5. 评估任务
        6. 结束录制
        7. 保存结果
        """
        env = self.environment
        task_id = example['id']
        instruction = example.get('instruction', '')

        print(f"\n{'='*60}")
        print(f"Processing Task {task_id}")
        print(f"Instruction: {instruction}")
        print(f"{'='*60}")

        try:
            # ============ 步骤 1: 配置设置 ============
            result_dir = self._get_result_dir(example)
            env.update_config(
                current_result_dir=result_dir,
                instruction=instruction,
                current_task_id=task_id
            )

            # ============ 步骤 2: 环境重置 ============
            print(f"🔄 Resetting environment...")
            env.reset(example)  # 执行 setup 步骤

            # ============ 步骤 3: 开始录制 ============
            print(f"🎥 Starting screen recording...")
            env.start_recording()

            # ============ 步骤 4: 多轮对话交互 ============
            # 这里包含：
            # - initial_wait
            # - 获取初始观测并保存 step_0
            # - 写入轨迹首条
            # - 多轮工具调用
            # - settle_wait
            messages, steps = self._run_conversation(example)

            # ============ 步骤 5: 评估任务 ============
            print(f"📊 Evaluating task...")
            score = env.evaluate()

            # ============ 步骤 6: 结束录制 ============
            recording_path = os.path.join(result_dir, 'recording.mp4')
            env.end_recording(recording_path)
            print(f"🎬 Recording saved: {os.path.basename(recording_path)}")

            # ============ 步骤 7: 保存结果 ============
            with open(os.path.join(result_dir, 'result.txt'), 'w') as f:
                f.write(f"{score}\n")

            # 构造返回结果
            result = {
                "task_id": task_id,
                "instruction": instruction,
                "score": float(score),
                "steps": steps,
                "messages": messages,
                "success": bool(score and score > 0),
                "error": None,
                "result_dir": result_dir
            }

            print(f"✓ Task {task_id} completed")
            print(f"  Score: {score}")
            print(f"  Steps: {steps}")

            return result

        except Exception as e:
            print(f"✗ Task {task_id} failed: {str(e)}")

            # 失败时也尝试保存录制和错误信息
            result_dir = self._get_result_dir(example)
            try:
                env.end_recording(os.path.join(result_dir, 'recording.mp4'))
            except:
                pass

            # 记录错误到轨迹
            traj_path = os.path.join(result_dir, 'traj.jsonl')
            if os.path.exists(traj_path):
                with open(traj_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'error': str(e)}, ensure_ascii=False) + '\n')

            return {
                "task_id": task_id,
                "instruction": instruction,
                "score": 0.0,
                "steps": 0,
                "messages": [],
                "success": False,
                "error": str(e),
                "result_dir": result_dir
            }

    def _run_conversation(self, example: Dict[str, Any]):
        """
        对话级交互管理

        流程:
        1. 初始等待
        2. 获取初始观测并保存 step_0
        3. 写入轨迹首条
        4. 构建 messages
        5. 创建 OpenAI client
        6. 多轮工具调用循环
        7. Settle 等待

        返回:
            (messages, step_count)
        """
        env = self.environment
        instruction = example.get('instruction', '')
        result_dir = env.get_config('current_result_dir')

        # ============ 步骤 1: 初始等待 ============
        # 让 VM 稳定下来
        print(f"⏳ Waiting {self.config.initial_wait}s for initialization...")
        time.sleep(self.config.initial_wait)

        # ============ 步骤 2: 获取初始观测并保存 step_0 ============
        obs0 = env.get_obs()
        ts0 = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
        init_png = os.path.join(result_dir, f'step_0_{ts0}.png')

        if obs0 and obs0.get('screenshot') is not None:
            with open(init_png, 'wb') as f:
                f.write(obs0['screenshot'])
            print(f"📸 Initial screenshot saved: {os.path.basename(init_png)}")

        # ============ 步骤 3: 写入轨迹首条 ============
        traj_path = os.path.join(result_dir, 'traj.jsonl')
        with open(traj_path, 'w', encoding='utf-8') as f:  # 'w' 模式创建新文件
            f.write(json.dumps({
                'step_num': 0,
                'action_timestamp': ts0,
                'action': '__init__',
                'reward': 0.0,
                'done': False,
                'info': {},
                'screenshot_file': os.path.basename(init_png),
                'instruction': instruction
            }, ensure_ascii=False) + '\n')

        # ============ 步骤 4: 构建 messages ============
        # 提取 a11y 树的前几行作为摘要
        a11y_tree = obs0.get('accessibility_tree', '') if obs0 else ''
        a11y_head = '\n'.join(a11y_tree.splitlines()[:10])

        messages = [
            {
                "role": "developer",
                "content": SYSTEM_PROMPT_OSWORLD
            },
            {
                "role": "user",
                "content": (
                    f"Instruction: {instruction}\n\n"
                    f"Initial observation:\n"
                    f"- screenshot_file: {os.path.basename(init_png)}\n"
                    f"- accessibility_tree (first 10 lines):\n{a11y_head}\n"
                )
            }
        ]

        # ============ 步骤 5: 创建 OpenAI client ============
        client = openai.OpenAI(
            api_key=openai.api_key,
            base_url=openai.base_url
        )

        # ============ 步骤 6: 多轮工具调用循环 ============
        turn_count = 0

        while turn_count < self.config.max_turns:
            retry = 0

            # 重试循环
            while retry < self.config.max_retries:
                try:
                    # 调用 OpenAI API
                    response = client.chat.completions.create(
                        model=self.config.model_name,
                        messages=messages,
                        tools=env.get_tool_schemas(),
                    )

                    assistant_message = response.choices[0].message
                    messages.append(assistant_message.model_dump())

                    if assistant_message.tool_calls:
                        # 执行工具调用
                        tool_call = assistant_message.tool_calls[0]
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        print(f"Round {turn_count + 1}: 🔧 Tool: {tool_name}")
                        print(f"Round {turn_count + 1}:    Args: {tool_args}")

                        # 执行工具（step_num 从 1 开始）
                        tool_result = env.execute_tool(
                            tool_name,
                            tool_args,
                            step_num=turn_count + 1  # 传递步数给 Tool
                        )

                        # 解析首行 JSON 判断是否完成
                        first_line = tool_result.splitlines()[0].strip() if tool_result else "{}"
                        try:
                            meta = json.loads(first_line)
                            done = meta.get('done', False)
                        except:
                            meta = {"done": False}
                            done = False

                        print(f"Round {turn_count + 1}:    Done: {done}")

                        # 添加工具返回到 messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": tool_result
                        })

                        # 检查是否完成
                        if done:
                            print(f"✅ Task marked as done at turn {turn_count + 1}")

                            # ============ 步骤 7: Settle 等待 ============
                            print(f"⏳ Waiting {self.config.settle_wait}s for settle...")
                            time.sleep(self.config.settle_wait)

                            return messages, turn_count + 1

                        # 继续下一轮
                        break

                    else:
                        # 没有工具调用，对话结束
                        print(f"💬 Agent stopped without tool call")

                        # Settle 等待
                        print(f"⏳ Waiting {self.config.settle_wait}s for settle...")
                        time.sleep(self.config.settle_wait)

                        return messages, turn_count + 1

                except Exception as e:
                    print(f"⚠️  Retry {retry + 1}/{self.config.max_retries}: {str(e)}")
                    retry += 1
                    if retry >= self.config.max_retries:
                        raise e

            turn_count += 1

        # 达到最大轮数
        print(f"⚠️  Max turns ({self.config.max_turns}) reached")

        # Settle 等待
        print(f"⏳ Waiting {self.config.settle_wait}s for settle...")
        time.sleep(self.config.settle_wait)

        return messages, turn_count
```

### 4.3 Tool 执行逻辑

```python
class DesktopActionTool(Tool):
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """
        执行桌面动作

        参数:
            params: 动作参数字典或字符串
            kwargs:
                - step_num: 步数（由 _run_conversation 传入）

        返回:
            首行 JSON + 文本摘要
        """
        env = self.osworld_env

        # ============ 步骤 1: 读取配置 ============
        result_dir = env.get_config('current_result_dir')
        instruction = env.get_config('instruction')
        pause = env.get_config('pause', 0.5)
        step_num = kwargs.get('step_num', 0)

        if not result_dir:
            # 配置缺失，返回错误
            meta = {"done": True, "reward": 0.0, "info": {"error": "result_dir missing"}}
            return json.dumps(meta, ensure_ascii=False) + "\n[Error] Missing result_dir"

        # ============ 步骤 2: 转换动作 ============
        if isinstance(params, str):
            action = params
        else:
            action = self._to_pyautogui(params)

        # ============ 步骤 3: 执行动作 ============
        obs, reward, done, info = env.step(action, pause=pause)

        # ============ 步骤 4: 保存截图 ============
        ts = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
        png_path = os.path.join(result_dir, f'step_{step_num}_{ts}.png')

        if obs and obs.get('screenshot') is not None:
            with open(png_path, 'wb') as f:
                f.write(obs['screenshot'])

        # ============ 步骤 5: 写入轨迹 ============
        traj_path = os.path.join(result_dir, 'traj.jsonl')
        with open(traj_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'step_num': step_num,
                'action_timestamp': ts,
                'action': action,
                'reward': reward,
                'done': done,
                'info': info or {},
                'screenshot_file': os.path.basename(png_path),
                'instruction': instruction
            }, ensure_ascii=False) + '\n')

        # ============ 步骤 6: 构造返回 ============
        # 摘要观测（不包含完整 base64）
        a11y_head = []
        if obs and obs.get('accessibility_tree'):
            a11y_head = obs['accessibility_tree'].splitlines()[:10]

        obs_summary = {
            "a11y_head": a11y_head,
            "screenshot_file": os.path.basename(png_path),
            "step_num": step_num
        }

        # 首行 JSON（供程序解析）
        meta = {
            "done": bool(done),
            "reward": float(reward),
            "info": info or {},
            "obs_summary": obs_summary
        }

        # 人类可读文本
        human_text = (
            f"Action: {action}\n"
            f"Reward: {reward}\n"
            f"Done: {done}\n"
            f"Observation:\n"
            f"  - screenshot: {os.path.basename(png_path)}\n"
            f"  - a11y_tree: {len(a11y_head)} lines shown\n"
            f"Info: {info}"
        )

        return json.dumps(meta, ensure_ascii=False) + "\n" + human_text

    def _to_pyautogui(self, params: dict) -> str:
        """
        将结构化参数转换为 pyautogui 命令或特殊动作

        支持:
        - click: {"action_type": "click", "coordinate": [x, y]}
        - type: {"action_type": "type", "text": "hello"}
        - key: {"action_type": "key", "key": "enter"}
        - hotkey: {"action_type": "hotkey", "keys": ["ctrl", "c"]}
        - scroll: {"action_type": "scroll", "clicks": 5}
        - pyautogui: {"action_type": "pyautogui", "command": "pyautogui.moveTo(100, 200)"}
        - WAIT: {"action_type": "WAIT"}
        - DONE: {"action_type": "DONE"}
        - FAIL: {"action_type": "FAIL"}
        """
        action_type = params.get("action_type")

        # 特殊动作
        if action_type in ("WAIT", "DONE", "FAIL"):
            return action_type

        # 点击
        if action_type == "click":
            x, y = params.get("coordinate", [None, None])
            if x is None or y is None:
                raise ValueError("click requires coordinate [x, y]")
            return f"pyautogui.click({x}, {y})"

        # 输入文本
        if action_type == "type":
            text = params.get("text", "")
            text_escaped = text.replace('"', '\\"')
            return f'pyautogui.typewrite("{text_escaped}")'

        # 按键
        if action_type == "key":
            key = params.get("key", "")
            return f"pyautogui.press('{key}')"

        # 组合键
        if action_type == "hotkey":
            keys = params.get("keys", [])
            keys_str = ", ".join([f"'{k}'" for k in keys])
            return f"pyautogui.hotkey({keys_str})"

        # 滚动
        if action_type == "scroll":
            clicks = params.get("clicks", 0)
            return f"pyautogui.scroll({int(clicks)})"

        # 原始命令
        if action_type == "pyautogui":
            command = params.get("command", "")
            if not command:
                raise ValueError("pyautogui requires command")
            return command

        raise ValueError(f"Unknown action_type: {action_type}")
```

**设计原因**:
1. **职责清晰**:
   - `run_single_task` 管理任务生命周期（重置、录制、评估）
   - `_run_conversation` 管理对话交互（等待、观测、多轮调用）
   - `DesktopActionTool` 执行具体动作并保存轨迹
2. **初始观测在对话中**:
   - 初始观测是对话的一部分，放在 `_run_conversation` 中更合理
   - step_0 属于轨迹的第一步，与后续步骤一致
3. **Settle 等待位置**:
   - 在 `done=True` 后立即 settle，确保 UI 稳定
   - 在 `_run_conversation` 结束前执行，evaluate 前已完成

---

## 5. 轨迹与结果保存

### 5.1 文件组织结构

```
results/
└── pyautogui/                          # action_space
    └── screenshot_a11y_tree/           # observation_type
        └── gpt-4.1-2025-04-14/         # model_name
            ├── args.json               # 全局配置
            ├── results_summary.jsonl   # 所有任务汇总
            ├── os/                     # domain (from related_apps)
            │   └── task-id-1/          # 单个任务目录
            │       ├── step_0_20251105@143022.png
            │       ├── step_1_20251105@143035.png
            │       ├── step_2_20251105@143048.png
            │       ├── traj.jsonl      # 轨迹
            │       ├── result.txt      # 评估分数
            │       └── recording.mp4   # 录屏
            └── chrome/
                └── task-id-2/
                    ├── ...
```

**设计原因**:
1. **层次清晰**: action_space → obs_type → model → domain → task
2. **便于比较**: 不同模型/配置的结果在平行目录
3. **域分组**: related_apps 作为域，同类任务聚合

### 5.2 轨迹保存时机

#### 时机 1: _run_conversation 开始时（step_0）

```python
# 在 _run_conversation 中
traj_path = os.path.join(result_dir, 'traj.jsonl')
with open(traj_path, 'w', encoding='utf-8') as f:  # 'w' 模式
    f.write(json.dumps({
        'step_num': 0,
        'action_timestamp': ts0,
        'action': '__init__',
        'reward': 0.0,
        'done': False,
        'info': {},
        'screenshot_file': os.path.basename(init_png),
        'instruction': instruction
    }, ensure_ascii=False) + '\n')
```

**设计原因**:
- 每个任务创建新的 traj.jsonl（'w' 模式）
- step_0 记录初始状态

#### 时机 2: Tool 执行时（step_1, 2, 3...）

```python
# 在 DesktopActionTool.call 中
traj_path = os.path.join(result_dir, 'traj.jsonl')
with open(traj_path, 'a', encoding='utf-8') as f:  # 'a' 模式追加
    f.write(json.dumps({
        'step_num': step_num,
        'action_timestamp': ts,
        'action': action,
        'reward': reward,
        'done': done,
        'info': info or {},
        'screenshot_file': os.path.basename(png_path),
        'instruction': instruction
    }, ensure_ascii=False) + '\n')
```

**设计原因**:
- 每次动作执行后立即写入
- 'a' 模式追加，不覆盖
- 即使程序崩溃，已执行的步骤也被记录

#### 时机 3: 异常时

```python
# 在 run_single_task 的 except 块中
traj_path = os.path.join(result_dir, 'traj.jsonl')
if os.path.exists(traj_path):
    with open(traj_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'error': str(e)}, ensure_ascii=False) + '\n')
```

**设计原因**:
- 记录错误信息到轨迹
- 便于调试分析

### 5.3 结果保存策略

#### 策略 1: 任务级结果（result.txt）

```python
# 在 run_single_task 中，evaluate 后保存
with open(os.path.join(result_dir, 'result.txt'), 'w') as f:
    f.write(f"{score}\n")
```

**设计原因**:
- 单行文本，简单明了
- 便于脚本解析

#### 策略 2: 批量汇总（results_summary.jsonl）

```python
class OSWorldRunner:
    def _write_single_result(self, result: Dict[str, Any]):
        """
        每个任务完成后立即写入汇总文件
        """
        if self.output_file is None:
            # 首次调用时创建文件路径
            top_dir = os.path.join(
                self.config.result_root,
                self.config.action_space,
                self.config.observation_type,
                self.config.model_name
            )
            os.makedirs(top_dir, exist_ok=True)
            self.output_file = os.path.join(top_dir, "results_summary.jsonl")

        # 精简结果（不包含完整 messages）
        result_summary = {
            "task_id": result["task_id"],
            "instruction": result.get("instruction", ""),
            "score": result["score"],
            "steps": result["steps"],
            "success": result["success"],
            "error": result.get("error"),
            "result_dir": result.get("result_dir")
        }

        # 追加到文件
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result_summary, ensure_ascii=False) + "\n")
```

**设计原因**:
1. **即时写入**: 每个任务完成后立即写入，避免内存占用
2. **断点续传**: 程序中断后，已完成的任务已记录
3. **精简数据**: 不包含完整 messages，减小文件大小

#### 策略 3: 配置保存（args.json）

```python
def _save_args(self):
    """在 run_benchmark 开始时保存配置"""
    top_dir = os.path.join(
        self.config.result_root,
        self.config.action_space,
        self.config.observation_type,
        self.config.model_name
    )
    os.makedirs(top_dir, exist_ok=True)

    args_file = os.path.join(top_dir, 'args.json')
    with open(args_file, 'w', encoding='utf-8') as f:
        json.dump(self.config.__dict__, f, indent=2, ensure_ascii=False)

    print(f"💾 Configuration saved to: {args_file}")
```

**设计原因**:
- 记录本次运行的所有配置
- 便于复现结果

### 5.4 录屏保存

```python
# 在 run_single_task 中
try:
    # 开始录制
    env.start_recording()

    # 执行对话
    messages, steps = self._run_conversation(example)

    # 保存录制
    recording_path = os.path.join(result_dir, 'recording.mp4')
    env.end_recording(recording_path)

except Exception as e:
    # 异常时也尝试保存录制
    try:
        env.end_recording(os.path.join(result_dir, 'recording.mp4'))
    except:
        pass
```

**设计原因**:
- 录制覆盖整个对话过程
- 异常时也尝试保存，避免丢失录像
- 文件名固定为 recording.mp4

---

## 6. 完整代码实现

### 6.1 envs/osworld_environment.py

```python
# AgentFlow/src/envs/osworld_environment.py
# -*- coding: utf-8 -*-
"""
OSWorld Environment - Wrapper for DesktopEnv

This module provides the only interface to access DesktopEnv.
All external modules (Runner, Tools) must use this wrapper's methods.
"""

from typing import Any, Dict, Optional
from envs.enviroment import Environment
from utils.desktop_env.desktop_env import DesktopEnv


class OSWorldEnvironment(Environment):
    """
    OSWorld Environment wrapper.

    Responsibilities:
    - Initialize and manage DesktopEnv lifecycle
    - Register DesktopActionTool
    - Provide unified interface for environment operations
    - Manage environment configuration
    """

    def __init__(self, **kwargs):
        """
        Initialize OSWorld environment.

        Args:
            **kwargs: Configuration passed to parent Environment
                Will be stored in self.config for later use
        """
        super().__init__(**kwargs)
        self._desktop_env: Optional[DesktopEnv] = None

    @property
    def mode(self) -> str:
        """Return environment mode identifier."""
        return "osworld"

    def _initialize_tools(self):
        """
        Initialize tools (called by parent Environment.__init__).

        This method:
        1. Initializes DesktopEnv from config
        2. Registers DesktopActionTool

        Design reason:
        - Called after self.config is set up
        - Ensures DesktopEnv is created before tool registration
        """
        # Import here to avoid circular dependency
        from tools.osworld_tools import DesktopActionTool

        # Step 1: Initialize DesktopEnv
        self._init_desktop_env_from_config()

        # Step 2: Register tool (passing self reference)
        self.register_tool(DesktopActionTool(self))

    def _init_desktop_env_from_config(self):
        """
        Initialize DesktopEnv from self.config.

        Design reason:
        - All configuration is read from self.config
        - Centralized parameter management
        - Easy to override via update_config()
        """
        # Read VM configuration
        provider_name = self.config.get("provider_name", "vmware")
        path_to_vm = self.config.get("path_to_vm")
        snapshot_name = self.config.get("snapshot_name", "init_state")
        action_space = self.config.get("action_space", "pyautogui")
        screen_size = self.config.get("screen_size", (1920, 1080))
        headless = self.config.get("headless", False)
        require_a11y_tree = self.config.get("require_a11y_tree", True)
        require_terminal = self.config.get("require_terminal", False)
        os_type = self.config.get("os_type", "Ubuntu")

        # Create DesktopEnv instance
        self._desktop_env = DesktopEnv(
            provider_name=provider_name,
            path_to_vm=path_to_vm,
            snapshot_name=snapshot_name,
            action_space=action_space,
            screen_size=screen_size,
            headless=headless,
            require_a11y_tree=require_a11y_tree,
            require_terminal=require_terminal,
            os_type=os_type,
        )

    # ============ Wrapper methods for DesktopEnv ============
    # These are the ONLY ways external modules can access DesktopEnv

    def reset(self, task_config: Dict[str, Any]):
        """
        Reset environment to initial state and execute setup steps.

        Args:
            task_config: Task configuration dictionary (example)
                - config: List of setup steps
                - evaluator: Evaluator configuration

        Returns:
            Initial observation

        Design reason:
        - Executes task-specific setup (e.g., delete files, prepare state)
        - Called at the start of each task
        """
        return self._desktop_env.reset(task_config=task_config)

    def step(self, action: str, pause: float = 0.5):
        """
        Execute an action in the environment.

        Args:
            action: Action string (pyautogui command or WAIT/DONE/FAIL)
            pause: Pause duration after action (seconds)

        Returns:
            (observation, reward, done, info)
            - observation: dict with screenshot, a11y_tree, etc.
            - reward: float (usually 0.0 during execution, 1.0 if done)
            - done: bool (whether task is complete)
            - info: dict with additional information

        Design reason:
        - Core interaction method
        - Pause ensures UI stability after action
        """
        return self._desktop_env.step(action, pause=pause)

    def get_obs(self) -> Dict[str, Any]:
        """
        Get current observation without executing action.

        Returns:
            Observation dictionary:
            {
                'screenshot': bytes,           # PNG image bytes
                'accessibility_tree': str,     # a11y tree text
                'som': dict,                   # Set-of-Mark (if available)
                ...
            }

        Design reason:
        - Used to get initial observation after reset
        - Does not advance environment state
        """
        return self._desktop_env._get_obs() or {}

    def evaluate(self) -> float:
        """
        Evaluate current state against task evaluator.

        Returns:
            Score: 0.0 (failed) to 1.0 (success)

        Design reason:
        - Called after task completion (DONE or max steps)
        - Uses evaluator defined in task config
        """
        return float(self._desktop_env.evaluate())

    def start_recording(self):
        """
        Start screen recording.

        Design reason:
        - Called at task start (after reset)
        - Records entire task execution
        """
        self._desktop_env.controller.start_recording()

    def end_recording(self, out_path: str):
        """
        End screen recording and save to file.

        Args:
            out_path: Output video file path (.mp4)

        Design reason:
        - Called after task completion or failure
        - Saves recording even on exceptions
        """
        self._desktop_env.controller.end_recording(out_path)

    def close(self):
        """
        Close environment and release resources.

        Design reason:
        - Called once after ALL tasks complete
        - Closes VM connection, cleans up resources
        """
        if self._desktop_env:
            self._desktop_env.close()
```

### 6.2 tools/osworld_tools.py

```python
# AgentFlow/src/tools/osworld_tools.py
# -*- coding: utf-8 -*-
"""
OSWorld Tools - Desktop action execution

This module defines DesktopActionTool for executing desktop actions.
"""

import json
import os
import datetime
from typing import Union, Dict, List, Any
from envs.enviroment import Tool


class DesktopActionTool(Tool):
    """
    Desktop Action Tool.

    Responsibilities:
    - Convert structured parameters to pyautogui commands
    - Execute actions via OSWorldEnvironment.step()
    - Save screenshots and trajectory
    - Return structured results (JSON + human text)
    """

    def __init__(self, osworld_env):
        """
        Initialize tool with environment reference.

        Args:
            osworld_env: OSWorldEnvironment instance

        Design reason:
        - Tool needs access to environment methods (step, get_config)
        - Passed during registration in _initialize_tools
        """
        self.osworld_env = osworld_env

    @property
    def name(self) -> str:
        """Tool name for function calling."""
        return "desktop_action"

    @property
    def description(self) -> str:
        """Tool description for LLM."""
        return (
            "Execute desktop actions via DesktopEnv. "
            "Supports: click, type, key, hotkey, scroll, pyautogui, WAIT, DONE, FAIL. "
            "Returns: first line JSON (for parsing) + human-readable summary."
        )

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        """
        Define tool parameters for OpenAI function calling.

        Design reason:
        - Structured parameters ensure type safety
        - Different action types require different parameters
        - Parent class converts this to OpenAI schema
        """
        return [
            {
                "name": "action_type",
                "type": "string",
                "required": True,
                "description": "Action type: click/type/key/hotkey/scroll/pyautogui/WAIT/DONE/FAIL"
            },
            {
                "name": "coordinate",
                "type": "array",
                "items": {"type": "number"},
                "required": False,
                "description": "[x, y] coordinates for click action"
            },
            {
                "name": "text",
                "type": "string",
                "required": False,
                "description": "Text to type (for type action)"
            },
            {
                "name": "key",
                "type": "string",
                "required": False,
                "description": "Single key to press (e.g., 'enter', 'tab', 'esc')"
            },
            {
                "name": "keys",
                "type": "array",
                "items": {"type": "string"},
                "required": False,
                "description": "Multiple keys for hotkey (e.g., ['ctrl', 'c'])"
            },
            {
                "name": "clicks",
                "type": "integer",
                "required": False,
                "description": "Number of scroll clicks (positive=up, negative=down)"
            },
            {
                "name": "command",
                "type": "string",
                "required": False,
                "description": "Raw pyautogui command string (for pyautogui action)"
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """
        Execute desktop action.

        Args:
            params: Action parameters (dict or string)
            **kwargs:
                - step_num: Current step number (passed by _run_conversation)

        Returns:
            First line: JSON metadata
            Remaining lines: Human-readable summary

            JSON structure:
            {
                "done": bool,
                "reward": float,
                "info": dict,
                "obs_summary": {
                    "a11y_head": list,
                    "screenshot_file": str,
                    "step_num": int
                }
            }

        Design reason:
        - First line JSON allows programmatic parsing (check done flag)
        - Human text helps LLM understand what happened
        - Screenshot and trajectory saved immediately
        """
        env = self.osworld_env

        # ============ Step 1: Read configuration ============
        result_dir = env.get_config('current_result_dir')
        instruction = env.get_config('instruction', '')
        pause = env.get_config('pause', 0.5)
        step_num = kwargs.get('step_num', 0)

        # Validate result_dir
        if not result_dir:
            meta = {
                "done": True,
                "reward": 0.0,
                "info": {"error": "result_dir missing"}
            }
            return json.dumps(meta, ensure_ascii=False) + "\n[Error] Missing result_dir in config"

        # ============ Step 2: Convert action ============
        try:
            if isinstance(params, str):
                action = params
            else:
                action = self._to_pyautogui(params)
        except Exception as e:
            meta = {
                "done": True,
                "reward": 0.0,
                "info": {"error": f"Action conversion failed: {str(e)}"}
            }
            return json.dumps(meta, ensure_ascii=False) + f"\n[Error] {str(e)}"

        # ============ Step 3: Execute action ============
        try:
            obs, reward, done, info = env.step(action, pause=pause)
        except Exception as e:
            meta = {
                "done": True,
                "reward": 0.0,
                "info": {"error": f"Action execution failed: {str(e)}"}
            }
            return json.dumps(meta, ensure_ascii=False) + f"\n[Error] {str(e)}"

        # ============ Step 4: Save screenshot ============
        ts = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
        png_path = os.path.join(result_dir, f'step_{step_num}_{ts}.png')

        if obs and obs.get('screenshot') is not None:
            try:
                with open(png_path, 'wb') as f:
                    f.write(obs['screenshot'])
            except Exception as e:
                print(f"Warning: Failed to save screenshot: {e}")

        # ============ Step 5: Write trajectory ============
        traj_path = os.path.join(result_dir, 'traj.jsonl')
        try:
            with open(traj_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'step_num': step_num,
                    'action_timestamp': ts,
                    'action': action,
                    'reward': reward,
                    'done': done,
                    'info': info or {},
                    'screenshot_file': os.path.basename(png_path),
                    'instruction': instruction
                }, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Warning: Failed to write trajectory: {e}")

        # ============ Step 6: Construct return value ============
        # Summarize observation (don't include full base64)
        a11y_head = []
        if obs and obs.get('accessibility_tree'):
            a11y_head = obs['accessibility_tree'].splitlines()[:10]

        obs_summary = {
            "a11y_head": a11y_head,
            "screenshot_file": os.path.basename(png_path),
            "step_num": step_num
        }

        # First line: JSON metadata (for programmatic parsing)
        meta = {
            "done": bool(done),
            "reward": float(reward),
            "info": info or {},
            "obs_summary": obs_summary
        }

        # Human-readable summary
        human_text = (
            f"Action: {action}\n"
            f"Reward: {reward}\n"
            f"Done: {done}\n"
            f"Observation:\n"
            f"  - Screenshot: {os.path.basename(png_path)}\n"
            f"  - A11y tree: {len(a11y_head)} lines shown (first 10)\n"
            f"  - Info: {info or {}}"
        )

        return json.dumps(meta, ensure_ascii=False) + "\n" + human_text

    def _to_pyautogui(self, params: dict) -> str:
        """
        Convert structured parameters to pyautogui command or special action.

        Args:
            params: Action parameters dictionary

        Returns:
            Action string (pyautogui command or WAIT/DONE/FAIL)

        Raises:
            ValueError: If parameters are invalid

        Design reason:
        - Structured input ensures type safety
        - Special actions (WAIT/DONE/FAIL) pass through unchanged
        - Generates executable pyautogui commands
        """
        action_type = params.get("action_type")

        # Special actions (pass through)
        if action_type in ("WAIT", "DONE", "FAIL"):
            return action_type

        # Click action
        if action_type == "click":
            coord = params.get("coordinate", [None, None])
            if len(coord) != 2 or coord[0] is None or coord[1] is None:
                raise ValueError("click requires coordinate [x, y]")
            x, y = coord
            return f"pyautogui.click({x}, {y})"

        # Type action
        if action_type == "type":
            text = params.get("text", "")
            # Escape quotes
            text_escaped = text.replace('"', '\\"')
            return f'pyautogui.typewrite("{text_escaped}")'

        # Key press action
        if action_type == "key":
            key = params.get("key", "")
            if not key:
                raise ValueError("key action requires key parameter")
            return f"pyautogui.press('{key}')"

        # Hotkey action
        if action_type == "hotkey":
            keys = params.get("keys", [])
            if not keys:
                raise ValueError("hotkey action requires keys parameter")
            keys_str = ", ".join([f"'{k}'" for k in keys])
            return f"pyautogui.hotkey({keys_str})"

        # Scroll action
        if action_type == "scroll":
            clicks = params.get("clicks", 0)
            return f"pyautogui.scroll({int(clicks)})"

        # Raw pyautogui command
        if action_type == "pyautogui":
            command = params.get("command", "")
            if not command:
                raise ValueError("pyautogui action requires command parameter")
            return command

        raise ValueError(f"Unknown action_type: {action_type}")
```

### 6.3 run_osworld.py (核心运行器)

完整代码见前面 v6 版本（已包含所有注释和设计原因）。

关键点总结:
1. **OSWorldConfig**: 全局配置的 dataclass
2. **OSWorldRunner**:
   - `setup_environment`: 创建并配置环境
   - `run_single_task`: 任务级生命周期（重置、录制、评估）
   - `_run_conversation`: 对话级交互（等待、观测、多轮调用）
   - `run_benchmark`: 批量执行（加载数据、逐任务执行、汇总结果）
3. **main**: CLI 参数解析和程序入口

---

## 7. 执行流程图

```
┌─────────────────────────────────────────────────────────────┐
│                        main()                                │
│  1. Parse CLI args                                           │
│  2. Create OSWorldConfig                                     │
│  3. Create OSWorldRunner(config)                             │
│  4. runner.setup_environment(**env_kwargs)                   │
│  5. runner.run_benchmark(examples_path)                      │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│              run_benchmark(examples_path)                    │
│  1. Load examples from JSONL                                 │
│  2. Save args.json                                           │
│  3. For each example:                                        │
│     - result = run_single_task(example)                      │
│     - _write_single_result(result)                           │
│  4. env.close()                                              │
│  5. Return summary                                           │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│               run_single_task(example)                       │
│  1. Setup: result_dir, update env.config                     │
│  2. env.reset(example)  # Execute setup steps                │
│  3. env.start_recording()                                    │
│  4. messages, steps = _run_conversation(example)             │
│  5. score = env.evaluate()                                   │
│  6. env.end_recording(recording_path)                        │
│  7. Save result.txt                                          │
│  8. Return result dict                                       │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│              _run_conversation(example)                      │
│  1. Wait initial_wait seconds                                │
│  2. obs0 = env.get_obs()                                     │
│  3. Save step_0 screenshot                                   │
│  4. Write first traj entry (step_0, __init__)                │
│  5. Build messages:                                          │
│     - developer: system prompt                               │
│     - user: instruction + initial obs summary                │
│  6. Create OpenAI client                                     │
│  7. Multi-turn loop (max_turns):                             │
│     ┌─────────────────────────────────────┐                 │
│     │ a. Call OpenAI API with tools       │                 │
│     │ b. If tool_calls:                   │                 │
│     │    - Execute desktop_action tool    │                 │
│     │    - Parse JSON first line for done │                 │
│     │    - Add tool result to messages    │                 │
│     │    - If done: break                 │                 │
│     │ c. Else: break (no tool call)       │                 │
│     │ d. Retry logic on exceptions        │                 │
│     └─────────────────────────────────────┘                 │
│  8. Wait settle_wait seconds                                 │
│  9. Return (messages, step_count)                            │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│       env.execute_tool('desktop_action', args,               │
│                         step_num=turn+1)                     │
│                         │                                    │
│                         ▼                                    │
│          DesktopActionTool.call(args, step_num=turn+1)       │
│  1. Read config: result_dir, instruction, pause              │
│  2. Convert params to pyautogui command                      │
│  3. obs, reward, done, info = env.step(action, pause)        │
│  4. Save screenshot: step_{num}_{timestamp}.png              │
│  5. Append to traj.jsonl                                     │
│  6. Return: JSON line + human text                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 关键设计决策

### 8.1 为什么 initial_wait 和 step_0 在 _run_conversation 中?

**原因**:
1. **语义一致性**: initial_wait 和 step_0 是对话的一部分，属于"观测-行动"循环的第一步
2. **职责清晰**: `run_single_task` 管理任务生命周期（重置、录制、评估），不应关心对话细节
3. **轨迹完整性**: step_0 是轨迹的第一条记录，与后续 step 在同一个流程中管理更自然

### 8.2 为什么 settle_wait 在 _run_conversation 结束前?

**原因**:
1. **UI 稳定性**: 等待 UI 完成所有动画和更新后再评估
2. **时序正确**: settle → evaluate，确保评估时状态稳定
3. **位置合理**: 在 done=True 或 max_turns 后立即执行，评估前完成

### 8.3 为什么工具返回首行 JSON + 文本?

**原因**:
1. **程序解析**: `_run_conversation` 需要解析 `done` 标志判断是否结束
2. **LLM 理解**: 人类可读文本帮助 LLM 理解执行结果，做出更好决策
3. **调试友好**: 日志中可以直接看到可读内容

### 8.4 为什么轨迹立即写入而不是缓存?

**原因**:
1. **防止丢失**: 程序崩溃时已执行的步骤不会丢失
2. **实时监控**: 可以在任务执行过程中查看轨迹
3. **内存效率**: 不需要在内存中缓存大量数据

### 8.5 为什么环境只在 run_benchmark 结束时关闭?

**原因**:
1. **资源复用**: 同一 VM 实例可以处理多个任务（通过 reset）
2. **效率**: 避免频繁启动/关闭 VM
3. **一致性**: 与 run.py 的环境管理模式一致

### 8.6 为什么配置通过 env.config 传递而不是函数参数?

**原因**:
1. **避免参数链过长**: 如果通过参数传递，需要 Runner → Tool 每层都传
2. **共享状态**: `env.config` 作为共享配置容器，所有模块都可访问
3. **灵活性**: 可以动态更新配置（如每个任务设置不同的 result_dir）

### 8.7 为什么 step_num 通过 kwargs 传递?

**原因**:
1. **动态值**: step_num 是调用时才确定的，不是配置的一部分
2. **调用上下文**: 由 `_run_conversation` 在调用工具时提供
3. **类型安全**: kwargs 可以传递任意额外参数，不影响接口签名

---

## 9. 可行性分析

### 9.1 架构合理性 ✓

- **职责清晰**: Runner、Environment、Tool 各司其职
- **封装良好**: 只有 OSWorldEnvironment 访问 DesktopEnv
- **扩展性**: 可以轻松添加新工具或新环境类型

### 9.2 与 AgentFlow 兼容性 ✓

- **继承 Environment**: OSWorldEnvironment 继承自 AgentFlow 的 Environment 基类
- **工具注册机制**: 使用 `register_tool` 标准方法
- **配置模式**: 使用 dataclass 和 config 字典，与 run.py 一致
- **CLI 风格**: argparse 和打印格式与 run.py 一致

### 9.3 数据流完整性 ✓

- **输入**: JSONL 格式，包含所有必要信息
- **处理**: 参数通过 config 和 kwargs 清晰传递
- **输出**: 轨迹、结果、录像、汇总多层次保存

### 9.4 错误处理健壮性 ✓

- **重试机制**: API 调用失败时自动重试
- **异常捕获**: 每个任务独立 try-except，不影响其他任务
- **降级保存**: 失败时仍尝试保存录像和错误信息

### 9.5 性能和效率 ✓

- **即时写入**: 轨迹和结果实时保存，不占用内存
- **资源复用**: VM 实例复用，减少启动开销
- **断点续传**: 已完成任务已记录，可从中断处继续

---

## 10. 总结

本方案提供了从数据输入到结果保存的完整生命周期设计:

1. **数据格式清晰**: 输入 JSONL、输出 traj/result/recording/summary
2. **参数传递明确**: Config dataclass → Runner → Environment → Tool
3. **环境设置规范**: 延迟初始化、工具注册、封装访问
4. **执行流程合理**: run_single_task (生命周期) + _run_conversation (交互) + Tool (执行)
5. **保存策略健壮**: 实时写入、异常处理、多层次保存
6. **设计决策有据**: 每个关键点都有明确的原因和权衡

**可行性**: ✅ 高
**兼容性**: ✅ 完全兼容 AgentFlow
**可维护性**: ✅ 职责清晰、注释详细
**可扩展性**: ✅ 易于添加新功能

---

**下一步**: 根据此方案实现代码，逐模块测试验证。
