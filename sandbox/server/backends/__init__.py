# sandbox/server/backends/__init__.py
"""
后端模块

提供两种资源类型：

1. Resource Backend（有状态后端，重量级）
   - 需要初始化的资源
   - 提供完整生命周期：warmup → initialize → cleanup → shutdown
   - 由开发者决定使用哪些接口
   - 位置：backends/resources/
   - 示例：VM、RAG

2. API Tools（无状态工具，轻量级）
   - 不需要初始化和 session
   - 使用 @register_api_tool 装饰器注册
   - 位置：backends/tools/
   - 示例：WebSearch（search、visit、image_search）

目录结构:
```
backends/
├── __init__.py          # 导出基类
├── base.py              # Backend 基类定义
│
├── resources/           # 有状态后端（重量级，需要 session）
│   ├── __init__.py      #   导出所有后端类
│   ├── vm.py            #   VM 后端（桌面自动化）
│   └── rag.py           #   RAG 后端（文档检索）
│
└── tools/               # 无状态工具（轻量级，无需 session）
    ├── __init__.py      #   @register_api_tool 装饰器
    └── websearch.py     #   WebSearch 工具（search、visit、image_search）
```

使用示例:

```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends import Backend, BackendConfig
from sandbox.server.core import tool


# 示例1: 有状态后端（VM）
class VMBackend(Backend):
    name = "vm"
    
    async def initialize(self, worker_id: str, config: dict) -> dict:
        controller = await create_vm(config)
        return {"controller": controller}
    
    async def cleanup(self, worker_id: str, session_info: dict):
        await session_info["data"]["controller"].close()
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: dict) -> dict:
        controller = session_info["data"]["controller"]
        return {"image": await controller.screenshot()}


# 示例2: 无状态工具（不需要 Backend 类）
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(query: str, **config) -> dict:
    '''配置从 apis.websearch 自动注入到 **config'''
    return {"results": [...]}
```

加载后端的两种方式:

```python
# 方式1: 代码中直接加载
from sandbox.server.backends.resources import VMBackend, RAGBackend

server = HTTPServiceServer()
server.load_backend(VMBackend())
server.load_backend(RAGBackend())

# 方式2: 通过配置文件加载（推荐）
from sandbox.server.config_loader import create_server_from_config

server = create_server_from_config("configs/profiles/dev.json")
# 后端会根据 resources 配置自动加载
```
"""

from .base import Backend, BackendConfig

__all__ = [
    "Backend",        # 后端基类
    "BackendConfig",  # 后端配置
]
