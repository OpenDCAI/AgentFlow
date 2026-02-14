# sandbox/server/backends/resources/__init__.py
"""
有状态资源后端模块

提供需要 session 管理的重量级后端 (Mock 实现)。
这些后端需要初始化资源、维护状态、并在结束时清理。

后端类型:
- VMBackend - 虚拟机交互（有状态，使用 initialize/cleanup）
- RAGBackend - 文档检索（共享资源，使用 warmup/shutdown）
- DatabaseBackend - SQL 检索（共享资源，使用 warmup/shutdown）

目录结构:
```
backends/
├── resources/           # 有状态后端（重量级，需要 session）
│   ├── __init__.py
│   ├── vm.py
│   └── rag.py
│
└── tools/               # 无状态工具（轻量级，无需 session）
    ├── __init__.py
    └── websearch.py
```

使用示例:
```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import (
    VMBackend, 
    RAGBackend
)

server = HTTPServiceServer()

# 加载有状态后端
server.load_backend(VMBackend())
server.load_backend(RAGBackend())

server.run()
```

配置文件使用:
```json
{
  "resources": {
    "vm": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
      "config": {"screen_size": [1920, 1080]}
    },
    "rag": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.rag.RAGBackend",
      "config": {"model_name": "e5-base", "index_type": "faiss"}
    }
  }
}
```
"""

from .vm import VMBackend, create_vm_backend
from .rag import RAGBackend, create_rag_backend
from .database import DatabaseBackend, create_database_backend

__all__ = [
    # 后端类
    "VMBackend",
    "RAGBackend",
    "DatabaseBackend",
    
    # 便捷函数
    "create_vm_backend",
    "create_rag_backend",
    "create_database_backend",
]

