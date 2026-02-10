# sandbox/server/__init__.py
"""
HTTP Service Server 模块

通过配置文件启动 Sandbox 服务器。

目录结构:
```
server/
├── __init__.py          # 模块导出
├── app.py               # HTTPServiceServer 主类
├── routes.py            # HTTP 路由定义
├── models.py            # Pydantic 请求模型
├── config_loader.py     # 配置加载器
├── core/                # 核心组件
│   ├── decorators.py        # @tool 装饰器
│   ├── resource_router.py   # 资源路由管理
│   └── tool_executor.py     # 工具执行器
└── backends/            # 后端实现
    ├── base.py              # Backend 基类
    ├── tools/               # 无状态 API 工具
    │   ├── __init__.py      # @register_api_tool 装饰器
    │   └── websearch.py     # WebSearch 工具（search、visit、image_search）
    └── examples/            # 示例后端
        ├── vm.py            # VM 后端（有状态）
        └── rag.py           # RAG 后端（无状态共享）
```

启动方式（推荐）:
```python
from sandbox.server import create_server_from_config

# 从配置文件创建并启动服务器
server = create_server_from_config("config.json", host="0.0.0.0", port=8080)
server.run()
```

命令行启动:
```bash
python -m sandbox.server.config_loader config.json --host 0.0.0.0 --port 8080
```

配置文件示例 (config.json):
```json
{
  "server": {
    "title": "My Sandbox",
    "session_ttl": 300
  },
  "resources": {
    "vm": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
      "config": {"screen_size": [1920, 1080]}
    }
  },
  "apis": {
    "websearch": {
      "serper_api_key": "${SERPER_API_KEY}",
      "jina_api_key": "${JINA_API_KEY}"
    }
  }
}
```

自定义有状态后端:
```python
from sandbox.server.backends import Backend, BackendConfig
from sandbox.server.core import tool

class MyBackend(Backend):
    name = "my_backend"
    description = "My Custom Backend"
    
    async def initialize(self, worker_id: str, config: dict) -> dict:
        return {"resource": create_resource()}
    
    async def cleanup(self, worker_id: str, session_info: dict):
        await session_info["data"]["resource"].close()
    
    @tool("my_backend:action")
    async def action(self, session_info: dict) -> dict:
        resource = session_info["data"]["resource"]
        return {"result": "..."}
```

自定义无状态 API 工具（推荐方式）:
```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("my_action", config_key="my_config")
async def my_action(param: str, **config) -> dict:
    '''配置从 apis.my_config 自动注入到 **config'''
    api_key = config.get("api_key")
    return {"result": param}
```
"""

from .app import HTTPServiceServer
from .core import ResourceRouter, ToolExecutor, tool, scan_tools
from .backends import Backend, BackendConfig
from .config_loader import (
    ConfigLoader,
    load_config,
    create_server_from_config,
    SandboxConfig,
    ServerConfig,
    ResourceConfig,
    expand_env_vars,
)

__all__ = [
    # Main Server
    "HTTPServiceServer",
    
    # Core Components
    "ResourceRouter",
    "ToolExecutor",
    "tool",
    "scan_tools",
    
    # Backend Base
    "Backend",
    "BackendConfig",
    
    # Config Loader (推荐的启动方式)
    "ConfigLoader",
    "load_config",
    "create_server_from_config",
    "SandboxConfig",
    "ServerConfig",
    "ResourceConfig",
    "expand_env_vars",
]

