# sandbox/server/core/resource_router.py
"""
资源路由表管理器

管理 worker_id -> resource_type -> session 的映射关系
支持自动创建和显式创建两种模式
"""

import asyncio
import logging
import re
import uuid
from typing import Dict, Any, Optional, List, Callable, Set
from datetime import datetime, timedelta

logger = logging.getLogger("ResourceRouter")


class ResourceRouter:
    """
    资源路由表管理器
    
    管理 worker_id -> resource_type -> session 的映射关系
    
    支持两种模式：
    1. 显式创建：client调用create_session显式创建session
    2. 自动创建：执行命令时如果没有session则自动创建（会在日志中提示）
    
    使用示例:
    ```python
    router = ResourceRouter(session_ttl=300)
    
    # 注册资源类型
    router.register_resource_type(
        "vm",
        initializer=init_vm,
        cleaner=cleanup_vm,
        default_config={"screen_size": [1920, 1080]}
    )
    
    # 获取或创建session
    session = await router.get_or_create_session("worker_1", "vm")
    
    # 销毁session
    await router.destroy_session("worker_1", "vm")
    ```
    """
    
    def __init__(self, session_ttl: int = 300, auto_create: bool = True):
        """
        初始化资源路由器
        
        Args:
            session_ttl: Session存活时间（秒）
            auto_create: 是否允许自动创建session
        """
        # 路由表: {worker_id: {resource_type: session_info}}
        self._routes: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # 资源初始化配置: {resource_type: init_config}
        self._resource_configs: Dict[str, Dict[str, Any]] = {}
        # 资源初始化回调: {resource_type: init_callback}
        self._resource_initializers: Dict[str, Callable] = {}
        # 资源清理回调: {resource_type: cleanup_callback}
        self._resource_cleaners: Dict[str, Callable] = {}
        self._session_ttl = session_ttl
        self._auto_create = auto_create
        self._session_counter: Dict[str, int] = {}
        self._lock = asyncio.Lock()
    
    def register_resource_type(
        self,
        resource_type: str,
        initializer: Optional[Callable] = None,
        cleaner: Optional[Callable] = None,
        default_config: Optional[Dict[str, Any]] = None
    ):
        """
        注册资源类型
        
        Args:
            resource_type: 资源类型名称
            initializer: 初始化回调函数 async def init(worker_id, config) -> session_info
            cleaner: 清理回调函数 async def cleanup(worker_id, session_info)
            default_config: 默认配置
        """
        if initializer:
            self._resource_initializers[resource_type] = initializer
        if cleaner:
            self._resource_cleaners[resource_type] = cleaner
        if default_config:
            self._resource_configs[resource_type] = default_config
        logger.info(f"Registered resource type: {resource_type}")
    
    def unregister_resource_type(self, resource_type: str) -> bool:
        """注销资源类型"""
        removed = False
        if resource_type in self._resource_initializers:
            del self._resource_initializers[resource_type]
            removed = True
        if resource_type in self._resource_cleaners:
            del self._resource_cleaners[resource_type]
            removed = True
        if resource_type in self._resource_configs:
            del self._resource_configs[resource_type]
            removed = True
        return removed
    
    def get_registered_types(self) -> List[str]:
        """获取已注册的资源类型列表"""
        types = set()
        types.update(self._resource_initializers.keys())
        types.update(self._resource_configs.keys())
        return list(types)
    
    def _normalize_custom_name(self, custom_name: Optional[str]) -> Optional[str]:
        """规范化用户自定义名称，避免非法字符或过长"""
        if not custom_name:
            return None
        safe_custom = re.sub(r"[^A-Za-z0-9_-]", "-", str(custom_name)).strip("-_")
        if not safe_custom:
            return None
        return safe_custom[:32]

    def _merge_resource_config(
        self,
        resource_type: str,
        config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """合并默认配置与用户配置（用户优先）"""
        merged = dict(self._resource_configs.get(resource_type, {}))
        if config:
            merged.update(config)
        return merged

    def _generate_session_name(
        self,
        worker_id: str,
        resource_type: str,
        custom_name: Optional[str] = None
    ) -> str:
        """生成可读的session名称"""
        # 规范化 worker_id，避免过长或包含不安全字符
        safe_worker_id = re.sub(r"[^A-Za-z0-9_-]", "-", worker_id).strip("-")
        if not safe_worker_id:
            safe_worker_id = "worker"
        max_len = 32
        worker_short = safe_worker_id[:max_len]
        
        counter_key = f"{worker_id}:{resource_type}"
        if counter_key not in self._session_counter:
            self._session_counter[counter_key] = 0
        self._session_counter[counter_key] += 1
        
        base_name = f"{resource_type}_{worker_short}_{self._session_counter[counter_key]:03d}"
        safe_custom = self._normalize_custom_name(custom_name)
        if safe_custom:
            return f"{base_name}_{safe_custom}"
        return base_name
    
    async def get_or_create_session(
        self,
        worker_id: str,
        resource_type: str,
        config: Optional[Dict[str, Any]] = None,
        auto_created: bool = False,
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取或创建资源session
        
        如果worker_id对应的resource_type已有session则直接返回，
        否则创建新的session
        
        Args:
            worker_id: Worker ID
            resource_type: 资源类型
            config: 初始化配置（可选，优先于默认配置）
            auto_created: 是否为自动创建（用于日志区分）
            
        Returns:
            session信息字典，包含:
            - session_id: 唯一标识
            - session_name: 可读名称
            - worker_id: Worker ID
            - resource_type: 资源类型
            - config: 配置
            - status: 状态 (active/error/initializing)
            - data: 资源特定数据
            - custom_name: 规范化后的自定义名称（如果提供）
        """
        async with self._lock:
            # 初始化worker路由
            if worker_id not in self._routes:
                self._routes[worker_id] = {}
            
            # 检查是否已有session
            if resource_type in self._routes[worker_id]:
                session_info = self._routes[worker_id][resource_type]
                # 更新最后活动时间
                session_info["last_activity"] = datetime.utcnow().isoformat()
                session_info["expires_at"] = (
                    datetime.utcnow() + timedelta(seconds=self._session_ttl)
                ).isoformat()
                return session_info
            
            # 生成session名称和ID
            session_name = self._generate_session_name(worker_id, resource_type, custom_name)
            session_id = f"{session_name}_{uuid.uuid4().hex[:8]}"
            
            init_config = self._merge_resource_config(resource_type, config)
            
            session_info = {
                "session_id": session_id,
                "session_name": session_name,
                "worker_id": worker_id,
                "resource_type": resource_type,
                "config": init_config,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self._session_ttl)).isoformat(),
                "status": "initializing",
                "auto_created": auto_created,
                "data": {},
                "custom_name": self._normalize_custom_name(custom_name)
            }
            
            # 调用初始化回调
            if resource_type in self._resource_initializers:
                try:
                    initializer = self._resource_initializers[resource_type]
                    if asyncio.iscoroutinefunction(initializer):
                        init_result = await initializer(worker_id, init_config)
                    else:
                        init_result = initializer(worker_id, init_config)

                    if init_result:
                        session_info["data"].update(init_result)
                    session_info["status"] = "active"
                except Exception as e:
                    logger.error(f"[{worker_id}] Resource init failed: {resource_type} - {e}")
                    session_info["status"] = "error"
                    session_info["error"] = str(e)
            else:
                # 资源类型没有注册 initializer，标记为兼容性创建
                session_info["status"] = "active"
                session_info["compatibility_mode"] = True
                session_info["compatibility_message"] = (
                    f"Resource type '{resource_type}' does not require session initialization. "
                    f"This session was created for compatibility but no initialization was performed."
                )

            self._routes[worker_id][resource_type] = session_info

            # 日志提示
            create_mode = "AUTO-CREATED" if auto_created else "CREATED"
            if resource_type not in self._resource_initializers:
                # 兼容性创建的日志
                logger.warning(
                    f"⚠️  [{worker_id}] Session {create_mode} (COMPATIBILITY MODE): {session_name} "
                    f"(id={session_id}, type={resource_type}) - Resource type does not require session"
                )
            else:
                logger.info(f"📦 [{worker_id}] Session {create_mode}: {session_name} (id={session_id}, type={resource_type})")
                if auto_created:
                    logger.info(f"   ↳ 提示: 该session由执行命令时自动创建，如需自定义配置请使用 create_session 显式创建")
            
            return session_info
    
    async def get_session(
        self,
        worker_id: str,
        resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """获取session（不自动创建）"""
        async with self._lock:
            if worker_id in self._routes:
                return self._routes[worker_id].get(resource_type)
        return None
    
    async def update_session(
        self,
        worker_id: str,
        resource_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """更新session数据"""
        async with self._lock:
            if worker_id in self._routes and resource_type in self._routes[worker_id]:
                self._routes[worker_id][resource_type]["data"].update(data)
                self._routes[worker_id][resource_type]["last_activity"] = datetime.utcnow().isoformat()
                return True
        return False
    
    async def destroy_session(
        self,
        worker_id: str,
        resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        销毁特定资源的session
        
        Returns:
            被销毁的session信息，如果不存在返回None
        """
        async with self._lock:
            if worker_id in self._routes and resource_type in self._routes[worker_id]:
                session_info = self._routes[worker_id][resource_type]
                session_name = session_info.get("session_name", "unknown")
                session_id = session_info.get("session_id", "unknown")
                
                # 调用清理回调
                if resource_type in self._resource_cleaners:
                    try:
                        cleaner = self._resource_cleaners[resource_type]
                        if asyncio.iscoroutinefunction(cleaner):
                            await cleaner(worker_id, session_info)
                        else:
                            cleaner(worker_id, session_info)
                    except Exception as e:
                        logger.error(f"[{worker_id}] Resource cleanup failed: {resource_type} - {e}")
                
                del self._routes[worker_id][resource_type]
                logger.info(f"🗑️ [{worker_id}] Session DESTROYED: {session_name} (id={session_id}, type={resource_type})")
                return session_info
        return None
    
    async def destroy_worker_sessions(self, worker_id: str) -> int:
        """销毁worker的所有session"""
        count = 0
        resource_types: List[str] = []
        
        async with self._lock:
            if worker_id in self._routes:
                resource_types = list(self._routes[worker_id].keys())
        
        # 在锁外执行清理，避免死锁
        for resource_type in resource_types:
            await self.destroy_session(worker_id, resource_type)
            count += 1
        
        async with self._lock:
            if worker_id in self._routes:
                del self._routes[worker_id]
        
        logger.info(f"[{worker_id}] Destroyed all {count} sessions")
        return count
    
    async def list_worker_sessions(self, worker_id: str) -> Dict[str, Dict[str, Any]]:
        """列出worker的所有session"""
        async with self._lock:
            if worker_id in self._routes:
                return dict(self._routes[worker_id])
        return {}
    
    async def list_all_sessions(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """列出所有session"""
        async with self._lock:
            return {wid: dict(sessions) for wid, sessions in self._routes.items()}
    
    async def cleanup_expired(self) -> int:
        """清理过期session"""
        now = datetime.utcnow()
        expired_list = []
        
        async with self._lock:
            for worker_id, sessions in self._routes.items():
                for resource_type, session_info in sessions.items():
                    expires_at = datetime.fromisoformat(session_info["expires_at"])
                    if expires_at < now:
                        expired_list.append((worker_id, resource_type))
        
        # 在锁外执行清理
        for worker_id, resource_type in expired_list:
            await self.destroy_session(worker_id, resource_type)
        
        return len(expired_list)
    
    async def get_active_resource_types(self, worker_id: str) -> Set[str]:
        """获取worker当前活跃的资源类型"""
        async with self._lock:
            if worker_id in self._routes:
                return set(self._routes[worker_id].keys())
        return set()
    
    async def refresh_session(self, worker_id: str, resource_type: str) -> bool:
        """刷新session的过期时间"""
        async with self._lock:
            if worker_id in self._routes and resource_type in self._routes[worker_id]:
                session_info = self._routes[worker_id][resource_type]
                old_expires_at = session_info.get("expires_at")
                session_info["last_activity"] = datetime.utcnow().isoformat()
                session_info["expires_at"] = (
                    datetime.utcnow() + timedelta(seconds=self._session_ttl)
                ).isoformat()
                logger.info(
                    "[%s] Session refreshed: %s (id=%s) expires_at %s -> %s",
                    worker_id,
                    resource_type,
                    session_info.get("session_id"),
                    old_expires_at,
                    session_info.get("expires_at"),
                )
                return True
        logger.warning("[%s] Session refresh skipped: %s (no active session)", worker_id, resource_type)
        return False

