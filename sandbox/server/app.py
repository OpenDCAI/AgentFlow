# sandbox/server/app.py
"""
HTTP Service Server - FastAPI Application

Server is the core container and scheduler, responsible for:
- Holding Backend instances and stateless tool containers
- Holding tool data structures (_tools, _tool_name_index, _tool_resource_types)
- Reflecting and scanning @tool marked methods and registering them
- Dispatching requests to corresponding tool functions

Usage examples:

1. Load stateful backend:
```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import VMBackend

server = HTTPServiceServer(host="0.0.0.0", port=8080)
server.load_backend(VMBackend())
server.run()
```

2. Register stateless API tools (via config loading):
```python
from sandbox.server.config_loader import create_server_from_config

server = create_server_from_config("configs/profiles/dev.json")
server.run()
# API tools will be automatically loaded and registered from config file
```

3. Manually register a single API tool:
```python
server.register_api_tool(
    name="search",
    func=my_search_func,
    config={"api_key": "xxx"},
    description="Search web pages"
)
```
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List, TYPE_CHECKING
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import ResourceRouter, ToolExecutor, scan_tools
from .backends.base import Backend, BackendConfig
from .routes import register_routes

# Import protocol for endpoints

logger = logging.getLogger("HTTPServiceServer")


class HTTPServiceServer:
    """
    HTTP Service Server - Core server (holder + scheduler)
    
    Server is responsible for:
    1. Holding Backend instances and stateless tool containers
    2. Holding tool data structures (three-layer mapping)
    3. Calling Backend lifecycle interfaces
    4. Reflecting and scanning @tool marked methods and registering them
    5. Automatic resource management and Session routing
    
    Tool data structures:
    - _tools: Dict[str, Callable] - Full name -> function mapping
    - _tool_name_index: Dict[str, List[str]] - Simple name -> full name list
    - _tool_resource_types: Dict[str, str] - Full name -> resource type
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        title: str = "HTTP Service Server",
        description: str = "Independent HTTP Service with JSON protocol",
        version: str = "1.0.0",
        enable_cors: bool = True,
        session_ttl: int = 300,
        warmup_resources: Optional[List[str]] = None
    ):
        """
        Initialize HTTP server

        Args:
            host: Bind address
            port: Port
            title: API title
            description: API description
            version: API version
            enable_cors: Whether to enable CORS
            session_ttl: Session TTL (seconds)
            warmup_resources: List of resources to warmup on startup
        """
        self.host = host
        self.port = port
        self.title = title
        self.description = description
        self.version = version
        self.enable_cors = enable_cors

        # Warmup configuration
        self.warmup_resources = warmup_resources or []

        # ====================================================================
        # Tool data structures (three-layer mapping, held by Server)
        # ====================================================================
        
        # Layer 1: Full name -> function mapping
        # Example: {"vm:screenshot": func, "search": func}
        self._tools: Dict[str, Callable] = {}
        
        # Layer 2: Simple name -> full name list (index)
        # Example: {"screenshot": ["vm:screenshot"], "search": ["search", "rag:search"]}
        self._tool_name_index: Dict[str, List[str]] = {}
        
        # Layer 3: Full name -> resource type mapping
        # Example: {"vm:screenshot": "vm", "rag:search": "rag"}
        self._tool_resource_types: Dict[str, str] = {}
        
        # ====================================================================
        # Core components
        # ====================================================================
        
        self.session_ttl = session_ttl
        self.resource_router = ResourceRouter(session_ttl=session_ttl)
        
        # ToolExecutor uses Server's data structure references
        # Use lambda to delay binding of ensure_backend_warmed_up method
        self._executor = ToolExecutor(
            tools=self._tools,
            tool_name_index=self._tool_name_index,
            tool_resource_types=self._tool_resource_types,
            resource_router=self.resource_router,
            warmup_callback=lambda backend_name: self.ensure_backend_warmed_up(backend_name)
        )
        
        # Backend holder
        self._backends: Dict[str, Backend] = {}
        
        # Warmup status tracking
        self._warmed_up_backends: Dict[str, bool] = {}
        self._warmup_lock = asyncio.Lock()
        
        # FastAPI application
        self._app: Optional[FastAPI] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    # ========================================================================
    # Tool registration (data structure operations)
    # ========================================================================
    
    def register_tool(
        self, 
        name: str, 
        func: Callable, 
        resource_type: Optional[str] = None
    ):
        """
        Register tool function
        
        Args:
            name: Tool name (can include resource type prefix like "vm:screenshot")
            func: Tool function
            resource_type: Resource type
        """
        # Parse name and resource type
        simple_name = name
        actual_resource_type = resource_type
        
        if ":" in name:
            parts = name.split(":", 1)
            actual_resource_type = parts[0]
            simple_name = parts[1]
        
        # Build full name
        if actual_resource_type:
            full_name = f"{actual_resource_type}:{simple_name}"
        else:
            full_name = simple_name
        
        # Layer 1: Store tool function mapping
        self._tools[full_name] = func
        
        # Layer 2: Update simple name index
        if simple_name not in self._tool_name_index:
            self._tool_name_index[simple_name] = []
        if full_name not in self._tool_name_index[simple_name]:
            self._tool_name_index[simple_name].append(full_name)
        
        # Layer 3: Store resource type mapping
        if actual_resource_type:
            self._tool_resource_types[full_name] = actual_resource_type
        
        logger.info(f"Registered tool: {full_name}" + 
                   (" (stateless)" if not actual_resource_type else ""))
    
    def _resolve_tool(self, action: str):
        """Resolve tool name"""
        if action in self._tools:
            resource_type = self._tool_resource_types.get(action)
            simple_name = action.split(":")[-1] if ":" in action else action
            return action, simple_name, resource_type
        
        if ":" in action:
            return None, None, None
        
        if action in self._tool_name_index:
            candidates = self._tool_name_index[action]
            if len(candidates) == 1:
                full_name = candidates[0]
                resource_type = self._tool_resource_types.get(full_name)
                return full_name, action, resource_type
        
        return None, None, None
    
    def list_tools(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """List all registered tools"""
        tools = []
        for full_name, func in self._tools.items():
            resource_type = self._tool_resource_types.get(full_name)
            simple_name = full_name.split(":")[-1] if ":" in full_name else full_name
            
            doc = func.__doc__ or ""
            if not include_hidden and doc.startswith("[HIDDEN]"):
                continue
            
            tools.append({
                "name": simple_name,
                "full_name": full_name,
                "resource_type": resource_type,
                "stateless": resource_type is None,
                "description": doc.strip() if doc else ""
            })
        return tools
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool information"""
        full_name, simple_name, resource_type = self._resolve_tool(name)
        
        if not full_name or full_name not in self._tools:
            return None
        
        func = self._tools[full_name]
        
        return {
            "name": simple_name,
            "full_name": full_name,
            "resource_type": resource_type,
            "stateless": resource_type is None,
            "description": (func.__doc__ or "").strip()
        }
    
    # ========================================================================
    # Tool execution (delegated to ToolExecutor)
    # ========================================================================
    
    async def execute(
        self, 
        action: str, 
        params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute tool
        
        Args:
            action: Action name
            params: Parameters
            **kwargs: Runtime parameters (worker_id, timeout, trace_id, etc.)
        """
        return await self._executor.execute(action, params, **kwargs)
    
    async def execute_batch(
        self,
        actions: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute tools in batch
        
        Args:
            actions: Action list
            **kwargs: Runtime parameters (worker_id, parallel, stop_on_error, trace_id, etc.)
        """
        return await self._executor.execute_batch(actions, **kwargs)
    
    # ========================================================================
    # Reflection scanning and registration
    # ========================================================================
    
    def scan_and_register(self, obj: Any, prefix: Optional[str] = None) -> List[str]:
        """
        Reflectively scan tools in object and register them
        
        Args:
            obj: Object to scan
            prefix: Optional name prefix
            
        Returns:
            List of registered tool names
        """
        registered = []
        tools = scan_tools(obj, prefix)
        
        for tool_info in tools:
            name = tool_info["name"]
            func = tool_info["func"]
            resource_type = tool_info.get("resource_type")
            
            self.register_tool(name, func, resource_type=resource_type)
            registered.append(name)
        
        if registered:
            logger.info(f"Scanned and registered {len(registered)} tools: {registered}")
        
        return registered
    
    # ========================================================================
    # Backend and tool loading
    # ========================================================================
    
    def load_backend(self, backend: Backend) -> List[str]:
        """
        Load stateful backend
        
        Args:
            backend: Backend instance
            
        Returns:
            List of registered tool names
        """
        backend.bind_server(self)
        self._backends[backend.name] = backend
        
        self.register_resource_type(
            resource_type=backend.name,
            initializer=backend.initialize,
            cleaner=backend.cleanup,
            default_config=backend.get_default_config()
        )
        
        registered = self.scan_and_register(backend, prefix=backend.name)

        logger.info(f"✅ Backend loaded: {backend.name} ({len(registered)} tools)")
        return registered

    def register_api_tool(
        self,
        name: str,
        func: Callable,
        config: Dict[str, Any],
        description: Optional[str] = None,
        hidden: bool = False
    ):
        """
        Register a single API tool (stateless)
        
        Configuration has been injected into BaseApiTool instance via set_config in register_all_tools,
        execute method gets configuration through self.get_config().
        
        Args:
            name: Tool name
            func: Tool function/instance (BaseApiTool instance or regular function)
            config: Tool configuration (already injected via set_config, this parameter kept for compatibility)
            description: Tool description
            hidden: Whether to hide
            
        Example:
            ```python
            class MyTool(BaseApiTool):
                async def execute(self, query: str, **kwargs) -> dict:
                    api_key = self.get_config("api_key")  # Get from instance internally
                    return {"results": [...]}
            
            # Configuration injected via set_config in register_all_tools
            server.register_api_tool(
                name="search",
                func=MyTool(),
                config={"api_key": "xxx"},  # Already injected into instance
                description="Search web pages"
            )
            ```
        """
        # Set description (directly on func, since BaseApiTool instance is callable)
        if description:
            func.__doc__ = ("[HIDDEN] " if hidden else "") + description
        elif func.__doc__:
            func.__doc__ = ("[HIDDEN] " if hidden else "") + func.__doc__
        
        # Directly register func (no wrapper needed, config already injected into instance via set_config)
        self.register_tool(name, func, resource_type=None)
        
        logger.debug(f"Registered API tool: {name}")
    
    def get_backend(self, name: str) -> Optional[Backend]:
        """Get loaded backend"""
        return self._backends.get(name)
    
    def list_backends(self) -> List[str]:
        """List all loaded backend names"""
        return list(self._backends.keys())
    
    # ========================================================================
    # Warmup management
    # ========================================================================
    
    async def warmup_backend(self, backend_name: str) -> bool:
        """
        Warmup a single backend
        
        Args:
            backend_name: Backend name
            
        Returns:
            Whether warmup succeeded
        """
        result = await self.warmup_backend_with_error(backend_name)
        return result["success"]
    
    async def warmup_backend_with_error(self, backend_name: str) -> Dict[str, Any]:
        """
        Warmup a single backend, return detailed error information
        
        Args:
            backend_name: Backend name
            
        Returns:
            Warmup result dictionary {"success": bool, "error": str | None}
        """
        async with self._warmup_lock:
            # Skip if already warmed up
            if self._warmed_up_backends.get(backend_name):
                return {"success": True, "error": None}
            
            backend = self._backends.get(backend_name)
            if not backend:
                error_msg = f"Backend not found: {backend_name}. Available backends: {list(self._backends.keys())}"
                logger.warning(error_msg)
                return {"success": False, "error": error_msg}
            
            try:
                logger.info(f"🔥 Warming up backend: {backend_name}")
                await backend.warmup()
                self._warmed_up_backends[backend_name] = True
                logger.info(f"✅ Backend warmed up: {backend_name}")
                return {"success": True, "error": None}
            except Exception as e:
                import traceback
                error_msg = f"Warmup exception: {str(e)}\n{traceback.format_exc()}"
                logger.error(f"❌ Warmup failed for {backend_name}: {error_msg}")
                return {"success": False, "error": error_msg}
    
    async def warmup_backends_with_errors(self, backend_names: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Warmup multiple backends, return detailed error information
        
        Args:
            backend_names: List of backend names to warmup, None means warmup all loaded backends
            
        Returns:
            Warmup result dictionary {backend_name: {"success": bool, "error": str | None}}
        """
        targets = backend_names or list(self._backends.keys())
        results = {}
        
        for name in targets:
            results[name] = await self.warmup_backend_with_error(name)
        
        return results
    
    async def ensure_backend_warmed_up(self, backend_name: str) -> bool:
        """
        Ensure backend is warmed up (for automatic warmup)
        
        Called when executing tools, automatically warms up backend if not already warmed up.
        This is an internal method, users don't need to call it.
        
        Args:
            backend_name: Backend name
            
        Returns:
            Whether warmup succeeded
        """
        if self._warmed_up_backends.get(backend_name):
            return True
        return await self.warmup_backend(backend_name)
    
    def get_warmup_status(self) -> Dict[str, Any]:
        """Get warmup status"""
        return {
            "backends": {
                name: {
                    "loaded": True,
                    "warmed_up": self._warmed_up_backends.get(name, False)
                }
                for name in self._backends.keys()
            },
            "summary": {
                "total": len(self._backends),
                "warmed_up": sum(1 for v in self._warmed_up_backends.values() if v),
                "pending": len(self._backends) - sum(1 for v in self._warmed_up_backends.values() if v)
            }
        }
    
    # ========================================================================
    # Resource type registration
    # ========================================================================
    
    def register_resource_type(
        self,
        resource_type: str,
        initializer: Optional[Callable] = None,
        cleaner: Optional[Callable] = None,
        default_config: Optional[Dict[str, Any]] = None
    ):
        """Register resource type"""
        self.resource_router.register_resource_type(
            resource_type, initializer, cleaner, default_config
        )
    
    # ========================================================================
    # FastAPI application
    # ========================================================================
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            logger.info("HTTP Service Server starting...")
            logger.info("Session TTL configured: %ss", self.session_ttl)

            # Execute warmup
            if self.warmup_resources:
                logger.info(f"🔥 Starting warmup for resources: {self.warmup_resources}")
                warmup_results = await self.warmup_backends_with_errors(self.warmup_resources)

                # Record warmup results
                for backend_name, result in warmup_results.items():
                    if result["success"]:
                        logger.info(f"✅ Warmup successful: {backend_name}")
                    else:
                        logger.error(f"❌ Warmup failed: {backend_name} - {result['error']}")

                # Count warmup results
                success_count = sum(1 for r in warmup_results.values() if r["success"])
                total_count = len(warmup_results)
                logger.info(f"🔥 Warmup completed: {success_count}/{total_count} backends ready")
                failed = {name: info for name, info in warmup_results.items() if not info["success"]}
                if failed:
                    details = "; ".join(
                        f"{name} -> {info.get('error') or 'unknown error'}" for name, info in failed.items()
                    )
                    raise RuntimeError(f"Warmup failed for backends: {details}")
            
            # After warmup completes (regardless of whether there are warmup resources), print server ready message
            print("=" * 80)
            print("✅ Server ready!")
            print(f"🌐 Access URL: http://{self.host}:{self.port}")
            print(f"📖 API Docs: http://{self.host}:{self.port}/docs")
            print(f"🔍 Health Check: http://{self.host}:{self.port}/health")
            print("=" * 80)
            print("\nPress Ctrl+C to stop the server\n")

            async def cleanup_task():
                while True:
                    await asyncio.sleep(300)
                    cleaned = await self.resource_router.cleanup_expired()
                    if cleaned > 0:
                        logger.info(f"Cleaned {cleaned} expired sessions")

            self._cleanup_task = asyncio.create_task(cleanup_task())

            yield

            logger.info("HTTP Service Server shutting down...")
            if self._cleanup_task:
                self._cleanup_task.cancel()

            # Cleanup all sessions before shutdown to ensure VM/container resources are released
            try:
                all_sessions = await self.resource_router.list_all_sessions()
                cleaned_count = 0
                for worker_id in list(all_sessions.keys()):
                    cleaned_count += await self.resource_router.destroy_worker_sessions(worker_id)
                logger.info("Cleaned %s sessions before shutdown", cleaned_count)
            except Exception as exc:
                logger.error("Failed to cleanup sessions before shutdown: %s", exc)

            # Shutdown all Backends
            logger.info("Shutting down all backends...")
            for backend_name in list(self._backends.keys()):
                backend = self._backends.get(backend_name)
                if backend:
                    try:
                        logger.info(f"Shutting down backend: {backend_name}")
                        await backend.shutdown()
                        logger.info(f"Backend {backend_name} shutdown complete")
                    except Exception as e:
                        logger.error(f"Failed to shutdown {backend_name}: {e}")
        
        app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            lifespan=lifespan
        )
        
        if self.enable_cors:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # 使用独立的路由模块
        register_routes(app, self)
        
        self._app = app
        return app
    
    def run(self, **kwargs):
        """Start server"""
        import uvicorn
        
        app = self.create_app()
        logger.info(f"Starting HTTP Service Server on {self.host}:{self.port}")
        uvicorn.run(app, host=self.host, port=self.port, **kwargs)

