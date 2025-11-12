# OSWorld AgentFlow 最小化集成方案

**版本**: v2.0
**日期**: 2025-11-05
**原则**: 最小化改动，复用现有架构，OSWorld 作为新的环境模式并存

---

## 核心理念

OSWorld **不是独立系统**，而是 AgentFlow 的一个新环境模式（mode），与 math/py/rag/web 并列。

**设计目标**:
1. ✅ 复用 `run.py` 的整体架构（不创建 run_osworld.py）
2. ✅ 添加 `OSWorldEnvironment` 到 `envs/` 模块
3. ✅ 添加 `DesktopActionTool` 到 `tools/` 模块
4. ✅ 在 `run.py` 中添加 `"osworld"` 模式支持
5. ✅ 最小化修改，保持与其他环境一致的使用方式

---

## 目录

1. [架构对比：Before & After](#1-架构对比before--after)
2. [需要修改的文件清单](#2-需要修改的文件清单)
3. [新增文件详细设计](#3-新增文件详细设计)
4. [修改现有文件详细设计](#4-修改现有文件详细设计)
5. [OSWorld 特殊处理逻辑](#5-osworld-特殊处理逻辑)
6. [数据格式与使用方式](#6-数据格式与使用方式)
7. [完整执行流程](#7-完整执行流程)
8. [与其他模式的对比](#8-与其他模式的对比)

---

## 1. 架构对比：Before & After

### 1.1 Before（现有架构）

```
AgentFlow/src/
├── envs/
│   ├── __init__.py           # 导出 Environment, Tool, 各环境类
│   └── enviroment.py         # Environment 基类 + MathEnvironment, PythonEnvironment, RAGEnvironment, WebEnvironment
├── tools/
│   ├── __init__.py
│   ├── calculator.py
│   ├── web_tools.py
│   ├── rag_tools.py
│   └── python_interpreter.py
├── benchmark/
│   └── benchmark.py          # Benchmark 基类
├── run.py                    # 统一的运行入口
└── data/
    ├── math_qa.jsonl
    ├── web_qa.jsonl
    └── ...
```

**使用方式**:
```bash
python run.py --mode math --data data/math_qa.jsonl
python run.py --mode web --data data/web_qa.jsonl
```

### 1.2 After（集成 OSWorld）

```
AgentFlow/src/
├── envs/
│   ├── __init__.py           # [修改] 添加 OSWorldEnvironment 导出
│   ├── enviroment.py         # [修改] 添加 OSWorldEnvironment 类
│   └── osworld_environment.py  # [新增] OSWorld 环境实现（可选，或直接写在 enviroment.py）
├── tools/
│   ├── __init__.py           # [修改] 添加 DesktopActionTool 导出
│   └── osworld_tools.py      # [新增] DesktopActionTool 实现
├── utils/
│   └── desktop_env/          # [已存在] 从 OSWorld 迁移的 DesktopEnv
│       ├── desktop_env.py
│       ├── controllers/
│       └── ...
├── benchmark/
│   └── benchmark.py          # [可选修改] 可以添加 OSWorldBenchmark 子类，或复用现有 Benchmark
├── run.py                    # [修改] 添加 "osworld" 模式支持 + OSWorld 特定参数
└── data/
    ├── math_qa.jsonl
    ├── web_qa.jsonl
    └── osworld_examples.jsonl  # [新增] OSWorld 任务数据
```

**使用方式**:
```bash
# 与其他模式完全一致的使用方式
python run.py --mode osworld \
              --data data/osworld_examples.jsonl \
              --provider vmware \
              --vm-path /path/to/vm.vmx \
              --max-turns 15
```

---

## 2. 需要修改的文件清单

### 2.1 新增文件（3个）

| 文件路径 | 说明 | 行数估计 |
|---------|------|---------|
| `tools/osworld_tools.py` | DesktopActionTool 实现 | ~200 |
| `data/osworld_examples.jsonl` | OSWorld 任务数据样例 | N/A |
| `envs/osworld_environment.py` | (可选) OSWorldEnvironment 独立文件 | ~150 |

### 2.2 修改文件（4个）

| 文件路径 | 修改内容 | 修改量 |
|---------|---------|--------|
| `envs/__init__.py` | 添加 OSWorldEnvironment 导出 | 2-3 行 |
| `envs/enviroment.py` | 添加 OSWorldEnvironment 类（如果不单独文件） | ~150 行 |
| `tools/__init__.py` | 添加 DesktopActionTool 导出 | 2-3 行 |
| `run.py` | 添加 osworld 模式支持 + CLI 参数 | ~50 行 |

**总计**: ~550 行新增代码，~60 行修改

---

## 3. 新增文件详细设计

### 3.1 tools/osworld_tools.py

```python
# AgentFlow/src/tools/osworld_tools.py
"""
Desktop Action Tool for OSWorld integration.

This tool enables desktop automation actions through the OSWorld DesktopEnv.
"""

import json
import os
import datetime
from typing import Union, Dict, List, Any
from envs.enviroment import Tool


class DesktopActionTool(Tool):
    """
    Desktop Action Tool - Execute desktop automation actions.

    This tool wraps OSWorld's DesktopEnv to provide structured desktop actions
    via OpenAI function calling interface.

    Design:
    - Receives structured action parameters from LLM
    - Converts to pyautogui commands or special actions (WAIT/DONE/FAIL)
    - Executes via OSWorldEnvironment.step()
    - Saves screenshots and trajectory
    - Returns JSON (first line) + human text
    """

    def __init__(self, osworld_env):
        """
        Initialize tool with OSWorldEnvironment reference.

        Args:
            osworld_env: OSWorldEnvironment instance

        Design reason:
        - Tool needs access to environment's step() and config
        - Passed during environment._initialize_tools()
        """
        self.osworld_env = osworld_env

    @property
    def name(self) -> str:
        return "desktop_action"

    @property
    def description(self) -> str:
        return (
            "Execute desktop actions in the VM environment. "
            "Supports: click, type, key, hotkey, scroll, WAIT, DONE, FAIL. "
            "Returns observation with screenshot and accessibility tree."
        )

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        """
        Define action parameters for function calling.

        Design:
        - action_type determines which other params are required
        - Array types use 'array_type' to specify item type
        - Parent Environment class converts this to OpenAI schema
        """
        return [
            {
                "name": "action_type",
                "type": "string",
                "required": True,
                "description": "Type of action: click/type/key/hotkey/scroll/pyautogui/WAIT/DONE/FAIL"
            },
            {
                "name": "coordinate",
                "type": "array",
                "array_type": "number",
                "required": False,
                "description": "Click coordinates [x, y]"
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
                "description": "Single key name (e.g., 'enter', 'tab')"
            },
            {
                "name": "keys",
                "type": "array",
                "array_type": "string",
                "required": False,
                "description": "Keys for hotkey combination (e.g., ['ctrl', 'c'])"
            },
            {
                "name": "clicks",
                "type": "integer",
                "required": False,
                "description": "Scroll clicks (positive=up, negative=down)"
            },
            {
                "name": "command",
                "type": "string",
                "required": False,
                "description": "Raw pyautogui command for advanced use"
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """
        Execute desktop action.

        Args:
            params: Action parameters (dict or string)
            **kwargs: Additional execution context
                - step_num: Current step number (from _run_conversation)

        Returns:
            First line: JSON metadata for programmatic parsing
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
            Remaining lines: Human-readable description

        Design reason:
        - First line JSON allows _run_conversation to parse done flag
        - Human text helps LLM understand what happened
        - Observation summary includes enough info for next action
        """
        env = self.osworld_env

        # Read configuration
        result_dir = env.get_config('current_result_dir')
        instruction = env.get_config('instruction', '')
        pause = env.get_config('pause', 0.5)
        step_num = kwargs.get('step_num', 0)

        if not result_dir:
            meta = {"done": True, "reward": 0.0, "info": {"error": "Missing result_dir"}}
            return json.dumps(meta, ensure_ascii=False) + "\n[Error] result_dir not configured"

        # Convert action
        try:
            action = self._to_pyautogui(params) if isinstance(params, dict) else params
        except Exception as e:
            meta = {"done": True, "reward": 0.0, "info": {"error": str(e)}}
            return json.dumps(meta, ensure_ascii=False) + f"\n[Error] Action conversion: {e}"

        # Execute action
        try:
            obs, reward, done, info = env.step(action, pause=pause)
        except Exception as e:
            meta = {"done": True, "reward": 0.0, "info": {"error": str(e)}}
            return json.dumps(meta, ensure_ascii=False) + f"\n[Error] Execution: {e}"

        # Save screenshot
        ts = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
        png_path = os.path.join(result_dir, f'step_{step_num}_{ts}.png')

        if obs and obs.get('screenshot'):
            try:
                with open(png_path, 'wb') as f:
                    f.write(obs['screenshot'])
            except Exception as e:
                print(f"Warning: Failed to save screenshot: {e}")

        # Write trajectory
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

        # Construct return value
        a11y_head = []
        if obs and obs.get('accessibility_tree'):
            a11y_head = obs['accessibility_tree'].splitlines()[:10]

        obs_summary = {
            "a11y_head": a11y_head,
            "screenshot_file": os.path.basename(png_path),
            "step_num": step_num
        }

        meta = {
            "done": bool(done),
            "reward": float(reward),
            "info": info or {},
            "obs_summary": obs_summary
        }

        human_text = (
            f"Action: {action}\n"
            f"Reward: {reward}\n"
            f"Done: {done}\n"
            f"Screenshot: {os.path.basename(png_path)}\n"
            f"A11y tree: {len(a11y_head)} lines\n"
            f"Info: {info or {}}"
        )

        return json.dumps(meta, ensure_ascii=False) + "\n" + human_text

    def _to_pyautogui(self, params: dict) -> str:
        """Convert structured params to pyautogui command or special action."""
        action_type = params.get("action_type")

        # Special actions
        if action_type in ("WAIT", "DONE", "FAIL"):
            return action_type

        # Click
        if action_type == "click":
            coord = params.get("coordinate", [None, None])
            if len(coord) != 2 or coord[0] is None or coord[1] is None:
                raise ValueError("click requires coordinate [x, y]")
            return f"pyautogui.click({coord[0]}, {coord[1]})"

        # Type
        if action_type == "type":
            text = params.get("text", "").replace('"', '\\"')
            return f'pyautogui.typewrite("{text}")'

        # Key press
        if action_type == "key":
            key = params.get("key", "")
            if not key:
                raise ValueError("key action requires key parameter")
            return f"pyautogui.press('{key}')"

        # Hotkey
        if action_type == "hotkey":
            keys = params.get("keys", [])
            if not keys:
                raise ValueError("hotkey requires keys parameter")
            keys_str = ", ".join([f"'{k}'" for k in keys])
            return f"pyautogui.hotkey({keys_str})"

        # Scroll
        if action_type == "scroll":
            clicks = params.get("clicks", 0)
            return f"pyautogui.scroll({int(clicks)})"

        # Raw pyautogui
        if action_type == "pyautogui":
            command = params.get("command", "")
            if not command:
                raise ValueError("pyautogui requires command parameter")
            return command

        raise ValueError(f"Unknown action_type: {action_type}")
```

### 3.2 envs/osworld_environment.py (可选，或直接写在 enviroment.py)

```python
# AgentFlow/src/envs/osworld_environment.py
"""
OSWorld Environment - Desktop automation environment for AgentFlow.

This environment wraps OSWorld's DesktopEnv to provide:
- Desktop automation via VM control
- Screenshot and accessibility tree observations
- Task evaluation
- Screen recording
"""

from typing import Any, Dict, Optional
from envs.enviroment import Environment
from utils.desktop_env.desktop_env import DesktopEnv


class OSWorldEnvironment(Environment):
    """
    OSWorld desktop automation environment.

    Design principles:
    - Inherits from AgentFlow's Environment base class
    - Only this class directly accesses DesktopEnv
    - Provides unified interface for Runner and Tools
    - Manages VM lifecycle (reset, step, evaluate, close)
    """

    def __init__(self, **kwargs):
        """
        Initialize OSWorld environment.

        Args:
            **kwargs: Configuration including:
                - provider_name: VM provider (vmware/virtualbox)
                - path_to_vm: Path to VM image
                - snapshot_name: VM snapshot name
                - screen_size: Tuple (width, height)
                - headless: bool
                - require_a11y_tree: bool
                - require_terminal: bool
                - os_type: str

        Design:
        - Parent __init__ calls _initialize_tools()
        - DesktopEnv created in _initialize_tools (after config is set)
        """
        super().__init__(**kwargs)
        self._desktop_env: Optional[DesktopEnv] = None

    @property
    def mode(self) -> str:
        """Environment mode identifier."""
        return "osworld"

    def _initialize_tools(self):
        """
        Initialize DesktopEnv and register tools.

        Called by parent Environment.__init__ after config is set.

        Design:
        1. Create DesktopEnv from config
        2. Register DesktopActionTool with self reference
        """
        # Import here to avoid circular dependency
        from tools.osworld_tools import DesktopActionTool

        # Initialize DesktopEnv
        self._init_desktop_env()

        # Register tool
        self.register_tool(DesktopActionTool(self))

    def _init_desktop_env(self):
        """Create DesktopEnv instance from configuration."""
        provider_name = self.config.get("provider_name", "vmware")
        path_to_vm = self.config.get("path_to_vm")
        snapshot_name = self.config.get("snapshot_name", "init_state")
        action_space = self.config.get("action_space", "pyautogui")
        screen_size = self.config.get("screen_size", (1920, 1080))
        headless = self.config.get("headless", False)
        require_a11y_tree = self.config.get("require_a11y_tree", True)
        require_terminal = self.config.get("require_terminal", False)
        os_type = self.config.get("os_type", "Ubuntu")

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
    # These are the ONLY ways to access DesktopEnv

    def reset(self, task_config: Dict[str, Any]):
        """
        Reset environment with task configuration.

        Args:
            task_config: Task dict with 'config' (setup steps) and 'evaluator'

        Returns:
            Initial observation

        Design:
        - Called at start of each task in run_single_task
        - Executes task setup steps (e.g., file cleanup)
        """
        return self._desktop_env.reset(task_config=task_config)

    def step(self, action: str, pause: float = 0.5):
        """
        Execute action in environment.

        Args:
            action: Action string (pyautogui command or WAIT/DONE/FAIL)
            pause: Pause after action (seconds)

        Returns:
            (observation, reward, done, info) tuple
        """
        return self._desktop_env.step(action, pause=pause)

    def get_obs(self) -> Dict[str, Any]:
        """
        Get current observation without executing action.

        Returns:
            Observation dict with screenshot, accessibility_tree, etc.

        Design:
        - Used to get initial observation after reset
        - Does not advance state
        """
        return self._desktop_env._get_obs() or {}

    def evaluate(self) -> float:
        """
        Evaluate task completion.

        Returns:
            Score 0.0-1.0

        Design:
        - Called after task completion (DONE or max steps)
        - Uses evaluator from task config
        """
        return float(self._desktop_env.evaluate())

    def start_recording(self):
        """Start screen recording."""
        self._desktop_env.controller.start_recording()

    def end_recording(self, out_path: str):
        """End recording and save to file."""
        self._desktop_env.controller.end_recording(out_path)

    def close(self):
        """Close environment and release resources."""
        if self._desktop_env:
            self._desktop_env.close()
```

### 3.3 data/osworld_examples.jsonl

```jsonl
{"id": "example_1", "instruction": "Open Firefox browser", "config": [], "related_apps": ["os"], "evaluator": {"func": "is_process_running", "result": {"process_name": "firefox"}}, "snapshot": "os_clean", "max_steps": 10}
{"id": "example_2", "instruction": "Create a new folder named 'test_folder' on the desktop", "config": [{"type": "execute", "command": "rm -rf ~/Desktop/test_folder"}], "related_apps": ["os"], "evaluator": {"func": "is_file_exist", "result": {"type": "vm_file", "path": "~/Desktop/test_folder"}}, "snapshot": "os_clean", "max_steps": 15}
```

---

## 4. 修改现有文件详细设计

### 4.1 envs/__init__.py

```python
# 在文件末尾添加 OSWorldEnvironment 导出

"""
Environment package for AgentFlow.
"""

from .enviroment import (
    Environment,
    Tool,
    MathEnvironment,
    PythonEnvironment,
    RAGEnvironment,
    WebEnvironment,
    OSWorldEnvironment,  # [新增]
    create_math_environment,
    create_python_environment,
    create_rag_environment,
    create_web_environment
)

__all__ = [
    "Environment",
    "Tool",
    "MathEnvironment",
    "PythonEnvironment",
    "RAGEnvironment",
    "WebEnvironment",
    "OSWorldEnvironment",  # [新增]
    "create_math_environment",
    "create_python_environment",
    "create_rag_environment",
    "create_web_environment"
]
```

### 4.2 envs/enviroment.py

在文件末尾添加 `OSWorldEnvironment` 类（如果不使用独立文件）:

```python
# 在文件末尾，WebEnvironment 类之后添加

class OSWorldEnvironment(Environment):
    """OSWorld desktop automation environment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._desktop_env: Optional[DesktopEnv] = None

    @property
    def mode(self) -> str:
        return "osworld"

    def _initialize_tools(self):
        """Initialize DesktopEnv and register tools."""
        from tools.osworld_tools import DesktopActionTool
        self._init_desktop_env()
        self.register_tool(DesktopActionTool(self))

    def _init_desktop_env(self):
        """Create DesktopEnv from config."""
        from utils.desktop_env.desktop_env import DesktopEnv

        self._desktop_env = DesktopEnv(
            provider_name=self.config.get("provider_name", "vmware"),
            path_to_vm=self.config.get("path_to_vm"),
            snapshot_name=self.config.get("snapshot_name", "init_state"),
            action_space=self.config.get("action_space", "pyautogui"),
            screen_size=self.config.get("screen_size", (1920, 1080)),
            headless=self.config.get("headless", False),
            require_a11y_tree=self.config.get("require_a11y_tree", True),
            require_terminal=self.config.get("require_terminal", False),
            os_type=self.config.get("os_type", "Ubuntu"),
        )

    def reset(self, task_config: Dict[str, Any]):
        return self._desktop_env.reset(task_config=task_config)

    def step(self, action: str, pause: float = 0.5):
        return self._desktop_env.step(action, pause=pause)

    def get_obs(self) -> Dict[str, Any]:
        return self._desktop_env._get_obs() or {}

    def evaluate(self) -> float:
        return float(self._desktop_env.evaluate())

    def start_recording(self):
        self._desktop_env.controller.start_recording()

    def end_recording(self, out_path: str):
        self._desktop_env.controller.end_recording(out_path)

    def close(self):
        if self._desktop_env:
            self._desktop_env.close()
```

### 4.3 tools/__init__.py

```python
# 添加 DesktopActionTool 导出

"""
Tools package for AgentFlow.
"""

from .calculator import CalculatorTool
from .web_tools import WebSearchTool, WebVisitTool

# Conditionally import other tools
try:
    from .python_interpreter import PythonInterpreterTool
except ImportError:
    PythonInterpreterTool = None

try:
    from .rag_tools import QueryRAGIndexTool
except ImportError:
    QueryRAGIndexTool = None

try:
    from .osworld_tools import DesktopActionTool  # [新增]
except ImportError:
    DesktopActionTool = None

__all__ = [
    "CalculatorTool",
    "WebSearchTool",
    "WebVisitTool",
    "PythonInterpreterTool",
    "QueryRAGIndexTool",
    "DesktopActionTool",  # [新增]
]
```

### 4.4 run.py

#### 4.4.1 修改 setup_environment 方法

```python
# 在 AgentRunner.setup_environment 方法中添加 osworld 分支

def setup_environment(self, mode: str, **kwargs) -> Environment:
    """
    Setup environment based on mode.

    Args:
        mode: Environment mode ("math", "py", "rag", "web", "osworld")  # [修改]
        **kwargs: Additional configuration for the environment

    Returns:
        Configured environment
    """
    print(f"Setting up {mode} environment...")

    if mode == "math":
        self.environment = MathEnvironment(**kwargs)
    elif mode == "py":
        self.environment = PythonEnvironment(**kwargs)
    elif mode == "rag":
        self.environment = RAGEnvironment(**kwargs)
    elif mode == "web":
        self.environment = WebEnvironment(**kwargs)
    elif mode == "osworld":  # [新增]
        self.environment = OSWorldEnvironment(**kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    print(f"Environment setup complete. Available tools: {self.environment.list_tools()}")
    return self.environment
```

#### 4.4.2 修改 run_single_task 方法（添加 OSWorld 特殊处理）

```python
# 在 AgentRunner.run_single_task 方法中添加 OSWorld 特殊处理

def run_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run agent on a single task.

    Args:
        task: Task dictionary with 'id' and 'question'
              For OSWorld: also contains 'instruction', 'config', 'evaluator'

    Returns:
        Result dictionary
    """
    if not self.environment:
        raise ValueError("Environment not set up")

    task_id = task["id"]

    # OSWorld uses 'instruction', others use 'question'
    question = task.get("instruction") or task.get("question", "")  # [修改]

    print(f"\n{'='*60}")
    print(f"Processing Task {task_id}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    try:
        # OSWorld: Special handling for reset, recording, evaluation
        if self.environment.mode == "osworld":  # [新增]
            result = self._run_osworld_task(task, task_id, question)
        else:
            # Standard flow for other environments
            messages = self._run_conversation(question, task_id)
            final_answer = self._extract_final_answer(messages)

            result = {
                "task_id": task_id,
                "question": question,
                "answer": final_answer,
                "messages": messages,
                "success": True,
                "error": None
            }

            print(f"✓ Task {task_id} completed successfully")
            if final_answer:
                print(f"Answer: {final_answer[:100]}...")

    except Exception as e:
        print(f"✗ Task {task_id} failed: {str(e)}")
        result = {
            "task_id": task_id,
            "question": question,
            "answer": "",
            "messages": [],
            "success": False,
            "error": str(e)
        }

    return result

def _run_osworld_task(self, task: Dict[str, Any], task_id: str, instruction: str) -> Dict[str, Any]:
    """
    Run OSWorld task with special handling.

    Design:
    - Setup result directory and config
    - Reset environment
    - Start recording
    - Run conversation (with initial obs handling)
    - Evaluate
    - End recording
    - Save results

    This method encapsulates OSWorld-specific logic without polluting the main flow.
    """
    import time
    import os
    import json
    import datetime

    env = self.environment

    # Setup result directory
    result_dir = self._get_osworld_result_dir(task)
    env.update_config(
        current_result_dir=result_dir,
        instruction=instruction,
        current_task_id=task_id
    )

    # Reset environment
    print(f"🔄 Resetting environment...")
    env.reset(task)

    # Initial wait
    initial_wait = self.config.max_turns  # Reuse max_turns for initial_wait (or add new config)
    if initial_wait > 20:  # Heuristic: if max_turns > 20, use 60s wait
        initial_wait = 60
    else:
        initial_wait = 20

    print(f"⏳ Waiting {initial_wait}s for initialization...")
    time.sleep(initial_wait)

    # Get initial observation and save step_0
    obs0 = env.get_obs()
    ts0 = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
    init_png = os.path.join(result_dir, f'step_0_{ts0}.png')

    if obs0 and obs0.get('screenshot'):
        with open(init_png, 'wb') as f:
            f.write(obs0['screenshot'])
        print(f"📸 Initial screenshot saved")

    # Write trajectory header
    traj_path = os.path.join(result_dir, 'traj.jsonl')
    with open(traj_path, 'w', encoding='utf-8') as f:
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

    # Start recording
    print(f"🎥 Starting recording...")
    env.start_recording()

    # Run conversation with initial observation
    messages = self._run_osworld_conversation(instruction, task_id, obs0, init_png)

    # Settle wait
    settle_wait = 20
    print(f"⏳ Waiting {settle_wait}s for settle...")
    time.sleep(settle_wait)

    # Evaluate
    print(f"📊 Evaluating...")
    score = env.evaluate()

    # Save result
    with open(os.path.join(result_dir, 'result.txt'), 'w') as f:
        f.write(f"{score}\n")

    # End recording
    recording_path = os.path.join(result_dir, 'recording.mp4')
    env.end_recording(recording_path)
    print(f"🎬 Recording saved")

    result = {
        "task_id": task_id,
        "question": instruction,
        "answer": f"Score: {score}",
        "score": score,
        "messages": messages,
        "success": bool(score > 0),
        "error": None,
        "result_dir": result_dir
    }

    print(f"✓ Task {task_id} completed - Score: {score}")
    return result

def _get_osworld_result_dir(self, task: Dict[str, Any]) -> str:
    """Build result directory for OSWorld task."""
    # results/{action_space}/{obs_type}/{model}/{domain}/{task_id}
    action_space = self.environment.config.get('action_space', 'pyautogui')
    obs_type = self.environment.config.get('observation_type', 'screenshot_a11y_tree')
    model = self.config.model_name
    domain = (task.get('related_apps') or [task.get('snapshot', 'os')])[0]
    task_id = task['id']

    result_dir = os.path.join('results', action_space, obs_type, model, domain, task_id)
    os.makedirs(result_dir, exist_ok=True)
    return result_dir

def _run_osworld_conversation(self, instruction: str, task_id: str,
                                obs0: Dict[str, Any], init_png: str) -> List[Dict[str, Any]]:
    """
    Run OSWorld conversation with initial observation.

    Design:
    - Build messages with initial obs in first user message
    - Multi-turn loop with tool calling
    - Parse done flag from tool return
    - Return messages
    """
    import openai
    import json

    env = self.environment

    # Build initial messages with observation
    a11y_tree = obs0.get('accessibility_tree', '')
    a11y_head = '\n'.join(a11y_tree.splitlines()[:10])

    system_prompt = """You are a desktop automation assistant. Use the desktop_action tool to interact with the desktop environment.

## Strategy
1. Analyze the current observation (screenshot + accessibility tree)
2. Plan your next action to progress towards the goal
3. Call desktop_action with appropriate parameters
4. Continue until task is complete (call with action_type="DONE")

## Actions
- click: {"action_type": "click", "coordinate": [x, y]}
- type: {"action_type": "type", "text": "..."}
- key: {"action_type": "key", "key": "enter"}
- hotkey: {"action_type": "hotkey", "keys": ["ctrl", "c"]}
- WAIT: {"action_type": "WAIT"}
- DONE: {"action_type": "DONE"}
- FAIL: {"action_type": "FAIL"}
"""

    messages = [
        {"role": "developer", "content": system_prompt},
        {"role": "user", "content": (
            f"Instruction: {instruction}\n\n"
            f"Initial observation:\n"
            f"- Screenshot: {os.path.basename(init_png)}\n"
            f"- Accessibility tree (first 10 lines):\n{a11y_head}\n"
        )}
    ]

    # Create OpenAI client
    client = openai.OpenAI(
        api_key=openai.api_key,
        base_url=openai.base_url
    )

    # Multi-turn loop
    turn_count = 0
    while turn_count < self.config.max_turns:
        retry = 0

        while retry < self.config.max_retries:
            try:
                response = client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    tools=env.get_tool_schemas(),
                )

                assistant_message = response.choices[0].message
                messages.append(assistant_message.model_dump())

                if assistant_message.tool_calls:
                    tool_call = assistant_message.tool_calls[0]
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"Round {turn_count + 1}: 🔧 {tool_name}")
                    print(f"Round {turn_count + 1}:    Args: {tool_args}")

                    # Execute tool
                    tool_result = env.execute_tool(
                        tool_name,
                        tool_args,
                        step_num=turn_count + 1
                    )

                    # Parse done flag
                    first_line = tool_result.splitlines()[0].strip() if tool_result else "{}"
                    try:
                        meta = json.loads(first_line)
                        done = meta.get('done', False)
                    except:
                        done = False

                    print(f"Round {turn_count + 1}:    Done: {done}")

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result
                    })

                    if done:
                        print(f"✅ Task marked as done")
                        return messages

                    break
                else:
                    print(f"💬 No tool call")
                    return messages

            except Exception as e:
                print(f"⚠️  Retry {retry + 1}/{self.config.max_retries}: {e}")
                retry += 1
                if retry >= self.config.max_retries:
                    raise e

        turn_count += 1

    print(f"⚠️  Max turns reached")
    return messages
```

#### 4.4.3 修改 main() 函数（添加 CLI 参数）

```python
def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AgentFlow - Agent execution with Environment and Benchmark")

    # Required arguments
    parser.add_argument("--mode", type=str,
                       choices=["math", "py", "rag", "web", "osworld"],  # [修改]
                       required=True, help="Environment mode")
    parser.add_argument("--data", type=str, required=True,
                       help="Path to benchmark data file")

    # ... existing arguments ...

    # OSWorld-specific arguments  # [新增]
    parser.add_argument("--provider", type=str,
                       choices=["vmware", "virtualbox"],
                       help="VM provider (for osworld mode)")
    parser.add_argument("--vm-path", type=str,
                       help="Path to VM image (for osworld mode)")
    parser.add_argument("--snapshot", type=str, default="init_state",
                       help="VM snapshot name (for osworld mode)")
    parser.add_argument("--screen-size", type=str, default="1920x1080",
                       help="Screen size WxH (for osworld mode)")
    parser.add_argument("--headless", action="store_true",
                       help="Run VM in headless mode (for osworld mode)")
    parser.add_argument("--action-space", type=str, default="pyautogui",
                       help="Action space (for osworld mode)")
    parser.add_argument("--observation-type", type=str, default="screenshot_a11y_tree",
                       help="Observation type (for osworld mode)")

    # ... existing code ...

    # Prepare environment-specific arguments
    env_kwargs = {}
    if args.mode == "web":
        env_kwargs.update({
            "web_search_top_k": args.web_search_top_k,
            "web_search_type": args.web_search_type
        })
    elif args.mode == "rag" and args.kb_path:
        # ... existing RAG code ...
        pass
    elif args.mode == "osworld":  # [新增]
        if not args.provider or not args.vm_path:
            parser.error("--provider and --vm-path are required for osworld mode")

        width, height = map(int, args.screen_size.split('x'))

        env_kwargs.update({
            "provider_name": args.provider,
            "path_to_vm": args.vm_path,
            "snapshot_name": args.snapshot,
            "screen_size": (width, height),
            "headless": args.headless,
            "action_space": args.action_space,
            "observation_type": args.observation_type,
            "require_a11y_tree": "a11y" in args.observation_type,
            "require_terminal": False,
            "os_type": "Ubuntu"
        })

    # ... rest of main() unchanged ...
```

---

## 5. OSWorld 特殊处理逻辑

### 5.1 为什么需要特殊处理？

OSWorld 与其他环境的差异:

| 特性 | Math/Web/RAG/Py | OSWorld |
|------|----------------|---------|
| 任务输入 | `question` 字段 | `instruction` 字段 |
| 环境重置 | 无需重置 | 每个任务需要 `reset(task_config)` |
| 初始等待 | 无 | 需要 60s 等待 VM 稳定 |
| 初始观测 | 无 | 需要获取并保存 step_0 |
| 录制 | 无 | 需要 start/end recording |
| 评估 | Benchmark.evaluate | Environment.evaluate() |
| 完成判断 | 最后一条消息 | Tool 返回 `done=True` |
| 结果保存 | answer 字段 | score + trajectory + recording |

### 5.2 特殊处理的实现方式

**选项 1: 在 run_single_task 中添加 if-else 分支** (推荐)

优点:
- 最小化修改
- 特殊逻辑集中在一处
- 其他环境不受影响

缺点:
- run_single_task 代码稍长

**选项 2: 子类化 AgentRunner**

创建 `OSWorldRunner(AgentRunner)` 并重写部分方法。

优点:
- 完全分离

缺点:
- 需要额外文件
- 违反"统一 run.py"的原则

**结论**: 使用选项 1，在 `run_single_task` 中添加 `if self.environment.mode == "osworld"` 分支。

---

## 6. 数据格式与使用方式

### 6.1 OSWorld 数据格式

```jsonl
{
  "id": "task-001",
  "instruction": "Open Firefox and navigate to google.com",
  "config": [
    {"type": "execute", "command": "killall firefox"}
  ],
  "related_apps": ["chrome"],
  "evaluator": {
    "func": "is_process_running",
    "result": {"process_name": "firefox"}
  },
  "snapshot": "os_0",
  "max_steps": 15
}
```

**字段映射到 Benchmark**:
- `id` → BenchmarkItem.id
- `instruction` → BenchmarkItem.question
- 其他字段 → BenchmarkItem.metadata

### 6.2 使用命令

```bash
# Math (existing)
python run.py --mode math --data data/math_qa.jsonl

# OSWorld (new)
python run.py --mode osworld \
              --data data/osworld_examples.jsonl \
              --provider vmware \
              --vm-path /path/to/ubuntu.vmx \
              --max-turns 15 \
              --headless

# Web (existing, unchanged)
python run.py --mode web --data data/web_qa.jsonl
```

---

## 7. 完整执行流程

```
main()
  ↓
  Parse args (--mode osworld --provider vmware --vm-path ...)
  ↓
  Create AgentConfig(max_turns=15, ...)
  ↓
  Create AgentRunner(config)
  ↓
runner.run(mode="osworld", data_path="...", **env_kwargs)
  ↓
runner.setup_environment("osworld", **env_kwargs)
  ├─ Create OSWorldEnvironment(**env_kwargs)
  │    ├─ Environment.__init__(**env_kwargs)
  │    │    ├─ Set self.config
  │    │    └─ Call _initialize_tools()
  │    └─ OSWorldEnvironment._initialize_tools()
  │         ├─ Create DesktopEnv from config
  │         └─ Register DesktopActionTool(self)
  └─ Return env
  ↓
runner.load_benchmark(data_path)
  └─ Load tasks from JSONL
  ↓
runner.run_benchmark()
  ├─ For each task:
  │    └─ runner.run_single_task(task)
  │         ├─ Detect mode == "osworld"
  │         └─ _run_osworld_task(task)
  │              ├─ Setup result_dir, update env.config
  │              ├─ env.reset(task)  # Execute setup steps
  │              ├─ Wait initial_wait (60s)
  │              ├─ Get obs0, save step_0 PNG
  │              ├─ Write traj header
  │              ├─ env.start_recording()
  │              ├─ _run_osworld_conversation(...)
  │              │    ├─ Build messages with initial obs
  │              │    ├─ OpenAI client creation
  │              │    └─ Multi-turn loop:
  │              │         ├─ Call OpenAI API
  │              │         ├─ Execute desktop_action tool
  │              │         │    └─ DesktopActionTool.call()
  │              │         │         ├─ Convert params to pyautogui
  │              │         │         ├─ env.step(action)
  │              │         │         ├─ Save screenshot
  │              │         │         ├─ Append to traj.jsonl
  │              │         │         └─ Return JSON + text
  │              │         ├─ Parse done flag
  │              │         └─ Break if done=True
  │              ├─ Wait settle_wait (20s)
  │              ├─ score = env.evaluate()
  │              ├─ Save result.txt
  │              ├─ env.end_recording(recording.mp4)
  │              └─ Return result
  └─ env.close()  # After ALL tasks
  ↓
runner.evaluate_results() (optional)
  ↓
runner.save_results()
  ↓
Return summary
```

---

## 8. 与其他模式的对比

### 8.1 代码路径对比

| 步骤 | Math/Web/RAG/Py | OSWorld |
|------|----------------|---------|
| setup_environment | MathEnvironment() | OSWorldEnvironment() |
| load_benchmark | Benchmark(data_path) | Benchmark(data_path) (same) |
| run_single_task | Standard flow | `_run_osworld_task()` |
| _run_conversation | Build messages, loop | `_run_osworld_conversation()` with obs |
| Tool execution | Calculator/WebSearch | DesktopActionTool |
| Result | {"answer": "..."} | {"score": 0.8, "result_dir": "..."} |
| Cleanup | None | env.close() |

### 8.2 改动量对比

| 文件 | 改动类型 | 行数 |
|------|---------|------|
| envs/__init__.py | 添加导出 | +2 |
| envs/enviroment.py | 添加类定义 | +150 |
| tools/__init__.py | 添加导出 | +2 |
| tools/osworld_tools.py | 新增文件 | +200 |
| run.py | 添加方法和分支 | +150 |
| data/osworld_examples.jsonl | 新增数据 | N/A |
| **总计** | | **~504 行** |

### 8.3 兼容性保证

- ✅ 不修改现有环境 (Math/Py/RAG/Web)
- ✅ 不修改 Benchmark 基类
- ✅ 不修改 Environment 基类
- ✅ 现有命令完全不受影响
- ✅ 新增代码集中在独立文件和可选分支

---

## 9. 实施检查清单

### 9.1 文件创建

- [ ] 创建 `tools/osworld_tools.py`
- [ ] 创建 `data/osworld_examples.jsonl`
- [ ] (可选) 创建 `envs/osworld_environment.py`

### 9.2 文件修改

- [ ] 修改 `envs/__init__.py` (添加导出)
- [ ] 修改 `envs/enviroment.py` (添加 OSWorldEnvironment 类)
- [ ] 修改 `tools/__init__.py` (添加导出)
- [ ] 修改 `run.py`:
  - [ ] setup_environment 添加 osworld 分支
  - [ ] run_single_task 添加 osworld 检测
  - [ ] 添加 _run_osworld_task 方法
  - [ ] 添加 _run_osworld_conversation 方法
  - [ ] 添加 _get_osworld_result_dir 方法
  - [ ] main() 添加 CLI 参数

### 9.3 测试

- [ ] 测试 Math 模式 (确保未受影响)
- [ ] 测试 Web 模式 (确保未受影响)
- [ ] 测试 OSWorld 模式:
  - [ ] Environment 初始化
  - [ ] Tool 注册
  - [ ] 单任务执行
  - [ ] 轨迹保存
  - [ ] 录像保存
  - [ ] 评估
  - [ ] 批量执行
  - [ ] Environment 关闭

---

## 10. 总结

### 10.1 核心设计原则

1. **最小化改动**: ~500 行新增代码，~60 行修改
2. **复用架构**: 使用 Environment/Tool/Benchmark 基类
3. **并存不冲突**: OSWorld 作为新模式，不影响现有模式
4. **统一接口**: 使用相同的 run.py 入口
5. **特殊处理集中**: OSWorld 特殊逻辑集中在可选分支

### 10.2 关键技术点

1. **Environment 继承**: OSWorldEnvironment 继承 Environment
2. **Tool 注册**: DesktopActionTool 通过 register_tool 注册
3. **配置传递**: 通过 env.config 和 kwargs 传递参数
4. **特殊逻辑**: 在 run_single_task 中通过 mode 检测分发
5. **状态管理**: reset/step/evaluate/close 封装访问

### 10.3 优势

✅ 不需要创建 run_osworld.py，复用现有 run.py
✅ 与其他环境并存，使用方式一致
✅ 改动集中、清晰、可维护
✅ 特殊处理逻辑封装在独立方法中
✅ 完全兼容现有架构和使用方式

---

**下一步**: 按照检查清单逐步实施，先创建新文件，再修改现有文件，最后测试验证。
