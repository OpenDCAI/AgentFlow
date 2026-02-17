# sandbox/protocol.py
"""
HTTP Protocol Definition - Standalone HTTP protocol definition module

JSON-based HTTP protocol definitions, fully independent of other modules.
Pydantic models are used consistently and shared by both Server and Client.

Message categories:
1. Lifecycle management (lifecycle) - health/status checks
2. Execution (execute) - tool invocation with optional resource prefix like vm:action
3. Session management (session) - create/destroy long-lived sessions
4. Initialization (initialize) - resource initialization configs
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Message type enum."""
    # Execution (supports resource-type prefixes)
    EXECUTE = "execute"
    EXECUTE_BATCH = "execute:batch"
    
    # Session management
    SESSION_CREATE = "session:create"
    SESSION_DESTROY = "session:destroy"
    SESSION_LIST = "session:list"
    SESSION_REFRESH = "session:refresh"
    
    # Initialization
    INIT_RESOURCE = "init:resource"
    INIT_BATCH = "init:batch"
    INIT_FROM_CONFIG = "init:from_config"


class BaseMessage(BaseModel):
    """Base message structure."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    worker_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        """Allow extra fields to keep backward compatibility."""
        extra = "ignore"
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
    
    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseMessage":
        return cls(**data)


# ============================================================================
# Execution request models
# ============================================================================

class ExecuteRequest(BaseMessage):
    """
    Execute request.

    The action field supports resource-type prefixes in the format:
    "resource_type:action_name"

    Examples:
    - "vm:screenshot" -> execute screenshot using VM
    - "rag:search" -> execute search using RAG
    - "TextSearch" -> no prefix; resolved from worker context
    """
    message_type: str = MessageType.EXECUTE.value
    # Use type: ignore to allow overriding Optional[str] in BaseMessage with required str.
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    action: str = Field(..., description="Action name, supports resource_type:action format")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    timeout: Optional[int] = Field(default=None, description="Execution timeout in seconds")
    async_mode: bool = False  # Whether to execute asynchronously
    
    def get_resource_type(self) -> Optional[str]:
        """Parse the resource-type prefix from action."""
        if ":" in self.action:
            prefix = self.action.split(":")[0]
            return prefix
        return None
    
    def get_action_name(self) -> str:
        """Get the actual action name without resource prefix."""
        if ":" in self.action:
            return self.action.split(":", 1)[1]
        return self.action


class ExecuteBatchRequest(BaseMessage):
    """Batch execute request."""
    message_type: str = MessageType.EXECUTE_BATCH.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    actions: List[Dict[str, Any]] = Field(..., description="Action list")
    # Each action format: {"action": "resource:name", "params": {...}, "timeout": ...}
    parallel: bool = Field(default=False, description="Whether to execute actions in parallel")
    stop_on_error: bool = Field(default=True, description="Whether to stop when any action fails")


# ============================================================================
# Session management models
# ============================================================================

class SessionCreateRequest(BaseMessage):
    """
    Session create request.
    Used for resources that require long-lived context.
    """
    message_type: str = MessageType.SESSION_CREATE.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_type: str = Field(..., description="Resource type")
    session_config: Dict[str, Any] = Field(default_factory=dict, description="Session configuration")
    ttl: int = 300  # Session time-to-live in seconds (default: 5 minutes)
    auto_extend: bool = True  # Auto-extend TTL when session is active


class SessionDestroyRequest(BaseMessage):
    """Session destroy request."""
    message_type: str = MessageType.SESSION_DESTROY.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_type: str = Field(..., description="Resource type")
    target_session_id: Optional[str] = None  # Target session to destroy; None means current


class SessionListRequest(BaseMessage):
    """Session list request."""
    message_type: str = MessageType.SESSION_LIST.value
    resource_type: Optional[str] = None  # Filter by specific resource type


class SessionRefreshRequest(BaseMessage):
    """Session refresh request."""
    message_type: str = MessageType.SESSION_REFRESH.value
    target_session_id: Optional[str] = None
    extend_ttl: int = 300


class WorkerDisconnectRequest(BaseMessage):
    """Worker disconnect request."""
    worker_id: str = Field(..., description="Worker ID")  # type: ignore


# ============================================================================
# Initialization models
# ============================================================================

class InitResourceRequest(BaseMessage):
    """
    Resource initialization request.
    Used to re-initialize a resource with a JSON config payload.
    """
    message_type: str = MessageType.INIT_RESOURCE.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_type: str = Field(..., description="Resource type")
    init_config: Dict[str, Any] = Field(default_factory=dict, description="Initialization config")
    # init_config can be inline content or a config-file reference


class InitBatchRequest(BaseMessage):
    """Batch initialization request."""
    message_type: str = MessageType.INIT_BATCH.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Resource configurations")
    # Format: {"resource_type": {"content": {...}, "config_file": "path/to/config.json"}}
    allocated_resources: Dict[str, Any] = Field(default_factory=dict)
    task_session_id: Optional[str] = None


class InitFromConfigRequest(BaseMessage):
    """Initialize from configuration file."""
    message_type: str = MessageType.INIT_FROM_CONFIG.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    config_path: str = Field(..., description="Configuration file path")
    override_params: Dict[str, Any] = Field(default_factory=dict, description="Override parameters")


# ============================================================================
# HTTP endpoint definitions
# ============================================================================

class HTTPEndpoints:
    """HTTP API endpoint constants."""
    HEARTBEAT = "/api/v1/lifecycle/heartbeat"
    STATUS = "/api/v1/lifecycle/status"
    
    # Execution
    EXECUTE = "/api/v1/execute"
    EXECUTE_BATCH = "/api/v1/execute/batch"
    
    # Session management
    SESSION_CREATE = "/api/v1/session/create"
    SESSION_DESTROY = "/api/v1/session/destroy"
    SESSION_LIST = "/api/v1/session/list"
    SESSION_REFRESH = "/api/v1/session/refresh"
    
    # Initialization
    INIT_RESOURCE = "/api/v1/init/resource"
    INIT_BATCH = "/api/v1/init/batch"
    INIT_FROM_CONFIG = "/api/v1/init/from-config"
    
    # Tool metadata
    TOOLS_LIST = "/api/v1/tools"
    
    # Health checks
    HEALTH = "/health"
    READY = "/ready"
    
    # Server control
    SHUTDOWN = "/api/v1/server/shutdown"
    
    # Warmup
    WARMUP = "/api/v1/warmup"
    WARMUP_STATUS = "/api/v1/warmup/status"


