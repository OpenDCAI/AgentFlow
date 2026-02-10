# sandbox/server/backends/base.py
"""
后端基类

Backend 是重量级资源的封装，提供完整的生命周期接口：
- warmup(): 预热（服务器启动时）
- initialize(): Session 初始化（可选，由开发者决定是否使用）
- cleanup(): Session 清理
- shutdown(): 关闭（服务器关闭时）

Server 只负责：
- 持有 Backend 实例
- 调用生命周期高级接口
- 管理 Session 句柄
- 扫描注册工具

具体如何实现这些接口由开发者决定。

使用示例：

```python
from sandbox.server.backends import Backend, BackendConfig
from sandbox.server.core import tool

# 示例1: 需要 Session 的后端（VM）
class VMBackend(Backend):
    name = "vm"
    
    async def warmup(self):
        # 可选：预热连接池
        self.pool = await create_pool()
    
    async def initialize(self, worker_id: str, config: dict) -> dict:
        # 为每个 worker 创建 VM
        controller = await self.pool.create_vm(config)
        return {"controller": controller}
    
    async def cleanup(self, worker_id: str, session_info: dict):
        # 销毁 VM
        await session_info["data"]["controller"].close()
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: dict) -> dict:
        return {"image": "..."}


# 示例2: 共享资源的后端（RAG）
class RAGBackend(Backend):
    name = "rag"
    
    async def warmup(self):
        # 加载模型和索引
        self.model = await load_model()
        self.index = await load_index()
    
    # 不需要 per-worker 初始化，使用默认实现
    # async def initialize() -> 默认返回 {}
    # async def cleanup() -> 默认空操作
    
    async def shutdown(self):
        await self.model.unload()
    
    @tool("rag:search")
    async def search(self, query: str) -> dict:
        return {"results": self.index.search(query)}
```

轻量级无状态工具使用 @register_api_tool 装饰器，不需要后端类。
"""

import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import HTTPServiceServer

logger = logging.getLogger("Backend")


# ============================================================================
# 配置
# ============================================================================

@dataclass
class BackendConfig:
    """
    后端配置
    
    Attributes:
        enabled: 是否启用
        default_config: 默认配置（用于 initialize）
        description: 后端描述
        metadata: 额外元数据
    """
    enabled: bool = True
    default_config: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 后端基类
# ============================================================================

class Backend(ABC):
    """
    后端基类
    
    提供完整的生命周期接口，由开发者决定使用哪些：
    
    生命周期方法：
    - warmup(): 预热 - 服务器启动时调用，加载模型/建立连接池等
    - initialize(): Session 初始化 - 为 worker 创建资源
    - cleanup(): Session 清理 - 销毁 worker 资源
    - shutdown(): 关闭 - 服务器关闭时调用，释放全局资源
    
    Server 调用流程：
    ```
    Server 启动
        │
        ▼
    server.load_backend(backend)      # 注册后端和工具
        │
        ▼
    (执行工具时或显式调用)
        │
        ▼
    backend.warmup()                  # 预热全局资源（自动或显式触发）
        │
        ▼
    ┌─────────────────────────────────────────────────────┐
    │  Worker 创建 Session                                 │
    │      │                                               │
    │      ▼                                               │
    │  session_data = backend.initialize(worker_id, cfg)  │
    │      │                                               │
    │      ▼                                               │
    │  session_info["data"] = session_data                │
    │      │                                               │
    │      ▼                                               │
    │  Worker 调用工具（工具可访问 session_info）           │
    │      │                                               │
    │      ▼                                               │
    │  backend.cleanup(worker_id, session_info)           │
    └─────────────────────────────────────────────────────┘
        │
        ▼
    backend.shutdown()                # 释放全局资源
    ```
    
    类属性:
        name: 后端名称（资源类型，如 "vm", "rag"）
        description: 后端描述
        version: 后端版本
    """
    
    name: str = "base"
    description: str = "Base Backend"
    version: str = "1.0.0"
    
    def __init__(self, config: Optional[BackendConfig] = None):
        """
        初始化后端
        
        Args:
            config: 后端配置
        """
        self.config = config or BackendConfig()
        self._server: Optional["HTTPServiceServer"] = None
    
    # ========================================================================
    # 生命周期方法（按需覆盖）
    # ========================================================================
    
    async def warmup(self):
        """
        预热（可选覆盖）
        
        在服务器启动时调用。用于预加载全局资源：
        - 加载模型
        - 建立连接池
        - 初始化索引
        
        示例：
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
        Session 初始化（可选覆盖）
        
        当为 worker 创建新 session 时调用。
        返回的数据将存储在 session_info["data"] 中，供工具方法使用。
        
        如果后端不需要 per-worker 资源，可以不覆盖此方法。
        
        Args:
            worker_id: Worker ID
            config: 初始化配置（合并了默认配置和用户配置）
            
        Returns:
            初始化结果，存储在 session_info["data"]
            
        示例：
        ```python
        async def initialize(self, worker_id: str, config: dict) -> dict:
            # 自定义初始化逻辑
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
        Session 清理（可选覆盖）
        
        当 session 被销毁时调用。用于释放 per-worker 资源。
        
        如果后端不需要 per-worker 资源，可以不覆盖此方法。
        
        Args:
            worker_id: Worker ID
            session_info: Session 信息（包含 data 中的资源）
            
        示例：
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
        关闭（可选覆盖）
        
        在服务器关闭时调用。用于释放全局资源。
        
        示例：
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
    # 辅助方法
    # ========================================================================
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return self.config.default_config.copy()
    
    def bind_server(self, server: "HTTPServiceServer"):
        """
        绑定服务器引用
        
        由 server.load_backend() 调用，建立双向引用。
        
        Args:
            server: HTTP 服务器实例
        """
        self._server = server
    
    def get_info(self) -> Dict[str, Any]:
        """获取后端信息"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "config": {
                "enabled": self.config.enabled,
                "default_config": self.config.default_config
            }
        }
