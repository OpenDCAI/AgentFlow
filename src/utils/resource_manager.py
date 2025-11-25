# -*- coding: utf-8 -*-
"""
资源管理器 - 统一管理重资产资源（VM、GPU等）

重构说明：
1. 引入 AbstractPoolManager 基类，封装通用的资源池管理逻辑（队列、锁、状态流转）。
2. VMPoolResourceManager._ManagerImpl 继承基类，专注于 VM 特定逻辑。
3. 统一了资源条目模型 ResourceEntry 和状态 ResourceStatus。
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
    List,
)

from utils.desktop_env.providers import create_vm_manager_and_provider

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# 1. 基础数据结构与抽象基类 (Base Structures & Abstract Class)
# -------------------------------------------------------------------------

class ResourceStatus(Enum):
    """通用资源状态"""
    FREE = "free"
    OCCUPIED = "occupied"
    INITIALIZING = "initializing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ResourceEntry:
    """通用资源条目基类"""
    resource_id: str
    status: ResourceStatus = ResourceStatus.FREE
    allocated_to: Optional[str] = None
    allocated_at: Optional[float] = None
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self):
        # 自动转换字符串状态
        if isinstance(self.status, str):
            self.status = ResourceStatus(self.status)


class AbstractPoolManager(ABC):
    """
    抽象资源池管理器
    封装了资源池的核心生命周期管理：初始化、分配、释放、统计。
    具体资源（如 VM、Docker 容器）的创建与重置逻辑由子类实现。
    """

    def __init__(self, num_items: int):
        self.num_items = num_items
        self.pool: Dict[str, ResourceEntry] = {}
        self.free_queue: Queue = Queue()
        self.pool_lock = threading.RLock()
        self.stats = {
            "total": 0, "free": 0, "occupied": 0,
            "error": 0, "allocations": 0, "releases": 0,
        }
        logger.info(f"{self.__class__.__name__} initialized with {num_items} items")

    # --- 抽象方法 (子类需实现) ---

    @abstractmethod
    def _create_resource(self, index: int) -> ResourceEntry:
        """创建一个新的资源实例"""
        pass

    @abstractmethod
    def _validate_resource(self, entry: ResourceEntry) -> bool:
        """检查资源是否可用（例如检查 IP 是否存在）"""
        pass

    @abstractmethod
    def _get_connection_info(self, entry: ResourceEntry) -> Dict[str, Any]:
        """获取资源的连接信息字典"""
        pass

    @abstractmethod
    def _reset_resource(self, entry: ResourceEntry) -> None:
        """重置资源状态（例如 revert snapshot）"""
        pass

    @abstractmethod
    def _stop_resource(self, entry: ResourceEntry) -> None:
        """停止/销毁资源"""
        pass

    # --- 模板方法 (通用逻辑) ---

    def initialize_pool(self) -> bool:
        """初始化资源池"""
        logger.info(f"Initializing pool with {self.num_items} resources...")
        success_count = 0
        for i in range(self.num_items):
            try:
                entry = self._create_resource(i)
                with self.pool_lock:
                    self.pool[entry.resource_id] = entry
                    if entry.status == ResourceStatus.FREE:
                        self.free_queue.put(entry.resource_id)
                        self.stats["free"] += 1
                        success_count += 1
                    else:
                        self.stats["error"] += 1
                    self.stats["total"] += 1
            except Exception as e:
                logger.error(f"Failed to create resource index {i}: {e}", exc_info=True)
                self.stats["error"] += 1
        
        logger.info(f"Pool initialization completed: {success_count}/{self.num_items} ready")
        return success_count == self.num_items

    def allocate(self, worker_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """分配资源"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resource_id = self.free_queue.get(timeout=1.0)
                with self.pool_lock:
                    entry = self.pool.get(resource_id)
                    if not entry: continue
                    if entry.status != ResourceStatus.FREE: continue
                    
                    # 校验资源有效性
                    if not self._validate_resource(entry):
                        logger.warning(f"Resource {resource_id} invalid during allocation, marking error.")
                        entry.status = ResourceStatus.ERROR
                        self.stats["free"] -= 1
                        self.stats["error"] += 1
                        continue

                    # 标记占用
                    entry.status = ResourceStatus.OCCUPIED
                    entry.allocated_to = worker_id
                    entry.allocated_at = time.time()
                    
                    self.stats["free"] -= 1
                    self.stats["occupied"] += 1
                    self.stats["allocations"] += 1

                    result = self._get_connection_info(entry)
                    # 确保返回结果包含 id
                    if "id" not in result:
                        result["id"] = resource_id
                        
                    logger.info(f"Allocated {resource_id} to {worker_id}")
                    return result

            except Empty:
                continue
            except Exception as exc:
                logger.error(f"Error allocating resource: {exc}", exc_info=True)
                continue
        return None

    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> bool:
        """释放资源"""
        with self.pool_lock:
            entry = self.pool.get(resource_id)
            if not entry:
                logger.warning(f"Resource {resource_id} not found for release")
                return False
            if entry.allocated_to != worker_id:
                logger.warning(f"Resource {resource_id} owned by {entry.allocated_to}, {worker_id} tried to release. Ignored.")
                return False

            # 执行重置逻辑
            if reset:
                try:
                    self._reset_resource(entry)
                except Exception as e:
                    logger.error(f"Failed to reset resource {resource_id}: {e}")
                    # 即使重置失败，我们也将其放回池中（或者标记为错误），这里选择放回但记录日志
                    # 实际生产中可能需要标记为 ERROR

            entry.status = ResourceStatus.FREE
            entry.allocated_to = None
            entry.allocated_at = None
            
            self.stats["occupied"] -= 1
            self.stats["free"] += 1
            self.stats["releases"] += 1
            
            self.free_queue.put(resource_id)
            logger.info(f"Released {resource_id} from {worker_id}")
            return True

    def stop_all(self) -> None:
        """停止所有资源"""
        logger.info("Stopping all resources...")
        with self.pool_lock:
            for rid, entry in self.pool.items():
                try:
                    self._stop_resource(entry)
                    entry.status = ResourceStatus.STOPPED
                except Exception as e:
                    logger.error(f"Failed to stop {rid}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        with self.pool_lock:
            stats = self.stats.copy()
            stats["statuses"] = {
                rid: entry.status.value for rid, entry in self.pool.items()
            }
            return stats


# 为了确保多进程兼容性，BaseManager 子类建议定义在模块层级
class _VMPoolManagerBase(BaseManager):
    """BaseManager 子类，用于跨进程托管 ManagerImpl"""
    pass


# -------------------------------------------------------------------------
# 2. 资源管理器接口与实现 (Resource Manager Interface & Implementation)
# -------------------------------------------------------------------------

class ResourceManager(ABC):
    """资源管理器通用接口"""

    @property
    @abstractmethod
    def resource_type(self) -> str:
        """资源类型标识"""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def stop_all(self) -> None:
        pass


class NoResourceManager(ResourceManager):
    """无重资产管理器 (Null Object Pattern)"""

    @property
    def resource_type(self) -> str:
        return "none"

    def initialize(self) -> bool:
        return True

    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Dict[str, Any]:
        return {"id": f"virtual-{worker_id}"}

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
    - Client 端 (本类)：暴露统一接口，作为 Proxy。
    - Server 端 (_ManagerImpl)：继承 AbstractPoolManager，实现 VM 具体逻辑。
    """

    class Config(TypedDict, total=False):
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

    @dataclass
    class Entry(ResourceEntry):
        """VM 特有的资源条目"""
        ip: Optional[str] = None
        port: int = 5000
        chromium_port: int = 9222
        vnc_port: int = 8006
        vlc_port: int = 8080
        path_to_vm: Optional[str] = None

    # -------------------------------------------------------------------------
    # Server Side Implementation
    # -------------------------------------------------------------------------

    class _ManagerImpl(AbstractPoolManager):
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
            # 初始化基类
            super().__init__(num_items=num_vms)
            
            # 保存 VM 特定配置
            self.provider_name = provider_name
            self.region = region
            self.path_to_vm_template = path_to_vm
            self.snapshot_name = snapshot_name
            self.action_space = action_space
            self.screen_size = screen_size
            self.headless = headless
            self.require_a11y_tree = require_a11y_tree
            self.require_terminal = require_terminal
            self.os_type = os_type
            self.client_password = client_password
            self.extra_kwargs = kwargs

        def _create_resource(self, index: int) -> 'VMPoolResourceManager.Entry':
            """实现 VM 创建逻辑"""
            vm_id = f"vm_{index + 1}"
            logger.info("Initializing %s...", vm_id)
            
            manager, provider = create_vm_manager_and_provider(
                self.provider_name, self.region or "", use_proxy=False
            )

            # 准备配置
            desktop_env_kwargs = {
                "provider_name": self.provider_name,
                "region": self.region,
                "path_to_vm": self.path_to_vm_template,
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

            # 解析 VM 路径
            if self.path_to_vm_template:
                vm_path = self.path_to_vm_template
            else:
                vm_path = manager.get_vm_path(
                    os_type=self.os_type,
                    region=self.region or "",
                    screen_size=self.screen_size,
                )
            
            if not vm_path:
                raise RuntimeError(f"Failed to resolve vm_path for {vm_id}")

            # 启动 VM
            provider.start_emulator(vm_path, self.headless, self.os_type)
            
            # 获取 IP
            vm_ip_ports = provider.get_ip_address(vm_path).split(":")
            vm_ip = vm_ip_ports[0]
            
            # 构造 Entry
            entry = VMPoolResourceManager.Entry(
                resource_id=vm_id,
                status=ResourceStatus.FREE,
                ip=vm_ip,
                port=int(vm_ip_ports[1]) if len(vm_ip_ports) > 1 else 5000,
                chromium_port=int(vm_ip_ports[2]) if len(vm_ip_ports) > 2 else 9222,
                vnc_port=int(vm_ip_ports[3]) if len(vm_ip_ports) > 3 else 8006,
                vlc_port=int(vm_ip_ports[4]) if len(vm_ip_ports) > 4 else 8080,
                path_to_vm=vm_path,
                config=desktop_env_kwargs
            )
            logger.info("✓ %s initialized: ip=%s", vm_id, vm_ip)
            return entry

        def _validate_resource(self, entry: 'ResourceEntry') -> bool:
            # 确保是 VM Entry 且 IP 存在
            if not isinstance(entry, VMPoolResourceManager.Entry): return False
            if entry.ip is None:
                logger.warning(f"VM {entry.resource_id} has no IP")
                return False
            return True

        def _get_connection_info(self, entry: 'ResourceEntry') -> Dict[str, Any]:
            # 返回 VM 连接信息
            assert isinstance(entry, VMPoolResourceManager.Entry)
            return {
                "id": entry.resource_id,
                "ip": entry.ip,
                "port": entry.port,
                "chromium_port": entry.chromium_port,
                "vnc_port": entry.vnc_port,
                "vlc_port": entry.vlc_port,
                "path_to_vm": entry.path_to_vm,
                "config": entry.config,
            }

        def _reset_resource(self, entry: 'ResourceEntry') -> None:
            # Revert VM Snapshot
            assert isinstance(entry, VMPoolResourceManager.Entry)
            if not entry.path_to_vm: return

            _, provider = create_vm_manager_and_provider(
                self.provider_name, self.region or "", use_proxy=False
            )
            
            new_vm_path = provider.revert_to_snapshot(entry.path_to_vm, self.snapshot_name)
            if new_vm_path and new_vm_path != entry.path_to_vm:
                logger.info(f"VM {entry.resource_id} path changed: {entry.path_to_vm} -> {new_vm_path}")
                entry.path_to_vm = new_vm_path

            # 重置后更新 IP
            vm_ip_ports = provider.get_ip_address(entry.path_to_vm).split(":")
            new_ip = vm_ip_ports[0]
            if new_ip != entry.ip:
                logger.info(f"VM {entry.resource_id} IP changed: {entry.ip} -> {new_ip}")
                entry.ip = new_ip
                if len(vm_ip_ports) > 1:
                    entry.port = int(vm_ip_ports[1])
                    # ... update other ports if needed

        def _stop_resource(self, entry: 'ResourceEntry') -> None:
            assert isinstance(entry, VMPoolResourceManager.Entry)
            if not entry.path_to_vm: return
            _, provider = create_vm_manager_and_provider(
                self.provider_name, self.region or "", use_proxy=False
            )
            provider.stop_emulator(entry.path_to_vm)

    # -------------------------------------------------------------------------
    # Client Side Proxy Implementation
    # -------------------------------------------------------------------------

    def __init__(
        self,
        vm_pool_manager: Optional[Any] = None,
        *,
        base_manager: Optional[BaseManager] = None,
        pool_config: Optional[Dict[str, Any]] = None,
    ):
        if vm_pool_manager is None:
            if pool_config is None:
                raise ValueError("pool_config must be provided when vm_pool_manager is None")
            
            self._pool_config = self._normalize_pool_config(pool_config)
            self._base_manager, self._vm_pool_manager = self._start_vm_pool_manager(self._pool_config)
        else:
            self._vm_pool_manager = vm_pool_manager
            self._base_manager = base_manager
            self._pool_config = {}

    @property
    def resource_type(self) -> str:
        return "vm"

    def initialize(self) -> bool:
        return self._vm_pool_manager.initialize_pool()

    def allocate(self, worker_id: str, timeout: float, **kwargs) -> Dict[str, Any]:
        # 调用基类的 allocate 方法
        result = self._vm_pool_manager.allocate(worker_id, timeout)
        if result is None:
            raise RuntimeError(f"Failed to allocate VM for worker {worker_id} (timeout={timeout}s)")
        
        logger.info("Worker %s allocated VM %s (Data Only)", worker_id, result['id'])
        return result

    def release(self, resource_id: str, worker_id: str, reset: bool = True) -> None:
        # 调用基类的 release 方法
        self._vm_pool_manager.release(resource_id, worker_id, reset=reset)

    def get_status(self) -> Dict[str, Any]:
        return self._vm_pool_manager.get_stats()

    def stop_all(self) -> None:
        if self._vm_pool_manager:
            try:
                self._vm_pool_manager.stop_all()
            except Exception:
                pass
        if self._base_manager:
            try:
                self._base_manager.shutdown()
            except Exception as exc:
                logger.warning("Failed to shutdown VM pool manager process: %s", exc)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _start_vm_pool_manager(config: Config):
        # 注册内部实现类
        _VMPoolManagerBase.register("ManagerImpl", VMPoolResourceManager._ManagerImpl)
        
        manager = _VMPoolManagerBase()
        manager.start()

        vm_pool_ctor = getattr(manager, "ManagerImpl")
        ctor_kwargs: MutableMapping[str, Any] = dict(config)
        extra_kwargs = ctor_kwargs.pop("extra_kwargs", {})
        vm_pool_manager_proxy = vm_pool_ctor(**ctor_kwargs, **extra_kwargs)

        return manager, vm_pool_manager_proxy

    @staticmethod
    def _ensure_bool(value: Any, default: bool) -> bool:
        if isinstance(value, bool): return value
        if value is None: return default
        return bool(value)

    @staticmethod
    def _normalize_pool_config(raw: Optional[Mapping[str, Any]]) -> Config:
        raw = raw or {}
        # ... (Config normalization logic remains same) ...
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


if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # Smoke Test (冒烟验证)
    # -------------------------------------------------------------------------
    def _smoke_test():
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        logger.info("Starting smoke test...")

        # 1. Test NoResourceManager
        logger.info("Testing NoResourceManager...")
        no_mgr = NoResourceManager()
        assert no_mgr.initialize()
        alloc = no_mgr.allocate("worker-1", 1.0)
        assert isinstance(alloc, dict)
        assert alloc["id"] == "virtual-worker-1"
        no_mgr.release("virtual-worker-1", "worker-1")
        logger.info("NoResourceManager test passed.")

        # 2. Test AbstractPoolManager Logic (using a Mock implementation)
        logger.info("Testing AbstractPoolManager logic...")
        
        class MockImpl(AbstractPoolManager):
            def _create_resource(self, index: int) -> ResourceEntry:
                return ResourceEntry(resource_id=f"mock-{index}")

            def _validate_resource(self, entry: ResourceEntry) -> bool:
                return True

            def _get_connection_info(self, entry: ResourceEntry) -> Dict[str, Any]:
                return {"id": entry.resource_id, "info": "mock"}

            def _reset_resource(self, entry: ResourceEntry) -> None:
                pass

            def _stop_resource(self, entry: ResourceEntry) -> None:
                pass

        # Init pool with 2 items
        pool = MockImpl(num_items=2)
        success = pool.initialize_pool()
        assert success
        assert pool.stats["total"] == 2
        assert pool.stats["free"] == 2

        # Allocate 1
        r1 = pool.allocate("w1", timeout=0.1)
        assert r1 is not None
        assert r1["id"] == "mock-0"
        
        # Allocate 2
        r2 = pool.allocate("w2", timeout=0.1)
        assert r2 is not None
        assert r2["id"] == "mock-1"

        # Allocate 3 (should fail)
        r3 = pool.allocate("w3", timeout=0.1)
        assert r3 is None

        # Release 1
        pool.release("mock-0", "w1")
        assert pool.stats["free"] == 1

        # Allocate again (should get mock-0)
        r4 = pool.allocate("w3", timeout=0.1)
        assert r4 is not None
        assert r4["id"] == "mock-0"

        pool.stop_all()
        logger.info("AbstractPoolManager logic test passed.")
        logger.info("Smoke test completed successfully.")

    _smoke_test()