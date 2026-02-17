# sandbox/server/core/decorators.py
"""
Tool Decorator Module

Provides @tool decorator for marking tool functions, supports reflection scanning and registration.

Design Philosophy:
- @tool only marks, does not perform registration
- Server identifies and registers through reflection scanning
- Separates marking and registration logic for more flexible code

Usage Examples:

1. Stateful backend (Backend class methods):
```python
from sandbox.server.core import tool
from sandbox.server.backends import Backend

class VMBackend(Backend):
    name = "vm"
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: dict) -> dict:
        '''Take a screenshot'''
        controller = session_info["data"]["controller"]
        return {"image": await controller.screenshot()}
    
    @tool("vm:click")
    async def click(self, x: int, y: int, session_info: dict) -> dict:
        '''Click at specified coordinates'''
        controller = session_info["data"]["controller"]
        await controller.click(x, y)
        return {"clicked": [x, y]}
```

2. Stateless API tools (recommended to use @register_api_tool):
```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(query: str, **config) -> dict:
    '''Execute web search, configuration automatically injected from apis.websearch'''
    api_key = config.get("serper_api_key")
    return {"results": [...]}
```

Scan and Register:
```python
server = HTTPServiceServer()
backend = VMBackend()
server.load_backend(backend)  # Automatically scan @tool markers and register
```
"""

import inspect
import logging
from typing import Dict, Any, Optional, List, Callable, Type, Union
from functools import wraps

logger = logging.getLogger("ToolDecorator")

# Tool marker attribute name
TOOL_MARKER = "_tool_metadata"


class ToolMetadata:
    """Tool metadata"""
    
    def __init__(
        self,
        name: str,
        resource_type: Optional[str] = None,
        description: Optional[str] = None,
        hidden: bool = False,
        schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize tool metadata
        
        Args:
            name: Tool name (can include resource type prefix like "vm:screenshot")
            resource_type: Resource type (if name doesn't contain prefix, can be specified separately)
            description: Tool description (optional, defaults to function docstring)
            hidden: Whether to hide tool (not shown in tool list)
            schema: JSON Schema (optional)
        """
        self.full_name = name
        self.resource_type = resource_type
        self.description = description
        self.hidden = hidden
        self.schema = schema
        
        # Parse name
        if ":" in name:
            parts = name.split(":", 1)
            self.resource_type = parts[0]
            self.simple_name = parts[1]
        else:
            self.simple_name = name
            if resource_type:
                self.full_name = f"{resource_type}:{name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.simple_name,
            "full_name": self.full_name,
            "resource_type": self.resource_type,
            "description": self.description,
            "hidden": self.hidden,
            "schema": self.schema,
            "stateless": self.resource_type is None
        }


def tool(
    name: Optional[str] = None,
    *,
    resource_type: Optional[str] = None,
    description: Optional[str] = None,
    hidden: bool = False,
    schema: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Tool decorator - marks function as a registerable tool
    
    Only marks, does not perform registration. Server identifies and registers through reflection scanning.
    
    Args:
        name: Tool name (can include resource type prefix like "vm:screenshot")
              If not provided, uses function name
        resource_type: Resource type (if name doesn't contain prefix)
        description: Tool description
        hidden: Whether to hide
        schema: JSON Schema
        
    Usage:
        # Stateful tool (requires session)
        @tool("vm:screenshot")
        async def screenshot(session_info: dict) -> dict:
            controller = session_info["data"]["controller"]
            return {"image": await controller.screenshot()}
        
        # Stateless tool (no session needed)
        @tool("search")
        async def search(query: str) -> dict:
            return {"results": [...]}
        
        # Use function name as tool name
        @tool()
        async def echo(message: str) -> dict:
            return {"echo": message}
        
        # Specify resource type
        @tool("click", resource_type="vm")
        async def click(x: int, y: int, session_info: dict) -> dict:
            return {"clicked": [x, y]}
    """
    def decorator(func: Callable) -> Callable:
        # Determine tool name
        tool_name = name if name else func.__name__
        
        # Determine description (prefer parameter, then use docstring)
        tool_description = description
        if tool_description is None and func.__doc__:
            # Extract first line of docstring as description
            doc_lines = func.__doc__.strip().split("\n")
            tool_description = doc_lines[0].strip()
        
        # Create metadata
        metadata = ToolMetadata(
            name=tool_name,
            resource_type=resource_type,
            description=tool_description,
            hidden=hidden,
            schema=schema
        )
        
        # Attach metadata to function
        setattr(func, TOOL_MARKER, metadata)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Copy metadata to wrapper
        setattr(wrapper, TOOL_MARKER, metadata)
        
        return wrapper
    
    return decorator


def is_tool(func: Callable) -> bool:
    """
    Check if function is marked with @tool decorator
    
    Args:
        func: Function to check
        
    Returns:
        Whether it is a tool function
    """
    return hasattr(func, TOOL_MARKER)


def get_tool_metadata(func: Callable) -> Optional[ToolMetadata]:
    """
    Get tool function metadata
    
    Args:
        func: Tool function
        
    Returns:
        Tool metadata, returns None if not a tool
    """
    return getattr(func, TOOL_MARKER, None)


def scan_tools(obj: Any, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan tool functions in object
    
    Scans all methods in object marked with @tool decorator.
    
    Args:
        obj: Object to scan (class instance or module)
        prefix: Optional name prefix (for stateful tools)
        
    Returns:
        List of tool information, each element contains:
        - name: Tool full name
        - func: Bound tool function
        - metadata: Tool metadata
        
    Example:
        >>> tools = scan_tools(backend)
        >>> for tool_info in tools:
        ...     print(f"Found tool: {tool_info['name']}")
        ...     executor.register_tool(tool_info['name'], tool_info['func'])
    """
    tools = []
    
    # Get all members
    for name in dir(obj):
        if name.startswith("_"):
            continue
        
        try:
            member = getattr(obj, name)
        except Exception:
            continue
        
        # Check if callable
        if not callable(member):
            continue
        
        # Check if has tool marker
        metadata = get_tool_metadata(member)
        if metadata is None:
            continue
        
        # Determine full name
        full_name = metadata.full_name
        if prefix and not metadata.resource_type:
            # If prefix provided and tool has no resource type, add prefix
            full_name = f"{prefix}:{metadata.simple_name}"
        
        tools.append({
            "name": full_name,
            "simple_name": metadata.simple_name,
            "resource_type": metadata.resource_type or prefix,
            "func": member,
            "metadata": metadata,
            "description": metadata.description or "",
            "hidden": metadata.hidden,
            "stateless": metadata.resource_type is None and prefix is None
        })
    
    return tools


def list_tool_names(obj: Any, prefix: Optional[str] = None) -> List[str]:
    """
    List names of all tools in object
    
    Args:
        obj: Object to scan
        prefix: Optional name prefix
        
    Returns:
        List of tool names
    """
    tools = scan_tools(obj, prefix)
    return [t["name"] for t in tools]


