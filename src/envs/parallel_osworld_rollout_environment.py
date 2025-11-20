# -*- coding: utf-8 -*-
"""
Parallel OSWorld Rollout Environment - 直接继承 Environment，适配 VM 资源池。

特性：
- 从 ResourceManager 分配/释放 DesktopEnv
- 支持 Task 级别配置（snapshot/proxy/fixed_ip/config）
- 复用 OSWorld 关键能力（Observation 格式化、录屏、评测等）
"""

import os
import sys
import json
import base64
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment, Tool
from envs.data_models import Observation
from utils.desktop_env.desktop_env import DesktopEnv
from utils.resource_manager import HeavyResourceManager
from utils.instance_tracker import get_instance_tracker

logger = logging.getLogger(__name__)


class ParallelOSWorldRolloutEnvironment(Environment):
    """Parallel OSWorld Environment built directly on Environment base class."""

    def __init__(
        self,
        resource_manager: Optional[HeavyResourceManager] = None,
        parallel_degree: int = 1,
        model_name: str = "gpt-4.1-2025-04-14",
        openai_api_key: Optional[str] = None,
        openai_api_url: Optional[str] = None,
        enable_terminal_bench: bool = False,
        **osworld_kwargs,
    ):
        # 保存初始化参数
        self._pending_osworld_kwargs = dict(osworld_kwargs)
        self._desktop_env: Optional[DesktopEnv] = None
        self._allocated_resource_id: Optional[str] = None

        # Task 级别配置
        self._task_snapshot: Optional[str] = None
        self._task_use_proxy: Optional[bool] = None
        self._task_fixed_ip: Optional[bool] = None
        self._task_config: Optional[List[Dict[str, Any]]] = None

        # 轨迹数据
        self._current_trajectory: List[Dict[str, Any]] = []
        self._current_task_id: Optional[str] = None

        super().__init__(
            model_name=model_name,
            openai_api_key=openai_api_key,
            openai_api_url=openai_api_url,
            enable_terminal_bench=enable_terminal_bench,
            defer_init=True,
            has_heavy_resource=True,
            resource_manager=resource_manager,
            parallel_degree=parallel_degree,
        )

        # 初始化工具注册标记
        self._tools_registered = False

    # ---------------------------------------------------------------------
    # Environment overrides
    # ---------------------------------------------------------------------
    @property
    def mode(self) -> str:
        return "osworld"

    def get_action_space(self) -> str:
        return self.config.get("osworld", {}).get("action_space", "computer_13")

    def _initialize_config(self):
        """构建 OSWorld 配置"""
        pending = getattr(self, "_pending_osworld_kwargs", {})
        osworld_defaults = {
            "path_to_vm": pending.get("path_to_vm"),
            "provider_name": pending.get("provider_name", "vmware"),
            "action_space": pending.get("action_space", "computer_13"),
            "observation_type": pending.get("observation_type", "screenshot_a11y_tree"),
            "screen_width": pending.get("screen_width", 1920),
            "screen_height": pending.get("screen_height", 1080),
            "headless": pending.get("headless", False),
            "os_type": pending.get("os_type", "Ubuntu"),
            "client_password": pending.get("client_password", "password"),
            "snapshot_name": pending.get("snapshot_name"),
            "require_terminal": pending.get("require_terminal"),
            "require_a11y_tree": pending.get("require_a11y_tree", True),
            "sleep_after_execution": pending.get("sleep_after_execution", 2),
            "enable_recording": pending.get("enable_recording", True),
        }

        self.config["osworld"] = osworld_defaults
        self.config["osworld_available"] = False

        # 清理缓存
        self._pending_osworld_kwargs = {}

        # 仍然保留父类初始化（Terminal Bench 等）
        super()._initialize_config()

    def _validate_config(self):
        super()._validate_config()
        osworld_config = self.config.get("osworld", {})

        if not osworld_config.get("action_space"):
            raise ValueError("action_space is required for ParallelOSWorldRolloutEnvironment")

        observation_type = osworld_config.get("observation_type")
        valid_obs = {"screenshot", "a11y_tree", "screenshot_a11y_tree", "som"}
        if observation_type not in valid_obs:
            raise ValueError(f"Invalid observation_type '{observation_type}'. Must be one of {valid_obs}")

    def _initialize_tools(self):
        """工具注册在 DesktopEnv 设置后再进行"""
        return

    # ---------------------------------------------------------------------
    # Task configuration
    # ---------------------------------------------------------------------
    def initialize_with_task_config(self, task_config: Dict[str, Any]) -> bool:
        self._task_env_config = task_config
        env_specific_config = task_config.get(self.mode, {})
        return self._apply_task_config(env_specific_config)

    def _apply_task_config(self, env_config: Dict[str, Any]) -> bool:
        if not env_config:
            return True

        if "snapshot" in env_config:
            self._task_snapshot = env_config["snapshot"]

        if "proxy" in env_config:
            self._task_use_proxy = env_config["proxy"]

        if "fixed_ip" in env_config:
            self._task_fixed_ip = env_config["fixed_ip"]

        if "config" in env_config:
            self._task_config = env_config["config"]

        return True

    # ---------------------------------------------------------------------
    # Resource management
    # ---------------------------------------------------------------------
    def allocate_resource(self, worker_id: str, timeout: float = 60.0) -> bool:
        """
        从资源管理器分配 VM 资源
        
        在分布式架构中：
        - resource_manager.allocate() 从 Manager 获取连接信息（IP、端口等）
        - 在 Worker 本地实例化 DesktopEnv（Attach 模式）
        - DesktopEnv 对象在 Worker 进程中创建，避免跨进程序列化问题
        - 从 self.config 提取配置并传递给 resource_manager.allocate()
        
        Returns:
            True if allocation successful, False otherwise
        """
        resource_manager = self.resource_manager
        if not resource_manager:
            logger.error("Resource manager not set")
            return False

        try:
            # 从 self.config 提取 OSWorld 配置
            osworld_config = self.config.get("osworld", {})
            
            # 构建 DesktopEnv 初始化参数
            desktop_env_kwargs = {
                "provider_name": osworld_config.get("provider_name", "vmware"),
                "action_space": osworld_config.get("action_space", "computer_13"),
                "screen_size": (
                    osworld_config.get("screen_width", 1920),
                    osworld_config.get("screen_height", 1080)
                ),
                "headless": osworld_config.get("headless", False),
                "require_a11y_tree": osworld_config.get("require_a11y_tree", True),
                "require_terminal": osworld_config.get("require_terminal", False),
                "os_type": osworld_config.get("os_type", "Ubuntu"),
                "client_password": osworld_config.get("client_password", "password"),
                "snapshot_name": osworld_config.get("snapshot_name"),
                "cache_dir": "cache",  # 默认缓存目录
            }
            
            # 移除 None 值（可选参数）
            desktop_env_kwargs = {k: v for k, v in desktop_env_kwargs.items() if v is not None}
            
            # resource_manager.allocate() 返回 (vm_id, desktop_env)
            # desktop_env 是在 Worker 本地实例化的（Attach 模式）
            resource_id, desktop_env = resource_manager.allocate(
                worker_id=worker_id,
                timeout=timeout,
                **desktop_env_kwargs
            )
            self._allocated_resource_id = resource_id
            self._set_desktop_env(desktop_env, vm_id=resource_id)
            logger.info(f"[resource] worker={worker_id} acquired vm={resource_id} (Attach mode, local instance)")
            return True
        except Exception as exc:
            logger.error(f"Failed to allocate resource: {exc}", exc_info=True)
            return False

    def release_resource(self, worker_id: str, reset: bool = True) -> None:
        """
        释放 VM 资源
        
        在分布式架构中：
        1. 先显式关闭本地 DesktopEnv 连接（防止 socket/file descriptor 泄漏）
        2. 然后释放 VM 到 Manager（触发快照重置）
        """
        # 1. 关闭本地 DesktopEnv 连接（防止 socket/file descriptor 泄漏）
        if self._desktop_env is not None:
            try:
                logger.info(f"[resource] worker={worker_id} closing local DesktopEnv connection")
                self._desktop_env.close()
            except Exception as exc:
                logger.warning(f"Failed to close DesktopEnv connection: {exc}")
            finally:
                self._desktop_env = None
        
        # 2. 释放 VM 到 Manager（触发快照重置）
        if self._allocated_resource_id and self.resource_manager:
            try:
                logger.info(
                    f"[resource] worker={worker_id} releasing vm={self._allocated_resource_id} reset={reset}"
                )
                self.resource_manager.release(
                    self._allocated_resource_id,
                    worker_id,
                    reset=reset,
                )
            except Exception as exc:
                logger.error(f"Failed to release resource: {exc}", exc_info=True)

        # 清理状态
        self._allocated_resource_id = None
        self._tools_registered = False
        self.config["osworld_available"] = False

    def get_allocated_resource_id(self) -> Optional[str]:
        return self._allocated_resource_id

    def cleanup(self, worker_id: str, reset: bool = True) -> None:
        try:
            self.env_close()
        finally:
            self.release_resource(worker_id, reset=reset)

    def attach_desktop_env(self, desktop_env: DesktopEnv, vm_id: str = "external") -> None:
        """
        手动注入 DesktopEnv（例如使用 NoResourceManager 场景）
        该方法会触发工具注册流程，因此必须在 DesktopEnv 可用后调用。
        """
        if desktop_env is None:
            raise ValueError("desktop_env cannot be None when attaching manually")
        self._allocated_resource_id = vm_id
        self._set_desktop_env(desktop_env, vm_id=vm_id)

    # ---------------------------------------------------------------------
    # DesktopEnv helpers
    # ---------------------------------------------------------------------
    def _set_desktop_env(self, desktop_env: DesktopEnv, vm_id: str) -> None:
        """
        设置 DesktopEnv 实例
        
        在分布式架构中，DesktopEnv 是在 Worker 本地实例化的（Attach 模式），
        连接到 Manager 管理的远程 VM。
        """
        self._desktop_env = desktop_env
        self.config["osworld_available"] = True
        if not self._tools_registered:
            self._register_tools_without_desktop_env()
            self._tools_registered = True
        logger.info(f"DesktopEnv set (vm_id={vm_id}, Attach mode)")

    def env_start(self) -> None:
        if self._desktop_env is None:
            logger.warning("DesktopEnv not set. In parallel mode, call allocate_resource() first.")

    def env_close(self) -> None:
        """
        关闭 DesktopEnv
        
        在 Attach 模式下，DesktopEnv.close() 不会关闭 VM（VM 由 Manager 管理），
        只会清理本地连接。
        """
        if self._desktop_env:
            try:
                # 在 Attach 模式下，close() 不会关闭 VM，只清理本地连接
                self._desktop_env.close()
            except Exception as exc:
                logger.warning(f"DesktopEnv close failed: {exc}")
            finally:
                self._desktop_env = None

    # ---------------------------------------------------------------------
    # Core interaction methods
    # ---------------------------------------------------------------------
    def reset(self, task_config: Dict[str, Any]):
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized. Call allocate_resource() first.")
        return self._desktop_env.reset(task_config=task_config)

    def step(self, action: str, pause: float = 2):
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        return self._desktop_env.step(action, pause=pause)

    def get_obs(self) -> Dict[str, Any]:
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        obs = self._desktop_env.get_obs()
        if obs is None:
            return {}
        if isinstance(obs, dict):
            return obs
        if isinstance(obs, (str, bytes, bytearray)):
            try:
                decoded = obs.decode("utf-8") if isinstance(obs, (bytes, bytearray)) else obs
                return json.loads(decoded)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        logger.warning(f"Unexpected observation type {type(obs)} from DesktopEnv._get_obs(), returning empty dict")
        return {}

    def evaluate(self) -> float:
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        return float(self._desktop_env.evaluate())

    def start_recording(self):
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        self._desktop_env.start_recording()

    def end_recording(self, output_path: str):
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        self._desktop_env.end_recording(output_path)

    # ---------------------------------------------------------------------
    # Observation formatting
    # ---------------------------------------------------------------------
    def _encode_image(self, image_content: bytes) -> str:
        if not image_content:
            return ""
        return base64.b64encode(image_content).decode("utf-8")

    def _linearize_accessibility_tree(self, accessibility_tree: Dict[str, Any]) -> str:
        def _traverse(node, depth=0):
            lines = []
            indent = "  " * depth
            role = node.get("role", "unknown")
            name = node.get("name", "")
            description = node.get("description", "")
            node_info = f"{indent}[{role}]"
            if name:
                node_info += f" {name}"
            if description:
                node_info += f" - {description}"
            lines.append(node_info)
            for child in node.get("children", []):
                if isinstance(child, dict):
                    lines.extend(_traverse(child, depth + 1))
            return lines

        if not accessibility_tree:
            return ""
        if isinstance(accessibility_tree, (str, bytes, bytearray)):
            try:
                return (
                    accessibility_tree.decode("utf-8")
                    if isinstance(accessibility_tree, (bytes, bytearray))
                    else accessibility_tree
                )
            except UnicodeDecodeError:
                return repr(accessibility_tree)
        if not isinstance(accessibility_tree, dict):
            return str(accessibility_tree)
        return "\n".join(_traverse(accessibility_tree))

    def _trim_accessibility_tree(self, linearized_tree: str, max_tokens: int) -> str:
        max_chars = max_tokens * 4
        if len(linearized_tree) <= max_chars:
            return linearized_tree
        return linearized_tree[:max_chars] + "\n...[accessibility tree truncated]"

    def _format_observation_for_llm(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        osworld_config = self.config.get("osworld", {})
        max_tokens = osworld_config.get("a11y_tree_max_tokens", 10000)
        a11y_tree = obs.get("accessibility_tree", {})
        linearized = self._linearize_accessibility_tree(a11y_tree)
        trimmed = self._trim_accessibility_tree(linearized, max_tokens)
        base64_image = self._encode_image(obs.get("screenshot", b""))
        return {"screenshot": base64_image, "a11y_tree": trimmed}

    def format_observation_by_type(
        self,
        raw_obs: Dict[str, Any],
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], List[Observation]]:
        if not raw_obs:
            return {} if output_format == "dict" else []

        osworld_config = self.config.get("osworld", {})
        observation_type = osworld_config.get("observation_type", "screenshot_a11y_tree")

        include_screenshot = observation_type in {"screenshot", "screenshot_a11y_tree", "som"}
        include_a11y_tree = observation_type in {"a11y_tree", "screenshot_a11y_tree", "som"}

        formatted = self._format_observation_for_llm(raw_obs)
        base64_image = formatted.get("screenshot", "") if include_screenshot else ""
        linearized_a11y_tree = formatted.get("a11y_tree", "") if include_a11y_tree else ""

        if output_format == "dict":
            result = {}
            if include_a11y_tree and linearized_a11y_tree:
                result["text"] = linearized_a11y_tree
            if include_screenshot and base64_image:
                result["image"] = base64_image
            return result

        if output_format == "observation_list":
            observation_objects = []
            if include_a11y_tree and linearized_a11y_tree:
                observation_objects.append(
                    Observation(
                        type="text",
                        content=linearized_a11y_tree,
                        timestamp=datetime.now().isoformat(),
                        metadata={"source": "accessibility_tree", "observation_type": observation_type},
                    )
                )
            if include_screenshot and base64_image:
                observation_objects.append(
                    Observation(
                        type="image",
                        content=base64_image,
                        timestamp=datetime.now().isoformat(),
                        metadata={"format": "png", "encoding": "base64", "observation_type": observation_type},
                    )
                )
            return observation_objects

        if output_format == "openai_message":
            content_parts = []
            if include_a11y_tree and linearized_a11y_tree:
                content_parts.append({"type": "text", "text": f"\n--- Current Page State ---\n{linearized_a11y_tree}"})
            if include_screenshot and base64_image:
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"},
                    }
                )
            return content_parts

        raise ValueError(f"Unknown output_format: {output_format}")

    # ---------------------------------------------------------------------
    # Task lifecycle
    # ---------------------------------------------------------------------
    def env_task_init(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        task_id = task.get("id", "unknown")
        logger.info(f"Initializing OSWorld environment for task {task_id}...")
        self._current_task_id = task_id

        if self._desktop_env:
            vm_identifier = self._desktop_env.get_path_to_vm()
            if vm_identifier:
                try:
                    tracker = get_instance_tracker()
                    tracker.record_instance_task(vm_identifier, task_id)
                except Exception as exc:
                    logger.warning(f"Failed to record instance-task mapping: {exc}")

        self.reset(task)

        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)
        if enable_recording:
            try:
                self.start_recording()
            except Exception as exc:
                logger.warning(f"Screen recording failed: {exc}")

        self._current_trajectory = []

        raw_obs = self.get_obs()
        if not raw_obs:
            logger.warning("Failed to get initial observation")
            return None

        formatted_obs = cast(Dict[str, Any], self.format_observation_by_type(raw_obs, output_format="dict"))
        self._current_trajectory.append(
            {"step": 0, "type": "initial_observation", "text": formatted_obs.get("text", ""), "image": formatted_obs.get("image", "")}
        )
        return formatted_obs

    def env_task_end(
        self,
        task_id: str,
        task_output_dir: Optional[str] = None,
        final_answer: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)

        if enable_recording and task_output_dir:
            try:
                recording_path = os.path.join(task_output_dir, f"task_{task_id}.mp4")
                self.end_recording(recording_path)
            except Exception as exc:
                logger.warning(f"Failed to save recording: {exc}")

        if task_output_dir and self._current_trajectory:
            self._save_trajectory_to_files(task_output_dir)

        self._current_trajectory = []
        self._current_task_id = None
        return {"answer": final_answer} if final_answer is not None else None

    def get_task_output_dir(self, base_output_dir: str, task_id: str, model_name: str) -> Optional[str]:
        task_output_dir = os.path.join(base_output_dir, self.mode, task_id, model_name)
        os.makedirs(task_output_dir, exist_ok=True)
        return task_output_dir

    def needs_trajectory_saving(self) -> bool:
        return True

    def has_internal_evaluation(self) -> bool:
        return True

    # ---------------------------------------------------------------------
    # Trajectory helpers
    # ---------------------------------------------------------------------
    def _save_trajectory_to_files(self, output_dir: str) -> None:
        for step_data in self._current_trajectory:
            step_num = step_data["step"]
            if step_data.get("image"):
                try:
                    screenshot_path = os.path.join(output_dir, f"step_{step_num}.png")
                    screenshot_bytes = base64.b64decode(step_data["image"])
                    with open(screenshot_path, "wb") as f:
                        f.write(screenshot_bytes)
                except Exception as exc:
                    logger.warning(f"Failed to save step {step_num} screenshot: {exc}")
            if step_data.get("text"):
                try:
                    a11y_path = os.path.join(output_dir, f"step_{step_num}_accessibility_tree.txt")
                    with open(a11y_path, "w", encoding="utf-8") as f:
                        f.write(step_data["text"])
                except Exception as exc:
                    logger.warning(f"Failed to save step {step_num} accessibility tree: {exc}")

    def add_step_to_trajectory(self, observation: Dict[str, Any], step_number: int) -> None:
        self._current_trajectory.append(
            {"step": step_number, "type": "action_observation", "text": observation.get("text", ""), "image": observation.get("image", "")}
        )

    # ---------------------------------------------------------------------
    # Tool registration (copied from OSWorldEnvironment)
    # ---------------------------------------------------------------------
    def _register_computer13_tools(self):
        from tools.osworld_tools import (
            MouseMoveTool,
            MouseClickTool,
            MouseRightClickTool,
            MouseDoubleClickTool,
            MouseButtonTool,
            MouseDragTool,
            ScrollTool,
            TypeTool,
            KeyPressTool,
            KeyHoldTool,
            HotkeyTool,
            ControlTool,
        )

        tools: List[Tool] = [
            cast(Tool, MouseMoveTool(self)),
            cast(Tool, MouseClickTool(self)),
            cast(Tool, MouseRightClickTool(self)),
            cast(Tool, MouseDoubleClickTool(self)),
            cast(Tool, MouseButtonTool(self)),
            cast(Tool, MouseDragTool(self)),
            cast(Tool, ScrollTool(self)),
            cast(Tool, TypeTool(self)),
            cast(Tool, KeyPressTool(self)),
            cast(Tool, KeyHoldTool(self)),
            cast(Tool, HotkeyTool(self)),
            cast(Tool, ControlTool(self)),
        ]

        for tool in tools:
            self.register_tool(tool)

    def _register_pyautogui_tools(self):
        from tools.osworld_tools import ExecutePythonScriptTool, ControlTool

        tools: List[Tool] = [
            cast(Tool, ExecutePythonScriptTool(self)),
            cast(Tool, ControlTool(self)),
        ]

        for tool in tools:
            self.register_tool(tool)

    def _register_tools_without_desktop_env(self):
        if self._desktop_env is None:
            raise ValueError(
                "DesktopEnv must be set before registering tools. "
                "请先调用 allocate_resource() 或 attach_desktop_env() 完成资源绑定。"
            )

        action_space = self.config.get("osworld", {}).get("action_space", "computer_13")
        if action_space == "computer_13":
            self._register_computer13_tools()
        elif action_space == "pyautogui":
            self._register_pyautogui_tools()
        else:
            logger.warning(f"Action space '{action_space}' not fully implemented, using computer_13 tools")
            self._register_computer13_tools()

        logger.info(f"Registered {len(self.tools)} OSWorld tools for '{action_space}' mode")

