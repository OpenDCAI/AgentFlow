# sandbox/server/backends/tools/__init__.py
"""
Stateless API Tool Registration Module

Provides a free single-tool registration mechanism. Each tool decides:
- Which sub-key to read from apis configuration
- How to initialize its own configuration

Usage:

1. Define tool function:
```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(query: str, max_results: int = 10, **config) -> dict:
    '''Search the web'''
    api_key = config.get("serper_api_key")
    # ... implementation logic
    return {"results": [...]}
```

2. Configuration file (apis section):
```json
{
  "apis": {
    "websearch": {
      "serper_api_key": "${SERPER_API_KEY}",
      "max_results": 10
    }
  }
}
```

3. Tool will automatically read apis.websearch configuration and inject into **config parameter
"""

import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("APITools")


@dataclass
class APIToolInfo:
    """API tool information"""
    name: str                           # Tool name
    func: Callable                      # Tool function
    config_key: Optional[str] = None    # Configuration key read from apis (None means no config read)
    description: Optional[str] = None   # Tool description
    hidden: bool = False                # Whether hidden


# Global tool registry
_API_TOOLS: Dict[str, APIToolInfo] = {}


def register_api_tool(
    name: str,
    *,
    config_key: Optional[str] = None,
    description: Optional[str] = None,
    hidden: bool = False
) -> Callable:
    """
    Decorator for registering API tools
    
    Args:
        name: Tool name (used for execute calls)
        config_key: Sub-key read from apis configuration (e.g., "websearch")
                    If None, tool function won't receive configuration
        description: Tool description (default extracted from docstring)
        hidden: Whether hidden
    
    Example:
        ```python
        @register_api_tool("search", config_key="websearch")
        async def search(query: str, **config) -> dict:
            '''Search the web'''
            api_key = config.get("serper_api_key")
            return {"results": [...]}
        ```
    """
    def decorator(func: Callable) -> Callable:
        tool_description = description
        if tool_description is None and func.__doc__:
            doc_lines = func.__doc__.strip().split("\n")
            tool_description = doc_lines[0].strip()
        
        # Auto-inject name into BaseApiTool instance
        # Use setattr to avoid mypy/linter errors for FunctionType attributes
        if hasattr(func, 'tool_name'):
            setattr(func, 'tool_name', name)
            logger.debug(f"Auto-injected tool_name='{name}' into instance")
        
        # Auto-inject resource_type into BaseApiTool instance
        # If config_key exists and instance's resource_type is still default "unknown", use config_key
        if hasattr(func, 'resource_type') and config_key:
            current_resource_type = getattr(func, 'resource_type')
            if current_resource_type == "unknown":
                setattr(func, 'resource_type', config_key)
                logger.debug(f"Auto-injected resource_type='{config_key}' into instance")

        # Save instance reference for later config injection
        tool_info = APIToolInfo(
            name=name,
            func=func,
            config_key=config_key,
            description=tool_description,
            hidden=hidden
        )
        
        _API_TOOLS[name] = tool_info
        logger.debug(f"Registered API tool: {name} (config_key={config_key})")
        
        return func
    
    return decorator


def get_api_tool(name: str) -> Optional[APIToolInfo]:
    """Get registered API tool"""
    return _API_TOOLS.get(name)


def get_all_api_tools() -> Dict[str, APIToolInfo]:
    """Get all registered API tools"""
    return _API_TOOLS.copy()


def list_api_tools(include_hidden: bool = False) -> List[Dict[str, Any]]:
    """List all API tool information"""
    result = []
    for name, info in _API_TOOLS.items():
        if info.hidden and not include_hidden:
            continue
        result.append({
            "name": info.name,
            "description": info.description,
            "config_key": info.config_key,
            "hidden": info.hidden
        })
    return result


def get_required_config_keys() -> List[str]:
    """Get all configuration keys required by tools"""
    keys = set()
    for info in _API_TOOLS.values():
        if info.config_key:
            keys.add(info.config_key)
    return list(keys)


def register_all_tools(server, apis_config: Dict[str, Any]) -> int:
    """
    Register all registered API tools to the server
    
    This function iterates through all tools registered via the @register_api_tool decorator,
    and registers them to the server using server.register_api_tool().
    
    Args:
        server: HTTPServiceServer instance
        apis_config: apis configuration dictionary, used to extract configuration for each tool
        
    Returns:
        Number of successfully registered tools
        
    Example:
        ```python
        from sandbox.server.backends.tools import register_all_tools
        
        server = HTTPServiceServer()
        apis_config = {"websearch": {"serper_api_key": "xxx"}}
        count = register_all_tools(server, apis_config)
        print(f"Registered {count} API tools")
        ```
    """
    registered_count = 0
    
    for tool_name, tool_info in _API_TOOLS.items():
        try:
            # Get configuration needed by this tool
            tool_config = {}
            if tool_info.config_key:
                tool_config = apis_config.get(tool_info.config_key, {})
                # Skip comment fields
                if isinstance(tool_config, dict):
                    tool_config = {k: v for k, v in tool_config.items() if not k.startswith("_")}
            
            # If it's a BaseApiTool instance, directly inject config into the instance
            if hasattr(tool_info.func, 'set_config'):
                tool_info.func.set_config(tool_config)
                logger.debug(f"  📦 Injected config into {tool_name} instance")
            
            # Register tool to server
            server.register_api_tool(
                name=tool_info.name,
                func=tool_info.func,
                config=tool_config,
                description=tool_info.description,
                hidden=tool_info.hidden
            )
            
            registered_count += 1
            config_info = f"(config_key={tool_info.config_key})" if tool_info.config_key else "(no config)"
            logger.debug(f"  ✅ Registered: {tool_name} {config_info}")
            
        except Exception as e:
            logger.error(f"❌ Failed to register API tool '{tool_name}': {e}")
    
    logger.info(f"✅ Registered {registered_count} API tools")
    return registered_count


# ============================================================================
# Import all tool modules to trigger registration
# ============================================================================

# Import websearch module (will automatically register tools in it)
from . import websearch
from . import ds_tool
from . import doc_tool
__all__ = [
    "register_api_tool",
    "get_api_tool",
    "get_all_api_tools",
    "list_api_tools",
    "get_required_config_keys",
    "register_all_tools",
    "APIToolInfo",
]
