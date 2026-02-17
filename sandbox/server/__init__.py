# sandbox/server/__init__.py
"""
HTTP Service Server Module

Start Sandbox server via configuration file.

Directory Structure:
```
server/
├── __init__.py          # Module exports
├── app.py               # HTTPServiceServer main class
├── routes.py            # HTTP route definitions
├── config_loader.py     # Configuration loader
├── core/                # Core components
│   ├── decorators.py        # @tool decorator
│   ├── resource_router.py   # Resource routing management
│   └── tool_executor.py     # Tool executor
└── backends/            # Backend implementations
    ├── base.py              # Backend base class
    ├── tools/               # Stateless API tools
    │   ├── __init__.py      # @register_api_tool decorator
    │   ├── websearch.py     # WebSearch tool (search, visit, image_search)
    │   └── ...               # Other API tools
    └── resources/           # Stateful backend resources
        ├── vm.py            # VM backend (stateful)
        └── rag.py           # RAG backend (stateless shared)
```

Startup Method (Recommended):
```python
from sandbox.server import create_server_from_config

# Create and start server from config file
server = create_server_from_config("config.json", host="0.0.0.0", port=8080)
server.run()
```

Command Line Startup:
```bash
python -m sandbox.server.config_loader config.json --host 0.0.0.0 --port 8080
```

Configuration File Example (config.json):
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

Custom Stateful Backend:
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

Custom Stateless API Tool (Recommended Method):
```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("my_action", config_key="my_config")
async def my_action(param: str, **config) -> dict:
    '''Configuration from apis.my_config is automatically injected into **config'''
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
    
    # Config Loader (recommended startup method)
    "ConfigLoader",
    "load_config",
    "create_server_from_config",
    "SandboxConfig",
    "ServerConfig",
    "ResourceConfig",
    "expand_env_vars",
]

