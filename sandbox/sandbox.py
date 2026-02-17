# sandbox/sandbox.py
"""
Sandbox - User-facing Facade Class

This is the primary interface for interacting with HTTP Service.
Each Sandbox instance holds a client; use start() to launch the service and warm resources,
and use create_session() to manually create required sessions.

Example:
```python
from sandbox import Sandbox

# Basic usage
sandbox = Sandbox()
await sandbox.start()  # Start server and warm resources
await sandbox.create_session(["vm", "rag"])  # Create required sessions
result = await sandbox.execute("vm:screenshot", {})
await sandbox.close()

# Use context manager
async with Sandbox() as sandbox:
    await sandbox.create_session("vm")  # Single resource
    result = await sandbox.execute("vm:screenshot", {})
```
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import uuid
from .client import HTTPServiceClient, HTTPClientConfig, HTTPClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sandbox")


# ============================================================================
# Default server configuration template
# ============================================================================

DEFAULT_SERVER_CONFIG = {
    "server": {
        # host/port are provided by Sandbox(server_url=...), not in config.
        "title": "Sandbox HTTP Service",
        "description": "HTTP Service for Sandbox",
        "session_ttl": 300
    },
    "resources": {
        # Heavy-resource backends (inherit Backend; support sessions and warmup).
        # Class path format: sandbox.server.backends.resources.{module}.{class_name}
        "vm": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
            "description": "VM backend - desktop automation"
        },
        "bash": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.bash.BashBackend",
            "description": "Bash backend - command-line interaction"
        },
        "browser": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.browser.BrowserBackend",
            "description": "Browser backend - web automation"
        },
        "code": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.code_executor.CodeExecutorBackend",
            "description": "Code execution backend - code sandbox"
        },
        "rag": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.rag.RAGBackend",
            "description": "RAG backend - document retrieval"
        }
    },
    "apis": {
        # Lightweight API tools (@register_api_tool), no Session required.
        "websearch": {}
    }
}


# ============================================================================
# Sandbox Configuration
# ============================================================================

@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    # Server connection settings
    server_url: str = "http://localhost:18890"
    worker_id: Optional[str] = None
    timeout: float = 60.0
    
    # Auto-start settings
    auto_start_server: bool = False
    server_config_path: Optional[str] = None  # Server config file path
    server_startup_timeout: float = 30.0  # Server startup timeout
    server_check_interval: float = 0.5  # Server status check interval
    
    # Warmup resource settings
    warmup_resources: Optional[List[str]] = None  # Resources to warm up during start()
    
    # Other settings
    retry_count: int = 3
    log_level: str = "INFO"
    
    def __post_init__(self):
        if not self.worker_id:
            self.worker_id = f"sandbox_{uuid.uuid4().hex[:8]}"


# ============================================================================
# Sandbox Exceptions
# ============================================================================

class SandboxError(Exception):
    """Base Sandbox exception"""
    pass


class SandboxConnectionError(SandboxError):
    """Connection error"""
    pass


class SandboxServerStartError(SandboxError):
    """Server startup error"""
    pass


class SandboxSessionError(SandboxError):
    """Session operation error"""
    pass


# ============================================================================
# Sandbox Class
# ============================================================================

class Sandbox:
    """
    Sandbox - User-facing facade class
    
    Each Sandbox instance holds an HTTPServiceClient.
    Use start() to launch the server and warm resources, and create_session() to manually create sessions.
    Use await sandbox.execute() as the main entry for all actions.
    
    Attributes:
        worker_id: Unique identifier of the current Sandbox instance
        is_connected: Whether connected to the server
        is_started: Whether started
        
    Example:
        ```python
        # Basic usage
        sandbox = Sandbox()
        await sandbox.start()  # Start and warm resources
        await sandbox.create_session(["vm", "rag"])  # Create sessions in batch
        result = await sandbox.execute("vm:screenshot", {})
        await sandbox.close()
        
        # Context manager (auto start and close)
        async with Sandbox() as sandbox:
            await sandbox.create_session("vm")
            result = await sandbox.execute("vm:screenshot", {})
        
        # Synchronous mode
        with Sandbox() as sandbox:
            sandbox.create_session_sync(["vm", "rag"])
            # Execute async methods via _run_async
        ```
    """
    
    def __init__(
        self,
        server_url: str = "http://localhost:18890",
        worker_id: Optional[str] = None,
        config: Optional[SandboxConfig] = None,
        warmup_resources: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize Sandbox
        
        Args:
            server_url: Server URL
            worker_id: Worker ID (auto-generated if not provided)
            config: Full config object
            warmup_resources: Resource list to warm during start()
            **kwargs: Other config arguments
        """
        if config:
            self._config = config
        else:
            self._config = SandboxConfig(
                server_url=server_url,
                worker_id=worker_id,
                warmup_resources=warmup_resources,
                **kwargs
            )
        
        self._client: Optional[HTTPServiceClient] = None
        self._server_process: Optional[subprocess.Popen] = None
        self._server_log_file = None  # Server log file
        self._connected = False
        self._started = False
        self._server_started_by_us = False
        
        # Set log level
        logger.setLevel(getattr(logging, self._config.log_level.upper()))
    
    # ========================================================================
    # Properties
    # ========================================================================
    
    @property
    def worker_id(self) -> str:
        """Get Worker ID"""
        return self._config.worker_id or ""
    
    @property
    def is_connected(self) -> bool:
        """Whether connected"""
        return self._connected
    
    @property
    def is_started(self) -> bool:
        """Whether started"""
        return self._started
    
    @property
    def server_url(self) -> str:
        """Server URL"""
        return self._config.server_url
    
    @property
    def client(self) -> Optional[HTTPServiceClient]:
        """Get underlying client (advanced use)"""
        return self._client
    
    # ========================================================================
    # Start - entry point
    # ========================================================================
    
    async def start(
        self,
        warmup_resources: Optional[List[str]] = None
    ) -> "Sandbox":
        """
        Start Sandbox
        
        1. Check whether the server is online; auto-start it if offline
        2. Connect to the server
        3. Warm resources from config (initialize backends only; no session creation)
        
        Args:
            warmup_resources: Override warmup resources in config
            
        Returns:
            self, supports chaining
            
        Example:
            ```python
            sandbox = Sandbox(warmup_resources=["vm", "rag"])
            await sandbox.start()  # Warm up vm and rag backends
            
            # Or pass warmup resources at start time
            sandbox = Sandbox()
            await sandbox.start(warmup_resources=["vm"])
            ```
        """
        if self._started:
            logger.warning("Sandbox already started")
            return self
        
        # Check whether server is online
        if not await self._check_server_online_async():
            if self._config.auto_start_server:
                logger.info(f"🔄 Server not online, starting server...")
                self._start_server()
                await self._wait_for_server_async()
            else:
                raise SandboxConnectionError(
                    f"Server at {self.server_url} is not online and auto_start_server is disabled"
                )
        
        # Create and connect client
        self._create_client()
        await self._client.connect()  # type: ignore
        self._connected = True
        self._started = True
        
        logger.info(f"🚀 Sandbox started (worker_id: {self.worker_id})")
        
        # Warm up resources (if configured)
        resources_to_warmup = warmup_resources or self._config.warmup_resources
        if resources_to_warmup:
            await self._warmup_backends(resources_to_warmup)
        
        return self
    
    def start_sync(
        self,
        warmup_resources: Optional[List[str]] = None
    ) -> "Sandbox":
        """
        Start Sandbox (sync version)
        """
        return self._run_async(self.start(warmup_resources))
    
    async def _warmup_backends(self, resources: List[str]):
        """
        Warm backend resources (initialize backends only; no session creation)
        
        Internal method used to warm backends during start().
        """
        if not resources:
            return {"status": "skipped", "message": "No resources to warmup"}
        
        logger.info(f"🔥 Warming up backends: {resources}")
        
        client = self._client
        if client is None:
            raise SandboxConnectionError("Not connected. Call start() first.")

        try:
            # Call server warmup endpoint
            from .protocol import HTTPEndpoints
            result = await client._request("POST", HTTPEndpoints.WARMUP, {"backends": resources})
            
            if result.get("status") == "success":
                logger.info(f"✅ Backends warmed up: {resources}")
            else:
                logger.warning(f"⚠️ Partial warmup: {result}")
            
            return result
        except Exception as e:
            logger.warning(f"⚠️ Backend warmup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def warmup(
        self,
        resources: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Warm backend resources
        
        Warmup calls backend warmup() to load models, create pools, and other global resources.
        After warmup, subsequent tool calls are faster.
        
        Note: even without explicit warmup, matching backends are warmed automatically during tool execution.
        Explicit warmup helps avoid first-call latency by initializing earlier.
        
        Args:
            resources: Resources to warm; can be:
                - None: warm all loaded backends
                - Single resource: "rag"
                - Resource list: ["rag", "vm", "browser"]
                
        Returns:
            Warmup result dict containing warmup state of each backend
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                # Warm up all backends
                result = await sandbox.warmup()
                
                # Warm up a specific backend
                result = await sandbox.warmup("rag")
                
                # Warm up multiple backends
                result = await sandbox.warmup(["rag", "vm"])
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        # Normalize input args
        if resources is None:
            backend_list = None  # None means warm up all backends
        elif isinstance(resources, str):
            backend_list = [resources]
        else:
            backend_list = list(resources)
        
        try:
            from .protocol import HTTPEndpoints
            result = await self._client._request("POST", HTTPEndpoints.WARMUP, {
                "backends": backend_list
            })
            
            if result.get("status") == "success":
                warmed = result.get("results", {})
                success_count = sum(1 for v in warmed.values() if v)
                total_count = len(warmed)
                logger.info(f"✅ Warmup complete: {success_count}/{total_count} backends ready")
            
            return result
        except Exception as e:
            logger.error(f"❌ Warmup failed: {e}")
            raise SandboxError(f"Warmup failed: {e}")
    
    def warmup_sync(
        self,
        resources: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """Warm backend resources (sync version)"""
        return self._run_async(self.warmup(resources))
    
    async def get_warmup_status(self) -> Dict[str, Any]:
        """
        Get warmup status
        
        Returns:
            Warmup status dict, including loaded/warmed state per backend
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                status = await sandbox.get_warmup_status()
                print(status)
                # {
                #     "backends": {
                #         "vm": {"loaded": True, "warmed_up": False},
                #         "rag": {"loaded": True, "warmed_up": True}
                #     },
                #     "summary": {"total": 2, "warmed_up": 1, "pending": 1}
                # }
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        from .protocol import HTTPEndpoints
        return await self._client._request("GET", HTTPEndpoints.WARMUP_STATUS)
    
    # ========================================================================
    # Create Session
    # ========================================================================
    
    async def create_session(
        self,
        resources: Union[str, List[str], Dict[str, Dict[str, Any]]],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Session (single or batch)
        
        Args:
            resources: Resources to create sessions for; can be:
                - Single resource: "vm"
                - Resource list: ["vm", "rag", "browser"]
                - Config dict: {"vm": {"screen_size": [1920, 1080]}, "rag": {"top_k": 10}}
            config: Config used when resources is a string (optional)
            
        Returns:
            Creation result including session info for each resource
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                # Option 1: single resource
                result = await sandbox.create_session("vm")
                
                # Option 2: multiple resources
                result = await sandbox.create_session(["vm", "rag", "browser"])
                
                # Option 3: multiple resources with config
                result = await sandbox.create_session({
                    "vm": {"screen_size": [2560, 1440]},
                    "rag": {"top_k": 20},
                    "browser": {"headless": True}
                })
                
                # Option 4: single resource with config
                result = await sandbox.create_session("vm", {"screen_size": [1920, 1080]})
                
                # Option 5: single resource with custom name
                result = await sandbox.create_session("vm", {"custom_name": "my_vm"})
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        results = {}
        create_start = time.time()
        
        # Normalize into dict format
        if isinstance(resources, str):
            # Single resource
            resource_configs = {resources: config or {}}
        elif isinstance(resources, list):
            # Resource list (with empty config)
            resource_configs = {r: {} for r in resources}
        elif isinstance(resources, dict):
            # Config dict
            resource_configs = resources
        else:
            raise SandboxSessionError(f"Invalid resources type: {type(resources)}")
        
        # Create sessions in batch
        for resource_type, res_config in resource_configs.items():
            try:
                custom_name = None
                if isinstance(res_config, dict) and "custom_name" in res_config:
                    custom_name = res_config.get("custom_name")
                    res_config = {k: v for k, v in res_config.items() if k != "custom_name"}
                result = await self._client.create_session(resource_type, res_config, custom_name=custom_name)

                # Parse new response format (Code/Message/Data/Meta)
                # result format: {"code": 0, "message": "success", "data": {...}, "meta": {...}}
                data = result.get("data", {})

                # Determine success: check code == 0 and data.session_status == "active"
                is_success = (
                    result.get("code") == 0 and
                    data.get("session_status") == "active"
                )

                results[resource_type] = {
                    "status": "success" if is_success else "error",
                    "session_id": data.get("session_id"),
                    "session_name": data.get("session_name"),
                    "config_applied": res_config,
                    "message": result.get("message", "")
                }

                # Propagate compatibility mode info
                if data.get("compatibility_mode"):
                    results[resource_type]["compatibility_mode"] = True
                    results[resource_type]["compatibility_message"] = data.get("compatibility_message", "")

                # Propagate error info
                if data.get("error"):
                    results[resource_type]["error"] = data.get("error")

                logger.info(f"📦 Session created: {resource_type} -> {results[resource_type]['session_name']}")
            except Exception as e:
                results[resource_type] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"❌ Session creation failed for {resource_type}: {e}")
        
        create_time = time.time() - create_start
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        
        return {
            "status": "success" if success_count == len(results) else ("partial" if success_count > 0 else "error"),
            "create_time_ms": create_time * 1000,
            "total": len(results),
            "success": success_count,
            "sessions": results
        }
    
    def create_session_sync(
        self,
        resources: Union[str, List[str], Dict[str, Dict[str, Any]]],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Session (sync version)"""
        return self._run_async(self.create_session(resources, config))
    
    # ========================================================================
    # Destroy Session
    # ========================================================================
    
    async def destroy_session(
        self,
        resources: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Destroy Session
        
        Args:
            resources: Resources to destroy; can be:
                - Single resource: "vm"
                - Resource list: ["vm", "rag"]
                - None: destroy all sessions
                
        Returns:
            Destroy result
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                await sandbox.create_session(["vm", "rag"])
                
                # Destroy one
                await sandbox.destroy_session("vm")
                
                # Destroy multiple
                await sandbox.destroy_session(["vm", "rag"])
                
                # Destroy all
                await sandbox.destroy_session()
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        results = {}
        resource_list: List[str]
        
        if resources is None:
            # Destroy all sessions
            sessions = await self._client.list_sessions()
            resource_list = [
                rt
                for s in sessions
                if isinstance(s, dict)
                for rt in [s.get("resource_type")]
                if isinstance(rt, str)
            ]
        elif isinstance(resources, str):
            resource_list = [resources]
        else:
            resource_list = [r for r in resources if isinstance(r, str)]
        
        for resource_type in resource_list:
            try:
                result = await self._client.destroy_session(resource_type)
                results[resource_type] = {
                    "status": "success",
                    "session_id": result.get("session_id"),
                    "message": result.get("message", "")
                }
                logger.info(f"🗑️ Session destroyed: {resource_type}")
            except Exception as e:
                results[resource_type] = {
                    "status": "error",
                    "error": str(e)
                }
        
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        
        return {
            "status": "success" if success_count == len(results) else "partial",
            "total": len(results),
            "success": success_count,
            "details": results
        }
    
    def destroy_session_sync(
        self,
        resources: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """Destroy Session (sync version)"""
        return self._run_async(self.destroy_session(resources))
    
    # ========================================================================
    # List Sessions
    # ========================================================================
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all current Sessions
        
        Returns:
            Session list
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        return await self._client.list_sessions()
    
    def list_sessions_sync(self) -> List[Dict[str, Any]]:
        """List all current Sessions (sync version)"""
        return self._run_async(self.list_sessions())
    
    # ========================================================================
    # Execute - main entry
    # ========================================================================
    
    async def execute(
        self, 
        action: str, 
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute action - main entry
        
        Args:
            action: Action name, e.g. "search", "vm:screenshot", "rag:search"
            params: Action parameters
            **kwargs: Extra parameters (merged into params for backend tools)
            timeout: Timeout (seconds)
            
        Returns:
            Execution result
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                await sandbox.create_session("vm")
                result = await sandbox.execute("vm:screenshot", {})
                result = await sandbox.execute("echo", {"message": "hello"})
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        merged_params = dict(params or {})
        for key, value in kwargs.items():
            if key not in merged_params and value is not None:
                merged_params[key] = value
        return await self._client.execute(action, merged_params, timeout)
    
    def execute_sync(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute action (sync version)"""
        return self._run_async(self.execute(action, params, timeout))
    
    # ========================================================================
    # Reinitialize resources
    # ========================================================================
    
    async def reinitialize(
        self,
        resource_type: str,
        new_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reinitialize one resource (without affecting others)
        
        Destroy existing session for this resource, then recreate with new config.
        
        Args:
            resource_type: Resource type to reinitialize
            new_config: New configuration parameters
            
        Returns:
            Reinitialize result
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        reinit_start = time.time()
        
        # Destroy existing session
        old_session = None
        try:
            destroy_result = await self._client.destroy_session(resource_type)
            old_session = destroy_result.get("session_id")
            logger.info(f"🔄 Reinitialize {resource_type}: destroyed old session")
        except Exception:
            logger.debug(f"🔄 Reinitialize {resource_type}: no existing session")
        
        # Create new session
        try:
            custom_name = None
            config = new_config or {}
            if isinstance(config, dict) and "custom_name" in config:
                custom_name = config.get("custom_name")
                config = {k: v for k, v in config.items() if k != "custom_name"}

            create_result = await self._client.create_session(resource_type, config, custom_name=custom_name)
            new_session = create_result.get("session_id")
            new_name = create_result.get("session_name")
            
            reinit_time = time.time() - reinit_start
            logger.info(f"✅ Reinitialize {resource_type}: new session {new_name}")
            
            return {
                "status": "success",
                "resource_type": resource_type,
                "old_session_id": old_session,
                "new_session_id": new_session,
                "new_session_name": new_name,
                "config_applied": new_config or {},
                "reinit_time_ms": reinit_time * 1000
            }
        except Exception as e:
            logger.error(f"❌ Reinitialize {resource_type} failed: {e}")
            return {
                "status": "error",
                "resource_type": resource_type,
                "old_session_id": old_session,
                "error": str(e)
            }
    
    def reinitialize_sync(
        self,
        resource_type: str,
        new_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Reinitialize resource (sync version)"""
        return self._run_async(self.reinitialize(resource_type, new_config))
    
    # ========================================================================
    # Refresh Sessions - keepalive
    # ========================================================================
    
    async def refresh_sessions(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refresh session TTL
        
        Args:
            resource_type: Resource type (optional; refresh all when omitted)
            
        Returns:
            Refresh result
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        return await self._client.refresh_session(resource_type)
    
    def refresh_sessions_sync(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refresh session TTL (sync version)"""
        return self._run_async(self.refresh_sessions(resource_type))
    
    # ========================================================================
    # Context Managers
    # ========================================================================
    
    def __enter__(self) -> "Sandbox":
        """Sync context manager entry"""
        self.start_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        self.close_sync()
    
    async def __aenter__(self) -> "Sandbox":
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    # ========================================================================
    # Close
    # ========================================================================
    
    async def close(self):
        """Close connection"""
        if not self._connected:
            return
        
        if self._client:
            await self._client.close()
            self._client = None
        
        self._connected = False
        self._started = False
        logger.info(f"👋 Sandbox closed (worker_id: {self.worker_id})")
    
    def close_sync(self):
        """Close connection (sync version)"""
        if not self._connected:
            return
        self._run_async(self.close())
    
    # ========================================================================
    # Shutdown Server
    # ========================================================================
    
    async def shutdown_server(
        self, 
        force: bool = False,
        cleanup_sessions: bool = True
    ) -> Dict[str, Any]:
        """
        Shutdown connected server
        
        Args:
            force: Whether to force shutdown
            cleanup_sessions: Whether to clean all sessions before shutdown
            
        Returns:
            Shutdown result
        """
        if not self._client:
            raise SandboxConnectionError("Not connected to server")
        
        logger.info("🛑 Sending shutdown request to server...")
        
        try:
            result = await self._client.shutdown_server(
                force=force,
                cleanup_sessions=cleanup_sessions
            )
            logger.info(f"✅ Server shutdown initiated")
            
            self._connected = False
            self._started = False
            
            if self._server_process and self._server_started_by_us:
                try:
                    self._server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._server_process.kill()
                self._server_process = None
                self._server_started_by_us = False
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to shutdown server: {e}")
            raise SandboxError(f"Server shutdown failed: {e}")
    
    def shutdown_server_sync(
        self,
        force: bool = False,
        cleanup_sessions: bool = True
    ) -> Dict[str, Any]:
        """Shutdown server (sync version)"""
        return self._run_async(self.shutdown_server(force, cleanup_sessions))
    
    # ========================================================================
    # Server Management (Internal)
    # ========================================================================
    
    async def _check_server_online_async(self) -> bool:
        """Check whether server is online"""
        import httpx  # pyright: ignore[reportMissingImports]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.server_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    def _check_server_online(self) -> bool:
        """Check whether server is online (sync)"""
        import httpx  # pyright: ignore[reportMissingImports]
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.server_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    def _start_server(self):
        """Start server"""
        config = self._load_server_config()
        
        from urllib.parse import urlparse
        parsed = urlparse(self.server_url)
        port = parsed.port or 18890
        host = parsed.hostname or "0.0.0.0"
        
        server_script = self._generate_server_script(config, host, port)
        
        # Create log file to capture server output (for debugging).
        import tempfile
        self._server_log_file = tempfile.NamedTemporaryFile(
            mode='w+', 
            suffix='_sandbox_server.log', 
            delete=False,
            encoding='utf-8'
        )
        
        self._server_process = subprocess.Popen(
            [sys.executable, "-c", server_script],
            stdout=self._server_log_file,
            stderr=subprocess.STDOUT,  # stderr merged into stdout
            start_new_session=True
        )
        self._server_started_by_us = True
        
        logger.info(f"✅ Server starting on {self.server_url}")
        logger.debug(f"📝 Server log: {self._server_log_file.name}")
    
    async def _wait_for_server_async(self):
        """Wait for server startup completion"""
        start_time = time.time()
        while time.time() - start_time < self._config.server_startup_timeout:
            if await self._check_server_online_async():
                return
            await asyncio.sleep(self._config.server_check_interval)
        
        if self._server_process:
            self._server_process.terminate()
        raise SandboxServerStartError(
            f"Server failed to start within {self._config.server_startup_timeout} seconds"
        )
    
    def get_server_log(self, tail_lines: int = 100) -> Optional[str]:
        """
        Get server log (for debugging)
        
        Args:
            tail_lines: Number of tail log lines to return
            
        Returns:
            Server log content; returns None if no log file exists
        """
        if not self._server_log_file:
            return None
        
        try:
            # Flush and read log
            self._server_log_file.flush()
            log_path = self._server_log_file.name
            
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                if tail_lines and len(lines) > tail_lines:
                    lines = lines[-tail_lines:]
                return ''.join(lines)
        except Exception as e:
            return f"[Failed to read log: {e}]"
    
    def _load_server_config(self) -> Dict[str, Any]:
        """Load server configuration"""
        config_path = self._config.server_config_path
        
        if config_path:
            # Try loading config file
            if os.path.exists(config_path):
                logger.info(f"📄 Loading config from: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                resources = [k for k in config.get("resources", {}).keys() if not k.startswith("_")]
                logger.info(f"   Resources in config: {resources}")
                return config
            else:
                # Config path is specified but does not exist
                logger.warning(f"⚠️ Config file not found: {config_path}")
                logger.warning(f"   Current working directory: {os.getcwd()}")
                logger.warning(f"   Absolute path would be: {os.path.abspath(config_path)}")
        
        # Use default config
        logger.info("📄 Using DEFAULT_SERVER_CONFIG")
        default_config = DEFAULT_SERVER_CONFIG.copy()
        resources = [k for k in default_config.get("resources", {}).keys() if not k.startswith("_")]
        logger.info(f"   Resources in default config: {resources}")
        return default_config
    
    def _generate_server_script(self, config: Dict[str, Any], host: str, port: int) -> str:
        """
        Generate server startup script
        
        Generated script supports:
        - Loading heavy-resource backends (resources section)
        - Loading lightweight tools (apis section)
        """
        config_json = json.dumps(config)
        
        script = f'''
import sys
sys.path.insert(0, "{Path(__file__).parent.parent.absolute()}")

import json
import logging
import importlib
import traceback

# Configure logging to stderr so it is visible.
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("SandboxServer")

# Print startup info
logger.info("=" * 60)
logger.info("🚀 Sandbox Server starting...")
logger.info("=" * 60)

from sandbox import HTTPServiceServer
from sandbox.server.backends.tools import register_all_tools
from sandbox.server.backends.base import BackendConfig

config = json.loads({repr(config_json)})

# Print config summary
resources_names = [k for k in config.get("resources", {{}}).keys() if not k.startswith("_")]
logger.info(f"📋 resources in config: {{resources_names}}")

server = HTTPServiceServer(
    host="{host}",
    port={port},
    title=config.get("server", {{}}).get("title", "Sandbox HTTP Service"),
    description=config.get("server", {{}}).get("description", ""),
    session_ttl=config.get("server", {{}}).get("session_ttl", 300)
)

# ============================================================================
# 1. Register heavy-resource backends (resources)
# ============================================================================
resources_config = config.get("resources", {{}})
loaded_backends = []
failed_backends = []

for name, res_config in resources_config.items():
    # Skip comment fields
    if name.startswith("_"):
        continue
    
    # Check enabled flag
    if not res_config.get("enabled", True):
        logger.info(f"⏭️ Skipping disabled resource: {{name}}")
        continue
    
    # Get backend class path
    backend_class_path = res_config.get("backend_class")
    if not backend_class_path:
        logger.warning(f"⚠️ Resource '{{name}}' has no backend_class, skipping")
        continue
    
    try:
        # Dynamically load backend class
        logger.info(f"📦 Loading backend: {{name}} ({{backend_class_path}})")
        module_path, class_name = backend_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        backend_cls = getattr(module, class_name)
        
        # Create backend config
        backend_config = BackendConfig(
            enabled=True,
            default_config=res_config.get("config", {{}}),
            description=res_config.get("description", "")
        )
        
        # Instantiate and load backend
        backend = backend_cls(config=backend_config)
        tools = server.load_backend(backend)
        
        loaded_backends.append(name)
        logger.info(f"✅ Loaded backend: {{name}} ({{len(tools)}} tools)")
        
    except Exception as e:
        failed_backends.append(name)
        logger.error(f"❌ Failed to register backend '{{name}}': {{e}}")
        logger.error(traceback.format_exc())

# Print backend load summary
logger.info("=" * 60)
logger.info(f"📊 Backend load result: {{len(loaded_backends)}} success, {{len(failed_backends)}} failed")
if loaded_backends:
    logger.info(f"   ✅ loaded: {{loaded_backends}}")
if failed_backends:
    logger.error(f"   ❌ failed: {{failed_backends}}")

# ============================================================================
# 2. Register lightweight tools (apis)
# ============================================================================
apis_config = config.get("apis", {{}})
if apis_config:
    logger.info(f"📦 Registering API tools: {{list(apis_config.keys())}}")
register_all_tools(server, apis_config)

# Start server
server.run()
'''
        return script
    
    def _create_client(self):
        """Create HTTPServiceClient"""
        client_config = HTTPClientConfig(
            base_url=self._config.server_url,
            timeout=self._config.timeout,
            max_retries=self._config.retry_count,
            worker_id=self._config.worker_id,
            auto_heartbeat=False
        )
        self._client = HTTPServiceClient(config=client_config)
    
    def _run_async(self, coro) -> Any:
        """Run async code in sync context"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    async def get_tools(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get available tool list"""
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        return await self._client.list_tools(include_hidden)
    
    def get_tools_sync(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get available tool list (sync version)"""
        return self._run_async(self.get_tools(include_hidden))
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        return await self._client.get_status()
    
    def get_status_sync(self) -> Dict[str, Any]:
        """Get current status (sync version)"""
        return self._run_async(self.get_status())
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        return self._load_server_config()
    
    def save_server_config(self, config: Dict[str, Any], path: str):
        """Save server configuration to file"""
        with open(path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Server config saved to {path}")
    
    @staticmethod
    def create_config_template(path: str):
        """Create config template file"""
        with open(path, 'w') as f:
            json.dump(DEFAULT_SERVER_CONFIG, f, indent=2, ensure_ascii=False)
        logger.info(f"📝 Config template created at {path}")
    
    def __repr__(self) -> str:
        status = "started" if self._started else ("connected" if self._connected else "disconnected")
        return f"Sandbox(worker_id={self.worker_id}, status={status}, server={self.server_url})"


# ============================================================================
# Convenience Functions
# ============================================================================

def create_sandbox(
    server_url: str = "http://localhost:18890",
    **kwargs
) -> Sandbox:
    """Convenience function to create Sandbox instance"""
    return Sandbox(server_url=server_url, **kwargs)


def get_default_config() -> Dict[str, Any]:
    """Get default server configuration"""
    return DEFAULT_SERVER_CONFIG.copy()
