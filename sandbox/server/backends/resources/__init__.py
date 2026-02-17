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

from .vm import VMBackend, create_vm_backend
from .rag import RAGBackend, create_rag_backend

__all__ = [
    # Backend classes
    "VMBackend",
    "RAGBackend",
    
    # Convenience factories
    "create_vm_backend",
    "create_rag_backend",
]

