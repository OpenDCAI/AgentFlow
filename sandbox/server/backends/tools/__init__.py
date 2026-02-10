# sandbox/server/backends/tools/__init__.py
"""
无状态 API 工具注册模块

提供自由的单工具注册机制。每个工具自己决定：
- 从 apis 配置中读取哪个子键
- 如何初始化自己的配置

使用方式：

1. 定义工具函数：
```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(query: str, max_results: int = 10, **config) -> dict:
    '''搜索网页'''
    api_key = config.get("serper_api_key")
    # ... 实现逻辑
    return {"results": [...]}
```

2. 配置文件 (apis 部分)：
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

3. 工具会自动读取 apis.websearch 配置并注入到 **config 参数
"""

import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("APITools")


@dataclass
class APIToolInfo:
    """API 工具信息"""
    name: str                           # 工具名称
    func: Callable                      # 工具函数
    config_key: Optional[str] = None    # 从 apis 中读取的配置键（None 表示不读取配置）
    description: Optional[str] = None   # 工具描述
    hidden: bool = False                # 是否隐藏


# 全局工具注册表
_API_TOOLS: Dict[str, APIToolInfo] = {}


def register_api_tool(
    name: str,
    *,
    config_key: Optional[str] = None,
    description: Optional[str] = None,
    hidden: bool = False
) -> Callable:
    """
    注册 API 工具的装饰器
    
    Args:
        name: 工具名称（用于 execute 调用）
        config_key: 从 apis 配置中读取的子键（如 "websearch"）
                   如果为 None，工具函数不会接收配置
        description: 工具描述（默认从 docstring 提取）
        hidden: 是否隐藏
    
    Example:
        ```python
        @register_api_tool("search", config_key="websearch")
        async def search(query: str, **config) -> dict:
            '''搜索网页'''
            api_key = config.get("serper_api_key")
            return {"results": [...]}
        ```
    """
    def decorator(func: Callable) -> Callable:
        tool_description = description
        if tool_description is None and func.__doc__:
            doc_lines = func.__doc__.strip().split("\n")
            tool_description = doc_lines[0].strip()
        
        # 自动注入 name 到 BaseApiTool 实例
        # 使用 setattr 以避免 mypy/linter 对 FunctionType 属性的检查报错
        if hasattr(func, 'tool_name'):
            setattr(func, 'tool_name', name)
            logger.debug(f"Auto-injected tool_name='{name}' into instance")
        
        # 自动注入 resource_type 到 BaseApiTool 实例
        # 如果 config_key 存在，且实例的 resource_type 仍为默认值 "unknown"，则使用 config_key
        if hasattr(func, 'resource_type') and config_key:
            current_resource_type = getattr(func, 'resource_type')
            if current_resource_type == "unknown":
                setattr(func, 'resource_type', config_key)
                logger.debug(f"Auto-injected resource_type='{config_key}' into instance")

        # 保存实例引用，用于后续注入配置
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
    """获取已注册的 API 工具"""
    return _API_TOOLS.get(name)


def get_all_api_tools() -> Dict[str, APIToolInfo]:
    """获取所有已注册的 API 工具"""
    return _API_TOOLS.copy()


def list_api_tools(include_hidden: bool = False) -> List[Dict[str, Any]]:
    """列出所有 API 工具信息"""
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
    """获取所有工具需要的配置键"""
    keys = set()
    for info in _API_TOOLS.values():
        if info.config_key:
            keys.add(info.config_key)
    return list(keys)


def register_all_tools(server, apis_config: Dict[str, Any]) -> int:
    """
    将所有已注册的 API 工具注册到服务器
    
    此函数遍历所有通过 @register_api_tool 装饰器注册的工具，
    并使用 server.register_api_tool() 将它们注册到服务器。
    
    Args:
        server: HTTPServiceServer 实例
        apis_config: apis 配置字典，用于提取各工具的配置
        
    Returns:
        成功注册的工具数量
        
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
            # 获取该工具需要的配置
            tool_config = {}
            if tool_info.config_key:
                tool_config = apis_config.get(tool_info.config_key, {})
                # 跳过注释字段
                if isinstance(tool_config, dict):
                    tool_config = {k: v for k, v in tool_config.items() if not k.startswith("_")}
            
            # 如果是 BaseApiTool 实例，直接注入配置到实例中
            if hasattr(tool_info.func, 'set_config'):
                tool_info.func.set_config(tool_config)
                logger.debug(f"  📦 Injected config into {tool_name} instance")
            
            # 注册工具到 server
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
# 导入所有工具模块以触发注册
# ============================================================================

# 导入 websearch 模块（会自动注册其中的工具）
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
