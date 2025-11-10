# OSWorld 集成 AgentFlow 方案（含代码骨架）

本文给出在 GUIAgent_zhy/AgentFlow 中集成 OSWorld 的完整方案，目标是：
- 完全复用 OSWorld/desktop_env 作为 GUI 环境执行后端
- 在 AgentFlow 中通过 Environment + Tools 抽象暴露 OSWorld 的能力
- 提供最小修改的 run_osworld 方案思路（本次仅写文档，不落盘脚本）

目录
- 1. 架构与职责边界
- 2. 组件设计与文件布局
- 3. Environment 与 Tools 设计
- 4. OSWorld 适配器设计（代码骨架）
- 5. run_osworld 思路（最小化改动）
- 6. 观测与动作的表示与约束
- 7. 配置、日志与评测落地
- 8. 风险与验证清单

---

## 1. 架构与职责边界

- 复用部分（无需修改）：
  - OSWorld/desktop_env（环境执行、截图、a11y、动作执行、评估）：
    - DesktopEnv.reset/step/_get_obs/evaluate 等（OSWorld/desktop_env/desktop_env.py:242-488）
  - OSWorld 控制器（pyautogui 后端、录屏等）
- AgentFlow 负责：
  - Environment 基类（工具注册、JSON Schema 导出、配置管理）：AgentFlow/src/envs/enviroment.py
  - Tools 工具层（将 OSWorld 能力以函数调用工具形式暴露）
  - Runner（对话循环 + OpenAI function calling）：AgentFlow/src/run.py
- 关键边界：
  - OSWorldDesktopAdapter 把 OSWorld DesktopEnv 封装为易用方法（initialize、step、observe、evaluate）
  - Tools 只通过 Adapter 访问 OSWorld，不直接依赖 OSWorld 内部细节

## 2. 组件设计与文件布局

新增/对接文件：
- AgentFlow/src/envs/osworld_adapter.py（新增）
  - OSWorldDesktopAdapter：封装 OSWorld DesktopEnv 的生命周期与调用
- AgentFlow/src/envs/enviroment.py（最小改动）
  - 新增 OSWorldEnvironment（仿照 WebEnvironment 注册工具）
  - 在 setup_environment 的上层（run.py）增加 "osworld" 模式时使用（如后续选择接入 CLI）
- AgentFlow/src/tools/osworld_tools.py（已存在）
  - 复用：DesktopSetupTool / DesktopActionTool / ScreenshotTool / AccessibilityTreeTool / TaskEvaluationTool / DesktopInfoTool
  - 这些类需要注入 OSWorldDesktopAdapter 实例
- AgentFlow/src/tools/__init__.py（按需）
  - 可选择导出上述工具类；或在 OSWorldEnvironment 内局部导入，避免循环依赖
- AgentFlow/docs/OSWorld_Integration_Plan.md（本文档）

备注：根据你的要求，本次仅写文档，不创建 run_osworld.py。

## 3. Environment 与 Tools 设计

- OSWorldEnvironment（新环境类）：
  - 负责读取配置（provider、VM 路径、快照名、action_space、observation_type、pause、max_steps 等）
  - 初始化 OSWorldDesktopAdapter
  - 注册一组 OSWorld 工具（见下）
- 工具注册（Function Calling 的工具名与参数 Schema）：
  - desktop_setup：初始化/重置环境，传入 task_config
  - desktop_action：执行动作（结构化 JSON → pyautogui 字符串 或 WAIT/DONE/FAIL）
  - screenshot：截图（默认返回信息摘要）
  - accessibility_tree：返回 a11y 树（summary/full/filtered）
  - evaluate_task：任务评估（数值/文本摘要）
  - desktop_info：环境/任务/VM 信息

## 4. OSWorld 适配器设计（代码骨架）

文件：AgentFlow/src/envs/osworld_adapter.py

```python
# -*- coding: utf-8 -*-
"""Adapter that wraps OSWorld DesktopEnv for AgentFlow tools."""
from typing import Any, Dict, Optional
import os

# 引入 OSWorld DesktopEnv（保持相对/绝对导入与你的仓库布局一致）
# 假设仓库结构为 /home/a1/sdb/zhy/GUIAgent_zhy/OSWorld
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OSWORLD_DIR = os.path.join(BASE_DIR, 'OSWorld')
if OSWORLD_DIR not in sys.path:
    sys.path.append(OSWORLD_DIR)

from desktop_env.desktop_env import DesktopEnv  # OSWorld 的环境


class OSWorldDesktopAdapter:
    def __init__(self,
                 provider_name: str = 'local',
                 path_to_vm: Optional[str] = None,
                 snapshot_name: Optional[str] = None,
                 action_space: str = 'pyautogui',  # 或 'computer_13'
                 observation_type: str = 'screenshot_a11y_tree',
                 headless: bool = False,
                 pause: float = 0.5,
                 max_steps: int = 50,
                 screen_size: Optional[str] = None,
                 **kwargs):
        self.provider_name = provider_name
        self.path_to_vm = path_to_vm
        self.snapshot_name = snapshot_name
        self.action_space = action_space
        self.observation_type = observation_type
        self.headless = headless
        self.pause = pause
        self.max_steps = max_steps
        self.screen_size = screen_size

        self.desktop_env: Optional[DesktopEnv] = None
        self.current_task_config: Optional[Dict[str, Any]] = None

    # ---------- lifecycle ----------
    def initialize_desktop_env(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create DesktopEnv if needed and reset with task_config, return initial observation."""
        self.current_task_config = task_config
        if self.desktop_env is None:
            # DesktopEnv 构造参数根据 OSWorld 实现与你的部署决定
            # 可在 task_config 中读取 evaluator 等字段
            self.desktop_env = DesktopEnv(
                provider_name=self.provider_name,
                path_to_vm=self.path_to_vm,
                snapshot_name=self.snapshot_name,
                action_space=self.action_space,
                observation_type=self.observation_type,
                headless=self.headless,
                screen_size=self.screen_size,
            )
        obs = self.desktop_env.reset(task_config=task_config)
        return obs or {}

    # ---------- stepping ----------
    def execute_desktop_action(self, action: str) -> Dict[str, Any]:
        """Execute one action string (pyautogui or special WAIT/DONE/FAIL) and return step result."""
        if not self.desktop_env:
            return {
                'success': False,
                'observation': None,
                'reward': 0.0,
                'done': True,
                'info': {'error': 'DesktopEnv not initialized'}
            }
        try:
            obs, reward, done, info = self.desktop_env.step(action, pause=self.pause)
            return {
                'success': True,
                'observation': obs,
                'reward': reward,
                'done': done,
                'info': info or {}
            }
        except Exception as e:
            return {
                'success': False,
                'observation': None,
                'reward': 0.0,
                'done': True,
                'info': {'error': str(e)}
            }

    # ---------- observation helpers ----------
    def _latest_obs(self) -> Dict[str, Any]:
        if not self.desktop_env:
            return {}
        return self.desktop_env._get_obs() or {}

    def get_screenshot(self) -> Optional[bytes]:
        obs = self._latest_obs()
        return obs.get('screenshot') if obs else None

    def get_accessibility_tree(self) -> Optional[str]:
        obs = self._latest_obs()
        return obs.get('a11y_tree') or obs.get('accessibility_tree')

    # ---------- evaluation & info ----------
    def evaluate_task(self) -> float:
        if not self.desktop_env:
            return 0.0
        return float(self.desktop_env.evaluate() or 0.0)

    def get_environment_info(self) -> Dict[str, Any]:
        return {
            'provider_name': self.provider_name,
            'path_to_vm': self.path_to_vm,
            'snapshot_name': self.snapshot_name,
            'action_space': self.action_space,
            'observation_type': self.observation_type,
            'headless': self.headless,
            'screen_size': self.screen_size,
            'desktop_env_initialized': self.desktop_env is not None,
            'current_task': (self.current_task_config or {}).get('id')
        }
```

说明：
- 该适配器严格通过 DesktopEnv 的公开 API 交互（reset/step/_get_obs/evaluate），便于后续升级。
- 注意 observation 字段名在不同版本里可能是 'a11y_tree' 或 'accessibility_tree'，故做兼容。

## 5. OSWorldEnvironment 设计（代码骨架）

在 AgentFlow/src/envs/enviroment.py 中新增一个环境类（示例骨架）：

```python
# 放在现有环境类后面
from typing import Any

class OSWorldEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "osworld"

    def _initialize_tools(self):
        # 延迟导入，避免循环依赖
        from tools.osworld_tools import (
            DesktopSetupTool, DesktopActionTool,
            ScreenshotTool, AccessibilityTreeTool,
            TaskEvaluationTool, DesktopInfoTool,
        )
        from envs.osworld_adapter import OSWorldDesktopAdapter

        # 读取配置（可从 self.config 获取 CLI 传入的参数）
        adapter = OSWorldDesktopAdapter(
            provider_name=self.config.get('provider_name', 'local'),
            path_to_vm=self.config.get('path_to_vm'),
            snapshot_name=self.config.get('snapshot_name'),
            action_space=self.config.get('action_space', 'pyautogui'),
            observation_type=self.config.get('observation_type', 'screenshot_a11y_tree'),
            headless=self.config.get('headless', False),
            pause=self.config.get('pause', 0.5),
            max_steps=self.config.get('max_steps', 50),
            screen_size=self.config.get('screen_size'),
        )
        # 注册工具
        self.register_tool(DesktopSetupTool(adapter))
        self.register_tool(DesktopActionTool(adapter))
        self.register_tool(ScreenshotTool(adapter))
        self.register_tool(AccessibilityTreeTool(adapter))
        self.register_tool(TaskEvaluationTool(adapter))
        self.register_tool(DesktopInfoTool(adapter))
```

若后续需要 CLI 支持，可在 AgentFlow/src/run.py：
- 增加模式枚举：run.py:518 处 choices 添加 "osworld"
- setup_environment：run.py:97-106 增加 elif 分支，实例化 OSWorldEnvironment(**env_kwargs)
- 新增 osworld 参数（provider_name、path_to_vm 等）并透传到 env_kwargs

本次按你的要求先只文档化，不改 run.py。

## 6. 观测与动作的表示与约束

- 动作
  - Tools 层选用结构化 JSON（DesktopActionTool.parameters 已定义），由工具内部转换为 pyautogui 字符串或特殊动作 WAIT/DONE/FAIL
  - 若后续需要改为 OSWorld “computer_13” JSON 动作，可在 Adapter 中新增一个 execute_computer_action(action_dict)
- 观察
  - AgentFlow 对话循环把工具输出当纯文本；避免大量 base64
  - ScreenshotTool 默认返回图像信息摘要；需要细粒度视觉时可新增 describe_screenshot 工具（调用多模态模型做文本摘要）
  - AccessibilityTreeTool 支持 summary/full/filtered，建议默认 summary 控制 token

## 7. 配置、日志与评测落地

- 配置
  - Environment.config 中承载 OSWorld 参数（provider_name、path_to_vm、snapshot_name、action_space、observation_type、headless、pause、max_steps、screen_size 等）
  - 可通过 AgentFlow CLI（未来）或直接在构造 OSWorldEnvironment 时传入
- 日志
  - DesktopActionTool 返回“动作摘要 + 执行结果 + 观察摘要”；若需要轨迹持久化，可在 Adapter 内部按步骤把 screenshot/a11y 落盘，并在工具返回中给出路径
- 评测
  - TaskEvaluationTool 调用 adapter.evaluate_task()，底层用 OSWorld DesktopEnv.evaluate()；返回 [0,1] 分数

## 8. 风险与验证清单

- 导入路径与依赖：确保 AgentFlow 能 import OSWorld 的 DesktopEnv（文中 adapter 通过 sys.path 追加 OSWorld 目录）
- OSWorld 版本差异：不同实现中 obs 字段名可能不一致（a11y_tree vs accessibility_tree），需兼容
- 资源与权限：pyautogui/VM 控制需要正确的宿主权限（Linux 下 X11/Wayland、权限与显示服务器配置）
- Token 控制：避免把截图 base64 放入消息；优先返回文本摘要
- 最小闭环验证建议：
  1) 用 DesktopInfoTool 确认环境参数
  2) DesktopSetupTool 以一个简单 task_config 初始化
  3) ScreenshotTool/AccessibilityTreeTool 拉取摘要
  4) DesktopActionTool 执行一次 click 或 type，看是否有新观测
  5) TaskEvaluationTool 查看分数是否变化

---

结语
- 本方案围绕“复用 OSWorld/desktop_env + 在 AgentFlow 侧以 Environment/Tools 暴露”的思路，实现低耦合、可持续演进的集成。
- 如需要，我可以基于本文档骨架，继续提交适配器与环境类的初版实现补丁。