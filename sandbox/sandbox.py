# sandbox/sandbox.py
"""
Sandbox - 用户交互的门面类 (Facade Class)

这是与 HTTP Service 交互的主要接口。
每个 Sandbox 实例持有一个 client，使用 start() 启动服务并预热资源，
使用 create_session() 手动创建需要的 session。

使用示例:
```python
from sandbox import Sandbox

# 基本使用
sandbox = Sandbox()
await sandbox.start()  # 启动服务器，预热资源
await sandbox.create_session(["vm", "rag"])  # 创建需要的 session
result = await sandbox.execute("vm:screenshot", {})
await sandbox.close()

# 使用上下文管理器
async with Sandbox() as sandbox:
    await sandbox.create_session("vm")  # 单个资源
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
# 默认服务器配置模板
# ============================================================================

DEFAULT_SERVER_CONFIG = {
    "server": {
        # host/port 由 Sandbox(server_url=...) 指定，不在配置中设置
        "title": "Sandbox HTTP Service",
        "description": "HTTP Service for Sandbox",
        "session_ttl": 300
    },
    "resources": {
        # 重资源后端（继承 Backend 类，支持 Session 管理和预热）
        # 类路径格式：sandbox.server.backends.resources.{模块}.{类名}
        "vm": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
            "description": "虚拟机后端 - 桌面自动化"
        },
        "bash": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.bash.BashBackend",
            "description": "Bash 后端 - 命令行交互"
        },
        "browser": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.browser.BrowserBackend",
            "description": "浏览器后端 - 网页自动化"
        },
        "code": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.code_executor.CodeExecutorBackend",
            "description": "代码执行后端 - 代码沙箱"
        },
        "rag": {
            "enabled": True,
            "backend_class": "sandbox.server.backends.resources.rag.RAGBackend",
            "description": "RAG 后端 - 文档检索"
        }
    },
    "apis": {
        # 轻资源 API 工具（使用 @register_api_tool 装饰器，无需 Session）
        "websearch": {}
    }
}


# ============================================================================
# Sandbox Configuration
# ============================================================================

@dataclass
class SandboxConfig:
    """Sandbox 配置"""
    # 服务器连接配置
    server_url: str = "http://localhost:18890"
    worker_id: Optional[str] = None
    timeout: float = 60.0
    
    # 自动启动配置
    auto_start_server: bool = False
    server_config_path: Optional[str] = None  # 服务器配置文件路径
    server_startup_timeout: float = 30.0  # 服务器启动超时
    server_check_interval: float = 0.5  # 检查服务器状态间隔
    
    # 预热资源配置
    warmup_resources: Optional[List[str]] = None  # start() 时预热的资源列表
    
    # 其他配置
    retry_count: int = 3
    log_level: str = "INFO"
    
    def __post_init__(self):
        if not self.worker_id:
            self.worker_id = f"sandbox_{uuid.uuid4().hex[:8]}"


# ============================================================================
# Sandbox Exceptions
# ============================================================================

class SandboxError(Exception):
    """Sandbox 基础异常"""
    pass


class SandboxConnectionError(SandboxError):
    """连接错误"""
    pass


class SandboxServerStartError(SandboxError):
    """服务器启动错误"""
    pass


class SandboxSessionError(SandboxError):
    """Session 操作错误"""
    pass


# ============================================================================
# Sandbox Class
# ============================================================================

class Sandbox:
    """
    Sandbox - 用户交互的门面类
    
    每个 Sandbox 实例持有一个 HTTPServiceClient。
    使用 start() 启动服务器并预热资源，使用 create_session() 手动创建 session。
    使用 await sandbox.execute() 作为主入口执行所有操作。
    
    Attributes:
        worker_id: 当前 Sandbox 实例的唯一标识
        is_connected: 是否已连接到服务器
        is_started: 是否已启动
        
    Example:
        ```python
        # 基本使用
        sandbox = Sandbox()
        await sandbox.start()  # 启动并预热资源
        await sandbox.create_session(["vm", "rag"])  # 批量创建 session
        result = await sandbox.execute("vm:screenshot", {})
        await sandbox.close()
        
        # 上下文管理器（自动 start 和 close）
        async with Sandbox() as sandbox:
            await sandbox.create_session("vm")
            result = await sandbox.execute("vm:screenshot", {})
        
        # 同步模式
        with Sandbox() as sandbox:
            sandbox.create_session_sync(["vm", "rag"])
            # 执行需要通过 _run_async 调用
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
        初始化 Sandbox
        
        Args:
            server_url: 服务器地址
            worker_id: Worker ID（自动生成如果不提供）
            config: 完整配置对象
            warmup_resources: start() 时预热的资源列表
            **kwargs: 其他配置参数
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
        self._server_log_file = None  # 服务器日志文件
        self._connected = False
        self._started = False
        self._server_started_by_us = False
        
        # 设置日志级别
        logger.setLevel(getattr(logging, self._config.log_level.upper()))
    
    # ========================================================================
    # Properties
    # ========================================================================
    
    @property
    def worker_id(self) -> str:
        """获取 Worker ID"""
        return self._config.worker_id or ""
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    @property
    def is_started(self) -> bool:
        """是否已启动"""
        return self._started
    
    @property
    def server_url(self) -> str:
        """服务器地址"""
        return self._config.server_url
    
    @property
    def client(self) -> Optional[HTTPServiceClient]:
        """获取底层 client（高级用法）"""
        return self._client
    
    # ========================================================================
    # Start - 启动入口
    # ========================================================================
    
    async def start(
        self,
        warmup_resources: Optional[List[str]] = None
    ) -> "Sandbox":
        """
        启动 Sandbox
        
        1. 检测服务器是否在线，不在线则自动启动
        2. 连接到服务器
        3. 预热配置中指定的资源（仅初始化后端，不创建 session）
        
        Args:
            warmup_resources: 覆盖配置中的预热资源列表
            
        Returns:
            self，支持链式调用
            
        Example:
            ```python
            sandbox = Sandbox(warmup_resources=["vm", "rag"])
            await sandbox.start()  # 预热 vm 和 rag 后端
            
            # 或者在 start 时指定
            sandbox = Sandbox()
            await sandbox.start(warmup_resources=["vm"])
            ```
        """
        if self._started:
            logger.warning("Sandbox already started")
            return self
        
        # 检查服务器是否在线
        if not await self._check_server_online_async():
            if self._config.auto_start_server:
                logger.info(f"🔄 Server not online, starting server...")
                self._start_server()
                await self._wait_for_server_async()
            else:
                raise SandboxConnectionError(
                    f"Server at {self.server_url} is not online and auto_start_server is disabled"
                )
        
        # 创建并连接 client
        self._create_client()
        await self._client.connect()  # type: ignore
        self._connected = True
        self._started = True
        
        logger.info(f"🚀 Sandbox started (worker_id: {self.worker_id})")
        
        # 预热资源（如果配置了）
        resources_to_warmup = warmup_resources or self._config.warmup_resources
        if resources_to_warmup:
            await self._warmup_backends(resources_to_warmup)
        
        return self
    
    def start_sync(
        self,
        warmup_resources: Optional[List[str]] = None
    ) -> "Sandbox":
        """
        启动 Sandbox（同步版本）
        """
        return self._run_async(self.start(warmup_resources))
    
    async def _warmup_backends(self, resources: List[str]):
        """
        预热后端资源（仅初始化后端，不创建 session）
        
        这是内部方法，用于在 start() 时预热后端
        """
        if not resources:
            return {"status": "skipped", "message": "No resources to warmup"}
        
        logger.info(f"🔥 Warming up backends: {resources}")
        
        try:
            # 调用服务器端的预热端点
            from .protocol import HTTPEndpoints
            result = await self._client._request("POST", HTTPEndpoints.WARMUP, {"backends": resources})
            
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
        预热后端资源
        
        预热会调用后端的 warmup() 方法，加载模型、建立连接池等全局资源。
        预热完成后，后续的工具调用会更快。
        
        注意：即使不显式调用此方法，在执行工具时也会自动预热对应的后端。
        但显式预热可以提前完成初始化，避免首次调用时的延迟。
        
        Args:
            resources: 要预热的资源，可以是：
                - None: 预热所有已加载的后端
                - 单个资源: "rag"
                - 资源列表: ["rag", "vm", "browser"]
                
        Returns:
            预热结果字典，包含每个后端的预热状态
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                # 预热所有后端
                result = await sandbox.warmup()
                
                # 预热特定后端
                result = await sandbox.warmup("rag")
                
                # 预热多个后端
                result = await sandbox.warmup(["rag", "vm"])
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        # 处理输入参数
        if resources is None:
            backend_list = None  # None 表示预热所有后端
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
        """预热后端资源（同步版本）"""
        return self._run_async(self.warmup(resources))
    
    async def get_warmup_status(self) -> Dict[str, Any]:
        """
        获取预热状态
        
        Returns:
            预热状态字典，包含每个后端的加载和预热状态
            
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
    # Create Session - Session 创建
    # ========================================================================
    
    async def create_session(
        self,
        resources: Union[str, List[str], Dict[str, Dict[str, Any]]],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建 Session（支持单个或批量）
        
        Args:
            resources: 要创建 session 的资源，可以是：
                - 单个资源: "vm"
                - 资源列表: ["vm", "rag", "browser"]
                - 带配置的字典: {"vm": {"screen_size": [1920, 1080]}, "rag": {"top_k": 10}}
            config: 当 resources 为字符串时使用的配置（可选）
            
        Returns:
            创建结果，包含每个资源的 session 信息
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                # 方式1: 单个资源
                result = await sandbox.create_session("vm")
                
                # 方式2: 多个资源（批量）
                result = await sandbox.create_session(["vm", "rag", "browser"])
                
                # 方式3: 带配置的多个资源
                result = await sandbox.create_session({
                    "vm": {"screen_size": [2560, 1440]},
                    "rag": {"top_k": 20},
                    "browser": {"headless": True}
                })
                
                # 方式4: 单个资源带配置
                result = await sandbox.create_session("vm", {"screen_size": [1920, 1080]})
                
                # 方式5: 单个资源带自定义名称
                result = await sandbox.create_session("vm", {"custom_name": "my_vm"})
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        results = {}
        create_start = time.time()
        
        # 统一转换为字典格式
        if isinstance(resources, str):
            # 单个资源
            resource_configs = {resources: config or {}}
        elif isinstance(resources, list):
            # 资源列表（使用空配置）
            resource_configs = {r: {} for r in resources}
        elif isinstance(resources, dict):
            # 带配置的字典
            resource_configs = resources
        else:
            raise SandboxSessionError(f"Invalid resources type: {type(resources)}")
        
        # 批量创建 session
        for resource_type, res_config in resource_configs.items():
            try:
                custom_name = None
                if isinstance(res_config, dict) and "custom_name" in res_config:
                    custom_name = res_config.get("custom_name")
                    res_config = {k: v for k, v in res_config.items() if k != "custom_name"}
                result = await self._client.create_session(resource_type, res_config, custom_name=custom_name)

                # 解析新格式响应 (Code/Message/Data/Meta)
                # result 格式: {"code": 0, "message": "success", "data": {...}, "meta": {...}}
                data = result.get("data", {})

                # 判断是否成功：检查 code == 0 或 data.session_status == "active"
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

                # 传递兼容性模式信息
                if data.get("compatibility_mode"):
                    results[resource_type]["compatibility_mode"] = True
                    results[resource_type]["compatibility_message"] = data.get("compatibility_message", "")

                # 传递错误信息
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
        """创建 Session（同步版本）"""
        return self._run_async(self.create_session(resources, config))
    
    # ========================================================================
    # Destroy Session - Session 销毁
    # ========================================================================
    
    async def destroy_session(
        self,
        resources: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        销毁 Session
        
        Args:
            resources: 要销毁的资源，可以是：
                - 单个资源: "vm"
                - 资源列表: ["vm", "rag"]
                - None: 销毁所有 session
                
        Returns:
            销毁结果
            
        Example:
            ```python
            async with Sandbox() as sandbox:
                await sandbox.create_session(["vm", "rag"])
                
                # 销毁单个
                await sandbox.destroy_session("vm")
                
                # 销毁多个
                await sandbox.destroy_session(["vm", "rag"])
                
                # 销毁所有
                await sandbox.destroy_session()
            ```
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        results = {}
        
        if resources is None:
            # 销毁所有 session
            sessions = await self._client.list_sessions()
            resource_list = [s.get("resource_type") for s in sessions.get("sessions", [])]
        elif isinstance(resources, str):
            resource_list = [resources]
        else:
            resource_list = resources
        
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
        """销毁 Session（同步版本）"""
        return self._run_async(self.destroy_session(resources))
    
    # ========================================================================
    # List Sessions
    # ========================================================================
    
    async def list_sessions(self) -> Dict[str, Any]:
        """
        列出当前所有 Session
        
        Returns:
            Session 列表
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        return await self._client.list_sessions()
    
    def list_sessions_sync(self) -> Dict[str, Any]:
        """列出当前所有 Session（同步版本）"""
        return self._run_async(self.list_sessions())
    
    # ========================================================================
    # Execute - 主入口
    # ========================================================================
    
    async def execute(
        self, 
        action: str, 
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行动作 - 主入口
        
        Args:
            action: 动作名称，如 "search", "vm:screenshot", "rag:search"
            params: 动作参数
            **kwargs: 额外参数（将并入 params 传给后端工具）
            timeout: 超时时间（秒）
            
        Returns:
            执行结果
            
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
        """执行动作（同步版本）"""
        return self._run_async(self.execute(action, params, timeout))
    
    # ========================================================================
    # Reinitialize - 重新初始化资源
    # ========================================================================
    
    async def reinitialize(
        self,
        resource_type: str,
        new_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        重新初始化指定资源（不影响其他资源）
        
        先销毁该资源的现有 session，然后用新配置重新创建。
        
        Args:
            resource_type: 要重新初始化的资源类型
            new_config: 新的配置参数
            
        Returns:
            重新初始化结果
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        reinit_start = time.time()
        
        # 销毁现有 session
        old_session = None
        try:
            destroy_result = await self._client.destroy_session(resource_type)
            old_session = destroy_result.get("session_id")
            logger.info(f"🔄 Reinitialize {resource_type}: destroyed old session")
        except Exception:
            logger.debug(f"🔄 Reinitialize {resource_type}: no existing session")
        
        # 创建新 session
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
        """重新初始化资源（同步版本）"""
        return self._run_async(self.reinitialize(resource_type, new_config))
    
    # ========================================================================
    # Refresh Sessions - 保活
    # ========================================================================
    
    async def refresh_sessions(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        刷新 Session 存活时间
        
        Args:
            resource_type: 资源类型（可选，不指定则刷新所有）
            
        Returns:
            刷新结果
        """
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        
        return await self._client.refresh_session(resource_type)
    
    def refresh_sessions_sync(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """刷新 Session 存活时间（同步版本）"""
        return self._run_async(self.refresh_sessions(resource_type))
    
    # ========================================================================
    # Context Managers
    # ========================================================================
    
    def __enter__(self) -> "Sandbox":
        """同步上下文管理器入口"""
        self.start_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步上下文管理器退出"""
        self.close_sync()
    
    async def __aenter__(self) -> "Sandbox":
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
    
    # ========================================================================
    # Close
    # ========================================================================
    
    async def close(self):
        """关闭连接"""
        if not self._connected:
            return
        
        if self._client:
            await self._client.close()
            self._client = None
        
        self._connected = False
        self._started = False
        logger.info(f"👋 Sandbox closed (worker_id: {self.worker_id})")
    
    def close_sync(self):
        """关闭连接（同步版本）"""
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
        关闭连接的服务器
        
        Args:
            force: 是否强制关闭
            cleanup_sessions: 关闭前是否清理所有 session
            
        Returns:
            关闭结果
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
        """关闭服务器（同步版本）"""
        return self._run_async(self.shutdown_server(force, cleanup_sessions))
    
    # ========================================================================
    # Server Management (Internal)
    # ========================================================================
    
    async def _check_server_online_async(self) -> bool:
        """检查服务器是否在线"""
        import httpx
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.server_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    def _check_server_online(self) -> bool:
        """检查服务器是否在线（同步）"""
        import httpx
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.server_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    def _start_server(self):
        """启动服务器"""
        config = self._load_server_config()
        
        from urllib.parse import urlparse
        parsed = urlparse(self.server_url)
        port = parsed.port or 18890
        host = parsed.hostname or "0.0.0.0"
        
        server_script = self._generate_server_script(config, host, port)
        
        # 创建日志文件用于捕获服务器输出（调试用）
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
            stderr=subprocess.STDOUT,  # stderr 合并到 stdout
            start_new_session=True
        )
        self._server_started_by_us = True
        
        logger.info(f"✅ Server starting on {self.server_url}")
        logger.debug(f"📝 Server log: {self._server_log_file.name}")
    
    async def _wait_for_server_async(self):
        """等待服务器启动完成"""
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
        获取服务器日志（用于调试）
        
        Args:
            tail_lines: 返回最后多少行日志
            
        Returns:
            服务器日志内容，如果没有日志文件则返回 None
        """
        if not self._server_log_file:
            return None
        
        try:
            # 刷新并读取日志
            self._server_log_file.flush()
            log_path = self._server_log_file.name
            
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                if tail_lines and len(lines) > tail_lines:
                    lines = lines[-tail_lines:]
                return ''.join(lines)
        except Exception as e:
            return f"[读取日志失败: {e}]"
    
    def _load_server_config(self) -> Dict[str, Any]:
        """加载服务器配置"""
        config_path = self._config.server_config_path
        
        if config_path:
            # 尝试加载配置文件
            if os.path.exists(config_path):
                logger.info(f"📄 Loading config from: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                resources = [k for k in config.get("resources", {}).keys() if not k.startswith("_")]
                logger.info(f"   Resources in config: {resources}")
                return config
            else:
                # 配置文件路径指定了但不存在
                logger.warning(f"⚠️ Config file not found: {config_path}")
                logger.warning(f"   Current working directory: {os.getcwd()}")
                logger.warning(f"   Absolute path would be: {os.path.abspath(config_path)}")
        
        # 使用默认配置
        logger.info("📄 Using DEFAULT_SERVER_CONFIG")
        default_config = DEFAULT_SERVER_CONFIG.copy()
        resources = [k for k in default_config.get("resources", {}).keys() if not k.startswith("_")]
        logger.info(f"   Resources in default config: {resources}")
        return default_config
    
    def _generate_server_script(self, config: Dict[str, Any], host: str, port: int) -> str:
        """
        生成服务器启动脚本
        
        生成的脚本支持:
        - 加载重资源后端 (resources 配置部分)
        - 加载轻资源工具 (apis 配置部分)
        """
        config_json = json.dumps(config)
        
        script = f'''
import sys
sys.path.insert(0, "{Path(__file__).parent.parent.absolute()}")

import json
import logging
import importlib
import traceback

# 配置日志同时输出到 stderr（确保能被看到）
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("SandboxServer")

# 打印启动信息
logger.info("=" * 60)
logger.info("🚀 Sandbox Server 启动中...")
logger.info("=" * 60)

from sandbox import HTTPServiceServer
from sandbox.server.backends.tools import register_all_tools
from sandbox.server.backends.base import BackendConfig

config = json.loads({repr(config_json)})

# 打印配置摘要
resources_names = [k for k in config.get("resources", {{}}).keys() if not k.startswith("_")]
logger.info(f"📋 配置中的 resources: {{resources_names}}")

server = HTTPServiceServer(
    host="{host}",
    port={port},
    title=config.get("server", {{}}).get("title", "Sandbox HTTP Service"),
    description=config.get("server", {{}}).get("description", ""),
    session_ttl=config.get("server", {{}}).get("session_ttl", 300)
)

# ============================================================================
# 1. 注册重资源后端 (resources)
# ============================================================================
resources_config = config.get("resources", {{}})
loaded_backends = []
failed_backends = []

for name, res_config in resources_config.items():
    # 跳过注释字段
    if name.startswith("_"):
        continue
    
    # 检查是否启用
    if not res_config.get("enabled", True):
        logger.info(f"⏭️ Skipping disabled resource: {{name}}")
        continue
    
    # 获取后端类路径
    backend_class_path = res_config.get("backend_class")
    if not backend_class_path:
        logger.warning(f"⚠️ Resource '{{name}}' has no backend_class, skipping")
        continue
    
    try:
        # 动态加载后端类
        logger.info(f"📦 Loading backend: {{name}} ({{backend_class_path}})")
        module_path, class_name = backend_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        backend_cls = getattr(module, class_name)
        
        # 创建后端配置
        backend_config = BackendConfig(
            enabled=True,
            default_config=res_config.get("config", {{}}),
            description=res_config.get("description", "")
        )
        
        # 实例化并加载后端
        backend = backend_cls(config=backend_config)
        tools = server.load_backend(backend)
        
        loaded_backends.append(name)
        logger.info(f"✅ Loaded backend: {{name}} ({{len(tools)}} tools)")
        
    except Exception as e:
        failed_backends.append(name)
        logger.error(f"❌ Failed to register backend '{{name}}': {{e}}")
        logger.error(traceback.format_exc())

# 打印加载结果摘要
logger.info("=" * 60)
logger.info(f"📊 后端加载结果: {{len(loaded_backends)}} 成功, {{len(failed_backends)}} 失败")
if loaded_backends:
    logger.info(f"   ✅ 已加载: {{loaded_backends}}")
if failed_backends:
    logger.error(f"   ❌ 失败: {{failed_backends}}")

# ============================================================================
# 2. 注册轻资源工具 (apis)
# ============================================================================
apis_config = config.get("apis", {{}})
if apis_config:
    logger.info(f"📦 Registering API tools: {{list(apis_config.keys())}}")
register_all_tools(server, apis_config)

# 启动服务器
server.run()
'''
        return script
    
    def _create_client(self):
        """创建 HTTPServiceClient"""
        client_config = HTTPClientConfig(
            base_url=self._config.server_url,
            timeout=self._config.timeout,
            max_retries=self._config.retry_count,
            worker_id=self._config.worker_id,
            auto_heartbeat=False
        )
        self._client = HTTPServiceClient(config=client_config)
    
    def _run_async(self, coro) -> Any:
        """在同步上下文中运行异步代码"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    async def get_tools(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        return await self._client.list_tools(include_hidden)
    
    def get_tools_sync(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """获取可用工具列表（同步版本）"""
        return self._run_async(self.get_tools(include_hidden))
    
    async def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        if not self._started or self._client is None:
            raise SandboxConnectionError("Not started. Call start() first.")
        return await self._client.get_status()
    
    def get_status_sync(self) -> Dict[str, Any]:
        """获取当前状态（同步版本）"""
        return self._run_async(self.get_status())
    
    def get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return self._load_server_config()
    
    def save_server_config(self, config: Dict[str, Any], path: str):
        """保存服务器配置到文件"""
        with open(path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Server config saved to {path}")
    
    @staticmethod
    def create_config_template(path: str):
        """创建配置模板文件"""
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
    """创建 Sandbox 实例的便捷函数"""
    return Sandbox(server_url=server_url, **kwargs)


def get_default_config() -> Dict[str, Any]:
    """获取默认服务器配置"""
    return DEFAULT_SERVER_CONFIG.copy()
