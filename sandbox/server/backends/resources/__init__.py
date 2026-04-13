# sandbox/server/backends/resources/__init__.py
"""
Stateful resource backend module.

Provides heavyweight backends (mock implementations) that require session
management. These backends initialize resources, maintain state, and clean up
when finished.

Backend types:
- VMBackend - VM interaction (stateful, uses initialize/cleanup)
- RAGBackend - Document retrieval (shared resource, uses warmup/shutdown)

Directory layout:
```
backends/
├── resources/           # Stateful backends (heavyweight, require sessions)
│   ├── __init__.py
│   ├── vm.py
│   └── rag.py
│
└── tools/               # Stateless tools (lightweight, no sessions)
    ├── __init__.py
    └── websearch.py
```

Usage example:
```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import (
    VMBackend, 
    RAGBackend
)

server = HTTPServiceServer()

# Load stateful backends.
server.load_backend(VMBackend())
server.load_backend(RAGBackend())

server.run()
```

Config example:
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

from importlib import import_module


_LAZY_IMPORTS = {
    "VMBackend": ".vm",
    "create_vm_backend": ".vm",
    "RAGBackend": ".rag",
    "create_rag_backend": ".rag",
    "MCPBackend": ".mcp",
}


def __getattr__(name):
    module_name = _LAZY_IMPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value

__all__ = [
    # Backend classes
    "VMBackend",
    "RAGBackend",
    "MCPBackend",
    
    # Convenience factories
    "create_vm_backend",
    "create_rag_backend",
]
