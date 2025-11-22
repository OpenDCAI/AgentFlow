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

from envs.enviroment import Environment
from envs.data_models import Observation
from tools.tool import Tool
from utils.desktop_env.desktop_env import DesktopEnv
from utils.resource_manager import HeavyResourceManager, ResourceManager, NoResourceManager, VMPoolResourceManager
from utils.instance_tracker import get_instance_tracker

logger = logging.getLogger(__name__)


class ParallelOSWorldRolloutEnvironment(Environment):
    """Parallel OSWorld Environment built directly on Environment base class."""

    @classmethod
    def setup_global_resources(cls, config: Any) -> ResourceManager:
        """
        根据配置初始化全局资源管理器（VM 池）
        
        Args:
            config: 并行运行配置对象，需要包含：
                - env_mode: 环境模式（应为 "osworld"）
                - use_resource_pool: 是否使用资源池
                - num_vms: VM 池大小
                - env_kwargs: 环境配置参数（provider_name, path_to_vm, snapshot_name 等）
        
        Returns:
            ResourceManager 实例（VMPoolResourceManager 或 NoResourceManager）
        """
        # 检查是否需要创建 VM 池
        if not (hasattr(config, 'env_mode') and config.env_mode == "osworld"):
            logger.info("Not OSWorld mode, using NoResourceManager")
            return NoResourceManager()
        
        if not (hasattr(config, 'use_resource_pool') and config.use_resource_pool):
            logger.info("Resource pool disabled, using NoResourceManager")
            return NoResourceManager()
        
        # 创建 VM 池资源管理器
        logger.info("Initializing VM pool (Distributed Worker Architecture)...")
        env_kwargs = getattr(config, 'env_kwargs', {}) or {}
        pool_config = {
            "num_vms": getattr(config, 'num_vms', 3),
            "provider_name": env_kwargs.get("provider_name", "vmware"),
            "path_to_vm": env_kwargs.get("path_to_vm"),
            "snapshot_name": env_kwargs.get("snapshot_name", "init_state"),
            "action_space": env_kwargs.get("action_space", "computer_13"),
            "screen_size": (
                env_kwargs.get("screen_width", 1920),
                env_kwargs.get("screen_height", 1080),
            ),
            "headless": env_kwargs.get("headless", False),
            "require_a11y_tree": env_kwargs.get("require_a11y_tree", True),
            "require_terminal": env_kwargs.get("require_terminal", False),
            "os_type": env_kwargs.get("os_type", "Ubuntu"),
            "client_password": env_kwargs.get("client_password", "password"),
        }
        resource_manager = VMPoolResourceManager(pool_config=pool_config)
        resource_manager.initialize()
        logger.info("VM pool initialized successfully (Distributed Worker Architecture)")
        return resource_manager

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

        # 工具注册标记（将在 allocate_resource 中注册）
        self._tools_registered = False

    # ---------------------------------------------------------------------
    # Environment overrides
    # ---------------------------------------------------------------------
    @property
    def mode(self) -> str:
        return "osworld"

    def _replace_prompt_placeholders(self, prompt: str) -> str:
        """替换 OSWorld 特定占位符"""
        prompt = super()._replace_prompt_placeholders(prompt)
        if "{CLIENT_PASSWORD}" in prompt:
            client_password = self.config.get("osworld", {}).get("client_password", "password")
            prompt = prompt.replace("{CLIENT_PASSWORD}", client_password)
        return prompt

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
        """工具注册在 DesktopEnv 设置后再进行（在 allocate_resource 中调用）"""
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
        - 工具注册在 DesktopEnv 实例化后立即进行
        
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
            
            # 在 DesktopEnv 实例化后立即注册工具
            if not self._tools_registered:
                self._register_tools()
                self._tools_registered = True
                logger.info(f"Registered {len(self.tools)} OSWorld tools after DesktopEnv allocation")
            
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
        # 注册工具
        if not self._tools_registered:
            self._register_tools()
            self._tools_registered = True

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
    # Private internal methods (formerly public methods)
    # ---------------------------------------------------------------------
    def _internal_reset(self, task_config: Dict[str, Any]):
        """内部重置方法（原 reset 方法）"""
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized. Call allocate_resource() first.")
        return self._desktop_env.reset(task_config=task_config)

    def _internal_get_obs(self) -> Dict[str, Any]:
        """内部获取观察方法（原 get_obs 方法）"""
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

    def _internal_evaluate(self) -> float:
        """内部评估方法（原 evaluate 方法）"""
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        return float(self._desktop_env.evaluate())

    def _internal_start_recording(self):
        """内部开始录屏方法（原 start_recording 方法）"""
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")
        self._desktop_env.start_recording()

    def _internal_end_recording(self, output_path: str):
        """内部结束录屏方法（原 end_recording 方法）"""
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
        """初始化任务环境并返回初始观察"""
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

        # 使用内部重置方法
        self._internal_reset(task)

        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)
        if enable_recording:
            try:
                self._internal_start_recording()
            except Exception as exc:
                logger.warning(f"Screen recording failed: {exc}")

        self._current_trajectory = []

        # 使用内部获取观察方法
        raw_obs = self._internal_get_obs()
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
        """结束任务执行：停止录屏、保存轨迹、返回最终结果"""
        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)

        if enable_recording and task_output_dir:
            try:
                recording_path = os.path.join(task_output_dir, f"task_{task_id}.mp4")
                self._internal_end_recording(recording_path)
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
    # Tool registration
    # ---------------------------------------------------------------------
    def _register_computer13_tools(self):
        """注册 computer_13 action space 工具"""
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
        """注册 pyautogui action space 工具"""
        from tools.osworld_tools import ExecutePythonScriptTool, ControlTool

        tools: List[Tool] = [
            cast(Tool, ExecutePythonScriptTool(self)),
            cast(Tool, ControlTool(self)),
        ]

        for tool in tools:
            self.register_tool(tool)

    def _register_tools(self):
        """注册工具（在 DesktopEnv 可用后调用）"""
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

    # ---------------------------------------------------------------------
    # Observation formatting for messages
    # ---------------------------------------------------------------------
    def format_initial_observation_for_message(self, initial_obs: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化初始观察结果，将其转换为消息内容部分
        
        Args:
            initial_obs: 初始观察字典，格式为 {"text": str, "image": str (base64)}
        
        Returns:
            消息内容部分列表
        """
        if not initial_obs:
            return []
        
        content_parts: List[Dict[str, Any]] = []
        
        # 添加文本部分
        text_part = initial_obs.get("text")
        if text_part:
            content_parts.append({"type": "text", "text": f"\n--- Initial Page State ---\n{text_part}"})
        
        # 添加图片部分
        image_part = initial_obs.get("image")
        if image_part:
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_part}", "detail": "high"},
                }
            )
        
        return content_parts

    # ---------------------------------------------------------------------
    # Agent execution (run_task and helpers)
    # ---------------------------------------------------------------------
    def run_task(self, task: Dict[str, Any], agent_config: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        """
        执行完整的 Agent 任务循环
        
        封装从任务初始化到结果返回的完整流程，包括：
        - 任务初始化（env_task_init）
        - Agent 对话循环（LLM -> Tool -> Env）
        - 评估（如果支持）
        - 任务清理（env_task_end）
        
        Args:
            task: 任务字典，包含 id, question, metadata 等字段
            agent_config: Agent 配置字典，包含 model_name, max_turns, max_retries 等
            logger: 日志记录器
        
        Returns:
            包含 task_id, question, answer, messages, success 等字段的结果字典
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized. Call allocate_resource() first.")

        task_id = task.get("id", "unknown")
        question = task.get("question", "")
        
        # 获取 Agent 配置参数
        model_name = agent_config.get("model_name", "gpt-4.1-2025-04-14")
        max_turns = agent_config.get("max_turns", 3)
        max_retries = agent_config.get("max_retries", 3)

        # 获取任务输出目录（如果环境支持）
        task_output_dir = None
        if hasattr(self, "get_task_output_dir") and callable(self.get_task_output_dir):
            task_output_dir = self.get_task_output_dir(
                agent_config.get("output_dir", "results"),
                task_id,
                model_name
            )

        # 初始化任务环境，获取初始观察
        initial_obs = self.env_task_init(task)

        # 执行对话，获取完整的消息列表
        messages = self._run_conversation(question, initial_obs, model_name, max_turns, max_retries, logger)
        
        # 从消息中提取最终答案
        final_answer = self._extract_final_answer(messages)

        # 构建任务结果字典
        result = {
            "task_id": task_id,
            "question": question,
            "answer": final_answer,
            "messages": messages,
            "success": True,
            "error": None,
        }

        # 如果环境支持内部评估，则执行评估并更新结果
        evaluation_score = None
        if self.has_internal_evaluation():
            try:
                logger.info(f"Evaluating task {task_id} via environment evaluator...")
                evaluation_score = self._internal_evaluate()
                result["evaluation_score"] = evaluation_score
                result["answer"] = str(evaluation_score)
                # 如果任务输出目录存在，将评估结果写入文件
                if task_output_dir:
                    result_file = os.path.join(task_output_dir, "result.txt")
                    with open(result_file, "w", encoding="utf-8") as f:
                        f.write(f"{evaluation_score}\n")
            except Exception as exc:
                # 评估失败不影响主流程，只记录警告
                logger.warning(f"Internal evaluation for task {task_id} failed: {exc}")

        # 调用环境的任务结束方法，进行清理和收尾工作
        try:
            self.env_task_end(
                task_id,
                task_output_dir if task_output_dir else None,
                result.get("answer")
            )
        except Exception as exc:
            # 任务结束处理失败不影响返回结果，只记录警告
            logger.warning(f"Failed to finalize task {task_id}: {exc}")

        # 如果任务输出目录存在，保存对话日志
        if task_output_dir:
            self._save_conversation_log(
                task_output_dir,
                task_id,
                question,
                model_name,
                messages,
                result
            )

        return result

    def _run_conversation(
        self,
        question: str,
        initial_obs: Optional[Dict[str, Any]],
        model_name: str,
        max_turns: int,
        max_retries: int,
        logger: logging.Logger,
    ) -> List[Dict[str, Any]]:
        """
        执行 Agent 对话循环
        
        Args:
            question: 任务问题
            initial_obs: 初始观察结果
            model_name: LLM 模型名称
            max_turns: 最大对话轮数
            max_retries: 每次调用的最大重试次数
            logger: 日志记录器
        
        Returns:
            完整的消息列表
        """
        system_prompt = self.get_system_prompt(question)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]

        # 构建用户消息内容，包含问题文本
        user_content: List[Dict[str, Any]] = [{"type": "text", "text": f"Question: {question}\n"}]
        # 如果环境支持格式化初始观察的功能，则将初始观察添加到消息中
        if initial_obs is not None:
            try:
                obs_content_parts = self.format_initial_observation_for_message(initial_obs)
                # 如果返回的是列表，则扩展用户内容；否则作为单个文本添加
                if isinstance(obs_content_parts, list):
                    user_content.extend(obs_content_parts)
                else:
                    user_content.append({"type": "text", "text": str(obs_content_parts)})
                logger.info("Initial observation added to conversation context")
            except Exception as exc:
                # 格式化失败不影响主流程，只记录警告
                logger.warning(f"Failed to format initial observation: {exc}")
        messages.append({"role": "user", "content": user_content})

        client = self._get_openai_client()
        turn_count = 0
        step_idx = 0

        # 主对话循环：在最大轮次限制内进行多轮对话
        while turn_count < max_turns:
            retry = 0
            # 重试循环：每次 API 调用失败后会重试，直到达到最大重试次数
            while retry < max_retries:
                try:
                    # 调用 OpenAI API 获取 LLM 响应
                    response = client.chat.completions.create(  # type: ignore[arg-type]
                        model=model_name,
                        messages=messages,  # type: ignore[arg-type]
                        tools=self.get_tool_schemas(),  # type: ignore[arg-type]
                    )
                    # 验证 API 响应是否有效
                    if not hasattr(response, "choices") or not response.choices:
                        raise ValueError("OpenAI API returned empty response")

                    # 提取助手消息并添加到消息列表
                    assistant_message = response.choices[0].message
                    assistant_dict = self._normalize_message(assistant_message)
                    messages.append(assistant_dict)

                    # 如果 LLM 返回了工具调用，则执行工具
                    if assistant_message.tool_calls:
                        tool_call = assistant_message.tool_calls[0]
                        function_call = getattr(tool_call, "function", None)
                        # 验证工具调用是否包含函数信息
                        if not function_call:
                            raise ValueError("Tool call missing function payload")
                        tool_name = function_call.name
                        tool_args = json.loads(function_call.arguments)
                        logger.info(f"Turn {turn_count}: executing tool {tool_name}")

                        # 执行工具，获取执行结果
                        tool_result_raw = self.execute_tool(tool_name, tool_args)
                        # 将工具结果转换为字典格式
                        if isinstance(tool_result_raw, dict):
                            tool_result = tool_result_raw
                        else:
                            try:
                                # 尝试将字符串解析为 JSON
                                tool_result = json.loads(tool_result_raw)
                            except json.JSONDecodeError:
                                # 解析失败则使用默认格式
                                tool_result = {"status": "unknown", "response": str(tool_result_raw), "observation": {}}

                        # 如果工具返回了观察结果，将其添加到轨迹中
                        observation = tool_result.get("observation") or {}
                        if observation:
                            step_idx += 1
                            if hasattr(self, "add_step_to_trajectory") and callable(self.add_step_to_trajectory):
                                self.add_step_to_trajectory(observation, step_idx)

                        # 格式化工具响应内容，准备添加到消息中
                        content_payload = self._format_tool_response_content(tool_result, observation)

                        # 将工具执行结果作为 tool 角色的消息添加到对话中
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": content_payload,
                            }
                        )
                        # 工具执行成功，跳出重试循环，进入下一轮对话
                        break

                    else:
                        # LLM 返回了最终答案（没有工具调用），对话结束
                        logger.info(f"Turn {turn_count}: final answer produced")
                        return messages

                except Exception as exc:
                    # API 调用或工具执行失败，进行重试
                    retry += 1
                    logger.warning(f"Retry {retry}/{max_retries} due to error: {exc}")
                    # 如果达到最大重试次数，则抛出异常
                    if retry >= max_retries:
                        raise

            # 完成一轮对话（可能包含多次重试），进入下一轮
            turn_count += 1

        # 达到最大轮次仍未获得最终答案，返回当前消息列表
        logger.warning("Max turns reached without final answer")
        return messages

    def _format_tool_response_content(self, tool_result: Dict[str, Any], observation: Dict[str, Any]) -> Any:
        """
        格式化工具响应内容，准备添加到消息中
        
        Args:
            tool_result: 工具执行结果字典
            observation: 观察结果字典
        
        Returns:
            格式化的内容（字符串或内容列表）
        """
        content_parts: List[Dict[str, Any]] = []
        base_result = {
            "status": tool_result.get("status", "unknown"),
            "response": tool_result.get("response", ""),
        }
        # 添加工具执行的基础结果（状态和响应）
        content_parts.append({"type": "text", "text": f"Execution Result:\n{json.dumps(base_result, indent=2)}"})

        # 如果观察结果存在，添加观察内容（文本和/或图片）
        if observation:
            text_part = observation.get("text")
            image_part = observation.get("image")
            # 如果有文本观察，添加文本内容
            if text_part:
                content_parts.append({"type": "text", "text": f"\n--- Current Page State ---\n{text_part}"})
            # 如果有图片观察，添加图片内容（base64 编码）
            if image_part:
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_part}", "detail": "high"},
                    }
                )

        # 如果只有一个内容部分，直接返回文本；否则返回内容列表
        if len(content_parts) == 1:
            return content_parts[0]["text"]
        return content_parts

    def _extract_final_answer(self, messages: List[Dict[str, Any]]) -> str:
        """
        从消息列表中提取最终答案
        从后往前遍历消息，找到第一个没有工具调用的助手消息作为最终答案
        """
        # 从后往前遍历消息列表，查找最后一个不含工具调用的助手消息
        for message in reversed(messages):
            normalized = self._normalize_message(message)
            # 如果是助手消息且没有工具调用，则认为是最终答案
            if normalized.get("role") == "assistant" and not normalized.get("tool_calls"):
                content = normalized.get("content", "")
                # 如果 content 是列表，提取文本部分
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            return part.get("text", "")
                    return ""
                return str(content)
        # 如果找不到最终答案，返回默认消息
        return "No final answer found"

    def _normalize_message(self, message: Any) -> Dict[str, Any]:
        """
        将消息对象标准化为字典格式
        如果消息对象有 model_dump 方法（如 Pydantic 模型），则调用该方法；否则直接返回原对象
        """
        # 如果消息对象是 Pydantic 模型，则使用 model_dump 方法转换为字典
        if hasattr(message, "model_dump"):
            return message.model_dump()
        # 如果已经是字典，直接返回
        if isinstance(message, dict):
            return message
        # 否则尝试转换为字符串表示
        return {"role": "unknown", "content": str(message)}

    def _save_conversation_log(
        self,
        output_dir: str,
        task_id: str,
        question: str,
        model_name: str,
        messages: List[Dict[str, Any]],
        result: Dict[str, Any],
    ) -> None:
        """
        保存对话日志到 JSON 文件
        
        Args:
            output_dir: 输出目录
            task_id: 任务 ID
            question: 问题文本
            model_name: 模型名称
            messages: 消息列表
            result: 任务结果字典
        """
        # 将消息列表中的每个消息标准化为可序列化的字典格式
        serializable_messages = [self._normalize_message(msg) for msg in messages]
        # 构建对话数据字典
        conversation_data = {
            "task_id": task_id,
            "question": question,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "evaluation_score": result.get("evaluation_score"),
            "messages": serializable_messages,
        }
        conversation_file = os.path.join(output_dir, "conversation.json")
        # 将对话数据写入 JSON 文件
        with open(conversation_file, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)