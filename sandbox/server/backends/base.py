# sandbox/server/backends/base.py
"""
Backend Base Class

Backend is a wrapper for heavyweight resources, providing complete lifecycle interfaces:
- warmup(): Warmup (called when server starts)
- initialize(): Session initialization (optional, decided by developer)
- cleanup(): Session cleanup
- shutdown(): Shutdown (called when server shuts down)

Server is only responsible for:
- Holding Backend instances
- Calling lifecycle high-level interfaces
- Managing Session handles
- Scanning and registering tools

How to implement these interfaces is decided by the developer.

Usage examples:

```python
from sandbox.server.backends import Backend, BackendConfig
from sandbox.server.core import tool

# Example 1: Backend that requires Session (VM)
class VMBackend(Backend):
    name = "vm"
    
    async def warmup(self):
        # Optional: warmup connection pool
        self.pool = await create_pool()
    
    async def initialize(self, worker_id: str, config: dict) -> dict:
        # Create VM for each worker
        controller = await self.pool.create_vm(config)
        return {"controller": controller}
    
    async def cleanup(self, worker_id: str, session_info: dict):
        # Destroy VM
        await session_info["data"]["controller"].close()
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: dict) -> dict:
        return {"image": "..."}


# Example 2: Backend with shared resources (RAG)
class RAGBackend(Backend):
    name = "rag"
    
    async def warmup(self):
        # Load model and index
        self.model = await load_model()
        self.index = await load_index()
    
    # No per-worker initialization needed, use default implementation
    # async def initialize() -> returns {} by default
    # async def cleanup() -> no-op by default
    
    async def shutdown(self):
        await self.model.unload()
    
    @tool("rag:search")
    async def search(self, query: str) -> dict:
        return {"results": self.index.search(query)}
```

Lightweight stateless tools use the @register_api_tool decorator and don't need a backend class.
"""

import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import HTTPServiceServer

logger = logging.getLogger("Backend")


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class BackendConfig:
    """
    Backend configuration
    
    Attributes:
        enabled: Whether the backend is enabled
        default_config: Default configuration (used for initialize)
        description: Backend description
        metadata: Additional metadata
    """
    enabled: bool = True
    default_config: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Backend Base Class
# ============================================================================

class Backend(ABC):
    """
    Backend base class
    
    Provides complete lifecycle interfaces, developer decides which to use:
    
    Lifecycle methods:
    - warmup(): Warmup - called when server starts, load models/establish connection pools, etc.
    - initialize(): Session initialization - create resources for worker
    - cleanup(): Session cleanup - destroy worker resources
    - shutdown(): Shutdown - called when server shuts down, release global resources
    
    Server call flow:
    ```
    Server starts
        │
        ▼
    server.load_backend(backend)      # Register backend and tools
        │
        ▼
    (When executing tools or explicitly called)
        │
        ▼
    backend.warmup()                  # Warmup global resources (auto or explicit trigger)
        │
        ▼
    ┌─────────────────────────────────────────────────────┐
    │  Worker creates Session                              │
    │      │                                               │
    │      ▼                                               │
    │  session_data = backend.initialize(worker_id, cfg)  │
    │      │                                               │
    │      ▼                                               │
    │  session_info["data"] = session_data                │
    │      │                                               │
    │      ▼                                               │
    │  Worker calls tools (tools can access session_info) │
    │      │                                               │
    │      ▼                                               │
    │  backend.cleanup(worker_id, session_info)           │
    └─────────────────────────────────────────────────────┘
        │
        ▼
    backend.shutdown()                # Release global resources
    ```
    
    Class attributes:
        name: Backend name (resource type, e.g., "vm", "rag")
        description: Backend description
        version: Backend version
    """
    
    name: str = "base"
    description: str = "Base Backend"
    version: str = "1.0.0"
    
    def __init__(self, config: Optional[BackendConfig] = None):
        """
        Initialize backend
        
        Args:
            config: Backend configuration
        """
        self.config = config or BackendConfig()
        self._server: Optional["HTTPServiceServer"] = None
    
    # ========================================================================
    # Lifecycle Methods (override as needed)
    # ========================================================================
    
    async def warmup(self):
        """
        Warmup (optional override)
        
        Called when server starts. Used to preload global resources:
        - Load models
        - Establish connection pools
        - Initialize indexes
        
        Example:
        ```python
        async def warmup(self):
            self.model = await load_embedding_model(
                self.config.default_config.get("model_name")
            )
            self.pool = await create_connection_pool(
                self.config.default_config.get("pool_size", 10)
            )
        ```
        """
        pass
    
    async def initialize(self, worker_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session initialization (optional override)
        
        Called when creating a new session for a worker.
        The returned data will be stored in session_info["data"] for tool methods to use.
        
        If the backend doesn't need per-worker resources, this method doesn't need to be overridden.
        
        Args:
            worker_id: Worker ID
            config: Initialization configuration (merged from default config and user config)
            
        Returns:
            Initialization result, stored in session_info["data"]
            
        Example:
        ```python
        async def initialize(self, worker_id: str, config: dict) -> dict:
            # Custom initialization logic
            vm_type = config.get("vm_type", "local")
            
            if vm_type == "local":
                controller = await create_local_vm(config)
            elif vm_type == "docker":
                controller = await create_docker_vm(config)
            elif vm_type == "cloud":
                controller = await self.pool.acquire(config)
            
            return {
                "controller": controller,
                "vm_type": vm_type,
                "created_at": time.time()
            }
        ```
        """
        return {}
    
    async def cleanup(self, worker_id: str, session_info: Dict[str, Any]):
        """
        Session cleanup (optional override)
        
        Called when session is destroyed. Used to release per-worker resources.
        
        If the backend doesn't need per-worker resources, this method doesn't need to be overridden.
        
        Args:
            worker_id: Worker ID
            session_info: Session information (contains resources in data)
            
        Example:
        ```python
        async def cleanup(self, worker_id: str, session_info: dict):
            data = session_info.get("data", {})
            controller = data.get("controller")
            
            if controller:
                await controller.close()
        ```
        """
        pass
    
    async def shutdown(self):
        """
        Shutdown (optional override)
        
        Called when server shuts down. Used to release global resources.
        
        Example:
        ```python
        async def shutdown(self):
            if self.model:
                await self.model.unload()
            if self.pool:
                await self.pool.close()
        ```
        """
        pass
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return self.config.default_config.copy()
    
    def bind_server(self, server: "HTTPServiceServer"):
        """
        Bind server reference
        
        Called by server.load_backend() to establish bidirectional reference.
        
        Args:
            server: HTTP server instance
        """
        self._server = server
    
    def get_info(self) -> Dict[str, Any]:
        """Get backend information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "config": {
                "enabled": self.config.enabled,
                "default_config": self.config.default_config
            }
        }
