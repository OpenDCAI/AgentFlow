import logging
import asyncio
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from ..error_codes import ErrorCode
from ..response_builder import build_success_response, build_error_response, ResponseTimer

logger = logging.getLogger("ApiTools")

class ToolBusinessError(Exception):
    """
    Expected business logic error.
    Throwing this exception will result in returning EXECUTION_ERROR or a custom error code.
    """
    def __init__(self, message: str, code: ErrorCode = ErrorCode.EXECUTION_ERROR, data: Any = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)

class BaseApiTool(ABC):
    """
    API tool base class.
    Handles all infrastructure logic: timing, logging, error handling, response building.
    """
    def __init__(self, tool_name: str = "unknown_tool", resource_type: str = "unknown"):
        """
        Args:
            tool_name: Tool name (e.g., "search", "visit").
                       If "unknown_tool", it will be automatically overridden by the name in the decorator during registration.
            resource_type: Resource type (e.g., "websearch", "database")
        """
        self.tool_name = tool_name
        self.resource_type = resource_type
        self._config: Dict[str, Any] = {}  # Config injected during registration
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set tool configuration (called by registrar during registration)
        
        Args:
            config: Configuration dictionary extracted from config file
        """
        self._config = config.copy() if config else {}
        logger.debug(f"[{self.tool_name}] Config injected: {list(self._config.keys())}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration item
        
        Args:
            key: Configuration key name
            default: Default value
            
        Returns:
            Configuration value, returns default if not found
        """
        return self._config.get(key, default)
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary (read-only copy)"""
        return self._config.copy()

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        [Must implement] Core business logic.
        
        Args:
            **kwargs: Contains all parameters passed to the tool (query, urls, goal, config, etc.)
            
        Returns:
            Any: Result data after successful business processing.
            
        Raises:
            ToolBusinessError: Raised when a business error occurs.
            Exception: Raised when an unexpected error occurs (will be caught by base class).
        """
        pass

    def _sanitize_inputs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input parameters for logging and response echo.
        Subclasses can override this method to customize parameter processing logic.
        """
        # Default filter list
        sensitive_keys = {
            'config', 'api_key', 'jina_api_key', 
            'serper_api_key', 'openai_api_key', 'session_info',
            'session_id', 'trace_id'  # session_id/trace_id already in meta, can be omitted from inputs
        }
        
        sanitized = {}
        for k, v in kwargs.items():
            if k in sensitive_keys:
                continue
            
            # Handle special types to ensure JSON serializable
            if isinstance(v, (str, int, float, bool, type(None))):
                if isinstance(v, str) and len(v) > 500:
                    sanitized[k] = v[:500] + "...[Truncated]"
                else:
                    sanitized[k] = v
            elif isinstance(v, (list, tuple)):
                # Only show first 10 items in list
                if len(v) > 10:
                    sanitized[k] = f"List(len={len(v)})"
                else:
                    # Simple recursive conversion to str to prevent complex objects in list
                    sanitized[k] = [str(i) if not isinstance(i, (str, int, float, bool, type(None))) else i for i in v]
            elif isinstance(v, dict):
                 # Simple summary for dict
                 if len(v) > 10:
                     sanitized[k] = f"Dict(len={len(v)})"
                 else:
                     sanitized[k] = {str(sk): str(sv) for sk, sv in v.items()}
            else:
                # Convert other objects to string
                sanitized[k] = str(v)
                
        return sanitized

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Infrastructure wrapper. Makes the instance directly callable.
        Called by the registered API tool executor.
        """
        # Try to extract session_id and trace_id from kwargs if they exist
        session_id = kwargs.get('session_id')
        trace_id = kwargs.get('trace_id')
        
        # Extract key parameters for logging, avoid logs being too large or leaking sensitive information
        log_params = self._sanitize_inputs(kwargs)
        
        with ResponseTimer() as timer:
            try:
                logger.info(f"🚀 [{self.tool_name}] Started. Params: {log_params}")
                
                # Execute subclass business logic
                # Pass all kwargs directly, including session_id, etc., let execute decide whether to use them
                result_data = await self.execute(**kwargs)

                # Build success response
                # Automatically put input parameters into data.inputs for debugging
                response_data = {
                    "result": result_data,
                    "inputs": log_params
                }
                
                # If business logic returns a dict and doesn't want to be nested in result, more complex processing can be done here
                # But for consistency, we default to putting it under the result field.
                # Unless the business logic already returns a structure like {result: ..., warning: ...}
                if isinstance(result_data, dict) and "result" in result_data:
                    # If returned structure already contains result, merge it
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
                # Catch expected business errors
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
                # Catch unexpected system crashes
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

