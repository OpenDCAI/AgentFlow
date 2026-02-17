# sandbox/client.py
"""
HTTP Service Client - Independent HTTP client implementation

An HTTP-protocol client template fully independent of the MCP Server.

Features:
- Automatic session naming: the server generates readable session names (e.g., vm_abc123_001).
- Flexible management: supports explicit create/destroy and automatic creation (with log hints).
- Explicit cleanup: sessions are released via explicit destroy_session calls.

Capabilities:
1. Session management - create_session/destroy_session/list_sessions
2. Execution - supports resource-type prefixes (e.g., vm:action)
3. Initialization - resource configuration initialization
4. Tool discovery - list available tools

Usage - Mode 1: Explicit session management (recommended):
```python
async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # Explicitly create a session with custom config
    result = await client.create_session("rag", {"top_k": 10})
    print(f"Session: {result['session_name']}")  # e.g.: rag_abc123_001
    
    # Execute command
    result = await client.execute("rag:search", {"query": "test"})
    
    # Explicitly destroy session
    await client.destroy_session("rag")
```

Usage - Mode 2: Automatic session creation (quick):
```python
async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # Execute directly; auto-create if no session exists (server logs will indicate).
    result = await client.execute("vm:screenshot", {})
    
    # List sessions
    sessions = await client.list_sessions()
    
    # Explicitly destroy when done
    await client.destroy_session("vm")
```
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import uuid

import httpx  # pyright: ignore[reportMissingImports]

from .protocol import HTTPEndpoints

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HTTPServiceClient")


# ============================================================================
# Client Configuration
# ============================================================================

@dataclass
class HTTPClientConfig:
    """Client configuration"""
    base_url: str = "http://localhost:8080"
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    auto_heartbeat: bool = True
    heartbeat_interval: float = 30.0
    worker_id: Optional[str] = None  # Auto-generated when None
    
    def __post_init__(self):
        if not self.worker_id:
            self.worker_id = f"worker_{uuid.uuid4().hex[:8]}"


# ============================================================================
# Exception Classes
# ============================================================================

class HTTPClientError(Exception):
    """HTTP client error"""
    
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
    HTTP Service Client - Independent HTTP client
    
    Resources are managed by the server automatically; the client only needs to execute actions.
    
    Example:
    ```python
    async with HTTPServiceClient(base_url="http://localhost:8080") as client:
        # Execute directly; server auto-manages resource sessions
        result = await client.execute("vm:screenshot", {})
        result = await client.execute("rag:search", {"query": "test"})
        
        # Batch execution
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
        Initialize client
        
        Args:
            base_url: Server URL
            worker_id: Worker ID for resource isolation (auto-generated if omitted)
            timeout: Default timeout
            config: Full config object (higher priority than other params)
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
        """Establish connection"""
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
        
        # Check server health status
        try:
            response = await self._client.get(HTTPEndpoints.HEALTH)
            if response.status_code != 200:
                raise ConnectionError(f"Server health check failed: {response.status_code}")
            logger.info(f"Connected to HTTP Service at {self.base_url} (worker_id: {self.worker_id})")
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            raise
        
        # Start heartbeat task
        if self.config.auto_heartbeat:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def close(self, destroy_sessions: bool = False):
        """
        Close connection
        
        Args:
            destroy_sessions: Whether to destroy all sessions (default False; explicit opt-in)
        """
        if self._closed:
            return
        
        self._closed = True
        
        # Stop heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Destroy sessions if requested
        if destroy_sessions:
            try:
                await self._request("POST", "/api/v1/worker/disconnect", {
                    "worker_id": self.worker_id
                })
                logger.info(f"🗑️ [{self.worker_id}] All sessions destroyed on close")
            except Exception as e:
                logger.warning(f"Failed to destroy sessions on close: {e}")
        
        # Close HTTP client
        if self._client:
            await self._client.aclose()
            self._client = None
        
        logger.info(f"HTTPServiceClient closed (worker_id: {self.worker_id})")
    
    async def _heartbeat_loop(self):
        """Heartbeat loop"""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
    
    async def _send_heartbeat(self):
        """Send heartbeat"""
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
        Send HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: request payload
            timeout: timeout
            
        Returns:
            Response data
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
    # Execution APIs
    # ========================================================================
    
    async def execute(
        self, 
        action: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute tool/action
        
        The server automatically manages sessions based on the action resource prefix.
        For example, "vm:screenshot" auto-creates or reuses a vm session.
        
        Args:
            action: Action name; supports resource prefix like "vm:screenshot", "rag:search"
            params: Action parameters
            timeout: Execution timeout
            
        Returns:
            Execution result
            
        Example:
            ```python
            # With resource prefix - server auto-manages sessions
            result = await client.execute("vm:screenshot", {})
            result = await client.execute("rag:search", {"query": "test"})
            
            # Normal tools without prefix
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
        Execute actions in batch
        
        Args:
            actions: Action list; each item format: {"action": "name", "params": {...}}
            parallel: Whether to run in parallel
            stop_on_error: Whether to stop on error
            
        Returns:
            Batch execution result
            
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
    # Status query APIs
    # ========================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current worker status
        
        Returns:
            Includes active resources, session details, etc.
        """
        return await self._request("POST", HTTPEndpoints.STATUS, {
            "worker_id": self.worker_id
        })
    
    # ========================================================================
    # Session management APIs (explicit operations)
    # ========================================================================
    
    async def create_session(
        self,
        resource_type: str,
        session_config: Optional[Dict[str, Any]] = None,
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Explicitly create a session
        
        Used to pre-create sessions or apply custom configuration.
        If this is not called, sessions are auto-created during execution (with logs).
        
        Args:
            resource_type: Resource type (e.g., "vm", "rag")
            session_config: Session config
            custom_name: Custom session name (optional)
            
        Returns:
            Creation result containing session_id and session_name
            
        Example:
            ```python
            # Explicitly create a session with custom config
            result = await client.create_session("rag", {"top_k": 10})
            print(f"Session created: {result['session_name']}")
            
            # Subsequent actions will use this session
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
        Explicitly destroy a session
        
        Release the session for a specific resource type.
        
        Args:
            resource_type: Resource type (e.g., "vm", "rag")
            
        Returns:
            Destroy result
            
        Example:
            ```python
            # Destroy vm resource session
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
        List all sessions for the current worker
        
        Returns:
            Session list; each item includes resource_type, session_id, session_name, etc.
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
        Destroy all sessions for the current worker
        
        Returns:
            Destroy result
        """
        return await self._request("POST", "/api/v1/worker/disconnect", {
            "worker_id": self.worker_id
        })
    
    async def refresh_session(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refresh session TTL (keepalive)
        
        Each action refreshes TTL automatically; this method provides explicit keepalive.
        
        Args:
            resource_type: Resource type (optional)
                - If specified, refresh only that resource session
                - If omitted, refresh all sessions
                
        Returns:
            Refresh result
            
        Example:
            ```python
            # Refresh session for a specific resource
            result = await client.refresh_session("vm")
            print(f"VM session expires at: {result['expires_at']}")
            
            # Refresh all sessions
            result = await client.refresh_session()
            print(f"Refreshed {result['refreshed_count']} sessions")
            ```
        """
        data = {"worker_id": self.worker_id}
        if resource_type:
            data["resource_type"] = resource_type
        return await self._request("POST", HTTPEndpoints.SESSION_REFRESH, data)
    
    # ========================================================================
    # Initialization APIs (optional, for preload/custom config)
    # ========================================================================
    
    async def init_resource(
        self,
        resource_type: str,
        init_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pre-initialize resources (optional)
        
        Usually not required; the server auto-initializes on first relevant action.
        This method is used for:
        1. Preload resources (reduce first-run latency)
        2. Initialize with custom configuration
        
        Args:
            resource_type: Resource type
            init_config: Initialization config (JSON payload)
            
        Returns:
            Initialization result
            
        Example:
            ```python
            # Pre-initialize rag resource with custom config
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
        Batch pre-initialize resources
        
        Args:
            resource_configs: Resource config dictionary
            
        Returns:
            Batch initialization result
            
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
        Initialize from config file
        
        Args:
            config_path: Config file path (server-side path)
            override_params: Override parameters
            
        Returns:
            Initialization result
        """
        return await self._request("POST", HTTPEndpoints.INIT_FROM_CONFIG, {
            "worker_id": self.worker_id,
            "config_path": config_path,
            "override_params": override_params or {}
        })
    
    # ========================================================================
    # Tool info APIs
    # ========================================================================
    
    async def list_tools(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """List all available tools"""
        result = await self._request("GET", f"{HTTPEndpoints.TOOLS_LIST}?include_hidden={include_hidden}")
        return result.get("tools", [])
    
    async def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get tool schema"""
        return await self._request("GET", f"/api/v1/tools/{tool_name}/schema")
    
    # ========================================================================
    # Server control APIs
    # ========================================================================
    
    async def shutdown_server(
        self, 
        force: bool = False,
        cleanup_sessions: bool = True
    ) -> Dict[str, Any]:
        """
        Shutdown server
        
        Args:
            force: Whether to force shutdown
            cleanup_sessions: Whether to clean up all sessions before shutdown
            
        Returns:
            Shutdown result
            
        Example:
            ```python
            # Graceful shutdown (cleanup sessions first)
            await client.shutdown_server()
            
            # Force shutdown
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
    Quickly execute a single action (without manual connection handling)
    
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
    """Convenience function to create a client"""
    return HTTPServiceClient(base_url=base_url, **kwargs)


# ============================================================================
# Usage Example
# ============================================================================

async def example_usage():
    """Usage example"""
    
    async with HTTPServiceClient(base_url="http://localhost:8080") as client:
        
        # ============================================
        # Mode 1: Explicit session creation (recommended for custom config)
        # ============================================
        print("=== Mode 1: Explicit Session Creation ===")
        
        # Explicitly create a session with custom config
        result = await client.create_session("rag", {"top_k": 10, "rerank": True})
        print(f"✅ RAG Session created: {result.get('session_name')}")
        
        # Execute commands using created session
        result = await client.execute("rag:search", {"query": "artificial intelligence"})
        print(f"RAG search result: {result}")
        
        # ============================================
        # Mode 2: Auto session creation (convenient, with logs)
        # ============================================
        print("\n=== Mode 2: Automatic Session Creation ===")
        
        # Execute directly; vm session is auto-created if missing (with logs).
        result = await client.execute("vm:screenshot", {})
        print(f"VM screenshot result: {result}")
        
        result = await client.execute("vm:click", {"x": 100, "y": 200})
        print(f"VM click result: {result}")
        
        # Normal tools without prefix (no session required)
        result = await client.execute("echo", {"message": "Hello World"})
        print(f"Echo result: {result}")
        
        # ============================================
        # Check session status
        # ============================================
        print("\n=== Session Status ===")
        sessions = await client.list_sessions()
        for s in sessions:
            auto_tag = "(auto-created)" if s.get("auto_created") else "(explicitly created)"
            print(f"  - {s['session_name']} [{s['resource_type']}] {auto_tag}")
        
        # ============================================
        # Batch execution
        # ============================================
        print("\n=== Batch Execution ===")
        batch_result = await client.execute_batch([
            {"action": "vm:screenshot", "params": {}},
            {"action": "rag:search", "params": {"query": "deep learning"}},
        ], parallel=False)
        print(f"Batch result: success={batch_result.get('success')}, executed={batch_result.get('executed')}")
        
        # ============================================
        # Explicitly destroy sessions
        # ============================================
        print("\n=== Explicit Session Destruction ===")
        
        # Destroy vm session
        result = await client.destroy_session("vm")
        print(f"🗑️ VM Session destroyed: {result.get('session_name', 'N/A')}")
        
        # Destroy rag session
        result = await client.destroy_session("rag")
        print(f"🗑️ RAG Session destroyed: {result.get('session_name', 'N/A')}")
        
        # Confirm sessions are destroyed
        sessions = await client.list_sessions()
        print(f"Remaining session count: {len(sessions)}")
        
        # ============================================
        # List tools
        # ============================================
        print("\n=== Tool List ===")
        tools = await client.list_tools()
        for tool in tools[:5]:
            rt = tool.get('resource_type', 'none')
            print(f"  - {tool.get('name')} (resource: {rt})")
        
        print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(example_usage())
