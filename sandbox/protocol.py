# sandbox/protocol.py
"""
HTTP Protocol Definition - 独立的HTTP协议定义模块

基于JSON的HTTP协议定义，完全独立于任何其他模块。
统一使用 Pydantic 模型定义，供 Server 和 Client 共同参考。

消息类型:
1. 生命周期管理 (lifecycle) - 资源分配、释放、健康检查
2. 执行信息 (execute) - 工具调用，支持资源类型前缀如 vm:action
3. 会话管理 (session) - 创建/销毁长期会话
4. 初始化 (initialize) - 资源初始化配置
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import uuid

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """消息类型枚举"""
    # 生命周期管理
    LIFECYCLE_ALLOCATE = "lifecycle:allocate"
    LIFECYCLE_RELEASE = "lifecycle:release"
    LIFECYCLE_HEARTBEAT = "lifecycle:heartbeat"
    LIFECYCLE_STATUS = "lifecycle:status"
    
    # 执行信息 (支持资源类型前缀)
    EXECUTE = "execute"
    EXECUTE_BATCH = "execute:batch"
    
    # 会话管理
    SESSION_CREATE = "session:create"
    SESSION_DESTROY = "session:destroy"
    SESSION_LIST = "session:list"
    SESSION_REFRESH = "session:refresh"
    
    # 初始化
    INIT_RESOURCE = "init:resource"
    INIT_BATCH = "init:batch"
    INIT_FROM_CONFIG = "init:from_config"
    
    # 响应
    RESPONSE = "response"
    ERROR = "error"


class ResourceType(str, Enum):
    """
    资源类型枚举
    
    可以根据实际需求扩展更多资源类型
    """
    VM_PYAUTOGUI = "vm_pyautogui"
    VM_COMPUTER_13 = "vm_computer_13"
    RAG = "rag"
    RAG_HYBRID = "rag_hybrid"
    SEARCH = "search"
    CUSTOM = "custom"  # 自定义资源类型
    
    @classmethod
    def from_string(cls, value: str) -> "ResourceType":
        """从字符串解析资源类型，支持未注册的类型"""
        try:
            return cls(value)
        except ValueError:
            return cls.CUSTOM


class BaseMessage(BaseModel):
    """基础消息结构"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    worker_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        """允许额外字段，保持兼容性"""
        extra = "ignore"
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
    
    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseMessage":
        return cls(**data)


# ============================================================================
# 生命周期管理消息
# ============================================================================

class LifecycleAllocateRequest(BaseMessage):
    """资源分配请求"""
    message_type: str = MessageType.LIFECYCLE_ALLOCATE.value
    resource_types: List[str] = Field(default_factory=list)
    timeout: int = 600  # 等待超时时间（秒）
    priority: int = 0  # 优先级，数值越大优先级越高


class LifecycleReleaseRequest(BaseMessage):
    """资源释放请求"""
    message_type: str = MessageType.LIFECYCLE_RELEASE.value
    resource_ids: List[str] = Field(default_factory=list)
    force: bool = False  # 是否强制释放


class LifecycleHeartbeatRequest(BaseMessage):
    """心跳请求"""
    message_type: str = MessageType.LIFECYCLE_HEARTBEAT.value
    resource_ids: List[str] = Field(default_factory=list)


class LifecycleStatusRequest(BaseMessage):
    """状态查询请求"""
    message_type: str = MessageType.LIFECYCLE_STATUS.value
    resource_ids: Optional[List[str]] = None  # None表示查询所有


# ============================================================================
# 执行信息消息
# ============================================================================

class ExecuteRequest(BaseMessage):
    """
    执行请求
    
    action字段支持资源类型前缀，格式: "resource_type:action_name"
    例如:
    - "vm:screenshot" -> 使用VM执行screenshot操作
    - "rag:search" -> 使用RAG执行search操作
    - "TextSearch" -> 无前缀，根据worker_id上下文确定资源
    """
    message_type: str = MessageType.EXECUTE.value
    # 使用 type: ignore 忽略类型覆盖警告，因为我们需要强制 worker_id 为必填
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    action: str = Field(..., description="动作名称，支持 resource_type:action 格式")
    params: Dict[str, Any] = Field(default_factory=dict, description="动作参数")
    timeout: Optional[int] = Field(default=None, description="执行超时时间")
    async_mode: bool = False  # 是否异步执行
    
    def get_resource_type(self) -> Optional[str]:
        """解析资源类型前缀"""
        if ":" in self.action:
            prefix = self.action.split(":")[0]
            return prefix
        return None
    
    def get_action_name(self) -> str:
        """获取实际的action名称"""
        if ":" in self.action:
            return self.action.split(":", 1)[1]
        return self.action


class ExecuteBatchRequest(BaseMessage):
    """批量执行请求"""
    message_type: str = MessageType.EXECUTE_BATCH.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    actions: List[Dict[str, Any]] = Field(..., description="动作列表")
    # 每个action格式: {"action": "resource:name", "params": {...}, "timeout": ...}
    parallel: bool = Field(default=False, description="是否并行执行")
    stop_on_error: bool = Field(default=True, description="遇到错误是否停止")


# ============================================================================
# 会话管理消息
# ============================================================================

class SessionCreateRequest(BaseMessage):
    """
    会话创建请求
    用于需要长期保持上下文的资源
    """
    message_type: str = MessageType.SESSION_CREATE.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_type: str = Field(..., description="资源类型")
    session_config: Dict[str, Any] = Field(default_factory=dict, description="Session配置")
    ttl: int = 300  # 会话生存时间（秒），默认5分钟
    auto_extend: bool = True  # 活动时自动延长TTL


class SessionDestroyRequest(BaseMessage):
    """会话销毁请求"""
    message_type: str = MessageType.SESSION_DESTROY.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_type: str = Field(..., description="资源类型")
    target_session_id: Optional[str] = None  # 要销毁的session，None则销毁当前


class SessionListRequest(BaseMessage):
    """会话列表请求"""
    message_type: str = MessageType.SESSION_LIST.value
    resource_type: Optional[str] = None  # 过滤特定资源类型


class SessionRefreshRequest(BaseMessage):
    """会话刷新请求"""
    message_type: str = MessageType.SESSION_REFRESH.value
    target_session_id: Optional[str] = None
    extend_ttl: int = 300


class WorkerDisconnectRequest(BaseMessage):
    """Worker断开连接请求"""
    worker_id: str = Field(..., description="Worker ID")  # type: ignore


# ============================================================================
# 初始化消息
# ============================================================================

class InitResourceRequest(BaseMessage):
    """
    资源初始化请求
    用于资源重新初始化，内部传递JSON配置
    """
    message_type: str = MessageType.INIT_RESOURCE.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_type: str = Field(..., description="资源类型")
    init_config: Dict[str, Any] = Field(default_factory=dict, description="初始化配置")
    # init_config 可以是具体配置或引用配置文件路径


class InitBatchRequest(BaseMessage):
    """批量初始化请求"""
    message_type: str = MessageType.INIT_BATCH.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    resource_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="资源配置")
    # 格式: {"resource_type": {"content": {...}, "config_file": "path/to/config.json"}}
    allocated_resources: Dict[str, Any] = Field(default_factory=dict)
    task_session_id: Optional[str] = None


class InitFromConfigRequest(BaseMessage):
    """从配置文件初始化"""
    message_type: str = MessageType.INIT_FROM_CONFIG.value
    worker_id: str = Field(..., description="Worker ID")  # type: ignore
    config_path: str = Field(..., description="配置文件路径")
    override_params: Dict[str, Any] = Field(default_factory=dict, description="覆盖参数")


# ============================================================================
# 响应消息
# ============================================================================

class Response(BaseMessage):
    """统一响应结构"""
    message_type: str = MessageType.RESPONSE.value
    code: int = 200
    data: Any = None
    error: Optional[str] = None
    request_id: Optional[str] = None  # 对应请求的message_id
    execution_time_ms: Optional[float] = None
    
    @classmethod
    def success_response(cls, data: Any, request_id: Optional[str] = None, 
                         execution_time_ms: Optional[float] = None) -> "Response":
        return cls(
            code=200,
            data=data,
            request_id=request_id,
            execution_time_ms=execution_time_ms
        )
    
    @classmethod
    def error_response(cls, error: str, code: int = 500, 
                       request_id: Optional[str] = None) -> "Response":
        return cls(
            code=code,
            error=error,
            request_id=request_id
        )


# ============================================================================
# 消息解析工具
# ============================================================================

MESSAGE_TYPE_MAP = {
    MessageType.LIFECYCLE_ALLOCATE.value: LifecycleAllocateRequest,
    MessageType.LIFECYCLE_RELEASE.value: LifecycleReleaseRequest,
    MessageType.LIFECYCLE_HEARTBEAT.value: LifecycleHeartbeatRequest,
    MessageType.LIFECYCLE_STATUS.value: LifecycleStatusRequest,
    MessageType.EXECUTE.value: ExecuteRequest,
    MessageType.EXECUTE_BATCH.value: ExecuteBatchRequest,
    MessageType.SESSION_CREATE.value: SessionCreateRequest,
    MessageType.SESSION_DESTROY.value: SessionDestroyRequest,
    MessageType.SESSION_LIST.value: SessionListRequest,
    MessageType.SESSION_REFRESH.value: SessionRefreshRequest,
    MessageType.INIT_RESOURCE.value: InitResourceRequest,
    MessageType.INIT_BATCH.value: InitBatchRequest,
    MessageType.INIT_FROM_CONFIG.value: InitFromConfigRequest,
    MessageType.RESPONSE.value: Response,
}


def parse_message(data: Union[str, Dict[str, Any]]) -> BaseMessage:
    """
    解析JSON消息为对应的消息对象
    
    Args:
        data: JSON字符串或字典
        
    Returns:
        对应的消息对象
        
    Raises:
        ValueError: 无法解析的消息类型
    """
    parsed_data: Dict[str, Any]
    if isinstance(data, str):
        parsed_data = json.loads(data)
    else:
        parsed_data = data
    
    message_type = parsed_data.get("message_type", "")
    
    if message_type in MESSAGE_TYPE_MAP:
        cls = MESSAGE_TYPE_MAP[message_type]
        # Pydantic 会自动过滤掉不需要的字段（如果配置了ignore），或者我们可以手动过滤
        # 这里直接传入，依赖 Pydantic 的验证
        return cls(**parsed_data)
    
    # 未知消息类型，返回基础消息
    return BaseMessage(**parsed_data)


def create_execute_request(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    worker_id: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout: Optional[int] = None,
    async_mode: bool = False
) -> ExecuteRequest:
    """
    创建执行请求的便捷函数
    
    Args:
        action: 动作名称，支持 "resource_type:action" 格式
        params: 动作参数
        worker_id: Worker ID
        session_id: Session ID
        timeout: 超时时间
        async_mode: 是否异步执行
        
    Returns:
        ExecuteRequest对象
    """
    return ExecuteRequest(
        action=action,
        params=params or {},
        worker_id=worker_id or "",  # Pydantic 模型要求 worker_id 必填，这里给空字符串或需要调用者保证
        session_id=session_id,
        timeout=timeout,
        async_mode=async_mode
    )


# ============================================================================
# HTTP端点定义
# ============================================================================

class HTTPEndpoints:
    """HTTP API端点定义"""
    
    # 生命周期管理
    ALLOCATE = "/api/v1/lifecycle/allocate"
    RELEASE = "/api/v1/lifecycle/release"
    HEARTBEAT = "/api/v1/lifecycle/heartbeat"
    STATUS = "/api/v1/lifecycle/status"
    
    # 执行
    EXECUTE = "/api/v1/execute"
    EXECUTE_BATCH = "/api/v1/execute/batch"
    
    # 会话管理
    SESSION_CREATE = "/api/v1/session/create"
    SESSION_DESTROY = "/api/v1/session/destroy"
    SESSION_LIST = "/api/v1/session/list"
    SESSION_REFRESH = "/api/v1/session/refresh"
    
    # 初始化
    INIT_RESOURCE = "/api/v1/init/resource"
    INIT_BATCH = "/api/v1/init/batch"
    INIT_FROM_CONFIG = "/api/v1/init/from-config"
    
    # 工具元信息
    TOOLS_LIST = "/api/v1/tools"
    TOOLS_SCHEMA = "/api/v1/tools/{tool_name}/schema"
    
    # 健康检查
    HEALTH = "/health"
    READY = "/ready"
    
    # 服务器控制
    SHUTDOWN = "/api/v1/server/shutdown"
    
    # 预热
    WARMUP = "/api/v1/warmup"
    WARMUP_STATUS = "/api/v1/warmup/status"


