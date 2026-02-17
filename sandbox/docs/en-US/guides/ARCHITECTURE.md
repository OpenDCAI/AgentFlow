# HTTP Service Project Architecture Summary

> **Related Documentation**:
> - This document: System architecture overview
> - [Backend Development Guide](../development/BACKEND_DEVELOPMENT.md): Complete backend development tutorial and examples
> - [Usage Guide](USAGE_GUIDE.md): Sandbox usage and startup methods

## 📋 Table of Contents

1. [Overall Architecture](#overall-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Lifecycle Management](#lifecycle-management)
5. [Session Management Mechanism](#session-management-mechanism)
6. [Tool Registration Mechanism](#tool-registration-mechanism)
7. [Backend Extension System](#backend-extension-system)
8. [Configuration System](#configuration-system)
9. [API Interfaces](#api-interfaces)

---

## 🏗️ Overall Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        User Layer                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Sandbox (Facade)                              │   │
│  │  - Unified entry point, simplified user interaction               │   │
│  │  - Automatic server startup/detection                             │   │
│  │  - Support sync/async dual mode                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              HTTPServiceClient (HTTP Client)                     │   │
│  │  - HTTP request encapsulation                                    │   │
│  │  - Worker ID management                                         │   │
│  │  - Automatic retry/error handling                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              │ HTTP/JSON                                  │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │
┌─────────────────────────────────────────────────────────────────────────┐
│                        Server Layer                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              HTTPServiceServer (FastAPI)                          │   │
│  │  - Holds tool data structures (three-layer mapping)              │   │
│  │  - Holds Backend instances                                       │   │
│  │  - Reflection scan @tool markers and register                     │   │
│  │  - HTTP routes (routes.py)                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│        ┌─────────────────────┴─────────────────────┐                   │
│        ▼                                             ▼                   │
│  ┌──────────────────┐                    ┌──────────────────┐          │
│  │  ToolExecutor    │                    │ ResourceRouter   │          │
│  │  - Tool execution│                    │  - Session mgmt   │          │
│  │  - Route parsing │                    │  - Resource routing│          │
│  │  - Param injection│                   │  - Temp Session   │          │
│  └──────────────────┘                    └──────────────────┘          │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Backend System                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ VMBackend     │  │ RAGBackend   │  │ API Tools    │          │   │
│  │  │ (Session)     │  │ (Shared)     │  │ (Lightweight)│          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Core Components

### 1. Sandbox (User Facade)

**Location**: `sandbox/sandbox.py`

**Responsibilities**:
- Provide unified user interface
- Encapsulate `HTTPServiceClient`
- Automatic server startup/detection
- Session batch creation management
- Support sync/async dual mode

**Key Methods**:
```python
- start()                    # Start server (triggers Backend.warmup)
- warmup()                   # Explicitly warm up backend resources
- get_warmup_status()        # Get warmup status
- create_session()           # Create Session (triggers Backend.initialize)
- execute()                  # Execute tool (can auto-create temp Session, auto warmup)
- destroy_session()          # Destroy Session (triggers Backend.cleanup)
- close()                    # Close connection
- shutdown_server()          # Shutdown server (triggers Backend.shutdown)
```

### 2. HTTPServiceServer (HTTP Server)

**Location**: `sandbox/server/app.py`

**Responsibilities**:
- **Hold tool data structures** (three-layer mapping)
- **Hold Backend instances**
- Reflection scan @tool markers and register
- Dispatch requests to corresponding tool functions
- Manage backend lifecycle

**Data Structures**:
```python
# Three-layer tool mapping (held by Server)
self._tools: Dict[str, Callable]           # Full name → function
self._tool_name_index: Dict[str, List[str]] # Simple name → full name list
self._tool_resource_types: Dict[str, str]   # Full name → resource type

# Backend instance holding
self._backends: Dict[str, Backend]          # Resource type → Backend instance
```

### 3. ToolExecutor (Tool Executor)

**Location**: `sandbox/server/core/tool_executor.py`

**Responsibilities**:
- Tool execution logic
- Resource type prefix parsing
- Session auto injection
- **Temporary Session management** (destroy after use)

### 4. ResourceRouter (Resource Router)

**Location**: `sandbox/server/core/resource_router.py`

**Responsibilities**:
- Session lifecycle management
- Worker resource isolation
- Register Backend's initialize/cleanup functions
- Expired Session cleanup

---

## 🔄 Data Flow

### Command Execution Flow

```
User Code
  │
  │ sandbox.execute("vm:screenshot", {})
  ▼
Sandbox.execute()
  │
  │ await client.execute("vm:screenshot", {})
  ▼
HTTPServiceClient.execute()
  │
  │ POST /execute
  │ Body: {"worker_id": "...", "action": "vm:screenshot", "params": {}}
  ▼
HTTPServiceServer (routes.py)
  │
  │ await server.execute(action, params, worker_id)
  ▼
ToolExecutor.execute()
  │
  │ 1. Parse: "vm:screenshot" → resource_type="vm"
  │ 2. Find tool: func = _tools["vm:screenshot"]
  │ 3. Get/create Session (may be temporary)
  │ 4. Inject params: params["session_info"] = session_info
  │ 5. Execute: result = await func(**params)
  │ 6. If temporary Session → auto destroy
  ▼
Return Result
  │
  │ {"success": True, "data": {...}, "temporary_session": True/False}
  ▼
User Code
```

---

## 📅 Lifecycle Management

### Backend Lifecycle Methods

| Method | Call Timing | Trigger | Purpose |
|--------|------------|---------|---------|
| `warmup()` | Server startup or explicit call | `sandbox.warmup()` or auto-trigger on tool execution | Warm up shared resources (resource pool, model loading) |
| `initialize()` | Create Session | `create_session()` or auto-create | Allocate worker-specific resources |
| `cleanup()` | Destroy Session | `destroy_session()` or auto-destroy | Recycle worker resources |
| `shutdown()` | Server shutdown | `shutdown_server()` | Release all shared resources |

---

## 📦 Session Management Mechanism

### Two Session Modes

| Mode | Creation Method | After Execution | Use Case |
|------|----------------|-----------------|----------|
| **Explicit Creation (Reuse Mode)** | `create_session()` | Remains alive | Multiple operations on same resource |
| **Auto Creation (Temporary Mode)** | Auto on execution | Immediately destroyed | Single operation |

---

## 🔌 Tool Registration Mechanism

### Two Registration Methods

| Method | Decorator | For | Registration Timing |
|--------|-----------|-----|-------------------|
| **Heavy Backend** | `@tool` | Backend class methods | `load_backend()` reflection scan |
| **Lightweight Tool** | `@register_api_tool` | `BaseApiTool` instances (function style is compatible) | Module import time |

---

## 🎨 Backend Extension System

### Backend Unified Base Class

```python
class Backend(ABC):
    """
    Backend base class - all methods are optional
    """
    name: str           # Backend name
    description: str    # Description
    version: str        # Version
    
    # Global lifecycle (optional)
    async def warmup(self) -> None: pass
    async def shutdown(self) -> None: pass
    
    # Session lifecycle (optional)
    async def initialize(self, worker_id, config) -> Dict: ...
    async def cleanup(self, worker_id, session_info) -> None: ...
```

### Three Backend Types

| Type | Methods Implemented | Use Case | Example |
|------|-------------------|----------|---------|
| **Shared Resource Backend** | `warmup()`, `shutdown()` | Warm up models, connection pools | RAG |
| **Session Resource Backend** | `initialize()`, `cleanup()` | Independent instance per worker | VM, Bash |
| **Mixed Backend** | All four | Shared + Session | Browser |

---

## ⚙️ Configuration System

### Configuration Structure

```json
{
  "server": {
    "title": "Sandbox HTTP Service",
    "session_ttl": 300
  },
  
  "resources": {
    "vm": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
      "config": {"pool_size": 10}
    }
  },
  
  "apis": {
    "websearch": {
      "serper_api_key": "${SERPER_API_KEY}",
      "max_results": 10
    }
  }
}
```

### Environment Variable Support

- `${VAR}` - Required environment variable
- `${VAR:-default}` - With default value

---

## 🔌 API Interfaces

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/execute` | POST | Execute tool |
| `/execute/batch` | POST | Batch execute |
| `/session/create` | POST | Create Session |
| `/session/destroy` | POST | Destroy Session |
| `/session/list` | POST | List Sessions |
| `/tools` | GET | List tools |
| `/health` | GET | Health check |

---

## 🎯 Key Design Principles

### 1. Layered Decoupling

- **Server**: Holds data structures, calls high-level interfaces
- **Backend**: Hides complex implementations (resource pools, models, etc.)
- **ToolExecutor**: Pure execution logic

### 2. Open Interface, Hidden Implementation

### 3. Flexible Session Management

- Explicit creation: Suitable for multiple operations
- Auto creation: Suitable for single operations
- Temporary Session: Destroy after use

### 4. Unified Tool Registration

- Heavyweight: `@tool` + reflection scan
- Lightweight: `@register_api_tool` + `BaseApiTool` config injection

---

*For detailed backend development documentation, see [Backend Development Guide](../development/BACKEND_DEVELOPMENT.md)*

