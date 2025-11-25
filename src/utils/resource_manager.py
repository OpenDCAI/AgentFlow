# src/utils/resource_manager.py
# -*- coding: utf-8 -*-
"""
资源管理器 - 统一管理重资产资源（VM、GPU等）

重构说明：
1. 引入 AbstractPoolManager 基类，封装通用的资源池管理逻辑（队列、锁、状态流转）。
2. VMPoolResourceManager._ManagerImpl 继承基类，专注于 VM 特定逻辑。
3. 统一了资源条目模型 ResourceEntry 和状态 ResourceStatus。
"""

import logging
from abc import ABC, abstractmethod
from multiprocessing.managers import BaseManager
from typing import (
    Any,
    Dict,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    TypedDict,
)

from utils.resource_pools.base import AbstractPoolManager, ResourceEntry, ResourceStatus
from utils.resource_pools.vm_pool import VMPoolImpl

logger = logging.getLogger(__name__)


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
    - Server 端 (VMPoolImpl)：继承 AbstractPoolManager，实现 VM 具体逻辑。
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
        _VMPoolManagerBase.register("ManagerImpl", VMPoolImpl)
        
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