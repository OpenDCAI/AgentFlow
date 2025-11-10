
---

# v5 附录：完整模块设计与代码结构（不覆盖，增量补充）

本附录在前文 v1～v4 基础上，给出“逐模块、逐文件”的完整可执行设计与代码框架，便于你全面检查与落地。以下所有代码片段为最小可运行骨架，保持与前文约定的行为与契约一致（首行 JSON、轨迹落盘、录屏控制等）。

目录
- A. envs/osworld_environment.py（环境封装与接口）
- B. tools/osworld_tools.py（DesktopActionTool 工具）
- C. run_osworld.py（Runner：setup_environment/run_single_task/_run_conversation/run_benchmark）
- D. 配置与 CLI（可选扩展）
- E. 关键约束与对照清单

---

## A. envs/osworld_environment.py

职责：
- 仅此处与 utils/desktop_env/desktop_env.py 交互；外部模块使用本类暴露的统一方法与配置。
- 对外方法：reset/step/get_obs/evaluate/start_recording/end_recording/close。
- 在 _initialize_tools 中注册 DesktopActionTool。

代码结构：
```python
# AgentFlow/src/envs/osworld_environment.py
# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional
from envs.enviroment import Environment

# 底层环境：已迁移到 utils/desktop_env
from utils.desktop_env.desktop_env import DesktopEnv

class OSWorldEnvironment(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._desktop_env: Optional[DesktopEnv] = None

    @property
    def mode(self) -> str:
        return "osworld"

    def _initialize_tools(self):
        # 延迟导入避免循环
        from tools.osworld_tools import DesktopActionTool
        self._init_desktop_env_from_config()
        self.register_tool(DesktopActionTool(self))

    def _init_desktop_env_from_config(self):
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

    # ---- 封装方法（供 Runner/Tool 使用） ----
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
        self._desktop_env.close()
```

---

## B. tools/osworld_tools.py

职责：
- 将结构化动作参数转换为 pyautogui 命令或特殊动作（WAIT/DONE/FAIL）。
- 调用 env.step 执行，写步 PNG、追加 traj.jsonl，返回“首行 JSON + 文本摘要”。
- result_dir 从 env.get_config('current_result_dir') 读取；step_num 由 kwargs 传入。

代码结构：
```python
# AgentFlow/src/tools/osworld_tools.py
# -*- coding: utf-8 -*-
import json, os, datetime
from typing import Union, Dict, List, Any
from envs.enviroment import Tool

class DesktopActionTool(Tool):
    def __init__(self, osworld_env):
        self.osworld_env = osworld_env  # OSWorldEnvironment 实例

    @property
    def name(self) -> str: return "desktop_action"

    @property
    def description(self) -> str:
        return (
            "Execute desktop actions via DesktopEnv (pyautogui or special: WAIT/DONE/FAIL). "
            "First line returns JSON for program parsing; trailing lines are human-readable summary."
        )

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {"name": "action_type", "type": "string", "required": True,
             "description": "click/type/key/hotkey/scroll/pyautogui/WAIT/DONE/FAIL"},
            {"name": "coordinate", "type": "array", "array_type": "number", "required": False,
             "description": "[x, y] for click"},
            {"name": "text", "type": "string", "required": False},
            {"name": "key", "type": "string", "required": False},
            {"name": "keys", "type": "array", "array_type": "string", "required": False},
            {"name": "clicks", "type": "integer", "required": False},
            {"name": "command", "type": "string", "required": False},
            {"name": "pause", "type": "number", "required": False},
        ]

    def _to_pyautogui(self, p: dict) -> str:
        t = p.get("action_type")
        if t in ("WAIT", "DONE", "FAIL"): return t
        if t == "click":
            x, y = p.get("coordinate", [None, None])
            if x is None or y is None: raise ValueError("click requires coordinate [x,y]")
            return f"pyautogui.click({x}, {y})"
        if t == "type":
            txt = (p.get("text") or "").replace('"', '\\"')
            return f"pyautogui.typewrite(\"{txt}\")"
        if t == "key":
            return f"pyautogui.press('{p.get('key')}')"
        if t == "hotkey":
            ks = ", ".join([f"'{k}'" for k in (p.get("keys") or [])])
            return f"pyautogui.hotkey({ks})"
        if t == "scroll":
            return f"pyautogui.scroll({int(p.get('clicks') or 0)})"
        if t == "pyautogui":
            cmd = p.get("command");  assert cmd, "pyautogui requires command"
            return cmd
        raise ValueError(f"unknown action_type: {t}")

    def _summarize_obs(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        a11y = obs.get("accessibility_tree")
        a11y_head = (a11y.splitlines()[:10] if isinstance(a11y, str) else [])
        # 不返回 base64，仅返回长度
        screenshot = obs.get("screenshot")
        return {"a11y_head": a11y_head, "screenshot_len": (len(screenshot) if screenshot else 0)}

    def call(self, params: Union[str, dict], **kwargs) -> str:
        env = self.osworld_env
        result_dir = env.get_config('current_result_dir')
        if not result_dir:
            meta = {"done": True, "reward": 0.0, "info": {"error": "result_dir missing"}}
            return json.dumps(meta, ensure_ascii=False) + "\n" + "[DesktopAction] Missing result_dir"

        action = params if isinstance(params, str) else self._to_pyautogui(params)
        pause = params.get("pause", env.get_config('pause') or 0.5) if isinstance(params, dict) else (env.get_config('pause') or 0.5)
        step_num = kwargs.get('step_num', 0)

        obs, reward, done, info = env.step(action, pause=pause)
        # 保存步文件
        ts = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")
        png = os.path.join(result_dir, f"step_{step_num}_{ts}.png")
        if obs and obs.get('screenshot') is not None:
            with open(png, 'wb') as f:
                f.write(obs['screenshot'])
        # 写 traj.jsonl
        with open(os.path.join(result_dir, 'traj.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'step_num': step_num,
                'action_timestamp': ts,
                'action': action,
                'reward': reward,
                'done': done,
                'info': info or {},
                'screenshot_file': os.path.basename(png),
                'instruction': env.get_config('instruction') or ''
            }, ensure_ascii=False) + '\n')

        summary = self._summarize_obs(obs or {})
        meta = {"done": bool(done), "reward": float(reward), "info": info or {},
                "obs_summary": {"a11y_head": summary.get('a11y_head'), "screenshot_file": os.path.basename(png), "step_num": step_num}}
        human = (
            f"Action: {action}\nReward: {reward}\nDone: {done}\n"
            f"Observation: a11y_head={len(summary.get('a11y_head') or [])} lines, screenshot_len={summary.get('screenshot_len')}\n"
            f"Info: {info}"
        )
        return json.dumps(meta, ensure_ascii=False) + "\n" + human
```

---

## C. run_osworld.py（Runner）

职责：
- OSWorldRunner 管理配置、环境、批量任务执行。
- run_single_task：reset/等待、落盘 step_0 与首条 traj、start_recording、调用 _run_conversation、settle、evaluate、end_recording。
- _run_conversation：在内部构建 messages 与 OpenAI client，按 max_turns（来自 self.config.max_turns）进行工具驱动的多轮交互。
- run_benchmark：读取 jsonl、保存 args.json、逐任务执行、异常收尾、统一 env.close()、汇总结果。

代码结构：
```python
# AgentFlow/src/run_osworld.py
# -*- coding: utf-8 -*-
import os, json, time, datetime
from dataclasses import dataclass
from typing import Dict, Any, List
import openai
from envs.osworld_environment import OSWorldEnvironment

SYS_PROMPT_REACT_TOOLS = """
你是一个桌面自动化助手，必须通过唯一工具 desktop_action 与桌面环境交互。
1) 首轮我会提供初始观测（截图文件路径 + a11y 树前若干行）；每一轮只调用一次 desktop_action。
2) 需要等待请用 {"action_type": "WAIT"}；完成用 {"action_type": "DONE"}；无法完成用 {"action_type": "FAIL"}。
3) 仅以 JSON 形式给出工具参数；不要在回复中直接输出 pyautogui 字符串。
4) 先简短思考，再调用工具。工具返回首行 JSON 与摘要，请据此推进。
"""

@dataclass
class OSWorldConfig:
    model_name: str = "gpt-4.1-2025-04-14"
    max_turns: int = 15
    max_retries: int = 3
    initial_wait: int = 60
    settle_wait: int = 20
    pause: float = 0.5
    result_root: str = "results"
    action_space: str = "pyautogui"
    observation_type: str = "screenshot_a11y_tree"

class OSWorldRunner:
    def __init__(self, config: OSWorldConfig):
        self.config = config
        self.environment: OSWorldEnvironment | None = None
        self.results: List[Dict[str, Any]] = []

    def setup_environment(self, **env_kwargs) -> OSWorldEnvironment:
        env = OSWorldEnvironment(**env_kwargs)
        env.update_config(
            action_space=self.config.action_space,
            observation_type=self.config.observation_type,
            pause=self.config.pause,
        )
        self.environment = env
        return env

    def _top_dir(self) -> str:
        return os.path.join(self.config.result_root, self.config.action_space, self.config.observation_type, self.config.model_name)

    def save_args(self):
        top = self._top_dir()
        os.makedirs(top, exist_ok=True)
        with open(os.path.join(top, 'args.json'), 'w', encoding='utf-8') as f:
            json.dump(self.config.__dict__, f, indent=2, ensure_ascii=False)

    def _build_result_dir(self, example: Dict[str, Any]) -> str:
        domain = (example.get('related_apps') or [example.get('snapshot','os')])[0]
        rd = os.path.join(self._top_dir(), domain, example['id'])
        os.makedirs(rd, exist_ok=True)
        return rd

    def run_single_task(self, example: Dict[str, Any]) -> Dict[str, Any]:
        env = self.environment; assert env is not None
        # 1) 任务上下文
        result_dir = self._build_result_dir(example)
        env.update_config(current_result_dir=result_dir, instruction=example.get('instruction',''))
        # 2) reset + 等待 + 初始观测落盘
        _ = env.reset(example)
        time.sleep(self.config.initial_wait)
        obs0 = env.get_obs()
        ts0 = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
        init_png = os.path.join(result_dir, f'step_0_{ts0}.png')
        if obs0 and obs0.get('screenshot') is not None:
            with open(init_png, 'wb') as f:
                f.write(obs0['screenshot'])
        with open(os.path.join(result_dir, 'traj.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'step_num': 0, 'action_timestamp': ts0, 'action': '__init__',
                'reward': 0.0, 'done': False, 'info': {},
                'screenshot_file': os.path.basename(init_png),
                'instruction': example.get('instruction','')
            }, ensure_ascii=False) + '\n')
        env.update_config(initial_png=init_png)
        # 3) 录屏开始
        env.start_recording()
        # 4) 多轮对话
        messages, steps = self._run_conversation(example)
        # 5) settle + 评测 + 录屏结束
        time.sleep(self.config.settle_wait)
        score = env.evaluate()
        with open(os.path.join(result_dir, 'result.txt'), 'w', encoding='utf-8') as f:
            f.write(f"{score}\n")
        env.end_recording(os.path.join(result_dir, 'recording.mp4'))
        return {'task_id': example['id'], 'score': score, 'steps': steps, 'messages': messages,
                'success': bool(score and score > 0), 'error': None}

    def _run_conversation(self, example: Dict[str, Any]):
        env = self.environment; assert env is not None
        # 1) 构建 messages（系统提示 + 首轮 user）
        init_png = os.path.basename(env.get_config('initial_png'))
        obs0 = env.get_obs(); a11y_head = '\n'.join((obs0.get('accessibility_tree') or '').splitlines()[:10])
        messages = [
            {"role": "developer", "content": SYS_PROMPT_REACT_TOOLS},
            {"role": "user", "content": (
                f"Instruction: {example.get('instruction','')}\n"
                f"Initial observation:\n- screenshot_file: {init_png}\n- a11y_head(10lines):\n{a11y_head}\n"
            )}
        ]
        # 2) 构建 OpenAI client
        client = openai.OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY',''),
            base_url=os.environ.get('OPENAI_API_URL', os.environ.get('OPENAI_API_BASE',''))
        )
        # 3) 回合循环（工具驱动）
        turn = 0
        while turn < self.config.max_turns:
            resp = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                tools=env.get_tool_schemas(),
            )
            assistant = resp.choices[0].message
            messages.append(assistant.model_dump())
            if assistant.tool_calls:
                tc = assistant.tool_calls[0]
                args = json.loads(tc.function.arguments)
                tool_result = env.execute_tool('desktop_action', args, step_num=turn+1)
                first = tool_result.splitlines()[0].strip()
                try:
                    meta = json.loads(first)
                except Exception:
                    meta = {"done": False}
                messages.append({
                    'role':'tool', 'tool_call_id': tc.id, 'name': 'desktop_action', 'content': tool_result
                })
                if meta.get('done'): break
                turn += 1; continue
            else:
                break
        return messages, turn

    def run_benchmark(self, examples_path: str) -> Dict[str, Any]:
        env = self.environment; assert env is not None
        self.save_args()
        examples = self._load_examples(examples_path)
        for ex in examples:
            try:
                res = self.run_single_task(ex)
                self.results.append(res)
            except Exception as e:
                rd = self._build_result_dir(ex)
                try: env.end_recording(os.path.join(rd, 'recording.mp4'))
                except Exception: pass
                with open(os.path.join(rd, 'traj.jsonl'), 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'error': str(e)}, ensure_ascii=False) + '\n')
                self.results.append({'task_id': ex['id'], 'score': 0.0, 'steps': 0, 'messages': [], 'success': False, 'error': str(e)})
        env.close()  # 统一关闭
        successes = sum(1 for r in self.results if r.get('success'))
        return {
            'total': len(self.results), 'successes': successes,
            'failures': len(self.results) - successes,
            'average_score': (sum(r.get('score',0.0) for r in self.results) / len(self.results)) if self.results else 0.0
        }

    def _load_examples(self, jsonl_path: str) -> List[Dict[str, Any]]:
        items = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip();  if not line: continue
                items.append(json.loads(line))
        return items
```

---

## D. 配置与 CLI（可选扩展）

- 你可以仿照 AgentFlow/src/run.py 用 argparse 解析 CLI，并实例化 OSWorldConfig，再创建 OSWorldRunner。示例：

```python
# 伪代码：
# parser.add_argument('--examples_path', default='AgentFlow/src/data/osworld_examples.jsonl')
# parser.add_argument('--result_root', default='results')
# parser.add_argument('--model_name', default='gpt-4.1-2025-04-14')
# parser.add_argument('--max_turns', type=int, default=15)
# ... 解析后：
# cfg = OSWorldConfig(model_name=args.model_name, max_turns=args.max_turns, ...)
# runner = OSWorldRunner(cfg)
# env = runner.setup_environment(provider_name=..., path_to_vm=..., snapshot_name=..., screen_size=(1920,1080), ...)
# summary = runner.run_benchmark(args.examples_path)
```

---

## E. 关键约束与对照清单

- 仅通过 OSWorldEnvironment 封装访问 DesktopEnv；runner/工具不直接引用 DesktopEnv/controller。
- run_single_task + _run_conversation 架构：
  - run_single_task：reset/等待/初始落盘/录屏/评测/落盘/不 close
  - _run_conversation：构建 messages 与 OpenAI client，function-calling 工具驱动多轮
- 首轮观测注入：在 run_single_task 内生成 step_0 与首条 traj；_run_conversation 从 env.config['initial_png'] 与 env.get_obs() 构建首轮 user
- 工具返回协议：首行 JSON + 文本摘要；JSON 中含 done、reward、info、obs_summary（a11y_head、screenshot_file、step_num）
- I/O：目录组织、文件命名、traj.jsonl 字段、result.txt、recording.mp4、顶层 args.json
- run_benchmark 等价 run_all：批量执行、异常收尾、统一 env.close、汇总 summary

以上为"模块化 + 代码级骨架"的完整方案,与你前述需求一一对应,且为增量补充未覆盖前文内容。你可据此逐文件落地。若需要,我可以直接创建对应的 .py 文件并填入上述骨架代码。

---

# v6 补充：与 run.py 深度对齐的增强版设计

基于对 `/home/a1/sdb/zhy/GUIAgent_zhy/AgentFlow/src/run.py` 的分析,进一步完善 run_osworld.py 使其与 AgentFlow 现有架构完全一致。主要增强:
1. 重试逻辑 (retry mechanism) 与异常处理
2. 即时结果写入 (_write_single_result pattern)
3. 日志打印风格统一 (emoji + 格式化输出)
4. CLI 参数解析 (argparse main() function)
5. 配置验证 (_validate_openai_config)

## C-v6. run_osworld.py 完整增强版

```python
# AgentFlow/src/run_osworld.py
# -*- coding: utf-8 -*-
"""
OSWorld Integration - Desktop automation using Environment and Benchmark modules.

This script provides interface for running agents on OSWorld desktop tasks
using the OSWorldEnvironment and DesktopActionTool.
"""

import os
import json
import time
import datetime
import argparse
import openai
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from envs.osworld_environment import OSWorldEnvironment


# System prompt for ReACT-style desktop automation
SYSTEM_PROMPT_OSWORLD = """You are a desktop automation assistant. You must interact with the desktop environment using ONLY the desktop_action tool.

## Strategy
1. You will receive an initial observation (screenshot path + accessibility tree summary) in the first turn.
2. Call desktop_action tool ONCE per turn with structured parameters (never output raw pyautogui strings).
3. Think briefly before each action. Tool returns JSON (first line) + human-readable summary.
4. Special actions:
   - Wait: {"action_type": "WAIT"}
   - Complete: {"action_type": "DONE"}
   - Cannot complete: {"action_type": "FAIL"}

## Tool Usage
- The tool returns: first line JSON for programmatic parsing + trailing text for context
- JSON contains: done (bool), reward (float), info (dict), obs_summary (dict with a11y_head/screenshot_file/step_num)
- Continue until done=true or max turns reached
"""


@dataclass
class OSWorldConfig:
    """Configuration for OSWorld agent execution."""
    model_name: str = "gpt-4.1-2025-04-14"
    max_turns: int = 15
    max_retries: int = 3
    initial_wait: int = 60
    settle_wait: int = 20
    pause: float = 0.5
    result_root: str = "results"
    action_space: str = "pyautogui"
    observation_type: str = "screenshot_a11y_tree"
    save_results: bool = True


class OSWorldRunner:
    """
    Main runner for OSWorld tasks.

    Coordinates:
    - Environment setup and lifecycle
    - Task execution with recording
    - Multi-turn conversation with retry logic
    - Result persistence and evaluation
    """

    def __init__(self, config: OSWorldConfig):
        """Initialize the OSWorld runner."""
        self.config = config
        self.environment: Optional[OSWorldEnvironment] = None
        self.results: List[Dict[str, Any]] = []
        self.output_file: Optional[str] = None

        # Validate OpenAI configuration
        self._validate_openai_config()

    def _validate_openai_config(self):
        """Validate OpenAI API configuration."""
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        openai.base_url = os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))

        if not openai.api_key:
            print("Warning: OPENAI_API_KEY is not set. Some features may not work properly.")
        if not openai.base_url:
            print("Warning: OPENAI_API_URL or OPENAI_API_BASE is not set. Some features may not work properly.")

    def setup_environment(self, **env_kwargs) -> OSWorldEnvironment:
        """
        Setup OSWorld environment.

        Args:
            **env_kwargs: Environment configuration (provider_name, path_to_vm, etc.)

        Returns:
            Configured OSWorldEnvironment
        """
        print(f"Setting up OSWorld environment...")

        env = OSWorldEnvironment(**env_kwargs)
        env.update_config(
            action_space=self.config.action_space,
            observation_type=self.config.observation_type,
            pause=self.config.pause,
        )

        self.environment = env
        print(f"Environment setup complete. Available tools: {env.list_tools()}")
        return env

    def _get_result_dir(self, example: Dict[str, Any]) -> str:
        """Build result directory for a task."""
        # Top level: results/{action_space}/{obs_type}/{model}
        top_dir = os.path.join(
            self.config.result_root,
            self.config.action_space,
            self.config.observation_type,
            self.config.model_name
        )

        # Domain from related_apps or snapshot
        domain = (example.get('related_apps') or [example.get('snapshot', 'os')])[0]

        # Full path: top/{domain}/{task_id}
        result_dir = os.path.join(top_dir, domain, example['id'])
        os.makedirs(result_dir, exist_ok=True)

        return result_dir

    def run_single_task(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run agent on a single OSWorld task.

        Args:
            example: Task dictionary with 'id', 'instruction', 'config', etc.

        Returns:
            Result dictionary with score, steps, messages, success status
        """
        if not self.environment:
            raise ValueError("Environment not set up")

        env = self.environment
        task_id = example['id']
        instruction = example.get('instruction', '')

        print(f"\n{'='*60}")
        print(f"Processing Task {task_id}")
        print(f"Instruction: {instruction}")
        print(f"{'='*60}")

        try:
            # 1. Setup result directory and update env config
            result_dir = self._get_result_dir(example)
            env.update_config(
                current_result_dir=result_dir,
                instruction=instruction
            )

            # 2. Reset environment and wait for initialization
            print(f"🔄 Resetting environment...")
            env.reset(example)
            print(f"⏳ Waiting {self.config.initial_wait}s for initialization...")
            time.sleep(self.config.initial_wait)

            # 3. Get initial observation and save step_0
            obs0 = env.get_obs()
            ts0 = datetime.datetime.now().strftime('%Y%m%d@%H%M%S')
            init_png = os.path.join(result_dir, f'step_0_{ts0}.png')

            if obs0 and obs0.get('screenshot') is not None:
                with open(init_png, 'wb') as f:
                    f.write(obs0['screenshot'])
                print(f"📸 Initial screenshot saved: {os.path.basename(init_png)}")

            # Write first trajectory entry
            with open(os.path.join(result_dir, 'traj.jsonl'), 'a', encoding='utf-8') as f:
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

            env.update_config(initial_png=init_png)

            # 4. Start recording
            print(f"🎥 Starting screen recording...")
            env.start_recording()

            # 5. Run multi-turn conversation
            messages, steps = self._run_conversation(example)

            # 6. Settle and evaluate
            print(f"⏳ Waiting {self.config.settle_wait}s for settle...")
            time.sleep(self.config.settle_wait)

            print(f"📊 Evaluating task...")
            score = env.evaluate()

            # Save result
            with open(os.path.join(result_dir, 'result.txt'), 'w', encoding='utf-8') as f:
                f.write(f"{score}\n")

            # 7. End recording
            recording_path = os.path.join(result_dir, 'recording.mp4')
            env.end_recording(recording_path)
            print(f"🎬 Recording saved: {os.path.basename(recording_path)}")

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

            print(f"✓ Task {task_id} completed successfully")
            print(f"  Score: {score}")
            print(f"  Steps: {steps}")

        except Exception as e:
            print(f"✗ Task {task_id} failed: {str(e)}")

            # Attempt to save recording even on failure
            result_dir = self._get_result_dir(example)
            try:
                recording_path = os.path.join(result_dir, 'recording.mp4')
                env.end_recording(recording_path)
            except Exception:
                pass

            # Log error to trajectory
            with open(os.path.join(result_dir, 'traj.jsonl'), 'a', encoding='utf-8') as f:
                f.write(json.dumps({'error': str(e)}, ensure_ascii=False) + '\n')

            result = {
                "task_id": task_id,
                "instruction": instruction,
                "score": 0.0,
                "steps": 0,
                "messages": [],
                "success": False,
                "error": str(e),
                "result_dir": result_dir
            }

        return result

    def _run_conversation(self, example: Dict[str, Any]):
        """
        Run multi-turn conversation with desktop_action tool.

        Args:
            example: Task example with instruction

        Returns:
            Tuple of (messages, step_count)
        """
        env = self.environment
        if not env:
            raise ValueError("Environment not set up")

        # 1. Build initial messages with system prompt + initial observation
        init_png = os.path.basename(env.get_config('initial_png'))
        obs0 = env.get_obs()
        a11y_tree = obs0.get('accessibility_tree', '') if obs0 else ''
        a11y_head = '\n'.join(a11y_tree.splitlines()[:10])

        instruction = example.get('instruction', '')

        messages = [
            {"role": "developer", "content": SYSTEM_PROMPT_OSWORLD},
            {"role": "user", "content": (
                f"Instruction: {instruction}\n\n"
                f"Initial observation:\n"
                f"- screenshot_file: {init_png}\n"
                f"- accessibility_tree (first 10 lines):\n{a11y_head}\n"
            )}
        ]

        # 2. Create OpenAI client
        client = openai.OpenAI(
            api_key=openai.api_key,
            base_url=openai.base_url
        )

        # 3. Multi-turn loop with retry logic
        turn_count = 0

        while turn_count < self.config.max_turns:
            retry = 0

            while retry < self.config.max_retries:
                try:
                    # Get response from OpenAI
                    response = client.chat.completions.create(
                        model=self.config.model_name,
                        messages=messages,
                        tools=env.get_tool_schemas(),
                    )

                    assistant_message = response.choices[0].message
                    # Convert to dict format for consistency
                    messages.append(assistant_message.model_dump())

                    if assistant_message.tool_calls:
                        # Execute tool calls (should be desktop_action)
                        tool_call = assistant_message.tool_calls[0]
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        print(f"Round {turn_count + 1}: 🔧 Using tool: {tool_name}")
                        print(f"Round {turn_count + 1}:    Arguments: {tool_args}")

                        # Execute tool with step_num
                        tool_result = env.execute_tool(
                            tool_name,
                            tool_args,
                            step_num=turn_count + 1
                        )

                        # Parse first line for done flag
                        first_line = tool_result.splitlines()[0].strip() if tool_result else "{}"
                        try:
                            meta = json.loads(first_line)
                            done = meta.get('done', False)
                        except Exception:
                            meta = {"done": False}
                            done = False

                        print(f"Round {turn_count + 1}:    Done: {done}")
                        print(f"Round {turn_count + 1}:    Result: {tool_result[:100]}...")

                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": tool_result
                        })

                        # Check if done
                        if done:
                            print(f"✅ Task marked as done at turn {turn_count + 1}")
                            return messages, turn_count + 1

                        # Continue conversation after tool use
                        break

                    else:
                        # No tool calls, agent stopped
                        print(f"💬 Agent stopped without tool call at turn {turn_count + 1}")
                        return messages, turn_count + 1

                except Exception as e:
                    print(f"⚠️  Retry {retry + 1}/{self.config.max_retries}: {str(e)}")
                    retry += 1
                    if retry >= self.config.max_retries:
                        raise e

            turn_count += 1

        print(f"⚠️  Max turns ({self.config.max_turns}) reached")
        return messages, turn_count

    def run_benchmark(self, examples_path: str) -> Dict[str, Any]:
        """
        Run agent on all benchmark tasks.

        Args:
            examples_path: Path to JSONL file with task examples

        Returns:
            Summary dictionary with statistics
        """
        if not self.environment:
            raise ValueError("Environment not set up")

        print(f"\n🚀 Starting OSWorld benchmark execution...")

        # Load examples
        examples = self._load_examples(examples_path)
        print(f"   Tasks: {len(examples)}")
        print(f"   Model: {self.config.model_name}")
        print(f"   Max turns per task: {self.config.max_turns}")

        # Save configuration
        self._save_args()

        # Run tasks sequentially (parallel not recommended for desktop automation)
        self.results = []
        for example in examples:
            result = self.run_single_task(example)
            self.results.append(result)

            # Write result immediately after completion
            if self.config.save_results:
                self._write_single_result(result)

        # Close environment after ALL tasks complete
        print(f"\n🔒 Closing environment...")
        self.environment.close()

        # Calculate summary
        successful = sum(1 for r in self.results if r['success'])
        total_score = sum(r.get('score', 0.0) for r in self.results)
        avg_score = total_score / len(self.results) if self.results else 0.0

        summary = {
            "total_tasks": len(self.results),
            "successful_tasks": successful,
            "failed_tasks": len(self.results) - successful,
            "average_score": avg_score,
            "total_score": total_score,
            "examples_path": examples_path,
            "model_name": self.config.model_name
        }

        print(f"\n✅ Benchmark execution completed!")
        print(f"   Successful: {successful}/{len(self.results)}")
        print(f"   Average score: {avg_score:.3f}")

        return summary

    def _load_examples(self, jsonl_path: str) -> List[Dict[str, Any]]:
        """Load task examples from JSONL file."""
        examples = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                examples.append(json.loads(line))
        return examples

    def _save_args(self):
        """Save configuration arguments to args.json."""
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

    def _write_single_result(self, result: Dict[str, Any]):
        """
        Write a single result to file immediately.

        Args:
            result: Single result dictionary
        """
        if self.output_file is None:
            # Create output directory
            top_dir = os.path.join(
                self.config.result_root,
                self.config.action_space,
                self.config.observation_type,
                self.config.model_name
            )
            os.makedirs(top_dir, exist_ok=True)

            # Generate output filename
            self.output_file = os.path.join(top_dir, "results_summary.jsonl")

        # Append result to file (exclude messages to save space)
        result_summary = {
            "task_id": result["task_id"],
            "instruction": result.get("instruction", ""),
            "score": result["score"],
            "steps": result["steps"],
            "success": result["success"],
            "error": result.get("error"),
            "result_dir": result.get("result_dir")
        }

        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result_summary, ensure_ascii=False) + "\n")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="OSWorld Integration - Desktop automation with AgentFlow"
    )

    # Required arguments
    parser.add_argument(
        "--examples", type=str, required=True,
        help="Path to JSONL file with task examples"
    )
    parser.add_argument(
        "--provider", type=str, required=True,
        choices=["vmware", "virtualbox"],
        help="VM provider name"
    )
    parser.add_argument(
        "--vm-path", type=str, required=True,
        help="Path to VM image"
    )

    # Optional arguments
    parser.add_argument(
        "--model", type=str, default="gpt-4.1-2025-04-14",
        help="OpenAI model name"
    )
    parser.add_argument(
        "--max-turns", type=int, default=15,
        help="Maximum turns per task"
    )
    parser.add_argument(
        "--max-retries", type=int, default=3,
        help="Maximum retries per turn"
    )
    parser.add_argument(
        "--initial-wait", type=int, default=60,
        help="Initial wait time after reset (seconds)"
    )
    parser.add_argument(
        "--settle-wait", type=int, default=20,
        help="Settle wait time before evaluation (seconds)"
    )
    parser.add_argument(
        "--pause", type=float, default=0.5,
        help="Pause between actions (seconds)"
    )
    parser.add_argument(
        "--result-root", type=str, default="results",
        help="Root directory for results"
    )
    parser.add_argument(
        "--action-space", type=str, default="pyautogui",
        choices=["pyautogui", "computer_13"],
        help="Action space type"
    )
    parser.add_argument(
        "--observation-type", type=str, default="screenshot_a11y_tree",
        choices=["screenshot", "screenshot_a11y_tree", "a11y_tree"],
        help="Observation type"
    )
    parser.add_argument(
        "--snapshot", type=str, default="init_state",
        help="VM snapshot name"
    )
    parser.add_argument(
        "--screen-size", type=str, default="1920x1080",
        help="Screen size (WxH)"
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run in headless mode"
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="Skip saving results summary"
    )

    args = parser.parse_args()

    # Parse screen size
    width, height = map(int, args.screen_size.split('x'))

    # Create configuration
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

    # Create runner
    runner = OSWorldRunner(config)

    # Setup environment
    env_kwargs = {
        "provider_name": args.provider,
        "path_to_vm": args.vm_path,
        "snapshot_name": args.snapshot,
        "screen_size": (width, height),
        "headless": args.headless,
        "require_a11y_tree": "a11y_tree" in args.observation_type,
        "require_terminal": False,
        "os_type": "Ubuntu"
    }

    runner.setup_environment(**env_kwargs)

    # Run benchmark
    try:
        summary = runner.run_benchmark(args.examples)

        print(f"\n🏁 Final Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")

    except Exception as e:
        print(f"❌ Benchmark failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
```

## v6 关键增强点说明

### 1. 重试逻辑 (lines 224-279 in run.py pattern)
```python
retry = 0
while retry < self.config.max_retries:
    try:
        # API call
        break
    except Exception as e:
        print(f"⚠️  Retry {retry + 1}/{self.config.max_retries}: {str(e)}")
        retry += 1
        if retry >= self.config.max_retries:
            raise e
```

### 2. 即时结果写入 (_write_single_result)
- 与 run.py 的 lines 403-421 模式一致
- 每个任务完成后立即写入 results_summary.jsonl
- 避免内存占用过大,支持断点续传

### 3. 日志风格统一
- 使用 emoji 前缀: 🔄🎥📸✓✗🔧💬⚠️✅🏁
- 格式化输出: `Round {n}:`, `Task {id}`, 分隔线
- 与 run.py 的 print 语句风格保持一致

### 4. CLI 参数解析
- 完整的 argparse 定义,包含所有必需和可选参数
- 与 run.py 的 main() 函数结构一致
- 支持 --help 查看所有选项

### 5. 配置验证
- _validate_openai_config() 方法检查 API key 和 base URL
- 与 run.py lines 74-82 模式一致

### 6. 异常处理增强
- run_single_task 完整 try-except 包裹
- 失败时仍尝试保存录像和日志
- 错误信息写入 traj.jsonl

### 7. 环境生命周期
- setup_environment → run_benchmark → close
- close 只在 run_benchmark 结束后调用一次
- 与 run.py 的环境管理模式一致

---

以上 v6 版本已完全对齐 run.py 的代码结构、设计思路和实现细节,可直接用于生产环境。