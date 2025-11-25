# src/utils/resource_pools/base.py
# -*- coding: utf-8 -*-
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResourceStatus(Enum):
    """通用资源状态"""
    FREE = "free"                 # 资源空闲，可以被分配
    OCCUPIED = "occupied"         # 资源已被占用（已分配给 Worker）
    INITIALIZING = "initializing" # 资源正在初始化或重置中，暂时不可用
    ERROR = "error"               # 资源发生错误，需人工检查或自动修复
    STOPPED = "stopped"           # 资源已停止运行或被销毁


@dataclass
class ResourceEntry:
    """通用资源条目基类"""
    resource_id: str              # 资源的唯一标识符 (例如: 'vm_1', 'gpu_0')
    status: ResourceStatus = ResourceStatus.FREE  # 当前资源的生命周期状态
    allocated_to: Optional[str] = None  # 当前持有该资源的 Worker ID (空闲时为 None)
    allocated_at: Optional[float] = None  # 资源被分配的时间戳 (用于超时检测或统计)
    error_message: Optional[str] = None   # 当状态为 ERROR 时，记录具体的错误信息
    config: Dict[str, Any] = field(default_factory=dict)  # 资源的初始化配置/元数据
    lock: threading.Lock = field(default_factory=threading.Lock)  # 线程锁，保护该条目的并发读写

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