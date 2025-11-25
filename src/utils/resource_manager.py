# -*- coding: utf-8 -*-
"""
资源管理器 - 统一管理重资产资源（VM、GPU等）

重构说明：
1. 移除了 HeavyResourceManager 中间层，VMPoolResourceManager 直接实现 ResourceManager 接口。
2. 移除了 is_heavy_resource 属性，采用"空对象模式"统一接口行为。
3. VMPoolManager 及其相关数据结构被内聚为 VMPoolResourceManager 的内部类，作为实现细节。
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


# 为了确保多进程兼容性，BaseManager 子类建议定义在模块层级
class _VMPoolManagerBase(BaseManager):
    """BaseManager 子类，用于跨进程托管 ManagerImpl"""
    pass


class ResourceManager(ABC):
    """资源管理器通用接口"""

    @property
    @abstractmethod
    def resource_type(self) -> str:
        """资源类型标识 (e.g., 'vm', 'gpu', 'none')"""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """初始化资源池"""
        pass

    @abstractmethod
    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        分配资源
        Returns:
            (resource_id, connection_info)
        """
        pass

    @abstractmethod
    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        """释放资源"""
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
    """
    无重资产管理器 - 轻量级实现 (Null Object Pattern)
    用于不需要 VM 池的场景，allocate 直接返回，无需阻塞。
    """

    @property
    def resource_type(self) -> str:
        return "none"

    def initialize(self) -> bool:
        return True

    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Tuple[str, Optional[Dict[str, Any]]]:
        # 立即返回虚拟 ID，connection_info 为 None 或空字典
        return (f"virtual-{worker_id}", {})

    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        pass

    def get_status(self) -> Dict[str, Any]:
        return {"type": "none", "status": "active"}

    def stop_all(self) -> None:
        pass


class VMPoolResourceManager(ResourceManager):
    """
    VM 池资源管理器
    
    架构：
    - Client 端 (本类)：暴露统一接口给 Env，作为 Proxy 运行在主进程或 Worker 进程中。
    - Server 端 (_ManagerImpl)：在独立进程中运行，维护全局唯一的 VM 池状态。
    """

    # -------------------------------------------------------------------------
    # 1. 内部配置与数据结构定义
    # -------------------------------------------------------------------------

    class Config(TypedDict, total=False):
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

    class Status(Enum):
        """VM状态"""
        FREE = "free"
        OCCUPIED = "occupied"
        INITIALIZING = "initializing"
        ERROR = "error"
        STOPPED = "stopped"

    @dataclass
    class Entry:
        """VM池条目 - 仅存储元数据"""
        vm_id: str
        ip: Optional[str] = None
        port: int = 5000
        chromium_port: int = 9222
        vnc_port: int = 8006
        vlc_port: int = 8080
        path_to_vm: Optional[str] = None
        status: 'VMPoolResourceManager.Status' = field(default="free") # type: ignore
        allocated_to: Optional[str] = None
        allocated_at: Optional[float] = None
        error_message: Optional[str] = None
        config: Dict[str, Any] = field(default_factory=dict)
        lock: threading.Lock = field(default_factory=threading.Lock)

        def __post_init__(self):
            # 处理默认值类型转换
            if isinstance(self.status, str):
                self.status = VMPoolResourceManager.Status(self.status)

    # -------------------------------------------------------------------------
    # 2. 核心逻辑实现 (Server Side Implementation)
    #    该类运行在独立的 BaseManager 进程中
    # -------------------------------------------------------------------------

    class _ManagerImpl:
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

            self.vm_pool: Dict[str, VMPoolResourceManager.Entry] = {}
            self.free_vm_queue: Queue = Queue()
            self.pool_lock = threading.RLock()
            self.stats = {
                "total_vms": 0, "free_vms": 0, "occupied_vms": 0, 
                "error_vms": 0, "total_allocations": 0, "total_releases": 0,
            }

            logger.info("VMPoolManagerImpl initialized: num_vms=%s provider=%s", num_vms, provider_name)

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
                    chromium_port = int(vm_ip_ports[2]) if len(vm_ip_ports) > 2 else 9222
                    vnc_port = int(vm_ip_ports[3]) if len(vm_ip_ports) > 3 else 8006
                    vlc_port = int(vm_ip_ports[4]) if len(vm_ip_ports) > 4 else 8080

                    vm_entry = VMPoolResourceManager.Entry(
                        vm_id=vm_id,
                        ip=vm_ip,
                        port=server_port,
                        chromium_port=chromium_port,
                        vnc_port=vnc_port,
                        vlc_port=vlc_port,
                        path_to_vm=vm_path,
                        status=VMPoolResourceManager.Status.FREE,
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
                    vm_entry = VMPoolResourceManager.Entry(
                        vm_id=vm_id,
                        status=VMPoolResourceManager.Status.ERROR,
                        error_message=str(exc),
                        config=desktop_env_kwargs if desktop_env_kwargs else {},
                    )
                    with self.pool_lock:
                        self.vm_pool[vm_id] = vm_entry
                        self.stats["total_vms"] += 1
                        self.stats["error_vms"] += 1

            logger.info("VM pool initialization completed: %s/%s successful", success_count, self.num_vms)
            return success_count == self.num_vms

        def allocate_vm(self, worker_id: str, timeout: float = 30.0) -> Optional[Tuple[str, Dict[str, Any]]]:
            """为 worker 分配 VM（返回连接信息）"""
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    vm_id = self.free_vm_queue.get(timeout=1.0)
                    with self.pool_lock:
                        vm_entry = self.vm_pool.get(vm_id)
                        if vm_entry is None: continue
                        if vm_entry.status != VMPoolResourceManager.Status.FREE: continue
                        if vm_entry.ip is None:
                            logger.warning("VM %s has no IP, skipping", vm_id)
                            vm_entry.status = VMPoolResourceManager.Status.ERROR
                            continue

                        vm_entry.status = VMPoolResourceManager.Status.OCCUPIED
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

                        logger.info("Allocated %s to worker %s", vm_id, worker_id)
                        return (vm_id, connection_info)
                except Empty:
                    continue
                except Exception as exc:
                    logger.error("Error allocating VM: %s", exc)
                    continue

            return None

        def release_vm(self, vm_id: str, worker_id: str, reset: bool = True) -> bool:
            """释放 VM"""
            with self.pool_lock:
                vm_entry = self.vm_pool.get(vm_id)
                if vm_entry is None:
                    logger.warning("VM %s not found in pool", vm_id)
                    return False
                if vm_entry.allocated_to != worker_id:
                    logger.warning("VM %s allocated to %s, not %s. Release ignored.", 
                                 vm_id, vm_entry.allocated_to, worker_id)
                    return False

                if reset and vm_entry.path_to_vm:
                    self._reset_vm_to_snapshot(vm_id, vm_entry)

                vm_entry.status = VMPoolResourceManager.Status.FREE
                vm_entry.allocated_to = None
                vm_entry.allocated_at = None
                self.stats["free_vms"] += 1
                self.stats["occupied_vms"] -= 1
                self.stats["total_releases"] += 1
                self.free_vm_queue.put(vm_id)

                logger.info("Released %s from worker %s", vm_id, worker_id)
                return True

        def _reset_vm_to_snapshot(self, vm_id: str, vm_entry: 'VMPoolResourceManager.Entry') -> None:
            """使用 Provider API 重置 VM"""
            if vm_entry.path_to_vm is None: return

            max_attempts = 5
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                try:
                    _, provider = create_vm_manager_and_provider(
                        self.provider_name, self.region or "", use_proxy=False
                    )
                    path_to_vm = vm_entry.path_to_vm
                    if not path_to_vm: return
                    
                    new_vm_path = provider.revert_to_snapshot(path_to_vm, self.snapshot_name)
                    if new_vm_path and new_vm_path != path_to_vm:
                        logger.info("VM %s path changed: %s -> %s", vm_id, path_to_vm, new_vm_path)
                        vm_entry.path_to_vm = new_vm_path
                        path_to_vm = new_vm_path

                    vm_ip_ports = provider.get_ip_address(path_to_vm).split(":")
                    new_ip = vm_ip_ports[0]
                    if new_ip != vm_entry.ip:
                        logger.info("VM %s IP changed: %s -> %s", vm_id, vm_entry.ip, new_ip)
                        vm_entry.ip = new_ip
                        if len(vm_ip_ports) > 1:
                            vm_entry.port = int(vm_ip_ports[1])
                            vm_entry.chromium_port = int(vm_ip_ports[2]) if len(vm_ip_ports) > 2 else vm_entry.chromium_port
                            vm_entry.vnc_port = int(vm_ip_ports[3]) if len(vm_ip_ports) > 3 else vm_entry.vnc_port
                            vm_entry.vlc_port = int(vm_ip_ports[4]) if len(vm_ip_ports) > 4 else vm_entry.vlc_port

                    logger.info("Reset %s to snapshot", vm_id)
                    return
                except KeyboardInterrupt:
                    return
                except Exception as exc:
                    message = str(exc).lower()
                    if "lasttokenprocessing" in message:
                        time.sleep(5)
                        continue
                    if "not found" in message:
                        return
                    logger.warning("Failed to reset %s: %s", vm_id, exc)
                    return

        def stop_all_vms(self) -> None:
            """停止所有 VM"""
            logger.info("Stopping all VMs...")
            _, provider = create_vm_manager_and_provider(
                self.provider_name, self.region or "", use_proxy=False
            )
            with self.pool_lock:
                for vm_id, vm_entry in self.vm_pool.items():
                    if vm_entry.path_to_vm is None: continue
                    try:
                        provider.stop_emulator(vm_entry.path_to_vm)
                        vm_entry.status = VMPoolResourceManager.Status.STOPPED
                    except Exception as exc:
                        logger.error("Failed to stop %s: %s", vm_id, exc)
            logger.info("All VMs stopped")

        def get_stats(self) -> Dict[str, Any]:
            with self.pool_lock:
                return {
                    **self.stats,
                    "vm_statuses": {
                        vm_id: entry.status.value for vm_id, entry in self.vm_pool.items()
                    },
                }

    # -------------------------------------------------------------------------
    # 3. 对外接口实现 (Proxy Implementation)
    # -------------------------------------------------------------------------

    def __init__(
        self,
        vm_pool_manager: Optional[Any] = None,
        *,
        base_manager: Optional[BaseManager] = None,
        pool_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            vm_pool_manager: 现有的代理实例（在 Worker 进程中传入）。
            pool_config: 配置字典（在主进程初始化时传入）。
        """
        if vm_pool_manager is None:
            if pool_config is None:
                raise ValueError("pool_config must be provided when vm_pool_manager is None")
            
            self._pool_config = self._normalize_pool_config(pool_config)
            # 启动独立进程
            self._base_manager, self._vm_pool_manager = self._start_vm_pool_manager(self._pool_config)
        else:
            # 使用现有的连接（通常在 Worker 中）
            self._vm_pool_manager = vm_pool_manager
            self._base_manager = base_manager
            self._pool_config = {}

    @property
    def resource_type(self) -> str:
        return "vm"

    def initialize(self) -> bool:
        return self._vm_pool_manager.initialize_pool()

    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Tuple[str, Dict[str, Any]]:
        result = self._vm_pool_manager.allocate_vm(worker_id, timeout)
        if result is None:
            raise RuntimeError(f"Failed to allocate VM for worker {worker_id} (timeout={timeout}s)")
        
        vm_id, connection_info = result
        logger.info("Worker %s allocated VM %s (Data Only)", worker_id, vm_id)
        return (vm_id, connection_info)

    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        self._vm_pool_manager.release_vm(resource_id, worker_id, reset=reset)

    def get_status(self) -> Dict[str, Any]:
        return self._vm_pool_manager.get_stats()

    def stop_all(self) -> None:
        if self._vm_pool_manager:
            try:
                self._vm_pool_manager.stop_all_vms()
            except Exception:
                pass
        if self._base_manager:
            try:
                self._base_manager.shutdown()
            except Exception as exc:
                logger.warning("Failed to shutdown VM pool manager process: %s", exc)

    # -------------------------------------------------------------------------
    # 4. 辅助方法 (Helpers)
    # -------------------------------------------------------------------------

    @staticmethod
    def _start_vm_pool_manager(config: Config):
        """启动 BaseManager 并注册内部的 _ManagerImpl"""
        # 注册内部实现类
        # 注意: BaseManager.register 需要一个 callable，这里传入类本身即可
        # _VMPoolManagerBase就是BaseManager
        _VMPoolManagerBase.register("ManagerImpl", VMPoolResourceManager._ManagerImpl)
        #将字符串 "ManagerImpl" 与 VMPoolResourceManager._ManagerImpl 类关联起来



        manager = _VMPoolManagerBase()
        manager.start()
        #创建了一个_VMPoolManagerBase实例（也就是_base_manager）
        #启动了一个独立的进程，这个进程将托管所有注册的对象

        # 获取代理构造函数
        vm_pool_ctor = getattr(manager, "ManagerImpl")


        ctor_kwargs: MutableMapping[str, Any] = dict(config)
        extra_kwargs = ctor_kwargs.pop("extra_kwargs", {})
        vm_pool_manager_proxy = vm_pool_ctor(**ctor_kwargs, **extra_kwargs)
        #准备构造_ManagerImpl实例所需的参数
        #调用代理构造函数，在_base_manager管理的独立进程中创建_ManagerImpl的实际实例
        #返回一个代理对象，这个代理对象就是_vm_pool_manager


        return manager, vm_pool_manager_proxy

    @staticmethod
    def _ensure_bool(value: Any, default: bool) -> bool:
        if isinstance(value, bool): return value
        if value is None: return default
        return bool(value)

    @staticmethod
    def _normalize_pool_config(raw: Optional[Mapping[str, Any]]) -> Config:
        raw = raw or {}

        def _get_int(key: str, default: int) -> int:
            value = raw.get(key, default)
            try: return int(value)
            except (TypeError, ValueError): return default

        def _get_tuple(key: str, default: Tuple[int, int]) -> Tuple[int, int]:
            value = raw.get(key)
            if isinstance(value, (list, tuple)) and len(value) == 2:
                try: return (int(value[0]), int(value[1]))
                except (TypeError, ValueError): pass
            return default

        known_keys = {
            "num_vms", "provider_name", "region", "path_to_vm", "snapshot_name",
            "action_space", "screen_size", "headless", "require_a11y_tree",
            "require_terminal", "os_type", "client_password",
        }
        extra_kwargs = {k: v for k, v in raw.items() if k not in known_keys}

        config: VMPoolResourceManager.Config = {
            "num_vms": _get_int("num_vms", 1),
            "provider_name": str(raw.get("provider_name") or "vmware"),
            "region": raw.get("region"),
            "path_to_vm": raw.get("path_to_vm"),
            "snapshot_name": str(raw.get("snapshot_name") or "init_state"),
            "action_space": str(raw.get("action_space") or "computer_13"),
            "screen_size": _get_tuple("screen_size", (1920, 1080)),
            "headless": VMPoolResourceManager._ensure_bool(raw.get("headless"), False),
            "require_a11y_tree": VMPoolResourceManager._ensure_bool(raw.get("require_a11y_tree"), True),
            "require_terminal": VMPoolResourceManager._ensure_bool(raw.get("require_terminal"), False),
            "os_type": str(raw.get("os_type") or "Ubuntu"),
            "client_password": str(raw.get("client_password") or "password"),
            "extra_kwargs": extra_kwargs,
        }
        return config