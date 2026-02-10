# sandbox/__init__.py
"""
HTTP Service Module - 独立的HTTP服务模块

此模块提供基于HTTP协议的服务端和客户端实现，完全独立于MCP Server。

特点：
- Session自动命名：自动生成可读的session名称（如 vm_abc123_001）
- 灵活的Session管理：支持显式创建/销毁，也支持自动创建（会在日志中提示）
- Session路由表：自动维护 worker_id -> resource_type -> session 映射

模块结构:
- protocol.py: HTTP协议定义和消息格式
- server.py: HTTP服务端实现（含ResourceRouter资源路由表）
- client.py: HTTP客户端实现

使用方式:

1. 服务端:
    from sandbox import HTTPServiceServer
    
    server = HTTPServiceServer(host="0.0.0.0", port=8080)
    
    # 加载后端（会自动扫描 @tool 装饰的方法并注册资源类型）
    server.load_backend(vm_backend)
    
    server.run()

2. 客户端 - 显式Session管理（推荐，可自定义配置）:
    from sandbox import HTTPServiceClient
    
    async with HTTPServiceClient(base_url="http://localhost:8080") as client:
        # 显式创建session
        result = await client.create_session("rag", {"top_k": 10})
        print(f"Session created: {result['session_name']}")
        
        # 执行命令
        result = await client.execute("rag:search", {"query": "test"})
        
        # 显式销毁session
        await client.destroy_session("rag")

3. 客户端 - 自动Session管理（快捷，日志会提示）:
    async with HTTPServiceClient(base_url="http://localhost:8080") as client:
        # 直接执行，没有session时会自动创建（日志提示）
        result = await client.execute("vm:screenshot", {})
        
        # 查看自动创建的session
        sessions = await client.list_sessions()
        
        # 完成后显式销毁
        await client.destroy_session("vm")
"""

from .protocol import (
    MessageType,
    ResourceType,
    HTTPEndpoints,
    BaseMessage,
    Response,
    ExecuteRequest,
    ExecuteBatchRequest,
    LifecycleAllocateRequest,
    LifecycleReleaseRequest,
    SessionCreateRequest,
    SessionDestroyRequest,
    InitResourceRequest,
    InitBatchRequest,
    parse_message,
    create_execute_request,
)

from .server import (
    HTTPServiceServer,
    ToolExecutor,
    ResourceRouter,
    create_server_from_config,
)

# 新的模块化后端（可选导入）
try:
    from .server.backends import Backend, BackendConfig
    from .server.backends.base import StatelessBackend
except ImportError:
    pass

from .client import (
    HTTPServiceClient,
    HTTPClientConfig,
    HTTPClientError,
    quick_execute,
    create_client,
)

from .sandbox import (
    Sandbox,
    SandboxConfig,
    SandboxError,
    SandboxConnectionError,
    SandboxServerStartError,
    DEFAULT_SERVER_CONFIG,
    create_sandbox,
    get_default_config,
)

from .result_formatter import (
    ToolResult,
    BashResult,
    CodeExecutionResult,
    VMResult,
    BrowserResult,
    WebSearchResult,
    VisitResult,
    RAGSearchResult,
    ResultFormatter,
    format_tool_result,
)

__version__ = "1.0.0"
__all__ = [
    # Protocol
    "MessageType",
    "ResourceType",
    "HTTPEndpoints",
    "BaseMessage",
    "Response",
    "ExecuteRequest",
    "ExecuteBatchRequest",
    "LifecycleAllocateRequest",
    "LifecycleReleaseRequest",
    "SessionCreateRequest",
    "SessionDestroyRequest",
    "InitResourceRequest",
    "InitBatchRequest",
    "parse_message",
    "create_execute_request",
    # Server
    "HTTPServiceServer",
    "ToolExecutor",
    "ResourceRouter",
    "create_server_from_config",
    # Client
    "HTTPServiceClient",
    "HTTPClientConfig",
    "HTTPClientError",
    "quick_execute",
    "create_client",
    # Sandbox (Facade)
    "Sandbox",
    "SandboxConfig",
    "SandboxError",
    "SandboxConnectionError",
    "SandboxServerStartError",
    "DEFAULT_SERVER_CONFIG",
    "create_sandbox",
    "get_default_config",
    # Result Formatter
    "ToolResult",
    "BashResult",
    "CodeExecutionResult",
    "VMResult",
    "BrowserResult",
    "WebSearchResult",
    "VisitResult",
    "RAGSearchResult",
    "ResultFormatter",
    "format_tool_result",
]
