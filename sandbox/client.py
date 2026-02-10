# sandbox/client.py
"""
HTTP Service Client - 独立的HTTP客户端实现

基于HTTP协议的客户端实现模板，完全独立于MCP Server。

特点：
- Session自动命名：Server自动生成可读的session名称（如 vm_abc123_001）
- 灵活管理：支持显式创建/销毁session，也支持自动创建（会在日志中提示）
- 显式释放：session需要显式调用destroy_session销毁

功能:
1. Session管理 - create_session/destroy_session/list_sessions
2. 执行信息 - 支持资源类型前缀 (如 vm:action)
3. 初始化 - 资源配置初始化
4. 工具查询 - 列出可用工具

使用示例 - 方式1: 显式Session管理（推荐）:
```python
async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # 显式创建session，使用自定义配置
    result = await client.create_session("rag", {"top_k": 10})
    print(f"Session: {result['session_name']}")  # 如: rag_abc123_001
    
    # 执行命令
    result = await client.execute("rag:search", {"query": "test"})
    
    # 显式销毁session
    await client.destroy_session("rag")
```

使用示例 - 方式2: 自动Session创建（快捷）:
```python
async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # 直接执行，没有session时会自动创建（Server日志会提示）
    result = await client.execute("vm:screenshot", {})
    
    # 查看session
    sessions = await client.list_sessions()
    
    # 完成后显式销毁
    await client.destroy_session("vm")
```
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import uuid

import httpx

from .protocol import HTTPEndpoints

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HTTPServiceClient")


# ============================================================================
# Client Configuration
# ============================================================================

@dataclass
class HTTPClientConfig:
    """客户端配置"""
    base_url: str = "http://localhost:8080"
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    auto_heartbeat: bool = True
    heartbeat_interval: float = 30.0
    worker_id: Optional[str] = None  # 自动生成如果为None
    
    def __post_init__(self):
        if not self.worker_id:
            self.worker_id = f"worker_{uuid.uuid4().hex[:8]}"


# ============================================================================
# Exception Classes
# ============================================================================

class HTTPClientError(Exception):
    """HTTP客户端错误"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


# ============================================================================
# HTTP Service Client
# ============================================================================

class HTTPServiceClient:
    """
    HTTP Service Client - 独立的HTTP客户端
    
    资源由Server自动管理，客户端只需要执行命令。
    
    使用示例:
    ```python
    async with HTTPServiceClient(base_url="http://localhost:8080") as client:
        # 直接执行，server自动管理资源session
        result = await client.execute("vm:screenshot", {})
        result = await client.execute("rag:search", {"query": "test"})
        
        # 批量执行
        results = await client.execute_batch([
            {"action": "vm:click", "params": {"x": 100, "y": 200}},
            {"action": "vm:screenshot", "params": {}},
        ])
    ```
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8080",
        worker_id: Optional[str] = None,
        timeout: float = 60.0,
        config: Optional[HTTPClientConfig] = None
    ):
        """
        初始化客户端
        
        Args:
            base_url: 服务器地址
            worker_id: Worker ID，用于资源隔离（自动生成如果不提供）
            timeout: 默认超时时间
            config: 完整配置对象（优先级高于其他参数）
        """
        if config:
            self.config = config
        else:
            self.config = HTTPClientConfig(
                base_url=base_url,
                timeout=timeout,
                worker_id=worker_id
            )
        
        self._client: Optional[httpx.AsyncClient] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._closed = False
    
    @property
    def worker_id(self) -> str:
        # worker_id is always set in __post_init__ if None
        return self.config.worker_id or ""
    
    @property
    def base_url(self) -> str:
        return self.config.base_url.rstrip("/")
    
    async def __aenter__(self) -> "HTTPServiceClient":
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        """建立连接"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.config.timeout,
                headers={
                    "Content-Type": "application/json",
                    "X-Worker-ID": self.worker_id
                }
            )
        
        # _client is guaranteed to be set after the block above
        assert self._client is not None
        
        # 检查服务器健康状态
        try:
            response = await self._client.get(HTTPEndpoints.HEALTH)
            if response.status_code != 200:
                raise ConnectionError(f"Server health check failed: {response.status_code}")
            logger.info(f"Connected to HTTP Service at {self.base_url} (worker_id: {self.worker_id})")
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            raise
        
        # 启动心跳任务
        if self.config.auto_heartbeat:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def close(self, destroy_sessions: bool = False):
        """
        关闭连接
        
        Args:
            destroy_sessions: 是否销毁所有session（默认False，需要显式调用）
        """
        if self._closed:
            return
        
        self._closed = True
        
        # 停止心跳
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # 如果指定了销毁session
        if destroy_sessions:
            try:
                await self._request("POST", "/api/v1/worker/disconnect", {
                    "worker_id": self.worker_id
                })
                logger.info(f"🗑️ [{self.worker_id}] All sessions destroyed on close")
            except Exception as e:
                logger.warning(f"Failed to destroy sessions on close: {e}")
        
        # 关闭HTTP客户端
        if self._client:
            await self._client.aclose()
            self._client = None
        
        logger.info(f"HTTPServiceClient closed (worker_id: {self.worker_id})")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
    
    async def _send_heartbeat(self):
        """发送心跳"""
        await self._request("POST", HTTPEndpoints.HEARTBEAT, {
            "worker_id": self.worker_id
        })
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            timeout: 超时时间
            
        Returns:
            响应数据
        """
        if self._client is None:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        request_timeout = timeout or self.config.timeout
        
        for attempt in range(self.config.max_retries):
            try:
                if method.upper() == "GET":
                    response = await self._client.get(endpoint, timeout=request_timeout)
                else:
                    response = await self._client.post(
                        endpoint, 
                        json=data,
                        timeout=request_timeout
                    )
                
                result = response.json()
                
                if response.status_code >= 400:
                    error_msg = result.get("message") or result.get("error") or str(result)
                    raise HTTPClientError(
                        f"Request failed: {error_msg}",
                        status_code=response.status_code,
                        response=result
                    )
                
                return result
                
            except httpx.TimeoutException:
                if attempt == self.config.max_retries - 1:
                    raise HTTPClientError(f"Request timed out after {self.config.max_retries} attempts")
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                
            except httpx.HTTPError as e:
                if attempt == self.config.max_retries - 1:
                    raise HTTPClientError(f"HTTP error: {e}")
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        # Should not reach here, but for type checker
        raise HTTPClientError("Request failed after all retries")
    
    # ========================================================================
    # 执行 API
    # ========================================================================
    
    async def execute(
        self, 
        action: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行工具/动作
        
        Server会根据action的资源类型前缀自动管理session。
        例如 "vm:screenshot" 会自动创建/获取vm类型的session。
        
        Args:
            action: 动作名称，支持资源类型前缀如 "vm:screenshot", "rag:search"
            params: 动作参数
            timeout: 执行超时
            
        Returns:
            执行结果
            
        Example:
            ```python
            # 带资源类型前缀 - server自动管理session
            result = await client.execute("vm:screenshot", {})
            result = await client.execute("rag:search", {"query": "test"})
            
            # 不带前缀的普通工具
            result = await client.execute("echo", {"message": "hello"})
            ```
        """
        return await self._request("POST", HTTPEndpoints.EXECUTE, {
            "worker_id": self.worker_id,
            "action": action,
            "params": params or {},
            "timeout": timeout
        }, timeout=timeout)
    
    async def execute_batch(
        self,
        actions: List[Dict[str, Any]],
        parallel: bool = False,
        stop_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        批量执行动作
        
        Args:
            actions: 动作列表，每个动作格式: {"action": "name", "params": {...}}
            parallel: 是否并行执行
            stop_on_error: 遇到错误是否停止
            
        Returns:
            批量执行结果
            
        Example:
            ```python
            results = await client.execute_batch([
                {"action": "vm:screenshot", "params": {}},
                {"action": "vm:click", "params": {"x": 100, "y": 200}},
                {"action": "rag:search", "params": {"query": "test"}},
            ], parallel=False)
            ```
        """
        return await self._request("POST", HTTPEndpoints.EXECUTE_BATCH, {
            "worker_id": self.worker_id,
            "actions": actions,
            "parallel": parallel,
            "stop_on_error": stop_on_error
        })
    
    # ========================================================================
    # 状态查询 API
    # ========================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取当前worker的状态
        
        Returns:
            包含活跃资源、session信息等
        """
        return await self._request("POST", HTTPEndpoints.STATUS, {
            "worker_id": self.worker_id
        })
    
    # ========================================================================
    # Session管理 API（显式操作）
    # ========================================================================
    
    async def create_session(
        self,
        resource_type: str,
        session_config: Optional[Dict[str, Any]] = None,
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        显式创建Session
        
        用于预先创建session或使用自定义配置。
        如果不调用此方法，执行命令时会自动创建session（会有日志提示）。
        
        Args:
            resource_type: 资源类型（如 "vm", "rag"）
            session_config: session配置
            custom_name: 自定义session名称（可选）
            
        Returns:
            创建结果，包含session_id和session_name
            
        Example:
            ```python
            # 显式创建session，使用自定义配置
            result = await client.create_session("rag", {"top_k": 10})
            print(f"Session created: {result['session_name']}")
            
            # 后续执行命令会使用这个session
            result = await client.execute("rag:search", {"query": "test"})
            ```
        """
        return await self._request("POST", HTTPEndpoints.SESSION_CREATE, {
            "worker_id": self.worker_id,
            "resource_type": resource_type,
            "session_config": session_config or {},
            "custom_name": custom_name
        })
    
    async def destroy_session(self, resource_type: str) -> Dict[str, Any]:
        """
        显式销毁Session
        
        释放指定资源类型的session。
        
        Args:
            resource_type: 资源类型（如 "vm", "rag"）
            
        Returns:
            销毁结果
            
        Example:
            ```python
            # 销毁vm资源的session
            result = await client.destroy_session("vm")
            print(f"Session destroyed: {result['session_name']}")
            ```
        """
        return await self._request("POST", HTTPEndpoints.SESSION_DESTROY, {
            "worker_id": self.worker_id,
            "resource_type": resource_type
        })
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        列出当前worker的所有session
        
        Returns:
            session列表，每个session包含resource_type, session_id, session_name等
        """
        result = await self._request("POST", HTTPEndpoints.SESSION_LIST, {
            "worker_id": self.worker_id
        })
        # Response uses Code/Message/Data/Meta wrapper; sessions live in data.sessions.
        if isinstance(result, dict):
            data = result.get("data", {})
            if isinstance(data, dict) and isinstance(data.get("sessions"), list):
                return data.get("sessions", [])
        return []
    
    async def destroy_all_sessions(self) -> Dict[str, Any]:
        """
        销毁当前worker的所有session
        
        Returns:
            销毁结果
        """
        return await self._request("POST", "/api/v1/worker/disconnect", {
            "worker_id": self.worker_id
        })
    
    async def refresh_session(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        刷新Session的存活时间（保活）
        
        每次执行 action 时会自动刷新，此方法用于显式保活。
        
        Args:
            resource_type: 资源类型（可选）
                - 指定时只刷新该资源的session
                - 不指定时刷新所有session
                
        Returns:
            刷新结果
            
        Example:
            ```python
            # 刷新特定资源的session
            result = await client.refresh_session("vm")
            print(f"VM session expires at: {result['expires_at']}")
            
            # 刷新所有session
            result = await client.refresh_session()
            print(f"Refreshed {result['refreshed_count']} sessions")
            ```
        """
        data = {"worker_id": self.worker_id}
        if resource_type:
            data["resource_type"] = resource_type
        return await self._request("POST", HTTPEndpoints.SESSION_REFRESH, data)
    
    # ========================================================================
    # 初始化 API（可选，用于预加载或自定义配置）
    # ========================================================================
    
    async def init_resource(
        self,
        resource_type: str,
        init_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        预初始化资源（可选）
        
        通常不需要调用此方法，server会在第一次执行相关命令时自动初始化。
        此方法用于：
        1. 预加载资源（减少首次执行延迟）
        2. 使用自定义配置初始化
        
        Args:
            resource_type: 资源类型
            init_config: 初始化配置（JSON数据）
            
        Returns:
            初始化结果
            
        Example:
            ```python
            # 预初始化rag资源，使用自定义配置
            result = await client.init_resource("rag", {
                "index_path": "/path/to/index",
                "top_k": 10
            })
            ```
        """
        return await self._request("POST", HTTPEndpoints.INIT_RESOURCE, {
            "worker_id": self.worker_id,
            "resource_type": resource_type,
            "init_config": init_config or {}
        })
    
    async def init_batch(
        self,
        resource_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量预初始化资源
        
        Args:
            resource_configs: 资源配置字典
            
        Returns:
            批量初始化结果
            
        Example:
            ```python
            result = await client.init_batch({
                "rag": {"content": {"index_path": "...", "top_k": 10}},
                "vm": {"content": {"screen_size": [1920, 1080]}}
            })
            ```
        """
        return await self._request("POST", HTTPEndpoints.INIT_BATCH, {
            "worker_id": self.worker_id,
            "resource_configs": resource_configs
        })
    
    async def init_from_config(
        self,
        config_path: str,
        override_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        从配置文件初始化
        
        Args:
            config_path: 配置文件路径（服务器端路径）
            override_params: 覆盖参数
            
        Returns:
            初始化结果
        """
        return await self._request("POST", HTTPEndpoints.INIT_FROM_CONFIG, {
            "worker_id": self.worker_id,
            "config_path": config_path,
            "override_params": override_params or {}
        })
    
    # ========================================================================
    # 工具信息 API
    # ========================================================================
    
    async def list_tools(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """列出所有可用工具"""
        result = await self._request("GET", f"{HTTPEndpoints.TOOLS_LIST}?include_hidden={include_hidden}")
        return result.get("tools", [])
    
    async def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """获取工具schema"""
        return await self._request("GET", f"/api/v1/tools/{tool_name}/schema")
    
    # ========================================================================
    # 服务器控制 API
    # ========================================================================
    
    async def shutdown_server(
        self, 
        force: bool = False,
        cleanup_sessions: bool = True
    ) -> Dict[str, Any]:
        """
        关闭服务器
        
        Args:
            force: 是否强制关闭
            cleanup_sessions: 关闭前是否清理所有session
            
        Returns:
            关闭结果
            
        Example:
            ```python
            # 正常关闭（清理session后关闭）
            await client.shutdown_server()
            
            # 强制关闭
            await client.shutdown_server(force=True)
            ```
        """
        return await self._request("POST", HTTPEndpoints.SHUTDOWN, {
            "force": force,
            "cleanup_sessions": cleanup_sessions
        })


# ============================================================================
# Convenience Functions
# ============================================================================

async def quick_execute(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: str = "http://localhost:8080",
    worker_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    快速执行单个动作（无需手动管理连接）
    
    Example:
        ```python
        result = await quick_execute(
            "rag:search", 
            {"query": "test"},
            base_url="http://localhost:8080"
        )
        ```
    """
    async with HTTPServiceClient(base_url=base_url, worker_id=worker_id) as client:
        return await client.execute(action, params)


def create_client(
    base_url: str = "http://localhost:8080",
    **kwargs
) -> HTTPServiceClient:
    """创建客户端的便捷函数"""
    return HTTPServiceClient(base_url=base_url, **kwargs)


# ============================================================================
# Usage Example
# ============================================================================

async def example_usage():
    """使用示例"""
    
    async with HTTPServiceClient(base_url="http://localhost:8080") as client:
        
        # ============================================
        # 方式1: 显式创建Session（推荐用于需要自定义配置的场景）
        # ============================================
        print("=== 方式1: 显式创建Session ===")
        
        # 显式创建session，使用自定义配置
        result = await client.create_session("rag", {"top_k": 10, "rerank": True})
        print(f"✅ RAG Session创建: {result.get('session_name')}")
        
        # 使用创建的session执行命令
        result = await client.execute("rag:search", {"query": "人工智能"})
        print(f"RAG搜索结果: {result}")
        
        # ============================================
        # 方式2: 自动创建Session（方便快捷，会有日志提示）
        # ============================================
        print("\n=== 方式2: 自动创建Session ===")
        
        # 直接执行，没有vm session时会自动创建（日志会提示）
        result = await client.execute("vm:screenshot", {})
        print(f"VM截图结果: {result}")
        
        result = await client.execute("vm:click", {"x": 100, "y": 200})
        print(f"VM点击结果: {result}")
        
        # 不带前缀的普通工具（不需要session）
        result = await client.execute("echo", {"message": "Hello World"})
        print(f"Echo结果: {result}")
        
        # ============================================
        # 查看Session状态
        # ============================================
        print("\n=== 查看Session状态 ===")
        sessions = await client.list_sessions()
        for s in sessions:
            auto_tag = "(自动创建)" if s.get("auto_created") else "(显式创建)"
            print(f"  - {s['session_name']} [{s['resource_type']}] {auto_tag}")
        
        # ============================================
        # 批量执行
        # ============================================
        print("\n=== 批量执行 ===")
        batch_result = await client.execute_batch([
            {"action": "vm:screenshot", "params": {}},
            {"action": "rag:search", "params": {"query": "深度学习"}},
        ], parallel=False)
        print(f"批量结果: 成功={batch_result.get('success')}, 执行={batch_result.get('executed')}")
        
        # ============================================
        # 显式销毁Session
        # ============================================
        print("\n=== 显式销毁Session ===")
        
        # 销毁vm session
        result = await client.destroy_session("vm")
        print(f"🗑️ VM Session销毁: {result.get('session_name', 'N/A')}")
        
        # 销毁rag session
        result = await client.destroy_session("rag")
        print(f"🗑️ RAG Session销毁: {result.get('session_name', 'N/A')}")
        
        # 确认session已销毁
        sessions = await client.list_sessions()
        print(f"剩余Session数: {len(sessions)}")
        
        # ============================================
        # 列出工具
        # ============================================
        print("\n=== 工具列表 ===")
        tools = await client.list_tools()
        for tool in tools[:5]:
            rt = tool.get('resource_type', 'none')
            print(f"  - {tool.get('name')} (resource: {rt})")
        
        print("\n=== 完成 ===")


if __name__ == "__main__":
    asyncio.run(example_usage())
