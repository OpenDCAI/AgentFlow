import logging
import asyncio
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from ..error_codes import ErrorCode
from ..response_builder import build_success_response, build_error_response, ResponseTimer

logger = logging.getLogger("ApiTools")

class ToolBusinessError(Exception):
    """
    业务逻辑预期内的错误。
    抛出此异常将导致返回 EXECUTION_ERROR 或自定义错误码。
    """
    def __init__(self, message: str, code: ErrorCode = ErrorCode.EXECUTION_ERROR, data: Any = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)

class BaseApiTool(ABC):
    """
    API 工具基类。
    负责处理所有基础设施逻辑：计时、日志、错误捕获、响应构建。
    """
    def __init__(self, tool_name: str = "unknown_tool", resource_type: str = "unknown"):
        """
        Args:
            tool_name: 工具名称 (如 "search", "visit")。
                       如果为 "unknown_tool"，注册时会自动被装饰器中的 name 覆盖。
            resource_type: 资源类型 (如 "websearch", "database")
        """
        self.tool_name = tool_name
        self.resource_type = resource_type
        self._config: Dict[str, Any] = {}  # 配置在注册时注入
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        设置工具配置（由注册器在注册时调用）
        
        Args:
            config: 从配置文件中提取的配置字典
        """
        self._config = config.copy() if config else {}
        logger.debug(f"[{self.tool_name}] Config injected: {list(self._config.keys())}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值，如果不存在则返回默认值
        """
        return self._config.get(key, default)
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置字典（只读副本）"""
        return self._config.copy()

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        【必须实现】核心业务逻辑。
        
        Args:
            **kwargs: 包含传递给工具的所有参数 (query, urls, goal, config等)
            
        Returns:
            Any: 业务处理成功后的结果数据。
            
        Raises:
            ToolBusinessError: 当发生业务错误时抛出。
            Exception: 当发生意外错误时抛出（会被基类捕获）。
        """
        pass

    def _sanitize_inputs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗输入参数，用于日志记录和响应回显。
        子类可以重写此方法以自定义参数处理逻辑。
        """
        # 默认过滤列表
        sensitive_keys = {
            'config', 'api_key', 'jina_api_key', 
            'serper_api_key', 'openai_api_key', 'session_info',
            'session_id', 'trace_id' # session_id/trace_id 已在 meta 中，inputs 里可以省去
        }
        
        sanitized = {}
        for k, v in kwargs.items():
            if k in sensitive_keys:
                continue
            
            # 处理特殊类型，确保 JSON 可序列化
            if isinstance(v, (str, int, float, bool, type(None))):
                if isinstance(v, str) and len(v) > 500:
                    sanitized[k] = v[:500] + "...[Truncated]"
                else:
                    sanitized[k] = v
            elif isinstance(v, (list, tuple)):
                # 列表只展示前 10 个
                if len(v) > 10:
                    sanitized[k] = f"List(len={len(v)})"
                else:
                    # 简单递归转 str，防止列表内有复杂对象
                    sanitized[k] = [str(i) if not isinstance(i, (str, int, float, bool, type(None))) else i for i in v]
            elif isinstance(v, dict):
                 # 字典简单摘要
                 if len(v) > 10:
                     sanitized[k] = f"Dict(len={len(v)})"
                 else:
                     sanitized[k] = {str(sk): str(sv) for sk, sv in v.items()}
            else:
                # 其他对象转字符串
                sanitized[k] = str(v)
                
        return sanitized

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        基础设施包装器。使得实例可以直接被调用。
        它被注册的 API 工具执行器调用。
        """
        # 尝试从 kwargs 中提取 session_id 和 trace_id，如果存在
        session_id = kwargs.get('session_id')
        trace_id = kwargs.get('trace_id')
        
        # 提取关键参数用于日志，避免日志过大或泄露敏感信息
        log_params = self._sanitize_inputs(kwargs)
        
        with ResponseTimer() as timer:
            try:
                logger.info(f"🚀 [{self.tool_name}] Started. Params: {log_params}")
                
                # 执行子类的业务逻辑
                # 直接传递所有 kwargs，包括 session_id 等，由 execute 自行决定是否使用
                result_data = await self.execute(**kwargs)

                # 构建成功响应
                # 自动将输入参数放入 data.inputs 中以便调试
                response_data = {
                    "result": result_data,
                    "inputs": log_params
                }
                
                # 如果业务逻辑返回的是字典且不想被嵌套在 result 中，这里可以做更复杂的处理
                # 但为了统一，我们默认放在 result 字段下。
                # 除非业务逻辑返回的已经是 {result: ..., warning: ...} 这种结构
                if isinstance(result_data, dict) and "result" in result_data:
                    # 如果返回结构已经包含 result，则合并
                    response_data = {**result_data, "inputs": log_params}

                return build_success_response(
                    data=response_data,
                    tool=self.tool_name,
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type=self.resource_type,
                    session_id=session_id,
                    trace_id=trace_id
                )

            except ToolBusinessError as e:
                # 捕获预期的业务错误
                logger.warning(f"⚠️ [{self.tool_name}] Business Error: {e.message}")
                return build_error_response(
                    code=e.code,
                    message=e.message,
                    tool=self.tool_name,
                    data={
                        "inputs": log_params,
                        "details": e.data if e.data else e.message
                    },
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type=self.resource_type,
                    session_id=session_id,
                    trace_id=trace_id
                )

            except Exception as e:
                # 捕获未预期的系统崩溃
                logger.error(f"❌ [{self.tool_name}] Unexpected Error: {e}", exc_info=True)
                return build_error_response(
                    code=ErrorCode.EXECUTION_ERROR,
                    message=f"Internal system error: {str(e)}",
                    tool=self.tool_name,
                    data={
                        "inputs": log_params,
                        "details": str(e)
                    },
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type=self.resource_type,
                    session_id=session_id,
                    trace_id=trace_id
                )

