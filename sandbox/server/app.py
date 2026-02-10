# sandbox/server/app.py
"""
HTTP Service Server - FastAPI应用

Server 是核心容器和调度器，负责：
- 持有 Backend 实例和无状态工具容器
- 持有工具数据结构（_tools, _tool_name_index, _tool_resource_types）
- 反射扫描 @tool 标记的方法并注册
- 调度请求到对应的工具函数

使用示例:

1. 加载有状态后端：
```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import VMBackend

server = HTTPServiceServer(host="0.0.0.0", port=8080)
server.load_backend(VMBackend())
server.run()
```

2. 注册无状态 API 工具（通过配置加载）：
```python
from sandbox.server.config_loader import create_server_from_config

server = create_server_from_config("configs/profiles/dev.json")
server.run()
# API 工具会自动从配置文件中加载并注册
```

3. 手动注册单个 API 工具：
```python
server.register_api_tool(
    name="search",
    func=my_search_func,
    config={"api_key": "xxx"},
    description="搜索网页"
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
    HTTP Service Server - 核心服务器（持有者 + 调度器）
    
    Server 负责：
    1. 持有 Backend 实例和无状态工具容器
    2. 持有工具数据结构（三层映射）
    3. 调用 Backend 的生命周期接口
    4. 反射扫描 @tool 标记方法并注册
    5. 资源自动管理和 Session 路由
    
    工具数据结构：
    - _tools: Dict[str, Callable] - 完整名称 -> 函数映射
    - _tool_name_index: Dict[str, List[str]] - 简单名称 -> 完整名称列表
    - _tool_resource_types: Dict[str, str] - 完整名称 -> 资源类型
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
        初始化HTTP服务器

        Args:
            host: 绑定地址
            port: 端口
            title: API标题
            description: API描述
            version: API版本
            enable_cors: 是否启用CORS
            session_ttl: Session TTL（秒）
            warmup_resources: 启动时需要预热的资源列表
        """
        self.host = host
        self.port = port
        self.title = title
        self.description = description
        self.version = version
        self.enable_cors = enable_cors

        # 预热配置
        self.warmup_resources = warmup_resources or []

        # ====================================================================
        # 工具数据结构（三层映射，由 Server 持有）
        # ====================================================================
        
        # 层1: 完整名称 -> 函数映射
        # 例如: {"vm:screenshot": func, "search": func}
        self._tools: Dict[str, Callable] = {}
        
        # 层2: 简单名称 -> 完整名称列表（索引）
        # 例如: {"screenshot": ["vm:screenshot"], "search": ["search", "rag:search"]}
        self._tool_name_index: Dict[str, List[str]] = {}
        
        # 层3: 完整名称 -> 资源类型映射
        # 例如: {"vm:screenshot": "vm", "rag:search": "rag"}
        self._tool_resource_types: Dict[str, str] = {}
        
        # ====================================================================
        # 核心组件
        # ====================================================================
        
        self.session_ttl = session_ttl
        self.resource_router = ResourceRouter(session_ttl=session_ttl)
        
        # ToolExecutor 使用 Server 的数据结构引用
        # 使用 lambda 延迟绑定 ensure_backend_warmed_up 方法
        self._executor = ToolExecutor(
            tools=self._tools,
            tool_name_index=self._tool_name_index,
            tool_resource_types=self._tool_resource_types,
            resource_router=self.resource_router,
            warmup_callback=lambda backend_name: self.ensure_backend_warmed_up(backend_name)
        )
        
        # 后端持有
        self._backends: Dict[str, Backend] = {}
        
        # 预热状态跟踪
        self._warmed_up_backends: Dict[str, bool] = {}
        self._warmup_lock = asyncio.Lock()
        
        # FastAPI应用
        self._app: Optional[FastAPI] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    # ========================================================================
    # 工具注册（数据结构操作）
    # ========================================================================
    
    def register_tool(
        self, 
        name: str, 
        func: Callable, 
        resource_type: Optional[str] = None
    ):
        """
        注册工具函数
        
        Args:
            name: 工具名称（可带资源类型前缀如 "vm:screenshot"）
            func: 工具函数
            resource_type: 资源类型
        """
        # 解析名称和资源类型
        simple_name = name
        actual_resource_type = resource_type
        
        if ":" in name:
            parts = name.split(":", 1)
            actual_resource_type = parts[0]
            simple_name = parts[1]
        
        # 构建完整名称
        if actual_resource_type:
            full_name = f"{actual_resource_type}:{simple_name}"
        else:
            full_name = simple_name
        
        # 层1: 存储工具函数映射
        self._tools[full_name] = func
        
        # 层2: 更新简单名称索引
        if simple_name not in self._tool_name_index:
            self._tool_name_index[simple_name] = []
        if full_name not in self._tool_name_index[simple_name]:
            self._tool_name_index[simple_name].append(full_name)
        
        # 层3: 存储资源类型映射
        if actual_resource_type:
            self._tool_resource_types[full_name] = actual_resource_type
        
        logger.info(f"Registered tool: {full_name}" + 
                   (" (stateless)" if not actual_resource_type else ""))
    
    def _resolve_tool(self, action: str):
        """解析工具名称"""
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
        """列出所有已注册的工具"""
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
        """获取工具信息"""
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
    # 工具执行（委托给 ToolExecutor）
    # ========================================================================
    
    async def execute(
        self, 
        action: str, 
        params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            action: 动作名称
            params: 参数
            **kwargs: 运行时参数（worker_id, timeout, trace_id 等）
        """
        return await self._executor.execute(action, params, **kwargs)
    
    async def execute_batch(
        self,
        actions: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量执行工具
        
        Args:
            actions: 动作列表
            **kwargs: 运行时参数（worker_id, parallel, stop_on_error, trace_id 等）
        """
        return await self._executor.execute_batch(actions, **kwargs)
    
    # ========================================================================
    # 反射扫描注册
    # ========================================================================
    
    def scan_and_register(self, obj: Any, prefix: Optional[str] = None) -> List[str]:
        """
        反射扫描对象中的工具并注册
        
        Args:
            obj: 要扫描的对象
            prefix: 可选的名称前缀
            
        Returns:
            已注册的工具名称列表
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
    # 后端和工具加载
    # ========================================================================
    
    def load_backend(self, backend: Backend) -> List[str]:
        """
        加载有状态后端
        
        Args:
            backend: Backend 实例
            
        Returns:
            已注册的工具名称列表
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
        注册单个 API 工具（无状态）
        
        配置已在 register_all_tools 中通过 set_config 注入到 BaseApiTool 实例，
        execute 方法通过 self.get_config() 获取配置。
        
        Args:
            name: 工具名称
            func: 工具函数/实例（BaseApiTool 实例或普通函数）
            config: 工具配置（已通过 set_config 注入，此参数保留用于兼容）
            description: 工具描述
            hidden: 是否隐藏
            
        Example:
            ```python
            class MyTool(BaseApiTool):
                async def execute(self, query: str, **kwargs) -> dict:
                    api_key = self.get_config("api_key")  # 从实例内部获取
                    return {"results": [...]}
            
            # 配置在 register_all_tools 中通过 set_config 注入
            server.register_api_tool(
                name="search",
                func=MyTool(),
                config={"api_key": "xxx"},  # 已注入到实例
                description="搜索网页"
            )
            ```
        """
        # 设置描述（直接在 func 上设置，因为 BaseApiTool 实例是可调用的）
        if description:
            func.__doc__ = ("[HIDDEN] " if hidden else "") + description
        elif func.__doc__:
            func.__doc__ = ("[HIDDEN] " if hidden else "") + func.__doc__
        
        # 直接注册 func（无需 wrapper，配置已通过 set_config 注入到实例）
        self.register_tool(name, func, resource_type=None)
        
        logger.debug(f"Registered API tool: {name}")
    
    def get_backend(self, name: str) -> Optional[Backend]:
        """获取已加载的后端"""
        return self._backends.get(name)
    
    def list_backends(self) -> List[str]:
        """列出所有已加载的后端名称"""
        return list(self._backends.keys())
    
    # ========================================================================
    # 预热管理
    # ========================================================================
    
    async def warmup_backend(self, backend_name: str) -> bool:
        """
        预热单个后端
        
        Args:
            backend_name: 后端名称
            
        Returns:
            是否预热成功
        """
        result = await self.warmup_backend_with_error(backend_name)
        return result["success"]
    
    async def warmup_backend_with_error(self, backend_name: str) -> Dict[str, Any]:
        """
        预热单个后端，返回详细的错误信息
        
        Args:
            backend_name: 后端名称
            
        Returns:
            预热结果字典 {"success": bool, "error": str | None}
        """
        async with self._warmup_lock:
            # 已预热则跳过
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
        预热多个后端，返回详细的错误信息
        
        Args:
            backend_names: 要预热的后端名称列表，为 None 时预热所有已加载的后端
            
        Returns:
            预热结果字典 {backend_name: {"success": bool, "error": str | None}}
        """
        targets = backend_names or list(self._backends.keys())
        results = {}
        
        for name in targets:
            results[name] = await self.warmup_backend_with_error(name)
        
        return results
    
    async def ensure_backend_warmed_up(self, backend_name: str) -> bool:
        """
        确保后端已预热（用于自动预热）
        
        在执行工具时调用，如果后端未预热则自动预热。
        此方法是内部方法，用户无需调用。
        
        Args:
            backend_name: 后端名称
            
        Returns:
            是否预热成功
        """
        if self._warmed_up_backends.get(backend_name):
            return True
        return await self.warmup_backend(backend_name)
    
    def get_warmup_status(self) -> Dict[str, Any]:
        """获取预热状态"""
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
    # 资源类型注册
    # ========================================================================
    
    def register_resource_type(
        self,
        resource_type: str,
        initializer: Optional[Callable] = None,
        cleaner: Optional[Callable] = None,
        default_config: Optional[Dict[str, Any]] = None
    ):
        """注册资源类型"""
        self.resource_router.register_resource_type(
            resource_type, initializer, cleaner, default_config
        )
    
    # ========================================================================
    # FastAPI 应用
    # ========================================================================
    
    def create_app(self) -> FastAPI:
        """创建FastAPI应用"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            logger.info("HTTP Service Server starting...")
            logger.info("Session TTL configured: %ss", self.session_ttl)

            # 执行预热
            if self.warmup_resources:
                logger.info(f"🔥 Starting warmup for resources: {self.warmup_resources}")
                warmup_results = await self.warmup_backends_with_errors(self.warmup_resources)

                # 记录预热结果
                for backend_name, result in warmup_results.items():
                    if result["success"]:
                        logger.info(f"✅ Warmup successful: {backend_name}")
                    else:
                        logger.error(f"❌ Warmup failed: {backend_name} - {result['error']}")

                # 统计预热结果
                success_count = sum(1 for r in warmup_results.values() if r["success"])
                total_count = len(warmup_results)
                logger.info(f"🔥 Warmup completed: {success_count}/{total_count} backends ready")
                failed = {name: info for name, info in warmup_results.items() if not info["success"]}
                if failed:
                    details = "; ".join(
                        f"{name} -> {info.get('error') or 'unknown error'}" for name, info in failed.items()
                    )
                    raise RuntimeError(f"Warmup failed for backends: {details}")
            
            # 预热完成后（无论是否有预热资源），打印服务器就绪提示
            print("=" * 80)
            print("✅ 服务器准备就绪！")
            print(f"🌐 访问地址: http://{self.host}:{self.port}")
            print(f"📖 API 文档: http://{self.host}:{self.port}/docs")
            print(f"🔍 健康检查: http://{self.host}:{self.port}/health")
            print("=" * 80)
            print("\n按 Ctrl+C 停止服务器\n")

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

            # 关闭前清理所有 session，确保 VM/容器等资源释放
            try:
                all_sessions = await self.resource_router.list_all_sessions()
                cleaned_count = 0
                for worker_id in list(all_sessions.keys()):
                    cleaned_count += await self.resource_router.destroy_worker_sessions(worker_id)
                logger.info("Cleaned %s sessions before shutdown", cleaned_count)
            except Exception as exc:
                logger.error("Failed to cleanup sessions before shutdown: %s", exc)

            # 关闭所有 Backend
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
        """启动服务器"""
        import uvicorn
        
        app = self.create_app()
        logger.info(f"Starting HTTP Service Server on {self.host}:{self.port}")
        uvicorn.run(app, host=self.host, port=self.port, **kwargs)

