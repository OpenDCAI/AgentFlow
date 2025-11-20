# -*- coding: utf-8 -*-
"""
资源管理器 - 统一管理重资产资源（VM、GPU等）

调用层级概览：

1. ResourceManager / HeavyResourceManager
   - 环境（如 ParallelOSWorldRolloutEnvironment）只依赖这层接口。
   - 提供 initialize / allocate / release / stop_all 等通用方法。

2. VMPoolResourceManager
   - HeavyResourceManager 的具体实现，面向主进程与 Worker。
   - 初始化时创建 `_VMPoolManagerBase`（BaseManager 子类），在独立进程里托管 VMPoolManager。
   - allocate()：向 VM 池请求连接信息，并在 Worker 本地实例化 DesktopEnv（Attach 模式）。

3. VMPoolManager（运行在 BaseManager 托管进程内）
   - 负责 VM 元数据与生命周期：initialize_pool / allocate_vm / release_vm / reset_vm 等。
   - 仅管理 IP、端口、path_to_vm 等信息，不直接暴露给 Worker。

4. DesktopEnv（Worker 本地）
   - 由 VMPoolResourceManager.allocate() 生成，使用 remote_ip 参数连接远程 VM。
   - ParallelOSWorldRolloutEnvironment 通过 _set_desktop_env() 注入后即可 reset/step 交互。

整体流程：
Env -> ResourceManager(接口) -> VMPoolResourceManager(跨进程代理) -> VMPoolManager(独立进程) -> Provider API / VM 元数据。
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from multiprocessing.managers import BaseManager
from queue import Queue, Empty
from typing import (
    Any,
    Dict,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    TypedDict,
)

from utils.desktop_env.providers import create_vm_manager_and_provider

logger = logging.getLogger(__name__)


class VMPoolConfig(TypedDict, total=False):
    """标准化后的 VM 池配置"""

    num_vms: int
    provider_name: str
    region: Optional[str]
    path_to_vm: Optional[str]
    snapshot_name: str
    action_space: str
    screen_size: Tuple[int, int]
    headless: bool
    require_a11y_tree: bool
    require_terminal: bool
    os_type: str
    client_password: str
    extra_kwargs: Dict[str, Any]


def _ensure_bool(value: Any, default: bool) -> bool:
    """将任意值规范化为 bool"""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return bool(value)


def _normalize_pool_config(raw: Optional[Mapping[str, Any]]) -> VMPoolConfig:
    """
    将外部传入的 pool_config 规范化，确保必填字段存在并提供默认值。
    """
    raw = raw or {}

    def _get_int(key: str, default: int) -> int:
        value = raw.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _get_tuple(key: str, default: Tuple[int, int]) -> Tuple[int, int]:
        value = raw.get(key)
        if isinstance(value, (list, tuple)) and len(value) == 2:
            try:
                return (int(value[0]), int(value[1]))
            except (TypeError, ValueError):
                pass
        return default

    known_keys = {
        "num_vms",
        "provider_name",
        "region",
        "path_to_vm",
        "snapshot_name",
        "action_space",
        "screen_size",
        "headless",
        "require_a11y_tree",
        "require_terminal",
        "os_type",
        "client_password",
    }

    extra_kwargs = {
        k: v for k, v in raw.items() if k not in known_keys
    }

    config: VMPoolConfig = {
        "num_vms": _get_int("num_vms", 1),
        "provider_name": str(raw.get("provider_name") or "vmware"),
        "region": raw.get("region"),
        "path_to_vm": raw.get("path_to_vm"),
        "snapshot_name": str(raw.get("snapshot_name") or "init_state"),
        "action_space": str(raw.get("action_space") or "computer_13"),
        "screen_size": _get_tuple("screen_size", (1920, 1080)),
        "headless": _ensure_bool(raw.get("headless"), False),
        "require_a11y_tree": _ensure_bool(raw.get("require_a11y_tree"), True),
        "require_terminal": _ensure_bool(raw.get("require_terminal"), False),
        "os_type": str(raw.get("os_type") or "Ubuntu"),
        "client_password": str(raw.get("client_password") or "password"),
        "extra_kwargs": extra_kwargs,
    }
    return config


def _build_desktop_env_params(
    connection_info: Mapping[str, Any],
    overrides: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    将 VM 池连接信息与外部 overrides 合并成 DesktopEnv 初始化参数。
    """
    config = connection_info.get("config", {})

    def _pick(key: str, default: Any = None):
        if key in overrides and overrides[key] is not None:
            return overrides[key]
        return config.get(key, default)

    path_to_vm_value = connection_info.get("path_to_vm")
    path_to_vm = path_to_vm_value if isinstance(path_to_vm_value, str) else ""

    return {
        "provider_name": _pick("provider_name", "vmware"),
        "region": _pick("region"),
        "path_to_vm": path_to_vm,
        "snapshot_name": _pick("snapshot_name", "init_state"),
        "action_space": _pick("action_space", "computer_13"),
        "cache_dir": _pick("cache_dir", "cache"),
        "screen_size": _pick("screen_size", (1920, 1080)),
        "headless": _ensure_bool(_pick("headless", True), True),
        "require_a11y_tree": _ensure_bool(_pick("require_a11y_tree", True), True),
        "require_terminal": _ensure_bool(_pick("require_terminal", False), False),
        "os_type": _pick("os_type", "Ubuntu"),
        "enable_proxy": _ensure_bool(_pick("enable_proxy", False), False),
        "client_password": _pick("client_password", "password"),
        "remote_ip": connection_info.get("ip"),
        "remote_port": connection_info.get("port", 5000),
        "remote_chromium_port": connection_info.get("chromium_port", 9222),
        "remote_vnc_port": connection_info.get("vnc_port", 8006),
        "remote_vlc_port": connection_info.get("vlc_port", 8080),
    }


class VMStatus(Enum):
    """VM状态"""

    FREE = "free"
    OCCUPIED = "occupied"
    INITIALIZING = "initializing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class VMPoolEntry:
    """VM池条目 - 仅存储元数据"""

    vm_id: str
    ip: Optional[str] = None
    port: int = 5000
    chromium_port: int = 9222
    vnc_port: int = 8006
    vlc_port: int = 8080
    path_to_vm: Optional[str] = None
    status: VMStatus = VMStatus.FREE
    allocated_to: Optional[str] = None
    allocated_at: Optional[float] = None
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


class VMPoolManager:
    """
    VM 池管理器 - 管理 VM 元数据与生命周期
    （该类将被 BaseManager 代理使用）
    """

    def __init__(
        self,
        num_vms: int = 5,
        provider_name: str = "aliyun",
        region: Optional[str] = None,
        path_to_vm: Optional[str] = None,
        snapshot_name: str = "init_state",
        action_space: str = "computer_13",
        screen_size: Tuple[int, int] = (1920, 1080),
        headless: bool = True,
        require_a11y_tree: bool = True,
        require_terminal: bool = False,
        os_type: str = "Ubuntu",
        client_password: str = "password",
        **kwargs,
    ):
        self.num_vms = num_vms
        self.provider_name = provider_name
        self.region = region
        self.path_to_vm = path_to_vm
        self.snapshot_name = snapshot_name
        self.action_space = action_space
        self.screen_size = screen_size
        self.headless = headless
        self.require_a11y_tree = require_a11y_tree
        self.require_terminal = require_terminal
        self.os_type = os_type
        self.client_password = client_password
        self.extra_kwargs = kwargs

        self.vm_pool: Dict[str, VMPoolEntry] = {}
        self.free_vm_queue: Queue = Queue()
        self.pool_lock = threading.RLock()
        self.stats = {
            "total_vms": 0,
            "free_vms": 0,
            "occupied_vms": 0,
            "error_vms": 0,
            "total_allocations": 0,
            "total_releases": 0,
        }

        logger.info(
            "VMPoolManager initialized: num_vms=%s provider=%s",
            num_vms,
            provider_name,
        )

    def initialize_pool(self) -> bool:
        """启动 VM 并记录元数据"""
        logger.info("Initializing VM pool with %s VMs...", self.num_vms)
        manager, provider = create_vm_manager_and_provider(
            self.provider_name, self.region or "", use_proxy=False
        )

        success_count = 0
        for i in range(self.num_vms):
            vm_id = f"vm_{i + 1}"
            desktop_env_kwargs: Dict[str, Any] = {}
            try:
                logger.info("Initializing %s...", vm_id)
                desktop_env_kwargs = {
                    "provider_name": self.provider_name,
                    "region": self.region,
                    "path_to_vm": self.path_to_vm,
                    "snapshot_name": self.snapshot_name,
                    "action_space": self.action_space,
                    "screen_size": self.screen_size,
                    "headless": self.headless,
                    "require_a11y_tree": self.require_a11y_tree,
                    "require_terminal": self.require_terminal,
                    "os_type": self.os_type,
                    "client_password": self.client_password,
                    **self.extra_kwargs,
                }

                if self.path_to_vm:
                    vm_path = self.path_to_vm
                else:
                    vm_path = manager.get_vm_path(
                        os_type=self.os_type,
                        region=self.region or "",
                        screen_size=self.screen_size,
                    )
                if not vm_path:
                    raise RuntimeError(f"Failed to resolve vm_path for {vm_id}")

                provider.start_emulator(vm_path, self.headless, self.os_type)

                vm_ip_ports = provider.get_ip_address(vm_path).split(":")
                vm_ip = vm_ip_ports[0]
                server_port = int(vm_ip_ports[1]) if len(vm_ip_ports) > 1 else 5000
                chromium_port = (
                    int(vm_ip_ports[2]) if len(vm_ip_ports) > 2 else 9222
                )
                vnc_port = int(vm_ip_ports[3]) if len(vm_ip_ports) > 3 else 8006
                vlc_port = int(vm_ip_ports[4]) if len(vm_ip_ports) > 4 else 8080

                vm_entry = VMPoolEntry(
                    vm_id=vm_id,
                    ip=vm_ip,
                    port=server_port,
                    chromium_port=chromium_port,
                    vnc_port=vnc_port,
                    vlc_port=vlc_port,
                    path_to_vm=vm_path,
                    status=VMStatus.FREE,
                    config=desktop_env_kwargs,
                )

                with self.pool_lock:
                    self.vm_pool[vm_id] = vm_entry
                    self.free_vm_queue.put(vm_id)
                    self.stats["total_vms"] += 1
                    self.stats["free_vms"] += 1

                logger.info("✓ %s initialized successfully: ip=%s", vm_id, vm_ip)
                success_count += 1
            except Exception as exc:
                logger.error("✗ Failed to initialize %s: %s", vm_id, exc, exc_info=True)
                vm_entry = VMPoolEntry(
                    vm_id=vm_id,
                    status=VMStatus.ERROR,
                    error_message=str(exc),
                    config=desktop_env_kwargs if desktop_env_kwargs else {},
                )
                with self.pool_lock:
                    self.vm_pool[vm_id] = vm_entry
                    self.stats["total_vms"] += 1
                    self.stats["error_vms"] += 1

        logger.info(
            "VM pool initialization completed: %s/%s successful",
            success_count,
            self.num_vms,
        )
        return success_count == self.num_vms

    def allocate_vm(
        self, worker_id: str, timeout: float = 30.0
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """为 worker 分配 VM（返回连接信息）"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                vm_id = self.free_vm_queue.get(timeout=1.0)
                with self.pool_lock:
                    vm_entry = self.vm_pool.get(vm_id)
                    if vm_entry is None:
                        continue
                    if vm_entry.status != VMStatus.FREE:
                        logger.warning(
                            "VM %s is not free (status=%s)", vm_id, vm_entry.status
                        )
                        continue
                    if vm_entry.ip is None:
                        logger.warning("VM %s has no IP, skipping allocation", vm_id)
                        vm_entry.status = VMStatus.ERROR
                        vm_entry.error_message = (
                            "IP address missing during allocation"
                        )
                        continue

                    vm_entry.status = VMStatus.OCCUPIED
                    vm_entry.allocated_to = worker_id
                    vm_entry.allocated_at = time.time()
                    self.stats["free_vms"] -= 1
                    self.stats["occupied_vms"] += 1
                    self.stats["total_allocations"] += 1

                    connection_info = {
                        "ip": vm_entry.ip,
                        "port": vm_entry.port,
                        "chromium_port": vm_entry.chromium_port,
                        "vnc_port": vm_entry.vnc_port,
                        "vlc_port": vm_entry.vlc_port,
                        "path_to_vm": vm_entry.path_to_vm,
                        "config": vm_entry.config,
                    }

                    logger.info(
                        "Allocated %s to worker %s: ip=%s",
                        vm_id,
                        worker_id,
                        vm_entry.ip,
                    )
                    return (vm_id, connection_info)
            except Empty:
                continue
            except Exception as exc:
                logger.error("Error allocating VM: %s", exc, exc_info=True)
                continue

        logger.warning(
            "Failed to allocate VM for worker %s (timeout=%ss)", worker_id, timeout
        )
        return None

    def release_vm(self, vm_id: str, worker_id: str, reset: bool = True) -> bool:
        """释放 VM"""
        with self.pool_lock:
            vm_entry = self.vm_pool.get(vm_id)
            if vm_entry is None:
                logger.warning("VM %s not found in pool", vm_id)
                return False
            if vm_entry.allocated_to != worker_id:
                logger.warning(
                    "VM %s is allocated to %s, not %s. Release ignored.",
                    vm_id,
                    vm_entry.allocated_to,
                    worker_id,
                )
                return False

            if reset and vm_entry.path_to_vm:
                self._reset_vm_to_snapshot(vm_id, vm_entry)

            vm_entry.status = VMStatus.FREE
            vm_entry.allocated_to = None
            vm_entry.allocated_at = None
            self.stats["free_vms"] += 1
            self.stats["occupied_vms"] -= 1
            self.stats["total_releases"] += 1
            self.free_vm_queue.put(vm_id)

            logger.info("Released %s from worker %s", vm_id, worker_id)
            return True

    def _reset_vm_to_snapshot(self, vm_id: str, vm_entry: VMPoolEntry) -> None:
        """使用 Provider API 重置 VM"""
        if vm_entry.path_to_vm is None:
            logger.warning("VM %s has no path_to_vm, cannot reset", vm_id)
            return

        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                _, provider = create_vm_manager_and_provider(
                    self.provider_name, self.region or "", use_proxy=False
                )
                path_to_vm = vm_entry.path_to_vm
                if not path_to_vm:
                    logger.warning("VM %s has no path_to_vm, skip reset", vm_id)
                    return
                new_vm_path = provider.revert_to_snapshot(
                    path_to_vm, self.snapshot_name
                )
                if new_vm_path and new_vm_path != path_to_vm:
                    logger.info(
                        "VM %s path changed after reset: %s -> %s",
                        vm_id,
                        path_to_vm,
                        new_vm_path,
                    )
                    vm_entry.path_to_vm = new_vm_path
                    path_to_vm = new_vm_path

                vm_ip_ports = provider.get_ip_address(path_to_vm).split(":")
                new_ip = vm_ip_ports[0]
                if new_ip != vm_entry.ip:
                    logger.info(
                        "VM %s IP changed after reset: %s -> %s",
                        vm_id,
                        vm_entry.ip,
                        new_ip,
                    )
                    vm_entry.ip = new_ip
                    if len(vm_ip_ports) > 1:
                        vm_entry.port = int(vm_ip_ports[1])
                        vm_entry.chromium_port = (
                            int(vm_ip_ports[2]) if len(vm_ip_ports) > 2 else vm_entry.chromium_port
                        )
                        vm_entry.vnc_port = (
                            int(vm_ip_ports[3]) if len(vm_ip_ports) > 3 else vm_entry.vnc_port
                        )
                        vm_entry.vlc_port = (
                            int(vm_ip_ports[4]) if len(vm_ip_ports) > 4 else vm_entry.vlc_port
                        )

                logger.info("Reset %s to snapshot", vm_id)
                return
            except KeyboardInterrupt:
                logger.warning("Reset of %s interrupted by KeyboardInterrupt", vm_id)
                return
            except Exception as exc:
                message = str(exc).lower()
                if "lasttokenprocessing" in message:
                    logger.warning(
                        "Reset of %s hit LastTokenProcessing (%s/%s), retrying...",
                        vm_id,
                        attempt,
                        max_attempts,
                    )
                    time.sleep(5)
                    continue
                if "not found" in message:
                    logger.info(
                        "%s instance already gone while resetting, skipping snapshot revert",
                        vm_id,
                    )
                    return
                logger.warning("Failed to reset %s: %s", vm_id, exc)
                return

    def get_vm_info(self, vm_id: str) -> Optional[Dict[str, Any]]:
        """获取单个 VM 信息"""
        with self.pool_lock:
            vm_entry = self.vm_pool.get(vm_id)
            if vm_entry:
                return {
                    "ip": vm_entry.ip,
                    "port": vm_entry.port,
                    "chromium_port": vm_entry.chromium_port,
                    "vnc_port": vm_entry.vnc_port,
                    "vlc_port": vm_entry.vlc_port,
                    "path_to_vm": vm_entry.path_to_vm,
                    "status": vm_entry.status.value,
                    "config": vm_entry.config,
                }
            return None

    def reset_vm(self, vm_id: str) -> bool:
        """外部调用的重置接口"""
        with self.pool_lock:
            vm_entry = self.vm_pool.get(vm_id)
            if vm_entry is None or vm_entry.path_to_vm is None:
                logger.warning("VM %s not found or missing path_to_vm", vm_id)
                return False
            try:
                self._reset_vm_to_snapshot(vm_id, vm_entry)
                logger.info("Reset %s to snapshot", vm_id)
                return True
            except Exception as exc:
                logger.error("Failed to reset %s: %s", vm_id, exc, exc_info=True)
                vm_entry.status = VMStatus.ERROR
                vm_entry.error_message = str(exc)
                return False

    def stop_vm(self, vm_id: str) -> bool:
        """停止单个 VM"""
        with self.pool_lock:
            vm_entry = self.vm_pool.get(vm_id)
            if vm_entry is None:
                logger.warning("VM %s not found", vm_id)
                return False
            if vm_entry.path_to_vm is None:
                logger.warning("VM %s has no path_to_vm", vm_id)
                return False
            try:
                _, provider = create_vm_manager_and_provider(
                    self.provider_name, self.region or "", use_proxy=False
                )
                provider.stop_emulator(vm_entry.path_to_vm)
                vm_entry.status = VMStatus.STOPPED
                logger.info("Stopped %s", vm_id)
                return True
            except Exception as exc:
                logger.error("Failed to stop %s: %s", vm_id, exc, exc_info=True)
                vm_entry.status = VMStatus.ERROR
                vm_entry.error_message = str(exc)
                return False

    def stop_all_vms(self) -> None:
        """停止所有 VM"""
        logger.info("Stopping all VMs...")
        _, provider = create_vm_manager_and_provider(
            self.provider_name, self.region or "", use_proxy=False
        )
        with self.pool_lock:
            for vm_id, vm_entry in self.vm_pool.items():
                if vm_entry.path_to_vm is None:
                    continue
                try:
                    provider.stop_emulator(vm_entry.path_to_vm)
                    vm_entry.status = VMStatus.STOPPED
                    logger.info("Stopped %s", vm_id)
                except Exception as exc:
                    logger.error("Failed to stop %s: %s", vm_id, exc)
        logger.info("All VMs stopped")

    def get_stats(self) -> Dict[str, Any]:
        """获取池统计"""
        with self.pool_lock:
            return {
                **self.stats,
                "vm_statuses": {
                    vm_id: entry.status.value for vm_id, entry in self.vm_pool.items()
                },
            }

    def get_pool_status(self) -> str:
        """格式化后的状态字符串"""
        stats = self.get_stats()
        return (
            "VM Pool Status: "
            f"Total={stats['total_vms']}, "
            f"Free={stats['free_vms']}, "
            f"Occupied={stats['occupied_vms']}, "
            f"Error={stats['error_vms']}, "
            f"Allocations={stats['total_allocations']}, "
            f"Releases={stats['total_releases']}"
        )


class _VMPoolManagerBase(BaseManager):
    """BaseManager 子类，用于跨进程托管 VMPoolManager"""

    pass
"""
调用 BaseManager.register，把字符串 "VMPoolManager" 绑定到本地类 VMPoolManager。注册后：
当在 _VMPoolManagerBase 实例上调用 manager.VMPoolManager() 时，
真实的 VMPoolManager 会在 Manager 进程内创建；
调用方得到的是一个代理对象，通过 RPC 调用 VMPoolManager 的方法 (initialize_pool(), allocate_vm() 等)，
实现跨进程通信。
"""

_VMPoolManagerBase.register("VMPoolManager", VMPoolManager)

"""
manager = _VMPoolManagerBase()
manager.start()                           # 启动独立进程
vm_pool_ctor = manager.VMPoolManager      # 这是自动注册的构造器
vm_pool = vm_pool_ctor(**pool_config)     # 真正的 VMPoolManager 在 Manager 进程里创建

"""

    # (Need to add methods replicate from previous file)
class ResourceManager(ABC):
    """资源管理器基类"""
    
    @property
    @abstractmethod
    def resource_type(self) -> str:
        """返回资源类型: 'vm', 'gpu', 'none'"""
        pass
    
    @property
    @abstractmethod
    def is_heavy_resource(self) -> bool:
        """是否为重资产"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化资源池"""
        pass
    
    @abstractmethod
    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Tuple[str, Any]:
        """
        分配资源
        
        Args:
            worker_id: Worker进程/线程标识符
            timeout: 等待超时时间(秒)
            **kwargs: 额外的配置参数（例如 DesktopEnv 初始化参数）
        
        Returns:
            (resource_id, resource_obj) 元组
        """
        pass
    
    @abstractmethod
    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        """
        释放资源
        
        Args:
            resource_id: 资源标识符
            worker_id: Worker进程/线程标识符
            reset: 是否在释放前重置资源
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取资源池状态"""
        pass
    
    @abstractmethod
    def stop_all(self) -> None:
        """停止所有资源"""
        pass


class NoResourceManager(ResourceManager):
    """无重资产管理器 - 轻量级实现"""
    
    @property
    def resource_type(self) -> str:
        return "none"
    
    @property
    def is_heavy_resource(self) -> bool:
        return False
    
    def initialize(self) -> bool:
        """直接返回 True，无需初始化"""
        return True
    
    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Tuple[str, None]:
        """返回虚拟资源 ID（忽略 kwargs）"""
        resource_id = f"virtual-{worker_id}"
        return (resource_id, None)
    
    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        """no-op"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        return {"type": "none", "status": "active"}
    
    def stop_all(self) -> None:
        """no-op"""
        pass


class HeavyResourceManager(ResourceManager):
    """重资产资源管理器接口"""
    
    @property
    def is_heavy_resource(self) -> bool:
        return True


# VMPoolManager 适配器 - 将 VMPoolManager 适配到 ResourceManager 接口
class VMPoolResourceManager(HeavyResourceManager):
    """
    VM 池资源管理器 - 整合 VMPoolManager、BaseManager 代理与 DesktopEnv Attach 逻辑
    """

    def __init__(
        self,
        vm_pool_manager: Optional[VMPoolManager] = None,
        *,
        base_manager: Optional[BaseManager] = None,
        pool_config: Optional[Dict[str, Any]] = None,
    ):
        if vm_pool_manager is None:
            if pool_config is None:
                raise ValueError(
                    "pool_config must be provided when vm_pool_manager is None"
                )
            self._pool_config = _normalize_pool_config(pool_config)
            (
                self._base_manager,
                self._vm_pool_manager,
            ) = self._start_vm_pool_manager(self._pool_config)
        else:
            self._vm_pool_manager = vm_pool_manager
            self._base_manager = base_manager
            self._pool_config = (
                _normalize_pool_config(pool_config)
                if pool_config is not None
                else {}
            )

    @staticmethod
    def _start_vm_pool_manager(config: VMPoolConfig):
        manager = _VMPoolManagerBase()
        manager.start()  # 启动独立进程，后续创建的对象都运行在该进程
        vm_pool_ctor = getattr(manager, "VMPoolManager")  # 获取注册的构造器代理
        ctor_kwargs: MutableMapping[str, Any] = dict(config)
        extra_kwargs = ctor_kwargs.pop("extra_kwargs", {})
        vm_pool_manager = vm_pool_ctor(**ctor_kwargs, **extra_kwargs)  # 在Manager进程中创建真实 VMPoolManager
        return manager, vm_pool_manager  # 返回 BaseManager 进程句柄与 VMPoolManager 代理

    @property
    def resource_type(self) -> str:
        return "vm"

    def initialize(self) -> bool:
        """初始化 VM 池"""
        return self._vm_pool_manager.initialize_pool()

    def allocate(
        self, worker_id: str, timeout: float, **desktop_env_kwargs
    ) -> Tuple[str, Any]:
        """分配 VM 并在本地实例化 DesktopEnv（Attach 模式）"""
        result = self._vm_pool_manager.allocate_vm(worker_id, timeout)
        if result is None:
            raise RuntimeError(
                f"Failed to allocate VM for worker {worker_id} (timeout={timeout}s)"
            )

        vm_id, connection_info = result

        from utils.desktop_env.desktop_env import DesktopEnv

        merged_kwargs = _build_desktop_env_params(connection_info, desktop_env_kwargs)

        desktop_env = DesktopEnv(**merged_kwargs)

        logger.info(
            "Worker %s instantiated DesktopEnv in Attach mode for VM %s",
            worker_id,
            vm_id,
        )
        return (vm_id, desktop_env)

    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        """释放 VM"""
        self._vm_pool_manager.release_vm(resource_id, worker_id, reset=reset)

    def get_status(self) -> Dict[str, Any]:
        """获取 VM 池状态"""
        return self._vm_pool_manager.get_stats()

    def stop_all(self) -> None:
        """停止所有 VM 并关闭 BaseManager 进程"""
        self._vm_pool_manager.stop_all_vms()
        if self._base_manager is not None:
            try:
                self._base_manager.shutdown()
            except Exception as exc:
                logger.warning(
                    "Failed to shutdown VM pool manager process: %s", exc
                )

