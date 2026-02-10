# sandbox/server/backends/response_builder.py
"""
Response Builder Utility

Provides helper functions to build standardized Code/Message/Data/Meta responses
"""

import time
import uuid
from typing import Dict, Any, Optional


def build_success_response(
    data: Any,
    tool: str,
    execution_time_ms: Optional[float] = None,
    resource_type: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a success response

    Args:
        data: Business data payload
        tool: Tool name
        execution_time_ms: Execution time in milliseconds
        resource_type: Resource type (e.g., "websearch", "rag")
        session_id: Session ID
        trace_id: Trace ID for distributed tracing

    Returns:
        Standardized success response
    """
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "meta": {
            "tool": tool,
            "execution_time_ms": execution_time_ms,
            "resource_type": resource_type,
            "session_id": session_id,
            "trace_id": trace_id or str(uuid.uuid4())
        }
    }


def build_error_response(
    code: int,
    message: str,
    tool: str,
    data: Optional[Any] = None,
    execution_time_ms: Optional[float] = None,
    resource_type: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build an error response

    Args:
        code: Error code (non-zero)
        message: Error message
        tool: Tool name
        data: Optional partial data (for partial failures)
        execution_time_ms: Execution time in milliseconds
        resource_type: Resource type
        session_id: Session ID
        trace_id: Trace ID

    Returns:
        Standardized error response
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "meta": {
            "tool": tool,
            "execution_time_ms": execution_time_ms,
            "resource_type": resource_type,
            "session_id": session_id,
            "trace_id": trace_id or str(uuid.uuid4())
        }
    }


class ResponseTimer:
    """Context manager for timing execution"""

    def __init__(self):
        self.start_time = None
        self.elapsed_ms = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.time() - self.start_time) * 1000

    def get_elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        if self.elapsed_ms is None:
            return (time.time() - self.start_time) * 1000
        return self.elapsed_ms
