# sandbox/server/core/resource_router.py
"""
Resource Routing Table Manager

Manages worker_id -> resource_type -> session mapping relationships
Supports both automatic creation and explicit creation modes
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
    Resource Routing Table Manager
    
    Manages worker_id -> resource_type -> session mapping relationships
    
    Supports two modes:
    1. Explicit creation: client calls create_session to explicitly create session
    2. Automatic creation: automatically creates session when executing commands if no session exists (will be logged)
    
    Usage example:
    ```python
    router = ResourceRouter(session_ttl=300)
    
    # Register resource type
    router.register_resource_type(
        "vm",
        initializer=init_vm,
        cleaner=cleanup_vm,
        default_config={"screen_size": [1920, 1080]}
    )
    
    # Get or create session
    session = await router.get_or_create_session("worker_1", "vm")
    
    # Destroy session
    await router.destroy_session("worker_1", "vm")
    ```
    """
    
    def __init__(self, session_ttl: int = 300, auto_create: bool = True):
        """
        Initialize resource router
        
        Args:
            session_ttl: Session TTL (seconds)
            auto_create: Whether to allow automatic session creation
        """
        # Routing table: {worker_id: {resource_type: session_info}}
        self._routes: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Resource initialization config: {resource_type: init_config}
        self._resource_configs: Dict[str, Dict[str, Any]] = {}
        # Resource initialization callback: {resource_type: init_callback}
        self._resource_initializers: Dict[str, Callable] = {}
        # Resource cleanup callback: {resource_type: cleanup_callback}
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
        Register resource type
        
        Args:
            resource_type: Resource type name
            initializer: Initialization callback function async def init(worker_id, config) -> session_info
            cleaner: Cleanup callback function async def cleanup(worker_id, session_info)
            default_config: Default configuration
        """
        if initializer:
            self._resource_initializers[resource_type] = initializer
        if cleaner:
            self._resource_cleaners[resource_type] = cleaner
        if default_config:
            self._resource_configs[resource_type] = default_config
        logger.info(f"Registered resource type: {resource_type}")
    
    def unregister_resource_type(self, resource_type: str) -> bool:
        """Unregister resource type"""
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
        """Get list of registered resource types"""
        types = set()
        types.update(self._resource_initializers.keys())
        types.update(self._resource_configs.keys())
        return list(types)
    
    def _normalize_custom_name(self, custom_name: Optional[str]) -> Optional[str]:
        """Normalize user-defined name to avoid illegal characters or excessive length"""
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
        """Merge default config with user config (user config takes priority)"""
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
        """Generate readable session name"""
        # Normalize worker_id to avoid excessive length or unsafe characters
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
        Get or create resource session
        
        If worker_id already has a session for resource_type, return it directly,
        otherwise create a new session
        
        Args:
            worker_id: Worker ID
            resource_type: Resource type
            config: Initialization config (optional, takes priority over default config)
            auto_created: Whether it's auto-created (for log distinction)
            
        Returns:
            Session info dictionary, containing:
            - session_id: Unique identifier
            - session_name: Readable name
            - worker_id: Worker ID
            - resource_type: Resource type
            - config: Configuration
            - status: Status (active/error/initializing)
            - data: Resource-specific data
            - custom_name: Normalized custom name (if provided)
        """
        async with self._lock:
            # Initialize worker routing
            if worker_id not in self._routes:
                self._routes[worker_id] = {}
            
            # Check if session already exists
            if resource_type in self._routes[worker_id]:
                session_info = self._routes[worker_id][resource_type]
                # Update last activity time
                session_info["last_activity"] = datetime.utcnow().isoformat()
                session_info["expires_at"] = (
                    datetime.utcnow() + timedelta(seconds=self._session_ttl)
                ).isoformat()
                return session_info
            
            # Generate session name and ID
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
            
            # Call initialization callback
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
                # Resource type has no registered initializer, mark as compatibility creation
                session_info["status"] = "active"
                session_info["compatibility_mode"] = True
                session_info["compatibility_message"] = (
                    f"Resource type '{resource_type}' does not require session initialization. "
                    f"This session was created for compatibility but no initialization was performed."
                )

            self._routes[worker_id][resource_type] = session_info

            # Log message
            create_mode = "AUTO-CREATED" if auto_created else "CREATED"
            if resource_type not in self._resource_initializers:
                # Compatibility creation log
                logger.warning(
                    f"⚠️  [{worker_id}] Session {create_mode} (COMPATIBILITY MODE): {session_name} "
                    f"(id={session_id}, type={resource_type}) - Resource type does not require session"
                )
            else:
                logger.info(f"📦 [{worker_id}] Session {create_mode}: {session_name} (id={session_id}, type={resource_type})")
                if auto_created:
                    logger.info(f"   ↳ Note: This session was auto-created when executing command. Use create_session to explicitly create with custom config if needed.")
            
            return session_info
    
    async def get_session(
        self,
        worker_id: str,
        resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get session (does not auto-create)"""
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
        """Update session data"""
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
        Destroy session for specific resource
        
        Returns:
            Destroyed session info, returns None if doesn't exist
        """
        async with self._lock:
            if worker_id in self._routes and resource_type in self._routes[worker_id]:
                session_info = self._routes[worker_id][resource_type]
                session_name = session_info.get("session_name", "unknown")
                session_id = session_info.get("session_id", "unknown")
                
                # Call cleanup callback
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
        """Destroy all sessions for worker"""
        count = 0
        resource_types: List[str] = []
        
        async with self._lock:
            if worker_id in self._routes:
                resource_types = list(self._routes[worker_id].keys())
        
        # Execute cleanup outside lock to avoid deadlock
        for resource_type in resource_types:
            await self.destroy_session(worker_id, resource_type)
            count += 1
        
        async with self._lock:
            if worker_id in self._routes:
                del self._routes[worker_id]
        
        logger.info(f"[{worker_id}] Destroyed all {count} sessions")
        return count
    
    async def list_worker_sessions(self, worker_id: str) -> Dict[str, Dict[str, Any]]:
        """List all sessions for worker"""
        async with self._lock:
            if worker_id in self._routes:
                return dict(self._routes[worker_id])
        return {}
    
    async def list_all_sessions(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """List all sessions"""
        async with self._lock:
            return {wid: dict(sessions) for wid, sessions in self._routes.items()}
    
    async def cleanup_expired(self) -> int:
        """Cleanup expired sessions"""
        now = datetime.utcnow()
        expired_list = []
        
        async with self._lock:
            for worker_id, sessions in self._routes.items():
                for resource_type, session_info in sessions.items():
                    expires_at = datetime.fromisoformat(session_info["expires_at"])
                    if expires_at < now:
                        expired_list.append((worker_id, resource_type))
        
        # Execute cleanup outside lock
        for worker_id, resource_type in expired_list:
            await self.destroy_session(worker_id, resource_type)
        
        return len(expired_list)
    
    async def get_active_resource_types(self, worker_id: str) -> Set[str]:
        """Get currently active resource types for worker"""
        async with self._lock:
            if worker_id in self._routes:
                return set(self._routes[worker_id].keys())
        return set()
    
    async def refresh_session(self, worker_id: str, resource_type: str) -> bool:
        """Refresh session expiration time"""
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

