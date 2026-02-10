# sandbox/server/core/__init__.py
"""
核心组件模块

包含:
- ResourceRouter: 资源路由表管理
- ToolExecutor: 工具执行器
- decorators: 工具装饰器（@tool）
"""

from .resource_router import ResourceRouter
from .tool_executor import ToolExecutor
from .decorators import tool, is_tool, get_tool_metadata, scan_tools, TOOL_MARKER

__all__ = [
    "ResourceRouter", 
    "ToolExecutor",
    # 装饰器相关
    "tool",
    "is_tool", 
    "get_tool_metadata",
    "scan_tools",
    "TOOL_MARKER"
]

