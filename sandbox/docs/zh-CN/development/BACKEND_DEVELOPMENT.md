# 后端开发详细指南

本文档详细介绍如何开发新的后端工具，包括轻量级 API 工具和重量级 Backend 后端两种类型。

> **相关文档**:
> - [系统架构总结](../guides/ARCHITECTURE.md)：整体架构概览
> - [使用指南](../guides/USAGE_GUIDE.md)：Sandbox 使用与启动方式
> - 本文档：完整的后端开发教程和示例

---

## 目录

1. [架构概览](#架构概览)
2. [文件结构](#文件结构)
3. [工具调用链路](#工具调用链路)
4. [Session 管理机制](#session-管理机制)
5. [轻量级 API 工具开发](#轻量级-api-工具开发)
6. [重量级 Backend 开发](#重量级-backend-开发)
7. [配置文件](#配置文件)
8. [工具命名规范](#工具命名规范)
9. [完整示例](#完整示例)

---

## 架构概览

### 两种实现方式

后端开发有两种选择：

```
┌─────────────────────────────────────────────────────────────────┐
│                1. 轻量级 API 工具                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ├── 使用 @register_api_tool 装饰器注册                        │
│   ├── 不需要继承任何类                                          │
│   ├── 配置从 config.json 的 apis 部分自动注入                   │
│   ├── 不需要 Session                                            │
│   ├── 工具名称: "search", "translate"                          │
│   └── 示例: WebSearch API, Translate API, LLM API              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                2. 重量级 Backend                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ├── 继承 Backend 基类                                         │
│   ├── 使用 @tool 装饰器标记工具方法                             │
│   ├── 可选实现 warmup/shutdown（全局资源）                      │
│   ├── 可选实现 initialize/cleanup（Session 资源）              │
│   ├── 工具名称: "vm:screenshot", "rag:search"                  │
│   └── 示例: VM, RAG, Browser, Bash Terminal                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 实现方式对照表

| 类型 | 基类 | 需要 Session | 生命周期方法 | 工具命名 | 示例 |
|------|------|-------------|-------------|---------|------|
| 轻量级 API 工具 | 无 | ❌ | 无 | `action` | WebSearch, Translate |
| 重量级 Backend（共享资源） | `Backend` | ❌ | `warmup()`, `shutdown()` | `resource:action` | RAG |
| 重量级 Backend（Session 资源） | `Backend` | ✅ | `initialize()`, `cleanup()` | `resource:action` | VM, Bash |
| 重量级 Backend（混合） | `Backend` | ✅ | 全部四个 | `resource:action` | Browser |

### Backend 类的定义

**Backend 类 = 统一的后端基类**

```python
class Backend(ABC):
    """
    后端基类
    
    所有重量级后端的统一基类。
    所有生命周期方法都是可选的，开发者根据需要选择实现。
    """
    
    # 类属性
    name: str                    # 后端名称（资源类型）
    description: str             # 后端描述
    version: str                 # 后端版本
    
    # ========== 全局生命周期（可选）==========
    
    async def warmup(self) -> None:
        """
        预热资源（可选）
        
        在服务器启动时调用，用于加载模型、建立连接池等。
        适用于所有 worker 共享的资源。
        """
        pass
    
    async def shutdown(self) -> None:
        """
        关闭资源（可选）
        
        在服务器关闭时调用（通过 sandbox.shutdown_server()），用于释放共享资源。
        注意：sandbox.close() 不会触发此方法，只有 shutdown_server() 才会。
        
        典型用途：释放 GPU 显存、关闭连接池、停止后台任务等。
        """
        pass
    
    # ========== Session 生命周期（可选）==========
    
    async def initialize(self, worker_id: str, config: Dict) -> Dict:
        """
        创建 Session（可选）
        
        为特定 worker 创建独立资源实例。
        返回值存储在 session_info["data"]。
        
        如果实现了此方法，工具函数可接收 session_info 参数。
        """
        raise NotImplementedError
    
    async def cleanup(self, worker_id: str, session_info: Dict) -> None:
        """
        销毁 Session（可选）
        
        清理特定 worker 的资源。
        """
        raise NotImplementedError
    
    # ========== 服务器绑定 ==========
    
    def bind_server(self, server) -> None:
        """绑定服务器实例（自动调用）"""
        self._server = server
```

---

## 文件结构

```
sandbox/
├── server/
│   ├── app.py                    # HTTPServiceServer 主类
│   ├── routes.py                 # HTTP 路由定义
│   ├── config_loader.py          # 配置加载器
│   ├── core/
│   │   ├── decorators.py         # @tool 装饰器和扫描工具
│   │   ├── tool_executor.py      # 工具执行器（核心）
│   │   └── resource_router.py    # 资源路由器（Session 管理）
│   │
│   └── backends/                 # 后端存放目录
│       ├── __init__.py           # 导出
│       ├── base.py               # Backend 基类
│       │
│       ├── resources/            # 重量级后端
│       │   ├── vm.py             # ✅ Session 后端: VM（桌面自动化）
│       │   ├── rag.py            # ✅ 共享后端: RAG（文档检索）
│       │   ├── rag_index.py      # ✅ RAG 索引实现（DenseE5RAGIndex）
│       │   ├── bash.py           # ✅ Session 后端: Bash（命令行）
│       │   ├── browser.py        # ✅ 混合后端: Browser（网页自动化）
│       │   └── code_executor.py  # ✅ Session 后端: CodeExecutor（代码沙箱）
│       │
│       └── tools/                # ✅ 轻量级 API 工具
│           ├── __init__.py       # 工具注册入口（@register_api_tool）
│           └── websearch.py      # WebSearch API（搜索、访问）
│
├── client.py                     # HTTP 客户端
└── sandbox.py                    # Sandbox 门面类
```

### 存放位置决策

```
需要预热或 Session 管理吗？
    │
    ├── 是 → backends/resources/xxx.py
    │         ├── 继承 Backend 类
    │         ├── 使用 @tool 装饰器标记工具方法
    │         ├── RAG: warmup() 加载模型和索引
    │         ├── VM: initialize() 分配实例
    │         └── Browser: warmup() + initialize() 混合模式
    │
    └── 否 → backends/tools/xxx.py
              ├── 使用 @register_api_tool 装饰器
              ├── 配置从 apis.xxx 自动注入
              └── WebSearch: 调用外部搜索 API
```

---

## 工具调用链路

### 完整调用流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端 → 后端 调用链路                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   前端调用                                                       │
│   await sandbox.execute("web:search", {"query": "hello"})           │
│       │                                                         │
│       ▼                                                         │
│   Sandbox.execute()                                             │
│   └── client.execute(action="search", params={...})             │
│       │                                                         │
│       ▼                                                         │
│   HTTPServiceClient._request()                                  │
│   └── POST /execute                                             │
│       {                                                         │
│           "worker_id": "sandbox_xxx",                          │
│           "action": "search",           ← 工具名称              │
│           "params": {"query": "hello"}  ← 参数                  │
│       }                                                         │
│       │                                                         │
│       ▼                                                         │
│   服务器端 routes.py                                             │
│   @app.post("/execute")                                         │
│   └── tool_executor.execute(action, params, worker_id)          │
│       │                                                         │
│       ▼                                                         │
│   ToolExecutor.execute()                                        │
│   ├── 1. _resolve_tool("search")                                │
│   │      → 查找注册的工具函数                                    │
│   │      → 返回 (full_name, simple_name, resource_type)         │
│   │                                                             │
│   ├── 2. 如果有 resource_type                                   │
│   │      → 检查是否有现有 Session                                │
│   │      → 有：复用现有 Session                                  │
│   │      → 无：自动创建临时 Session                              │
│   │                                                             │
│   ├── 3. 自动注入参数                                            │
│   │      → worker_id, session_id, session_info                  │
│   │                                                             │
│   ├── 4. await func(**params)                                   │
│   │      → 执行工具函数                                          │
│   │                                                             │
│   └── 5. 如果是临时 Session                                      │
│          → 自动销毁                                              │
│       │                                                         │
│       ▼                                                         │
│   返回结果                                                       │
│   {                                                             │
│       "success": true,                                          │
│       "data": {"results": [...]},                              │
│       "execution_time_ms": 150,                                 │
│       "temporary_session": false                                │
│   }                                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 工具名称解析逻辑

```
┌─────────────────────────────────────────────────────────────────┐
│                    工具名称解析 (_resolve_tool)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   输入: action = "search"                                       │
│       │                                                         │
│       ▼                                                         │
│   策略1: 精确匹配完整名称                                        │
│   _tools["search"] 存在？ → 返回                                │
│       │ 不存在                                                  │
│       ▼                                                         │
│   策略2: 检查是否带前缀                                          │
│   ":" in action? → "vm:screenshot" → 精确匹配                   │
│       │ 无前缀                                                  │
│       ▼                                                         │
│   策略3: 在索引中查找                                            │
│   _tool_name_index["search"] = ["web:search"]             │
│       │                                                         │
│       ├── 唯一匹配 → 返回 "web:search"                    │
│       └── 多个匹配 → 报错，要求指定前缀                          │
│                                                                 │
│   返回: (full_name, simple_name, resource_type)                 │
│         ("search", "search", None)  ← 无状态                    │
│         ("vm:screenshot", "screenshot", "vm") ← 有状态          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## rag:search 与 search 细节调用

本节追踪两类典型工具的“端到端”调用细节，并标注涉及模块与关键函数。

### rag:search（有状态后端工具）

**调用入口**

```
用户代码
  └── Sandbox.execute("rag:search", {"query": "...", "top_k": 5})
      └── HTTPServiceClient.execute() -> POST /execute
          └── routes.execute_action() -> server.execute()
              └── ToolExecutor.execute()
```

**关键模块与职责**

- `sandbox/sandbox.py`：门面入口，发起 `execute("rag:search")`。
- `sandbox/client.py`：HTTP 客户端，向 `/execute` 发送 JSON 请求。
- `sandbox/server/routes.py`：接收请求并调用 `HTTPServiceServer.execute()`。
- `sandbox/server/app.py`：持有工具映射与后端实例，委托给 `ToolExecutor`。
- `sandbox/server/core/tool_executor.py`：
  - `_resolve_tool()` 解析 `rag:search` 的 `resource_type="rag"`。
  - 自动预热 `ensure_backend_warmed_up("rag")`（如未预热）。
  - 通过 `ResourceRouter` 获取/创建 `rag` session。
  - 自动注入 `session_id/session_info` 参数。
  - 调用实际工具函数。
- `sandbox/server/backends/resources/rag.py`：
  - `@tool("rag:search")` 真实实现入口。
  - `warmup()` 加载模型与索引并启动 `QueryBatcher`。
  - `search()` 使用 `QueryBatcher.submit()` 统一检索。
- `sandbox/server/backends/resources/rag_index.py`：
  - `DenseE5RAGIndex.batch_query()` 执行向量检索。
  - 负责模型编码、Faiss 索引搜索与结果格式化。

**核心执行流程（简化）**

```
ToolExecutor.execute("rag:search")
  ├── warmup rag（如未预热）
  ├── ResourceRouter.get_or_create_session("rag")
  └── RAGBackend.search()
      └── QueryBatcher.submit()
          └── DenseE5RAGIndex.batch_query()
              └── 返回 context
```

---

### search（无状态 API 工具）

**调用入口**

```
用户代码
  └── Sandbox.execute("web:search", {"query": "..."})
      └── HTTPServiceClient.execute() -> POST /execute
          └── routes.execute_action() -> server.execute()
              └── ToolExecutor.execute()
```

**关键模块与职责**

- `sandbox/sandbox.py` / `sandbox/client.py` / `sandbox/server/routes.py`：同上。
- `sandbox/server/core/tool_executor.py`：
  - `_resolve_tool()` 解析 `search`，无 `resource_type`。
  - 不创建 session，直接执行工具函数。
- `sandbox/server/backends/tools/__init__.py`：
  - `@register_api_tool("search", config_key="websearch")` 注册工具。
  - `register_all_tools()` 将工具注册到 `HTTPServiceServer`。
- `sandbox/server/backends/tools/websearch.py`：
  - `search()` 为工具函数入口（标准响应格式）。
  - `_get_search_tool()` 延迟初始化 `WebSearchTool`。
  - `WebSearchTool.call()` 调用 Serper API 并格式化结果。

**配置注入路径**

```
apis.websearch (配置文件)
  └── register_all_tools()
      └── server.register_api_tool(..., config=apis.websearch)
          └── wrapper(...) 自动注入 **config 到 search()
```

**核心执行流程（简化）**

```
ToolExecutor.execute("web:search")
  └── websearch.search()
      └── WebSearchTool.call() -> Serper API
          └── build_success_response / build_error_response
```

---

## Session 管理机制

### Session 模式对比

系统支持两种 Session 使用模式：

| 模式 | 创建方式 | 执行后 | 适用场景 |
|------|---------|--------|---------|
| **显式创建（复用模式）** | `create_session()` | 保持存活 | 多次操作同一资源 |
| **自动创建（临时模式）** | 执行时自动 | 立即销毁 | 单次操作、无状态调用 |

### 显式创建 Session（复用模式）

用户显式调用 `create_session()` 创建 Session，可多次复用：

```python
async with Sandbox() as sandbox:
    # 显式创建 session - 会复用
    await sandbox.create_session("vm", {
        "screen_size": [1920, 1080],
        "custom_name": "my_vm"
    })
    
    # 多次执行，复用同一个 session
    await sandbox.execute("vm:screenshot", {})   # 复用 session
    await sandbox.execute("vm:click", {"x": 100})  # 复用 session
    await sandbox.execute("vm:type", {"text": "hello"})  # 复用 session
    
    # 显式销毁
    await sandbox.destroy_session("vm")
```

**执行流程**：

```
create_session("vm", config)
    → Backend.initialize(worker_id, config)
    → 返回 session_info
    → Session 存入 ResourceRouter
    → ResourceRouter 合并默认配置（用户覆盖）

execute("vm:screenshot", {})
    → 检测到现有 Session
    → 复用 Session（is_temporary_session = False）
    → 执行工具
    → 刷新 Session 存活时间

destroy_session("vm")
    → Backend.cleanup(worker_id, session_info)
    → Session 从 ResourceRouter 移除
```

### 自动创建临时 Session

不创建 Session 直接执行时，系统自动创建临时 Session，用完即销毁：

```python
async with Sandbox() as sandbox:
    # 不创建 session，直接执行
    # 自动创建临时 session → 执行 → 自动销毁
    await sandbox.execute("vm:screenshot", {})
    # session 已销毁
    
    # 再次执行会再创建一个新的临时 session
    await sandbox.execute("vm:click", {"x": 100})
    # session 又销毁了
```

**执行流程**：

```
execute("vm:screenshot", {})
    → 检测到无现有 Session
    → 自动创建临时 Session（is_temporary_session = True）
    → Backend.initialize(worker_id, config)
    → 执行工具
    → Backend.cleanup(worker_id, session_info)  ← 自动销毁
    → 返回结果（含 temporary_session: true）
```

### 返回结果字段

执行结果中包含 `temporary_session` 字段：

```python
{
    "success": True,
    "data": {...},
    "tool": "screenshot",
    "resource_type": "vm",
    "session_id": "xxx",
    "temporary_session": True  # 是否为临时 session
}
```

### Session 超时机制

显式创建的 Session 有 TTL（存活时间）：

- 每次工具调用会刷新 TTL
- 超时未使用的 Session 会被自动清理
- TTL 可在配置中设置（默认 300 秒）

```json
{
  "server": {
    "session_ttl": 300
  }
}
```

---

## 轻量级 API 工具开发

### 特点

- ✅ 使用 `@register_api_tool` 装饰器
- ❌ 不需要继承任何类
- ❌ 不需要 Session 管理
- ✅ 配置从 `config.json` 的 `apis` 部分自动注入
- ✅ 适合调用外部 API 的工具

### 适用场景

- 调用外部 API（Google Search, DeepL, OpenAI）
- 简单计算/转换工具
- 无需初始化重资源的工具

### 存放位置

```
sandbox/server/backends/tools/
├── __init__.py       # 注册入口
├── websearch.py      # WebSearch API
├── translate.py      # 翻译 API
└── llm.py            # LLM API
```

### 开发方式

使用 `@register_api_tool` 装饰器注册工具：

```python
# backends/tools/websearch.py
"""
WebSearch 工具 - 使用 @register_api_tool 注册
"""
import httpx
from typing import Dict, Any, Optional
from . import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(
    query: str,
    max_results: int = 10,
    **config  # ← 配置自动注入到这里
) -> Dict[str, Any]:
    """
    Google 搜索
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数
        **config: 从 apis.websearch 注入的配置
    """
    api_key = config.get("api_key")
    cx = config.get("cx")
    
    if not api_key:
        return {"error": "API key not configured"}
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": api_key, "cx": cx, "q": query, "num": max_results}
        )
        data = resp.json()
    
    return {
        "query": query,
        "results": data.get("items", []),
        "total": len(data.get("items", []))
    }


@register_api_tool("visit", config_key="websearch")
async def visit(
    url: str,
    **config
) -> Dict[str, Any]:
    """访问网页并提取内容"""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, follow_redirects=True)
        return {
            "url": url,
            "status": resp.status_code,
            "content": resp.text[:10000]
        }
```

### 配置注入机制

1. 装饰器指定 `config_key`（如 `"websearch"`）
2. 服务器启动时从 `config.json` 的 `apis.websearch` 读取配置
3. 调用工具时，配置自动注入到 `**config` 参数

配置文件：

```json
{
  "apis": {
    "websearch": {
      "api_key": "${GOOGLE_API_KEY}",
      "cx": "${GOOGLE_CX}",
      "max_results": 10
    }
  }
}
```

### 注册入口

```python
# backends/tools/__init__.py
"""
轻量级 API 工具注册入口
"""
from typing import Callable, Dict, Any
from ...core import tool as core_tool

# 全局工具注册表
_API_TOOLS: Dict[str, Dict[str, Any]] = {}


def register_api_tool(name: str, config_key: str):
    """
    注册 API 工具装饰器
    
    Args:
        name: 工具名称
        config_key: 配置键名（对应 apis 中的键）
    """
    def decorator(func: Callable) -> Callable:
        # 使用 core @tool 装饰器标记
        marked_func = core_tool(name=name, resource_type=None)(func)
        
        # 注册到全局表
        _API_TOOLS[name] = {
            "func": marked_func,
            "config_key": config_key,
            "name": name,
            "description": (func.__doc__ or "").strip()
        }
        return marked_func
    return decorator


def get_api_tool(name: str) -> Optional[Dict[str, Any]]:
    """获取已注册的 API 工具"""
    return _API_TOOLS.get(name)


def get_all_api_tools() -> Dict[str, Dict[str, Any]]:
    """获取所有已注册的 API 工具"""
    return _API_TOOLS.copy()
```

---

## 重量级 Backend 开发

### 特点

- ✅ 继承 `Backend` 基类
- ✅ 使用 `@tool` 装饰器标记工具方法
- ✅ 可选实现生命周期方法
- ✅ 支持 Session 管理

### 生命周期方法

所有生命周期方法都是**可选**的，根据需要实现：

| 方法 | 调用时机 | 用途 | 示例 |
|------|---------|------|------|
| `warmup()` | 服务器启动 | 加载模型、建立连接池 | RAG 加载 Embedding |
| `shutdown()` | 服务器关闭 | 释放共享资源 | 关闭连接池 |
| `initialize()` | 创建 Session | 分配 worker 专属资源 | VM 分配实例 |
| `cleanup()` | 销毁 Session | 释放 worker 资源 | VM 释放实例 |

### 三种 Backend 类型

#### 类型 1：共享资源后端（如 RAG）

只实现 `warmup()` 和 `shutdown()`，不需要 Session：

```python
# backends/resources/rag.py
"""
RAG 后端 - 共享资源，不需要 Session
"""
import logging
from typing import Dict, Any, Optional, List
from ..base import Backend

logger = logging.getLogger("RAGBackend")


class RAGBackend(Backend):
    """
    RAG 后端
    
    - 只实现 warmup/shutdown
    - 不实现 initialize/cleanup（不需要 Session）
    - 所有 worker 共享模型
    """
    
    name = "rag"
    description = "RAG Backend - 文档检索服务"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._model = None
        self._index = None
        
        # 配置
        config = config or {}
        self._model_name = config.get("model_name", "intfloat/e5-base-v2")
        self._device = config.get("device", "cpu")
        self._default_top_k = config.get("default_top_k", 10)
    
    async def warmup(self) -> None:
        """预热：加载 Embedding 模型"""
        logger.info(f"🔥 Loading embedding model: {self._model_name}")
        # self._model = load_model(self._model_name, device=self._device)
        logger.info("✅ RAG Backend warmed up")
    
    async def shutdown(self) -> None:
        """关闭：释放模型和 GPU 显存"""
        logger.info("🛑 Shutting down RAG Backend")
        # 释放 GPU 资源（通过 sandbox.shutdown_server() 触发）
        # if self._rag_index:
        #     self._rag_index.release()  # 释放 GPU 显存
        # self._model = None
        pass
    
    # ⭐ 不实现 initialize/cleanup，使用 @tool 标记工具方法
    
    @tool("rag:search")
    async def search(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """检索文档"""
        actual_top_k = top_k or self._default_top_k
        # results = self._model.search(query, top_k=actual_top_k)
        return {
            "query": query,
            "results": [],
            "top_k": actual_top_k
        }
    
    @tool("rag:index")
    async def index(self, documents: List[str]) -> Dict[str, Any]:
        """索引文档"""
        # self._index.add(documents)
        return {"indexed": len(documents)}
```

**调用方式**：

```python
# 不需要创建 session，直接调用
result = await sandbox.execute("rag:search", {"query": "Python tutorial"})
```

#### 类型 2：Session 资源后端（如 VM）

只实现 `initialize()` 和 `cleanup()`，需要 Session：

```python
# backends/resources/vm.py
"""
VM 后端 - Session 资源，每个 worker 独立实例
"""
import logging
from typing import Dict, Any, Optional
from ..base import Backend
from ...core import tool

logger = logging.getLogger("VMBackend")


class VMBackend(Backend):
    """
    VM 后端
    
    - 只实现 initialize/cleanup
    - 每个 worker 分配独立 VM 实例
    - 工具函数接收 session_info（自动注入）
    """
    
    name = "vm"
    description = "Virtual Machine Backend"
    version = "1.0.0"
    
    async def initialize(self, worker_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建 Session - 为 worker 分配 VM 实例
        
        返回值存储在 session_info["data"]
        """
        screen_size = config.get("screen_size", [1920, 1080])
        
        # vm = create_vm_instance(screen_size)
        
        logger.info(f"📦 [{worker_id}] Allocated VM instance")
        return {
            "vm": None,  # 实际 VM 实例
            "screen_size": screen_size
        }
    
    async def cleanup(self, worker_id: str, session_info: Dict[str, Any]) -> None:
        """销毁 Session - 释放 VM 实例"""
        vm = session_info.get("data", {}).get("vm")
        if vm:
            # vm.close()
            pass
        logger.info(f"🗑️ [{worker_id}] Released VM instance")
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        截图
        
        session_info 由系统自动注入
        """
        vm = session_info["data"]["vm"]
        # image = vm.screenshot()
        return {"image": "base64..."}
    
    @tool("vm:click")
    async def click(
        self,
        x: int,
        y: int,
        session_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """点击指定坐标"""
        vm = session_info["data"]["vm"]
        # vm.click(x, y)
        return {"clicked": [x, y]}
    
    @tool("vm:type")
    async def type_text(
        self,
        text: str,
        session_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """输入文本"""
        vm = session_info["data"]["vm"]
        # vm.type(text)
        return {"typed": text}
```

**调用方式**：

```python
# 方式 1：显式创建 Session（复用）
await sandbox.create_session("vm", {"screen_size": [1920, 1080]})
result = await sandbox.execute("vm:screenshot", {})
result = await sandbox.execute("vm:click", {"x": 100, "y": 200})
await sandbox.destroy_session("vm")

# 方式 2：直接执行（临时 Session）
result = await sandbox.execute("vm:screenshot", {})
# Session 自动创建和销毁
```

#### 类型 3：混合后端（共享 + Session）

同时实现所有生命周期方法：

```python
# backends/resources/browser.py
"""
Browser 后端 - 共享连接池 + Session 实例
"""
import logging
from typing import Dict, Any, Optional
from ..base import Backend
from ...core import tool

logger = logging.getLogger("BrowserBackend")


class BrowserBackend(Backend):
    """
    Browser 后端（混合模式）
    
    - warmup: 启动浏览器进程池
    - shutdown: 关闭进程池
    - initialize: 分配 Page 实例
    - cleanup: 释放 Page 实例
    """
    
    name = "browser"
    description = "Browser Automation Backend"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._browser = None
        self._pool = []
    
    async def warmup(self) -> None:
        """预热：启动浏览器进程"""
        logger.info("🔥 Starting browser process...")
        # self._browser = await launch_browser()
        logger.info("✅ Browser Backend warmed up")
    
    async def shutdown(self) -> None:
        """关闭：停止浏览器进程"""
        logger.info("🛑 Shutting down browser...")
        # await self._browser.close()
        self._browser = None
    
    async def initialize(self, worker_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建 Session - 分配 Page 实例"""
        # page = await self._browser.new_page()
        logger.info(f"📦 [{worker_id}] Created browser page")
        return {"page": None}
    
    async def cleanup(self, worker_id: str, session_info: Dict[str, Any]) -> None:
        """销毁 Session - 关闭 Page"""
        page = session_info.get("data", {}).get("page")
        if page:
            # await page.close()
            pass
        logger.info(f"🗑️ [{worker_id}] Closed browser page")
    
    @tool("browser:goto")
    async def goto(self, url: str, session_info: Dict[str, Any]) -> Dict[str, Any]:
        """导航到 URL"""
        page = session_info["data"]["page"]
        # await page.goto(url)
        return {"url": url}
    
    @tool("browser:screenshot")
    async def screenshot(self, session_info: Dict[str, Any]) -> Dict[str, Any]:
        """页面截图"""
        page = session_info["data"]["page"]
        # image = await page.screenshot()
        return {"image": "base64..."}
```

---

## 配置文件

### 完整配置结构

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "session_ttl": 300
  },

  "backends": {
    "_comment": "重量级后端 - 继承 Backend 类",
    
    "rag": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.rag.RAGBackend",
      "config": {
        "model_name": "intfloat/e5-base-v2",
        "device": "cuda",
        "index_path": "/data/indices"
      }
    },
    
    "vm": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
      "config": {
        "screen_size": [1920, 1080],
        "headless": true
      }
    },
    
    "browser": {
      "enabled": false
    }
  },

  "apis": {
    "_comment": "轻量级 API 工具 - 配置自动注入",
    
    "websearch": {
      "api_key": "${GOOGLE_API_KEY}",
      "cx": "${GOOGLE_CX}",
      "max_results": 10
    },
    
    "translate": {
      "api_key": "${DEEPL_API_KEY}",
      "base_url": "https://api.deepl.com/v2"
    },
    
    "llm": {
      "api_key": "${OPENAI_API_KEY}",
      "base_url": "${OPENAI_BASE_URL:-https://api.openai.com/v1}",
      "model": "gpt-4"
    }
  }
}
```

### 环境变量展开

配置支持环境变量展开：

- `${VAR}` - 必需的环境变量
- `${VAR:-default}` - 带默认值的环境变量

---

## 工具命名规范

### 命名格式

| 格式 | 示例 | 类型 | 说明 |
|------|------|------|------|
| `action` | `search`, `translate` | 轻量级 API 工具 | 使用 @register_api_tool |
| `resource:action` | `vm:screenshot`, `rag:search` | 重量级 Backend | 继承 Backend 类 |

### 解析规则

```python
# tool_executor.py 中的解析逻辑

"search"           → resource_type = None      (轻量级工具，无 Session)
"vm:screenshot"    → resource_type = "vm"      (有 Session)
"rag:search"       → resource_type = "rag"     (无 Session，共享资源)
```

> **关键**: 是否需要 Session 取决于后端是否实现了 `initialize()`/`cleanup()`。

### 调用时的自动匹配

```python
# 注册时
@tool("vm:screenshot")

# 调用时 - 两种方式都可以（如果名称唯一）
await execute("vm:screenshot", {})  # 完整名称
await execute("screenshot", {})      # 简单名称（自动匹配）
```

### 冲突处理

```python
# 如果多个资源有同名工具
@tool("vm:status")
@tool("rag:status")

# 调用 "status" 会报错
await execute("status", {})
# Error: Ambiguous tool name 'status'. Multiple matches: ['vm:status', 'rag:status']

# 必须指定完整名称
await execute("vm:status", {})   # ✅
await execute("rag:status", {})  # ✅
```

---

## 完整示例

### 示例 1: 轻量级翻译工具

```python
# backends/tools/translate.py
"""翻译工具 - 使用 @register_api_tool"""
import httpx
from typing import Dict, Any
from . import register_api_tool


@register_api_tool("translate", config_key="translate")
async def translate(
    text: str,
    target_lang: str = "EN",
    source_lang: str = None,
    **config
) -> Dict[str, Any]:
    """
    翻译文本
    
    Args:
        text: 要翻译的文本
        target_lang: 目标语言 (EN, ZH, JA, ...)
        source_lang: 源语言（可选，自动检测）
        **config: 从 apis.translate 注入的配置
    """
    api_key = config.get("api_key")
    base_url = config.get("base_url", "https://api.deepl.com/v2")
    
    if not api_key:
        return {"error": "Translation API key not configured"}
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/translate",
            headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
            data={
                "text": text,
                "target_lang": target_lang,
                "source_lang": source_lang
            }
        )
        data = resp.json()
    
    return {
        "original": text,
        "translated": data["translations"][0]["text"],
        "source_lang": data["translations"][0].get("detected_source_language"),
        "target_lang": target_lang
    }
```

### 示例 2: Bash 终端后端

```python
# backends/resources/bash.py
"""Bash 终端后端 - Session 资源"""
import asyncio
import logging
from typing import Dict, Any, Optional
from ..base import Backend
from ...core import tool

logger = logging.getLogger("BashBackend")


class BashBackend(Backend):
    """
    Bash 终端后端
    
    每个 worker 分配独立的 shell 进程
    """
    
    name = "bash"
    description = "Bash Terminal Backend"
    version = "1.0.0"
    
    async def initialize(self, worker_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建 Session - 启动 shell 进程"""
        cwd = config.get("cwd", "/tmp")
        
        # 启动 shell 进程
        process = await asyncio.create_subprocess_shell(
            "/bin/bash",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        logger.info(f"📦 [{worker_id}] Started bash process (PID: {process.pid})")
        return {
            "process": process,
            "cwd": cwd
        }
    
    async def cleanup(self, worker_id: str, session_info: Dict[str, Any]) -> None:
        """销毁 Session - 终止 shell 进程"""
        process = session_info.get("data", {}).get("process")
        if process:
            process.terminate()
            await process.wait()
        logger.info(f"🗑️ [{worker_id}] Terminated bash process")
    
    @tool("bash:run")
    async def run(
        self,
        command: str,
        timeout: int = 30,
        session_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        执行命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            session_info: 自动注入的 session 信息
        """
        process = session_info["data"]["process"]
        
        # 发送命令
        process.stdin.write(f"{command}\n".encode())
        await process.stdin.drain()
        
        # 读取输出（简化版）
        try:
            stdout = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=timeout
            )
            return {
                "command": command,
                "stdout": stdout.decode(),
                "exit_code": 0
            }
        except asyncio.TimeoutError:
            return {
                "command": command,
                "error": "Command timed out",
                "exit_code": -1
            }
```

### 客户端调用示例

```python
from sandbox import Sandbox

async def main():
    async with Sandbox() as sandbox:
        # ========== 轻量级工具（无 Session）==========
        
        # 搜索
        result = await sandbox.execute("web:search", {"query": "Python tutorial"})
        
        # 翻译
        result = await sandbox.execute("translate", {
            "text": "Hello",
            "target_lang": "ZH"
        })
        
        # ========== 共享资源后端（无 Session）==========
        
        # RAG 搜索（不需要创建 session）
        result = await sandbox.execute("rag:search", {"query": "文档内容"})
        
        # ========== Session 资源后端 ==========
        
        # 方式 1：显式创建 Session（复用）
        await sandbox.create_session("vm", {"screen_size": [1920, 1080]})
        result = await sandbox.execute("vm:screenshot", {})
        result = await sandbox.execute("vm:click", {"x": 100, "y": 200})
        await sandbox.destroy_session("vm")
        
        # 方式 2：直接执行（临时 Session，用完即销毁）
        result = await sandbox.execute("vm:screenshot", {})
        # Session 已自动销毁
        
        # 方式 3：Bash 终端
        await sandbox.create_session("bash", {"cwd": "/home/user"})
        result = await sandbox.execute("bash:run", {"command": "ls -la"})
        result = await sandbox.execute("bash:run", {"command": "pwd"})
        await sandbox.destroy_session("bash")

asyncio.run(main())
```

---

## 总结

### Sandbox API 与 Backend 生命周期对应关系

| Sandbox API | 触发的 Backend 方法 | 说明 |
|-------------|-------------------|------|
| `sandbox.start(warmup_resources=["vm"])` | `Backend.warmup()` | 启动服务器，预热指定后端（可选） |
| `sandbox.warmup(["vm", "rag"])` | `Backend.warmup()` | 显式预热后端 |
| `sandbox.execute(action, params)` | 自动 warmup + 工具函数 + 可能的 initialize/cleanup | 执行工具，自动预热后端，可能自动创建临时 Session |
| `sandbox.create_session(type, config)` | `Backend.initialize(worker_id, config)` | 显式创建 Session |
| `sandbox.destroy_session(type)` | `Backend.cleanup(worker_id, session_info)` | 显式销毁 Session |
| `sandbox.close()` | - | 关闭客户端连接（服务器继续运行） |
| `sandbox.shutdown_server()` | `Backend.shutdown()` | 关闭服务器，释放 GPU 等资源 |

### 后端类型决策流程

```
需要预热或 Session 吗？
    │
    ├── 否 → 轻量级 API 工具
    │        └── @register_api_tool("name", config_key="xxx")
    │            配置从 apis.xxx 自动注入
    │
    └── 是 → 重量级 Backend
             │
             │ 需要全局共享资源吗？（模型、连接池）
             │
             ├── 是 → 实现 warmup() / shutdown()
             │
             └── 否（只需要 Session）
             
             │ 需要 worker 独立资源吗？
             │
             ├── 是 → 实现 initialize() / cleanup()
             │        工具函数接收 session_info
             │
             └── 否 → 只用 warmup() / shutdown()
```

### 快速参考

| 我要开发... | 选择 | 装饰器 | Session |
|------------|------|--------|---------|
| 调用外部 API | 轻量级工具 | `@register_api_tool` | ❌ |
| 共享模型/连接池 | Backend + warmup | `@tool` | ❌ |
| 每用户独立实例 | Backend + initialize | `@tool` | ✅（可复用或临时） |
| 混合模式 | Backend + 全部方法 | `@tool` | ✅ |

---

## 🌳 Backend 还是 APITool？决策树

面对一个新的工具需求，使用以下决策树来选择正确的实现方式：

```
                     开始：我需要开发一个新工具
                                  │
                                  ▼
               ┌─────────────────────────────────────┐
               │ 问题1: 需要维护长连接或持久状态吗？      │
               │                                     │
               │ - TCP/WebSocket 长连接              │
               │ - 进程句柄                          │
               │ - VM/容器实例                       │
               │ - 数据库连接池                      │
               │ - 浏览器 Session                   │
               └─────────────────────────────────────┘
                         │              │
                        是              否
                         │              │
                         ▼              ▼
              ┌──────────────┐  ┌─────────────────────────┐
              │  Backend 类   │  │ 问题2: 需要预加载资源吗？ │
              │              │  │                         │
              │ 继续下一步... │  │ - ML 模型               │
              └──────────────┘  │ - 向量索引               │
                         │      │ - 大型配置文件           │
                         │      └─────────────────────────┘
                         │               │           │
                         │              是           否
                         │               │           │
                         │               ▼           ▼
                         │    ┌──────────────┐  ┌──────────────────┐
                         │    │  Backend 类   │  │ @register_api_tool │
                         │    │ (共享资源型)  │  │   (轻量级工具)      │
                         │    └──────────────┘  └──────────────────┘
                         │
                         ▼
              ┌───────────────────────────────────┐
              │ 问题3: 资源是全局共享还是用户独立？   │
              └───────────────────────────────────┘
                         │              │
                     全局共享        用户独立
                         │              │
                         ▼              ▼
              ┌─────────────────┐  ┌─────────────────┐
              │ 实现 warmup()   │  │ 实现 initialize()│
              │     shutdown()  │  │     cleanup()   │
              │                 │  │                 │
              │ 例: RAG、模型    │  │ 例: VM、Bash    │
              └─────────────────┘  └─────────────────┘
                         │              │
                         ▼              ▼
               ┌─────────────────────────────────────┐
               │ 问题4: 是否同时需要两种资源？          │
               │                                     │
               │ 例: 浏览器（共享进程 + 独立页面）      │
               └─────────────────────────────────────┘
                         │              │
                        是              否
                         │              │
                         ▼              ▼
              ┌─────────────────┐  ┌─────────────────┐
              │ 混合后端        │  │ 完成！          │
              │ 实现全部四个方法 │  │                 │
              └─────────────────┘  └─────────────────┘
```

### 边界情况指南

| 场景 | 推荐选择 | 原因 |
|-----|---------|------|
| 需要鉴权的复杂 API Client | APITool | 鉴权是无状态的，每次请求独立 |
| 带连接池的 API Client | Backend (warmup) | 连接池需要生命周期管理 |
| 需要 Session Cookie 的 API | Backend (initialize) | Session 状态需要跨请求维护 |
| 简单的 HTTP API 调用 | APITool | 请求-响应模式，无状态 |
| 需要重试逻辑的 API | APITool | 重试是无状态操作 |
| 需要限流/熔断的 API | Backend (warmup) | 限流器需要全局状态 |

---

## 🔍 CI/CD 验证

### 配置预检

由于 Backend 使用动态类加载和反射扫描，建议在 CI/CD 阶段进行配置预检：

```bash
# 验证配置文件（推荐在 CI/CD 中使用）
python -m sandbox server --config configs/profiles/production.json --validate

# 只检查不启动
python -m sandbox server --config configs/profiles/dev.json --validate
```

### 验证内容

| 检查项 | 描述 | 示例错误 |
|-------|------|---------|
| `backend_class` 路径 | 验证类路径可导入 | `sandbox.server.backends.resources.VMBackend` 不存在 |
| @tool 装饰器 | 验证工具方法存在 | Backend 类没有任何 @tool 标记的方法 |
| API 工具注册 | 验证 config_key 匹配 | `websearch` 工具的 config_key 在配置中未找到 |
| 配置完整性 | 验证必需配置项 | `vm.default` 缺少必需的 `screen_size` 配置 |

### CI/CD 集成示例

```yaml
# .github/workflows/validate.yml
name: Validate Configuration

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Validate production config
        run: python -m sandbox server --config configs/profiles/production.json --validate
      
      - name: Validate dev config
        run: python -m sandbox server --config configs/profiles/dev.json --validate
```

### 验证失败处理

```
❌ 验证失败: configs/profiles/production.json

错误:
  1. [backend_class] 无法导入 'sandbox.server.backends.MyBackend'
     → 检查类名拼写或确保模块已正确导出
  
  2. [api_tool] 配置键 'websearch' 未找到匹配的注册工具
     → 确保工具已使用 @register_api_tool 注册

警告:
  1. [backend] VMBackend 没有 @tool 标记的方法
     → 建议添加至少一个工具方法

验证结果: 2 错误, 1 警告
```
