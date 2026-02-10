# sandbox/server/core/decorators.py
"""
工具装饰器模块

提供 @tool 装饰器，用于标记工具函数，支持反射扫描注册。

设计理念：
- @tool 只做标记，不执行注册
- Server 通过反射扫描识别并注册
- 分离标记和注册逻辑，使代码更灵活

使用示例：

1. 有状态后端（Backend 类方法）：
```python
from sandbox.server.core import tool
from sandbox.server.backends import Backend

class VMBackend(Backend):
    name = "vm"
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: dict) -> dict:
        '''截取屏幕截图'''
        controller = session_info["data"]["controller"]
        return {"image": await controller.screenshot()}
    
    @tool("vm:click")
    async def click(self, x: int, y: int, session_info: dict) -> dict:
        '''点击指定坐标'''
        controller = session_info["data"]["controller"]
        await controller.click(x, y)
        return {"clicked": [x, y]}
```

2. 无状态 API 工具（推荐使用 @register_api_tool）：
```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(query: str, **config) -> dict:
    '''执行网页搜索，配置从 apis.websearch 自动注入'''
    api_key = config.get("serper_api_key")
    return {"results": [...]}
```

扫描注册：
```python
server = HTTPServiceServer()
backend = VMBackend()
server.load_backend(backend)  # 自动扫描 @tool 标记并注册
```
"""

import inspect
import logging
from typing import Dict, Any, Optional, List, Callable, Type, Union
from functools import wraps

logger = logging.getLogger("ToolDecorator")

# 工具标记属性名
TOOL_MARKER = "_tool_metadata"


class ToolMetadata:
    """工具元数据"""
    
    def __init__(
        self,
        name: str,
        resource_type: Optional[str] = None,
        description: Optional[str] = None,
        hidden: bool = False,
        schema: Optional[Dict[str, Any]] = None
    ):
        """
        初始化工具元数据
        
        Args:
            name: 工具名称（可带资源类型前缀如 "vm:screenshot"）
            resource_type: 资源类型（如果 name 不包含前缀，可以单独指定）
            description: 工具描述（可选，默认使用函数 docstring）
            hidden: 是否隐藏工具（不在工具列表中显示）
            schema: JSON Schema（可选）
        """
        self.full_name = name
        self.resource_type = resource_type
        self.description = description
        self.hidden = hidden
        self.schema = schema
        
        # 解析名称
        if ":" in name:
            parts = name.split(":", 1)
            self.resource_type = parts[0]
            self.simple_name = parts[1]
        else:
            self.simple_name = name
            if resource_type:
                self.full_name = f"{resource_type}:{name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
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
    工具装饰器 - 标记函数为可注册的工具
    
    只做标记，不执行注册。Server 通过反射扫描识别并注册。
    
    Args:
        name: 工具名称（可带资源类型前缀如 "vm:screenshot"）
              如果不提供，使用函数名
        resource_type: 资源类型（如果 name 不包含前缀）
        description: 工具描述
        hidden: 是否隐藏
        schema: JSON Schema
        
    Usage:
        # 有状态工具（需要 session）
        @tool("vm:screenshot")
        async def screenshot(session_info: dict) -> dict:
            controller = session_info["data"]["controller"]
            return {"image": await controller.screenshot()}
        
        # 无状态工具（不需要 session）
        @tool("search")
        async def search(query: str) -> dict:
            return {"results": [...]}
        
        # 使用函数名作为工具名
        @tool()
        async def echo(message: str) -> dict:
            return {"echo": message}
        
        # 指定资源类型
        @tool("click", resource_type="vm")
        async def click(x: int, y: int, session_info: dict) -> dict:
            return {"clicked": [x, y]}
    """
    def decorator(func: Callable) -> Callable:
        # 确定工具名称
        tool_name = name if name else func.__name__
        
        # 确定描述（优先使用参数，其次使用 docstring）
        tool_description = description
        if tool_description is None and func.__doc__:
            # 提取 docstring 的第一行作为描述
            doc_lines = func.__doc__.strip().split("\n")
            tool_description = doc_lines[0].strip()
        
        # 创建元数据
        metadata = ToolMetadata(
            name=tool_name,
            resource_type=resource_type,
            description=tool_description,
            hidden=hidden,
            schema=schema
        )
        
        # 将元数据附加到函数
        setattr(func, TOOL_MARKER, metadata)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 复制元数据到 wrapper
        setattr(wrapper, TOOL_MARKER, metadata)
        
        return wrapper
    
    return decorator


def is_tool(func: Callable) -> bool:
    """
    检查函数是否被 @tool 装饰器标记
    
    Args:
        func: 要检查的函数
        
    Returns:
        是否是工具函数
    """
    return hasattr(func, TOOL_MARKER)


def get_tool_metadata(func: Callable) -> Optional[ToolMetadata]:
    """
    获取工具函数的元数据
    
    Args:
        func: 工具函数
        
    Returns:
        工具元数据，如果不是工具则返回 None
    """
    return getattr(func, TOOL_MARKER, None)


def scan_tools(obj: Any, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    扫描对象中的工具函数
    
    扫描对象中所有被 @tool 装饰器标记的方法。
    
    Args:
        obj: 要扫描的对象（类实例或模块）
        prefix: 可选的名称前缀（用于有状态工具）
        
    Returns:
        工具信息列表，每个元素包含:
        - name: 工具完整名称
        - func: 绑定的工具函数
        - metadata: 工具元数据
        
    Example:
        >>> tools = scan_tools(backend)
        >>> for tool_info in tools:
        ...     print(f"Found tool: {tool_info['name']}")
        ...     executor.register_tool(tool_info['name'], tool_info['func'])
    """
    tools = []
    
    # 获取所有成员
    for name in dir(obj):
        if name.startswith("_"):
            continue
        
        try:
            member = getattr(obj, name)
        except Exception:
            continue
        
        # 检查是否可调用
        if not callable(member):
            continue
        
        # 检查是否有工具标记
        metadata = get_tool_metadata(member)
        if metadata is None:
            continue
        
        # 确定完整名称
        full_name = metadata.full_name
        if prefix and not metadata.resource_type:
            # 如果提供了前缀且工具没有资源类型，添加前缀
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
    列出对象中所有工具的名称
    
    Args:
        obj: 要扫描的对象
        prefix: 可选的名称前缀
        
    Returns:
        工具名称列表
    """
    tools = scan_tools(obj, prefix)
    return [t["name"] for t in tools]


