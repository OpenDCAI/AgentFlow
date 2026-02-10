# sandbox/server/backends/examples/vm.py
"""
VM (Virtual Machine) 后端示例

有状态后端，提供虚拟机/桌面自动化功能

这是一个有状态后端的典型示例：
- 需要session管理
- 每个worker维护独立的VM资源
- 需要初始化和清理

使用示例:
```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import VMBackend

server = HTTPServiceServer()
server.load_backend(VMBackend())
server.run()
```

客户端调用:
```python
async with Sandbox() as sandbox:
    # 自动创建session并执行
    result = await sandbox.execute("vm:screenshot", {})
    result = await sandbox.execute("vm:click", {"x": 100, "y": 200})
    result = await sandbox.execute("vm:type", {"text": "Hello"})
```
"""

import asyncio
import base64
import logging
import os
import time
import tempfile
from collections import deque
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Tuple, Union, cast
from dataclasses import dataclass
from uuid import uuid4

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.server.core import tool
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import (
    build_success_response,
    build_error_response,
    ResponseTimer,
)
from sandbox.server.backends.resources.utils.desktop_env.controllers.python import PythonController
from sandbox.server.backends.resources.utils.desktop_env.controllers.setup import SetupController
from sandbox.server.backends.resources.utils.desktop_env.providers import create_vm_manager_and_provider
from sandbox.server.backends.resources.utils.desktop_env.evaluators import metrics, getters
import re

def _fix_pyautogui_less_than_bug(command: str) -> str:
    """
    Fix PyAutoGUI '<' character bug by converting it to hotkey("shift", ',') calls.
    
    This fixes the known PyAutoGUI issue where typing '<' produces '>' instead.
    References:
    - https://github.com/asweigart/pyautogui/issues/198
    - https://github.com/xlang-ai/OSWorld/issues/257
    
    Args:
        command (str): The original pyautogui command
        
    Returns:
        str: The fixed command with '<' characters handled properly
    """
    # Pattern to match press('<') or press('\\u003c') calls  
    press_pattern = r'pyautogui\.press\(["\'](?:<|\\u003c)["\']\)'

    # Handle press('<') calls
    def replace_press_less_than(match):
        return 'pyautogui.hotkey("shift", ",")'
    
    # First handle press('<') calls
    command = re.sub(press_pattern, replace_press_less_than, command)

    # Pattern to match typewrite calls with quoted strings
    typewrite_pattern = r'pyautogui\.typewrite\((["\'])(.*?)\\1\)'
    
    # Then handle typewrite calls
    def process_typewrite_match(match):
        quote_char = match.group(1)
        content = match.group(2)
        
        # Preprocess: Try to decode Unicode escapes like \u003c to actual '<'
        # This handles cases where '<' is represented as escaped Unicode
        try:
            # Attempt to decode unicode escapes
            decoded_content = content.encode('utf-8').decode('unicode_escape')
            content = decoded_content
        except UnicodeDecodeError:
            # If decoding fails, proceed with original content to avoid breaking existing logic
            pass  # English comment: Graceful degradation - fall back to original content if decoding fails
        
        # Check if content contains '<'
        if '<' not in content:
            return match.group(0)
        
        # Split by '<' and rebuild
        parts = content.split('<')
        result_parts = []
        
        for i, part in enumerate(parts):
            if i == 0:
                # First part
                if part:
                    result_parts.append(f"pyautogui.typewrite({quote_char}{part}{quote_char})")
            else:
                # Add hotkey for '<' and then typewrite for the rest
                result_parts.append('pyautogui.hotkey("shift", ",")')
                if part:
                    result_parts.append(f"pyautogui.typewrite({quote_char}{part}{quote_char})")
        
        return '; '.join(result_parts)
    
    command = re.sub(typewrite_pattern, process_typewrite_match, command)
    
    return command


if TYPE_CHECKING:
    from sandbox.server.app import HTTPServiceServer

logger = logging.getLogger("VMBackend")



@dataclass
class VMPoolItem:
    pool_id: str
    provider_name: str
    manager: Any
    provider: Any
    path_to_vm: str
    vm_ip: str
    server_port: int
    chromium_port: int
    vnc_port: int
    vlc_port: int
    os_type: str
    screen_size: Tuple[int, int]
    headless: bool
    created_at: float
    last_used_at: float


class DesktopVMController:
    """
    真实 VM Controller 适配层，保持与 VMController 相同的异步接口。
    """

    def __init__(self, controller: PythonController, screen_size: Tuple[int, int]):
        self._controller = controller
        self.screen_size = screen_size

    async def screenshot(self) -> str:
        image = await asyncio.to_thread(self._controller.get_screenshot)
        if image is None:
            raise RuntimeError("Failed to get screenshot from VM")
        if isinstance(image, (bytes, bytearray)):
            return base64.b64encode(image).decode("ascii")
        return str(image)

    async def accessibility_tree(self) -> Optional[str]:
        return await asyncio.to_thread(self._controller.get_accessibility_tree)


    async def click(self, x: int, y: int, button: str = "left") -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "CLICK", "parameters": {"x": x, "y": y, "button": button}},
        )
        return True

    async def double_click(self, x: int, y: int) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "DOUBLE_CLICK", "parameters": {"x": x, "y": y}},
        )
        return True

    async def type_text(self, text: str, interval: float = 0.0) -> bool:
        _ = interval  # interval is kept for compatibility, not used by PythonController
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "TYPING", "parameters": {"text": text}},
        )
        return True

    async def press_key(self, key: str) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "PRESS", "parameters": {"key": key}},
        )
        return True

    async def hotkey(self, *keys: str) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "HOTKEY", "parameters": {"keys": list(keys)}},
        )
        return True

    async def scroll(self, x: int, y: int, clicks: int) -> bool:
        _ = (x, y)
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "SCROLL", "parameters": {"dx": 0, "dy": clicks}},
        )
        return True

    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "MOVE_TO", "parameters": {"x": start_x, "y": start_y}},
        )
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "DRAG_TO", "parameters": {"x": end_x, "y": end_y}},
        )
        return True

    async def move(self, x: int, y: int) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "MOVE_TO", "parameters": {"x": x, "y": y}},
        )
        return True

    async def mouse_down(self, button: str = "left") -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "MOUSE_DOWN", "parameters": {"button": button}},
        )
        return True

    async def mouse_up(self, button: str = "left") -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "MOUSE_UP", "parameters": {"button": button}},
        )
        return True

    async def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        parameters: Dict[str, Any] = {}
        if x is not None and y is not None:
            parameters = {"x": x, "y": y}
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "RIGHT_CLICK", "parameters": parameters},
        )
        return True

    async def key_down(self, key: str) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "KEY_DOWN", "parameters": {"key": key}},
        )
        return True

    async def key_up(self, key: str) -> bool:
        await asyncio.to_thread(
            self._controller.execute_action,
            {"action_type": "KEY_UP", "parameters": {"key": key}},
        )
        return True

    async def execute_pyautogui(self, command: str) -> Any:
        return await asyncio.to_thread(self._controller.execute_python_command, command)

    async def close(self):
        return True


@dataclass
class _EvalEnv:
    controller: PythonController
    vm_ip: str
    server_port: int
    chromium_port: int
    vnc_port: int
    vlc_port: int
    cache_dir: str
    current_use_proxy: bool = False


class VMBackend(Backend):
    """
    VM 后端
    
    提供虚拟机/桌面自动化功能
    
    工具列表:
    - vm:screenshot - 截图
    - vm:click - 点击
    - vm:mouse_down - 鼠标按下
    - vm:mouse_up - 鼠标抬起
    - vm:right_click - 右键点击
    - vm:double_click - 双击
    - vm:type - 输入文本
    - vm:key - 按键
    - vm:key_down - 按下按键
    - vm:key_up - 抬起按键
    - vm:hotkey - 组合键
    - vm:scroll - 滚动
    - vm:drag - 拖拽
    - vm:move - 移动鼠标
    - vm:wait - 等待
    - vm:done - 标记完成
    - vm:pyautogui - 执行 pyautogui.* 命令
    
    配置项:
    - screen_size: 屏幕分辨率 [width, height]
    - connection_type: 连接类型 (vnc/rdp/local)
    - host: 远程主机地址
    - port: 端口
    - provider: VM 提供方 (docker/aliyun)
    - region: 区域（云厂商使用）
    - os_type: 操作系统类型 (Ubuntu/Windows)
    - headless: 是否无头模式
    - pool_size: 预热池大小
    - pool_reset: 是否在回收到池时重置VM（默认True）
    - snapshot_name: 回收重置时使用的快照名（为空则仅重启）
    - recording: 是否启用录屏
    - recording_path: 录屏文件路径或目录
    """
    
    name = "vm"
    description = "Virtual Machine Backend - 提供桌面自动化功能"
    version = "1.0.0"
    stateless = False  # VM是有状态的
    
    def __init__(self, config: Optional[BackendConfig] = None):
        """
        初始化VM后端
        
        Args:
            config: 后端配置
        """
        if config is None:
            config = BackendConfig(
                enabled=True,
                default_config={
                    "screen_size": [1920, 1080],
                    "connection_type": "local",
                    "host": None,
                    "port": None,
                    "provider": "docker",
                    "region": None,
                    "os_type": "Ubuntu",
                    "headless": True,
                    "pool_size": 0,
                    "setup": [],
                    "pool_reset": True,
                    "snapshot_name": None,
                    "use_proxy": False,
                    "client_password": "password",
                    "server_port": 5000,
                    "chromium_port": 9222,
                    "vnc_port": 8006,
                    "vlc_port": 8080,
                    "recording": False,
                    "recording_path": None
                },
                description="Virtual Machine Backend"
            )
        super().__init__(config)
        self._pool_lock = asyncio.Lock()
        self._vm_pool: deque[VMPoolItem] = deque()
        self._pool_config: Optional[Dict[str, Any]] = None
        self._pool_size: int = 0
        self._pool_initialized: bool = False
        self._max_action_history = 50

    # ========================================================================
    # Pool helpers
    # ========================================================================

    def _merge_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if config is None:
            return self.get_default_config()
        return dict(config)

    def _normalize_screen_size(self, screen_size: Any) -> Tuple[int, int]:
        if isinstance(screen_size, (list, tuple)) and len(screen_size) == 2:
            return int(screen_size[0]), int(screen_size[1])
        return 1920, 1080

    def _build_pool_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider": config.get("provider", "docker"),
            "region": config.get("region"),
            "os_type": config.get("os_type", "Ubuntu"),
            "headless": bool(config.get("headless", True)),
            "screen_size": self._normalize_screen_size(config.get("screen_size")),
            "server_port": int(config.get("server_port", 5000)),
            "chromium_port": int(config.get("chromium_port", 9222)),
            "vnc_port": int(config.get("vnc_port", 8006)),
            "vlc_port": int(config.get("vlc_port", 8080)),
            "use_proxy": bool(config.get("use_proxy", False)),
            "vm_path": config.get("vm_path"),  # 支持自定义VM镜像路径
        }

    def _pool_config_matches(self, config: Dict[str, Any]) -> bool:
        if not self._pool_config:
            return False
        candidate = self._build_pool_config(config)
        return candidate == self._pool_config

    def _parse_vm_address(
        self,
        address: str,
        defaults: Dict[str, int],
    ) -> Tuple[str, int, int, int, int]:
        if not address:
            return (
                "localhost",
                defaults["server_port"],
                defaults["chromium_port"],
                defaults["vnc_port"],
                defaults["vlc_port"],
            )
        parts = address.split(":")
        if len(parts) >= 2 and all(p.isdigit() for p in parts[1:]):
            host = parts[0]
            ports = [int(p) for p in parts[1:]]
            fallback = [
                defaults["server_port"],
                defaults["chromium_port"],
                defaults["vnc_port"],
                defaults["vlc_port"],
            ]
            while len(ports) < 4:
                ports.append(fallback[len(ports)])
            return host, ports[0], ports[1], ports[2], ports[3]
        return (
            address,
            defaults["server_port"],
            defaults["chromium_port"],
            defaults["vnc_port"],
            defaults["vlc_port"],
        )

    async def _create_pool_item(self, config: Dict[str, Any]) -> VMPoolItem:
        provider_name = config["provider"]
        region = config.get("region") or ""
        os_type = config.get("os_type", "Ubuntu")
        screen_size = config.get("screen_size", (1920, 1080))
        headless = config.get("headless", True)

        manager, provider = create_vm_manager_and_provider(provider_name, region, use_proxy=config.get("use_proxy", False))
        
        # 如果配置中指定了vm_path，直接使用；否则通过manager获取
        if config.get("vm_path"):
            path_to_vm = os.path.abspath(os.path.expandvars(os.path.expanduser(config["vm_path"])))
            logger.info(f"Using custom VM path from config: {path_to_vm}")
        else:
            path_to_vm = manager.get_vm_path(os_type=os_type, region=region, screen_size=screen_size)

        try:
            await asyncio.to_thread(cast(Any, provider).start_emulator, path_to_vm, headless, os_type)
        except TypeError:
            await asyncio.to_thread(provider.start_emulator, path_to_vm, headless)

        vm_address = await asyncio.to_thread(provider.get_ip_address, path_to_vm)
        vm_ip, server_port, chromium_port, vnc_port, vlc_port = self._parse_vm_address(
            vm_address,
            {
                "server_port": config["server_port"],
                "chromium_port": config["chromium_port"],
                "vnc_port": config["vnc_port"],
                "vlc_port": config["vlc_port"],
            },
        )

        now = time.time()
        return VMPoolItem(
            pool_id=uuid4().hex[:8],
            provider_name=provider_name,
            manager=manager,
            provider=provider,
            path_to_vm=path_to_vm,
            vm_ip=vm_ip,
            server_port=server_port,
            chromium_port=chromium_port,
            vnc_port=vnc_port,
            vlc_port=vlc_port,
            os_type=os_type,
            screen_size=screen_size,
            headless=headless,
            created_at=now,
            last_used_at=now,
        )

    async def _acquire_pool_item(self, config: Dict[str, Any]) -> Tuple[VMPoolItem, bool]:
        if self._pool_config_matches(config):
            async with self._pool_lock:
                if self._vm_pool:
                    item = self._vm_pool.popleft()
                    item.last_used_at = time.time()
                    return item, True
        item = await self._create_pool_item(self._build_pool_config(config))
        return item, False

    async def _release_pool_item(self, item: VMPoolItem, config: Dict[str, Any]):
        item.last_used_at = time.time()
        async with self._pool_lock:
            can_reuse = self._pool_size > 0 and len(self._vm_pool) < self._pool_size
        if not can_reuse:
            await self._stop_pool_item(item)
            return
        cleanup_ok = await self._cleanup_pool_item(item, config)
        if not cleanup_ok:
            await self._stop_pool_item(item)
            return
        async with self._pool_lock:
            if self._pool_size > 0 and len(self._vm_pool) < self._pool_size:
                self._vm_pool.append(item)
                return
        await self._stop_pool_item(item)

    async def _apply_setup(
        self,
        item: VMPoolItem,
        setup_config: Any,
        config: Dict[str, Any],
        label: str,
    ) -> bool:
        if not setup_config:
            return True
        if not isinstance(setup_config, list):
            logger.error("[VM] %s must be a list, got %s", label, type(setup_config))
            return False

        use_proxy = bool(config.get("use_proxy", False))
        client_password = str(config.get("client_password", ""))
        _, setup_controller = self._build_controllers(item)

        try:
            if use_proxy:
                await asyncio.to_thread(setup_controller._proxy_setup, client_password)
            success = await asyncio.to_thread(setup_controller.setup, setup_config, use_proxy)
            return bool(success)
        except Exception as exc:
            logger.warning("[VM] %s failed: %s", label, exc)
            return False

    async def _cleanup_pool_item(self, item: VMPoolItem, config: Dict[str, Any]) -> bool:
        reset_ok = await self._reset_pool_item(item, config)
        if not reset_ok:
            return False

        base_setup = config.get("setup")
        if base_setup:
            base_ok = await self._apply_setup(item, base_setup, config, "pool base setup")
            if not base_ok:
                return False

        return True

    async def _reset_pool_item(self, item: VMPoolItem, config: Dict[str, Any]) -> bool:
        if not bool(config.get("pool_reset", True)):
            return True

        snapshot_name = config.get("snapshot_name")
        try:
            if snapshot_name:
                new_path = await asyncio.to_thread(
                    item.provider.revert_to_snapshot,
                    item.path_to_vm,
                    snapshot_name,
                )
                if isinstance(new_path, str) and new_path:
                    item.path_to_vm = new_path
            else:
                await asyncio.to_thread(item.provider.stop_emulator, item.path_to_vm)

            try:
                await asyncio.to_thread(
                    cast(Any, item.provider).start_emulator,
                    item.path_to_vm,
                    item.headless,
                    item.os_type,
                )
            except TypeError:
                await asyncio.to_thread(item.provider.start_emulator, item.path_to_vm, item.headless)
            vm_address = await asyncio.to_thread(item.provider.get_ip_address, item.path_to_vm)
            vm_ip, server_port, chromium_port, vnc_port, vlc_port = self._parse_vm_address(
                vm_address,
                {
                    "server_port": item.server_port,
                    "chromium_port": item.chromium_port,
                    "vnc_port": item.vnc_port,
                    "vlc_port": item.vlc_port,
                },
            )
            item.vm_ip = vm_ip
            item.server_port = server_port
            item.chromium_port = chromium_port
            item.vnc_port = vnc_port
            item.vlc_port = vlc_port
            return True
        except Exception as exc:
            logger.warning("[VM] pool reset failed: %s", exc)
            return False

    async def _stop_pool_item(self, item: VMPoolItem):
        try:
            await asyncio.to_thread(item.provider.stop_emulator, item.path_to_vm)
        except Exception as exc:
            logger.warning("Failed to stop VM %s: %s", item.path_to_vm, exc)

    def _build_controllers(self, item: VMPoolItem) -> Tuple[DesktopVMController, SetupController]:
        controller = PythonController(
            vm_ip=item.vm_ip,
            server_port=item.server_port,
            instance_id=item.path_to_vm,
        )
        setup_controller = SetupController(
            vm_ip=item.vm_ip,
            server_port=item.server_port,
            chromium_port=item.chromium_port,
            vlc_port=item.vlc_port,
            screen_width=item.screen_size[0],
            screen_height=item.screen_size[1],
        )
        return DesktopVMController(controller, item.screen_size), setup_controller

    def _get_controller_or_error(
        self,
        session_info: Optional[Dict[str, Any]],
        tool_name: str,
        timer: ResponseTimer,
    ):
        if not session_info or "data" not in session_info or "controller" not in session_info["data"]:
            return None, build_error_response(
                code=ErrorCode.RESOURCE_NOT_INITIALIZED,
                message="VM session not initialized",
                tool=tool_name,
                execution_time_ms=timer.get_elapsed_ms(),
                resource_type="vm",
                session_id=session_info.get("session_id") if session_info else None,
            )
        return session_info["data"]["controller"], None

    async def _get_accessibility_tree(self, controller: Optional[DesktopVMController]) -> Optional[str]:
        if controller is None:
            return None
        try:
            return await controller.accessibility_tree()
        except Exception as exc:
            logger.warning("[VM] Failed to get accessibility tree: %s", exc)
            return None

    def _build_eval_env(self, session_info: Dict[str, Any]) -> _EvalEnv:
        data = session_info.get("data", {})
        controller = data.get("controller")
        if controller is None:
            raise RuntimeError("VM controller not initialized")
        if hasattr(controller, "_controller"):
            controller = controller._controller

        session_id = session_info.get("session_id") or "unknown_session"
        cache_dir = os.path.join(tempfile.gettempdir(), "sandbox_eval", session_id)
        os.makedirs(cache_dir, exist_ok=True)

        return _EvalEnv(
            controller=controller,
            vm_ip=data.get("vm_ip", "localhost"),
            server_port=int(data.get("server_port", 5000)),
            chromium_port=int(data.get("chromium_port", 9222)),
            vnc_port=int(data.get("vnc_port", 8006)),
            vlc_port=int(data.get("vlc_port", 8080)),
            cache_dir=cache_dir,
            current_use_proxy=bool(data.get("use_proxy", False)),
        )

    def _normalize_eval_list(self, value: Any, expected_len: int) -> List[Any]:
        if isinstance(value, list):
            if len(value) != expected_len:
                raise ValueError("Evaluator list lengths do not match")
            return value
        return [value for _ in range(expected_len)]

    def _get_raw_controller(self, controller: Any) -> Any:
        if hasattr(controller, "_controller"):
            return controller._controller
        return controller

    def _resolve_recording_path(self, session_info: Dict[str, Any], data: Dict[str, Any]) -> str:
        session_id = session_info.get("session_id") or "unknown_session"
        configured_path = data.get("recording_path")
        if isinstance(configured_path, str) and configured_path.strip():
            configured_path = configured_path.strip()
            root, ext = os.path.splitext(configured_path)
            if ext:
                return configured_path
            return os.path.join(configured_path, f"{session_id}.mp4")
        return os.path.join(os.getcwd(), "sandbox_recordings", f"{session_id}.mp4")

    def _record_action(
        self,
        session_info: Optional[Dict[str, Any]],
        tool_name: str,
        success: bool,
    ) -> None:
        if not session_info:
            return
        data = session_info.get("data")
        if not isinstance(data, dict):
            return
        history = data.setdefault("action_history", [])
        if not isinstance(history, list):
            history = []
            data["action_history"] = history
        history.append({"tool": tool_name, "ok": success, "ts": time.time()})
        if len(history) > self._max_action_history:
            del history[:-self._max_action_history]
        data["last_action"] = tool_name
        data["last_action_failed"] = not success

    def _resolve_metric(self, func_name: str):
        metric_fn = getattr(metrics, func_name, None)
        if metric_fn is None:
            raise ValueError(f"Unknown metric function: {func_name}")
        return metric_fn

    def _resolve_getter(self, getter_type: str):
        getter_fn = getattr(getters, f"get_{getter_type}", None)
        if getter_fn is None:
            raise ValueError(f"Unknown getter type: {getter_type}")
        return getter_fn
    
    async def initialize(self, worker_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        初始化VM资源
        
        创建VM控制器连接
        
        Args:
            worker_id: Worker ID
            config: 初始化配置
            
        Returns:
            包含controller的初始化结果
        """
        merged_config = self._merge_config(config)
        session_setup = merged_config.get("setup")
        screen_size = self._normalize_screen_size(merged_config.get("screen_size"))
        provider_name = merged_config.get("provider", "docker")
        connection_type = merged_config.get("connection_type", "local")
        
        logger.info(
            "[%s] Initializing VM: size=%s, type=%s, provider=%s",
            worker_id,
            screen_size,
            connection_type,
            provider_name,
        )
        
        pool_item, pooled = await self._acquire_pool_item(merged_config)
        controller, setup_controller = self._build_controllers(pool_item)

        use_proxy = bool(merged_config.get("use_proxy", False))
        client_password = str(merged_config.get("client_password", ""))
        proxy_ready = False
        if use_proxy:
            proxy_ready = await asyncio.to_thread(setup_controller._proxy_setup, client_password)

        if not pooled:
            default_config = self.get_default_config()
            base_setup = default_config.get("setup")
            base_ok = await self._apply_setup(pool_item, base_setup, default_config, "base setup")
            if not base_ok:
                raise RuntimeError("VM base setup failed")

        if session_setup:
            if not isinstance(session_setup, list):
                raise ValueError("VM setup config must be a list of steps")
            await asyncio.to_thread(
                setup_controller.setup,
                session_setup,
                use_proxy,
            )

        recording_enabled = bool(merged_config.get("recording", False))
        recording_path = merged_config.get("recording_path")
        recording_started = False
        if recording_enabled:
            raw_controller = self._get_raw_controller(controller)
            if hasattr(raw_controller, "start_recording"):
                await asyncio.to_thread(raw_controller.start_recording)
                recording_started = True
            else:
                logger.warning("[VM] Controller does not support recording")
        
        return {
            "controller": controller,
            "setup_controller": setup_controller,
            "pool_item": pool_item,
            "pooled": pooled,
            "session_config": merged_config,
            "vm_ip": pool_item.vm_ip,
            "path_to_vm": pool_item.path_to_vm,
            "screen_size": pool_item.screen_size,
            "provider": provider_name,
            "server_port": pool_item.server_port,
            "chromium_port": pool_item.chromium_port,
            "vnc_port": pool_item.vnc_port,
            "vlc_port": pool_item.vlc_port,
            "use_proxy": use_proxy,
            "client_password": client_password,
            "proxy_ready": proxy_ready,
            "action_history": [],
            "last_action": None,
            "last_action_failed": False,
            "recording_enabled": recording_enabled,
            "recording_started": recording_started,
            "recording_path": recording_path,
        }
    
    async def cleanup(self, worker_id: str, session_info: Dict[str, Any]):
        """
        清理VM资源
        
        关闭VM控制器连接
        
        Args:
            worker_id: Worker ID
            session_info: Session信息
        """
        data = session_info.get("data", {})
        controller = data.get("controller")
        pool_item: Optional[VMPoolItem] = data.get("pool_item")
        pooled = bool(data.get("pooled"))
        recording_enabled = bool(data.get("recording_enabled"))

        if recording_enabled and controller:
            raw_controller = self._get_raw_controller(controller)
            if hasattr(raw_controller, "end_recording"):
                output_path = self._resolve_recording_path(session_info, data)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                await asyncio.to_thread(raw_controller.end_recording, output_path)
                data["recording_path"] = output_path
            else:
                logger.warning("[VM] Controller does not support recording stop")

        if pool_item:
            if pooled:
                await self._release_pool_item(pool_item, self.get_default_config())
            else:
                await self._stop_pool_item(pool_item)
        
        if controller and hasattr(controller, "close"):
            await controller.close()

            logger.info(f"[{worker_id}] VM resource cleaned up")

    async def warmup(self):
        config = self.get_default_config()
        base_setup = config.get("setup")
        pool_size = int(config.get("pool_size", 0) or 0)
        provider_name = config.get("provider", "docker")
        if pool_size <= 0:
            logger.info("[VM] warmup skipped (pool_size=%s, provider=%s)", pool_size, provider_name)
            return

        async with self._pool_lock:
            if self._pool_initialized:
                return
            self._pool_initialized = True
            self._pool_size = pool_size
            self._pool_config = self._build_pool_config(config)

        logger.info("[VM] warmup start: provider=%s, pool_size=%s", provider_name, pool_size)
        for idx in range(pool_size):
            try:
                item = await self._create_pool_item(self._pool_config)
                if base_setup:
                    base_ok = await self._apply_setup(item, base_setup, config, "warmup base setup")
                    if not base_ok:
                        await self._stop_pool_item(item)
                        logger.error("[VM] warmup base setup failed for pool item %s", idx + 1)
                        continue
                async with self._pool_lock:
                    self._vm_pool.append(item)
                logger.info("[VM] warmup created pool item %s/%s (vm=%s)", idx + 1, pool_size, item.path_to_vm)
            except Exception as exc:
                logger.error("[VM] warmup failed to create pool item %s: %s", idx + 1, exc)

    async def shutdown(self):
        async with self._pool_lock:
            items = list(self._vm_pool)
            self._vm_pool.clear()
        for item in items:
            await self._stop_pool_item(item)
    
    # ========================================================================
    # 工具方法（使用 @tool 装饰器）
    # ========================================================================
    
    @tool("vm:screenshot")
    async def screenshot(
        self,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM截图

        Returns:
            截图结果，包含base64编码的图像
        """
        session_id = session_info.get("session_id") if session_info else None
        session_name = session_info.get("session_name") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:screenshot", timer)
                if error:
                    return error
                assert controller is not None
                image = await controller.screenshot()
                accessibility_tree = await self._get_accessibility_tree(controller)

                return build_success_response(
                    data={
                        "image": image,
                        "size": list(controller.screen_size),
                        "session": session_name,
                        "accessibility_tree": accessibility_tree,
                    },
                    tool="vm:screenshot",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:screenshot",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
    
    @tool("vm:click")
    async def click(
        self,
        x: int,
        y: int,
        button: str = "left",
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM点击

        Args:
            x: X坐标
            y: Y坐标
            button: 按钮 (left/right/middle)
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:click", timer)
                if error:
                    self._record_action(session_info, "vm:click", False)
                    return error
                assert controller is not None
                success = await controller.click(x, y, button)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:click", True)
                    return build_success_response(
                        data={
                            "clicked": [x, y],
                            "button": button,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:click",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:click", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message="Click operation failed",
                        tool="vm:click",
                        data={"clicked": [x, y], "button": button},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:click", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:click",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
    
    @tool("vm:double_click")
    async def double_click(
        self,
        x: int,
        y: int,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM双击

        Args:
            x: X坐标
            y: Y坐标
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:double_click", timer)
                if error:
                    self._record_action(session_info, "vm:double_click", False)
                    return error
                assert controller is not None
                success = await controller.double_click(x, y)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:double_click", True)
                    return build_success_response(
                        data={
                            "clicked": [x, y],
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:double_click",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:double_click", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message="Double click operation failed",
                        tool="vm:double_click",
                        data={"clicked": [x, y]},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:double_click", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:double_click",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:type")
    async def type_text(
        self,
        text: str,
        interval: float = 0.0,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM输入文本

        Args:
            text: 要输入的文本
            interval: 按键间隔（秒）
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:type", timer)
                if error:
                    self._record_action(session_info, "vm:type", False)
                    return error
                assert controller is not None
                success = await controller.type_text(text, interval)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:type", True)
                    return build_success_response(
                        data={
                            "typed": text,
                            "length": len(text),
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:type",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:type", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message="Type text operation failed",
                        tool="vm:type",
                        data={"typed": text},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:type", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:type",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:key")
    async def press_key(
        self,
        key: str,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM按键

        Args:
            key: 键名 (enter/tab/escape/space/backspace等)
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:key", timer)
                if error:
                    self._record_action(session_info, "vm:key", False)
                    return error
                assert controller is not None
                success = await controller.press_key(key)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:key", True)
                    return build_success_response(
                        data={
                            "key": key,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:key",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:key", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message=f"Press key '{key}' failed",
                        tool="vm:key",
                        data={"key": key},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:key", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:key",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:hotkey")
    async def hotkey(
        self,
        keys: List[str],
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM组合键

        Args:
            keys: 键名列表 (如 ["ctrl", "c"])
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:hotkey", timer)
                if error:
                    self._record_action(session_info, "vm:hotkey", False)
                    return error
                assert controller is not None
                success = await controller.hotkey(*keys)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:hotkey", True)
                    return build_success_response(
                        data={
                            "keys": keys,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:hotkey",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:hotkey", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message=f"Hotkey '{keys}' failed",
                        tool="vm:hotkey",
                        data={"keys": keys},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:hotkey", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:hotkey",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:scroll")
    async def scroll(
        self,
        x: int,
        y: int,
        clicks: int,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM滚动

        Args:
            x: X坐标
            y: Y坐标
            clicks: 滚动量（正数向上，负数向下）
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:scroll", timer)
                if error:
                    self._record_action(session_info, "vm:scroll", False)
                    return error
                assert controller is not None
                success = await controller.scroll(x, y, clicks)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:scroll", True)
                    return build_success_response(
                        data={
                            "position": [x, y],
                            "clicks": clicks,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:scroll",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:scroll", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message="Scroll operation failed",
                        tool="vm:scroll",
                        data={"position": [x, y], "clicks": clicks},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:scroll", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:scroll",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:drag")
    async def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM拖拽

        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:drag", timer)
                if error:
                    self._record_action(session_info, "vm:drag", False)
                    return error
                assert controller is not None
                success = await controller.drag(start_x, start_y, end_x, end_y)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:drag", True)
                    return build_success_response(
                        data={
                            "from": [start_x, start_y],
                            "to": [end_x, end_y],
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:drag",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:drag", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message="Drag operation failed",
                        tool="vm:drag",
                        data={"from": [start_x, start_y], "to": [end_x, end_y]},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:drag", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:drag",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:move")
    async def move(
        self,
        x: int,
        y: int,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM移动鼠标

        Args:
            x: X坐标
            y: Y坐标
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:move", timer)
                if error:
                    self._record_action(session_info, "vm:move", False)
                    return error
                assert controller is not None
                success = await controller.move(x, y)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:move", True)
                    return build_success_response(
                        data={
                            "position": [x, y],
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:move",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                else:
                    self._record_action(session_info, "vm:move", False)
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message="Move operation failed",
                        tool="vm:move",
                        data={"position": [x, y]},
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
            except Exception as e:
                self._record_action(session_info, "vm:move", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:move",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:mouse_down")
    async def mouse_down(
        self,
        button: str = "left",
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM鼠标按下
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:mouse_down", timer)
                if error:
                    self._record_action(session_info, "vm:mouse_down", False)
                    return error
                assert controller is not None
                success = await controller.mouse_down(button)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:mouse_down", True)
                    return build_success_response(
                        data={
                            "button": button,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:mouse_down",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                self._record_action(session_info, "vm:mouse_down", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message="Mouse down operation failed",
                    tool="vm:mouse_down",
                    data={"button": button},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:mouse_down", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:mouse_down",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:mouse_up")
    async def mouse_up(
        self,
        button: str = "left",
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM鼠标抬起
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:mouse_up", timer)
                if error:
                    self._record_action(session_info, "vm:mouse_up", False)
                    return error
                assert controller is not None
                success = await controller.mouse_up(button)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:mouse_up", True)
                    return build_success_response(
                        data={
                            "button": button,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:mouse_up",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                self._record_action(session_info, "vm:mouse_up", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message="Mouse up operation failed",
                    tool="vm:mouse_up",
                    data={"button": button},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:mouse_up", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:mouse_up",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:right_click")
    async def right_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM右键点击
        """
        if (x is None) ^ (y is None):
            return build_error_response(
                code=ErrorCode.INVALID_INPUT,
                message="x and y must be provided together",
                tool="vm:right_click",
                resource_type="vm",
                session_id=session_info.get("session_id") if session_info else None
            )
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:right_click", timer)
                if error:
                    self._record_action(session_info, "vm:right_click", False)
                    return error
                assert controller is not None
                success = await controller.right_click(x, y)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:right_click", True)
                    return build_success_response(
                        data={
                            "clicked": [x, y] if x is not None and y is not None else None,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:right_click",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                self._record_action(session_info, "vm:right_click", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message="Right click operation failed",
                    tool="vm:right_click",
                    data={"clicked": [x, y] if x is not None and y is not None else None},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:right_click", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:right_click",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:key_down")
    async def key_down(
        self,
        key: str,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM按下按键
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:key_down", timer)
                if error:
                    self._record_action(session_info, "vm:key_down", False)
                    return error
                assert controller is not None
                success = await controller.key_down(key)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:key_down", True)
                    return build_success_response(
                        data={
                            "key": key,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:key_down",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                self._record_action(session_info, "vm:key_down", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"Key down '{key}' failed",
                    tool="vm:key_down",
                    data={"key": key},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:key_down", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:key_down",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:key_up")
    async def key_up(
        self,
        key: str,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM抬起按键
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:key_up", timer)
                if error:
                    self._record_action(session_info, "vm:key_up", False)
                    return error
                assert controller is not None
                success = await controller.key_up(key)
                accessibility_tree = await self._get_accessibility_tree(controller)

                if success:
                    self._record_action(session_info, "vm:key_up", True)
                    return build_success_response(
                        data={
                            "key": key,
                            "accessibility_tree": accessibility_tree,
                        },
                        tool="vm:key_up",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                self._record_action(session_info, "vm:key_up", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"Key up '{key}' failed",
                    tool="vm:key_up",
                    data={"key": key},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:key_up", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:key_up",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:wait")
    async def wait(
        self,
        seconds: float = 1.0,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM等待
        """
        if seconds < 0:
            return build_error_response(
                code=ErrorCode.INVALID_INPUT,
                message="seconds must be non-negative",
                tool="vm:wait",
                resource_type="vm",
                session_id=session_info.get("session_id") if session_info else None
            )
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:wait", timer)
                if error:
                    self._record_action(session_info, "vm:wait", False)
                    return error
                assert controller is not None
                await asyncio.sleep(seconds)
                accessibility_tree = await self._get_accessibility_tree(controller)

                self._record_action(session_info, "vm:wait", True)
                return build_success_response(
                    data={
                        "waited": seconds,
                        "accessibility_tree": accessibility_tree,
                    },
                    tool="vm:wait",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:wait", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:wait",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:done")
    async def done(
        self,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM标记完成
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                controller, error = self._get_controller_or_error(session_info, "vm:done", timer)
                if error:
                    self._record_action(session_info, "vm:done", False)
                    return error
                assert controller is not None
                self._record_action(session_info, "vm:done", True)
                return build_success_response(
                    data={
                        "done": True,
                    },
                    tool="vm:done",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:done", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:done",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:pyautogui")
    async def pyautogui(
        self,
        command: Optional[Union[str, List[str]]] = None,
        commands: Optional[List[str]] = None,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行 PyAutoGUI 命令（仅允许 pyautogui.*）

        Args:
            command: 单条命令或命令列表
            commands: 命令列表（可与 command 并用）
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                command_list: List[str] = []
                if command is not None:
                    if isinstance(command, list):
                        command_list.extend(command)
                    elif isinstance(command, str):
                        command_list.append(command)
                    else:
                        return build_error_response(
                            code=ErrorCode.INVALID_INPUT,
                            message="command must be a string or list of strings",
                            tool="vm:pyautogui",
                            execution_time_ms=timer.get_elapsed_ms(),
                            resource_type="vm",
                            session_id=session_id
                        )
                if commands is not None:
                    if not isinstance(commands, list):
                        return build_error_response(
                            code=ErrorCode.INVALID_INPUT,
                            message="commands must be a list of strings",
                            tool="vm:pyautogui",
                            execution_time_ms=timer.get_elapsed_ms(),
                            resource_type="vm",
                            session_id=session_id
                        )
                    command_list.extend(commands)

                command_list = [cmd for cmd in command_list if isinstance(cmd, str) and cmd.strip()]
                if not command_list:
                    return build_error_response(
                        code=ErrorCode.INVALID_INPUT,
                        message="command/commands cannot be empty",
                        tool="vm:pyautogui",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )

                for cmd in command_list:
                    stripped = cmd.strip()
                    if not stripped.startswith("pyautogui."):
                        return build_error_response(
                            code=ErrorCode.INVALID_INPUT,
                            message="only pyautogui.* commands are allowed",
                            tool="vm:pyautogui",
                            execution_time_ms=timer.get_elapsed_ms(),
                            resource_type="vm",
                            session_id=session_id
                        )

                controller, error = self._get_controller_or_error(session_info, "vm:pyautogui", timer)
                if error:
                    self._record_action(session_info, "vm:pyautogui", False)
                    return error
                assert controller is not None

                results: List[Any] = []
                failed_indices: List[int] = []
                for idx, cmd in enumerate(command_list):
                    fixed_command = _fix_pyautogui_less_than_bug(cmd)
                    exec_result = await controller.execute_pyautogui(fixed_command)
                    results.append(exec_result)
                    if exec_result is None:
                        failed_indices.append(idx)

                accessibility_tree = await self._get_accessibility_tree(controller)

                if failed_indices:
                    self._record_action(session_info, "vm:pyautogui", False)
                    return build_error_response(
                        code=ErrorCode.EXECUTION_ERROR,
                        message="PyAutoGUI command execution failed",
                        tool="vm:pyautogui",
                        data={
                            "commands": command_list,
                            "results": results,
                            "failed_indices": failed_indices,
                            "accessibility_tree": accessibility_tree,
                        },
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )

                self._record_action(session_info, "vm:pyautogui", True)
                return build_success_response(
                    data={
                        "commands": command_list,
                        "results": results,
                        "accessibility_tree": accessibility_tree,
                    },
                    tool="vm:pyautogui",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                self._record_action(session_info, "vm:pyautogui", False)
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:pyautogui",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:fail")
    async def fail(
        self,
        reason: Optional[str] = None,
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        显式标记当前会话失败状态，用于评测 FAIL 语义。
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                data = session_info.get("data") if session_info else None
                if not isinstance(data, dict):
                    return build_error_response(
                        code=ErrorCode.RESOURCE_NOT_INITIALIZED,
                        message="Session not initialized",
                        tool="vm:fail",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )

                data["last_action_failed"] = True
                self._record_action(session_info, "vm:fail", False)

                payload: Dict[str, Any] = {"fail": True}
                if reason:
                    payload["reason"] = reason

                return build_success_response(
                    data=payload,
                    tool="vm:fail",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[VM] Error: {str(e)}",
                    tool="vm:fail",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )

    @tool("vm:evaluate")
    async def evaluate(
        self,
        evaluator: Dict[str, Any],
        session_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        VM 评测入口

        Args:
            evaluator: 评测配置，包含 func/result/expected/options/conj
        """
        session_id = session_info.get("session_id") if session_info else None
        with ResponseTimer() as timer:
            try:
                _, error = self._get_controller_or_error(session_info, "vm:evaluate", timer)
                if error:
                    return error
                assert session_info is not None

                env = self._build_eval_env(session_info)

                data = session_info.get("data", {})
                setup_controller = data.get("setup_controller")
                postconfig = evaluator.get("postconfig", [])
                use_proxy = bool(data.get("use_proxy", False))
                if postconfig:
                    if not isinstance(postconfig, list):
                        raise ValueError("evaluator.postconfig must be a list")
                    if setup_controller is not None:
                        if use_proxy and not data.get("proxy_ready", False):
                            proxy_ready = await asyncio.to_thread(
                                setup_controller._proxy_setup,
                                str(data.get("client_password", "")),
                            )
                            data["proxy_ready"] = proxy_ready
                        await asyncio.to_thread(
                            setup_controller.setup,
                            postconfig,
                            use_proxy,
                        )

                funcs = evaluator.get("func")
                if not funcs:
                    raise ValueError("evaluator.func is required")
                func_list = funcs if isinstance(funcs, list) else [funcs]

                last_action_failed = bool(data.get("last_action_failed"))
                if funcs == "infeasible":
                    final_score = 1.0 if last_action_failed else 0.0
                    return build_success_response(
                        data={
                            "score": final_score,
                            "results": [],
                            "details": [],
                            "evaluator": evaluator,
                            "last_action_failed": last_action_failed,
                        },
                        tool="vm:evaluate",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )
                if last_action_failed:
                    return build_success_response(
                        data={
                            "score": 0.0,
                            "results": [],
                            "details": [],
                            "evaluator": evaluator,
                            "last_action_failed": last_action_failed,
                        },
                        tool="vm:evaluate",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="vm",
                        session_id=session_id
                    )

                results_cfg = evaluator.get("result")
                if results_cfg is None:
                    raise ValueError("evaluator.result is required")

                expected_cfg = evaluator.get("expected")
                options_cfg = evaluator.get("options", {})
                conj = evaluator.get("conj", "and")

                results_cfg_list = self._normalize_eval_list(results_cfg, len(func_list))
                expected_cfg_list = self._normalize_eval_list(expected_cfg, len(func_list)) if expected_cfg is not None else [None] * len(func_list)
                options_list = self._normalize_eval_list(options_cfg, len(func_list))

                metric_results = []
                details = []

                for idx, func_name in enumerate(func_list):
                    metric_fn = self._resolve_metric(func_name)

                    result_getter_cfg = results_cfg_list[idx]
                    result_getter = self._resolve_getter(result_getter_cfg["type"])
                    result_state = result_getter(env, result_getter_cfg)

                    expected_state = None
                    expected_getter_cfg = expected_cfg_list[idx]
                    if expected_getter_cfg is not None:
                        expected_getter = self._resolve_getter(expected_getter_cfg["type"])
                        expected_state = expected_getter(env, expected_getter_cfg)

                    metric_options = options_list[idx] or {}
                    if expected_state is None:
                        score = metric_fn(result_state, **metric_options)
                    else:
                        score = metric_fn(result_state, expected_state, **metric_options)

                    metric_results.append(score)
                    details.append({
                        "func": func_name,
                        "score": score,
                        "result": result_state,
                        "expected": expected_state,
                    })

                    if conj == "and" and float(score) == 0.0:
                        final_score = 0.0
                        break
                    if conj == "or" and float(score) == 1.0:
                        final_score = 1.0
                        break
                else:
                    if conj == "and":
                        final_score = sum(metric_results) / len(metric_results)
                    else:
                        final_score = max(metric_results) if metric_results else 0.0

                return build_success_response(
                    data={
                        "score": final_score,
                        "results": metric_results,
                        "details": details,
                        "evaluator": evaluator,
                    },
                    tool="vm:evaluate",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )
            except Exception as e:
                return build_error_response(
                    code=ErrorCode.EXECUTION_ERROR,
                    message=f"[VM] Evaluation error: {str(e)}",
                    tool="vm:evaluate",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="vm",
                    session_id=session_id
                )


# ============================================================================
# 便捷函数
# ============================================================================

def create_vm_backend(
    screen_size: tuple = (1920, 1080),
    connection_type: str = "local",
    host: Optional[str] = None,
    port: Optional[int] = None,
    provider: str = "docker",
    region: Optional[str] = None,
    os_type: str = "Ubuntu",
    headless: bool = True,
    pool_size: int = 0
) -> VMBackend:
    """
    创建VM后端的便捷函数
    
    Args:
        screen_size: 屏幕分辨率
        connection_type: 连接类型 (local/vnc/rdp)
        host: 远程主机地址
        port: 端口
        provider: VM 提供方 (docker/aliyun)
        region: 区域（云厂商使用）
        os_type: 操作系统类型
        headless: 是否无头模式
        pool_size: 预热池大小
        
    Returns:
        VMBackend实例
        
    Example:
        ```python
        # 本地VM
        backend = create_vm_backend()
        
        # 远程VNC
        backend = create_vm_backend(
            connection_type="vnc",
            host="192.168.1.100",
            port=5900
        )
        
        server.load_backend(backend)
        ```
    """
    config = BackendConfig(
        enabled=True,
        default_config={
            "screen_size": list(screen_size),
            "connection_type": connection_type,
            "host": host,
            "port": port,
            "provider": provider,
            "region": region,
            "os_type": os_type,
            "headless": headless,
            "pool_size": pool_size
        }
    )
    return VMBackend(config)
