# Sandbox 工具注册方式详解

本文档详细介绍 Sandbox 中两种工具注册方式：**重资源后端注册** 和 **轻资源工具注册**。

---

## 目录

- [概述](#概述)
- [如何选择？决策树](#如何选择决策树)
- [重资源后端注册](#重资源后端注册)
  - [注册流程](#重资源注册流程)
  - [配置文件格式](#重资源配置文件格式)
  - [后端类定义](#后端类定义)
  - [@tool 装饰器](#tool-装饰器)
  - [代码示例](#重资源代码示例)
- [轻资源工具注册](#轻资源工具注册)
  - [注册流程](#轻资源注册流程)
  - [配置文件格式](#轻资源配置文件格式)
  - [@register_api_tool 装饰器](#register_api_tool-装饰器)
  - [代码示例](#轻资源代码示例)
- [对比总结](#对比总结)
- [边界案例与常见问题](#边界案例与常见问题)
- [完整流程图](#完整流程图)

---

## 概述

Sandbox 支持两种工具类型，对应两种不同的注册方式：

| 类型 | 描述 | 注册方式 | 适用场景 |
|------|------|---------|---------|
| **重资源后端** | 有状态，需要生命周期管理 | `server.load_backend()` | VM、Browser、Bash |
| **轻资源工具** | 无状态，纯函数调用 | `server.register_api_tool()` | WebSearch、翻译 API |

---

## 如何选择？决策树

> **新手必读**：不确定该用 Backend 还是 API Tool？按照以下决策树判断。

### 决策流程图

```
                        ┌─────────────────────────────────┐
                        │   你的工具需要什么？             │
                        └─────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
        ┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
        │ 维护长连接/会话？  │ │ 独占硬件资源？ │ │ 每次调用独立？    │
        │ (TCP/WebSocket/   │ │ (GPU/VM/容器) │ │ (无状态 HTTP)     │
        │  Session)         │ │               │ │                   │
        └───────────────────┘ └───────────────┘ └───────────────────┘
                │                    │                    │
                ▼                    ▼                    ▼
        ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
        │   ✅ Backend  │    │   ✅ Backend  │    │ ✅ API Tool   │
        │               │    │               │    │               │
        │ 需要 Session  │    │ 需要资源池   │    │ 无状态函数    │
        │ 管理生命周期  │    │ 管理分配释放 │    │ 配置注入即可  │
        └───────────────┘    └───────────────┘    └───────────────┘
```

### 快速判断表

| 问题 | 是 → Backend | 否 → API Tool |
|------|--------------|---------------|
| 需要维护 **TCP 长连接**？（如 VNC、SSH、数据库连接池） | ✅ | |
| 需要维护 **Session 上下文**？（如浏览器 Cookie、登录态） | ✅ | |
| 需要 **独占硬件资源**？（如 GPU、VM 实例） | ✅ | |
| 需要 **初始化/清理** 流程？（如加载模型、释放内存） | ✅ | |
| 多个 worker 需要 **独立资源**？（如各自的 VM） | ✅ | |
| 只是 **HTTP API 调用**？（如 OpenAI、搜索引擎） | | ✅ |
| 只需要 **配置注入**？（如 API Key） | | ✅ |
| 调用之间 **完全独立**，无共享状态？ | | ✅ |

### 典型场景分类

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ✅ 使用 Backend                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🖥️ 虚拟机/桌面自动化                                                   │
│     - VNC 连接需要保持                                                  │
│     - 每个 worker 需要独立的 VM 实例                                    │
│     - 需要 initialize()/cleanup() 管理生命周期                          │
│                                                                         │
│  🌐 浏览器自动化 (Playwright/Selenium)                                   │
│     - 浏览器实例需要保持                                                │
│     - Cookie/Session 需要跨请求共享                                     │
│     - 需要 cleanup() 关闭浏览器                                         │
│                                                                         │
│  💻 终端/Shell 会话                                                      │
│     - SSH 连接需要保持                                                  │
│     - 工作目录、环境变量需要跨命令保持                                   │
│                                                                         │
│  🧠 本地 AI 模型推理                                                     │
│     - 模型加载耗时，需要 warmup() 预热                                   │
│     - GPU 内存需要管理                                                  │
│     - 可设置 stateless=True 让所有 worker 共享模型                       │
│                                                                         │
│  📦 数据库连接池                                                         │
│     - 连接池需要初始化                                                  │
│     - 连接需要 acquire/release                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        ✅ 使用 API Tool                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🔍 搜索引擎 API                                                        │
│     - Serper、Google、Bing                                              │
│     - 每次调用独立，只需 API Key                                        │
│                                                                         │
│  🤖 LLM API 调用                                                        │
│     - OpenAI、Claude、Gemini                                            │
│     - 无状态 HTTP 调用                                                  │
│                                                                         │
│  🌍 翻译/OCR API                                                        │
│     - Google Translate、Azure Vision                                    │
│     - 请求独立，无需 Session                                            │
│                                                                         │
│  📧 邮件/通知 API                                                       │
│     - SendGrid、Twilio                                                  │
│     - 发送即完成，无需保持连接                                           │
│                                                                         │
│  🗄️ 对象存储 API                                                        │
│     - S3、OSS（无需连接池时）                                            │
│     - 每次操作独立                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 边界案例指南

有些场景需要具体分析：

| 场景 | 推荐 | 理由 |
|------|------|------|
| **带鉴权的复杂 API Client** | API Tool | 如果只是 OAuth Token，可以在 `**config` 中注入。Token 刷新可以在工具函数内部处理。 |
| **需要鉴权 + 保持 Session** | Backend | 如果需要维护登录态（Cookie-based），使用 Backend 更合适。 |
| **云端 AI 推理 API** | API Tool | OpenAI 这类无状态 API，用 API Tool。 |
| **本地模型推理** | Backend | 需要加载模型到 GPU，用 Backend + `stateless=True`。 |
| **S3 简单上传下载** | API Tool | 每次操作独立。 |
| **S3 + 连接池优化** | Backend | 如果需要连接池管理，用 Backend。 |
| **Redis 缓存操作** | Backend | 需要连接池管理。 |
| **简单 HTTP Webhook** | API Tool | 发送即完成。 |

### 还是不确定？问自己这个问题

> **"如果服务器重启，我的工具需要重新初始化什么吗？"**

- **需要** → Backend（有状态，需要生命周期管理）
- **不需要** → API Tool（无状态，配置注入即可）

---

## 重资源后端注册

### 重资源注册流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│  配置文件 (profiles/dev.json)                                           │
│  "resources": {                                                         │
│    "vm": {                                                              │
│      "backend_class": "sandbox.server.backends.resources.vm.VMBackend", │
│      "config": {"screen_size": [1920, 1080]}                           │
│    }                                                                    │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ConfigLoader.create_server()                                           │
│                                                                         │
│  1. load_class("...VMBackend")  →  动态导入 VMBackend 类               │
│  2. backend = VMBackend(config=BackendConfig(...))  →  实例化          │
│  3. server.load_backend(backend)  →  注册到服务器                       │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  server.load_backend(backend) 内部执行：                                │
│                                                                         │
│  ├── backend.bind_server(server)          # 绑定服务器引用              │
│  ├── self._backends["vm"] = backend       # 保存后端实例                │
│  ├── register_resource_type(              # 注册资源类型                │
│  │       resource_type="vm",                                            │
│  │       initializer=backend.initialize,  # Session 初始化函数          │
│  │       cleaner=backend.cleanup          # Session 清理函数            │
│  │   )                                                                  │
│  └── scan_and_register(backend, prefix="vm")  # 反射扫描 @tool 方法    │
│          └── 注册工具: vm:screenshot, vm:click, vm:type, ...           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 重资源配置文件格式

```json
{
  "resources": {
    "vm": {
      "enabled": true,
      "stateless": false,
      "description": "虚拟机后端",
      "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
      "config": {
        "screen_size": [1920, 1080],
        "headless": false
      }
    },
    "rag": {
      "enabled": true,
      "stateless": true,
      "description": "RAG 检索后端",
      "backend_class": "sandbox.server.backends.resources.rag.RAGBackend",
      "config": {
        "default_top_k": 5
      }
    }
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | bool | 是否启用此后端 |
| `stateless` | bool | 是否无状态（共享资源） |
| `description` | string | 后端描述 |
| `backend_class` | string | 后端类的完整路径 |
| `config` | object | 传递给后端的默认配置 |

### 后端类定义

```python
# sandbox/server/backends/resources/vm.py

from sandbox.server.backends import Backend, BackendConfig
from sandbox.server.core import tool

class VMBackend(Backend):
    """VM 后端"""
    
    name = "vm"                    # 资源类型名称
    description = "虚拟机后端"
    stateless = False              # 有状态（每个 worker 独立资源）
    
    def __init__(self, config: BackendConfig = None):
        super().__init__(config)
    
    # ========================================================================
    # 生命周期方法（按需实现）
    # ========================================================================
    
    async def warmup(self):
        """预热（服务器启动时调用）"""
        self.pool = await create_connection_pool()
    
    async def initialize(self, worker_id: str, config: dict) -> dict:
        """Session 初始化（创建 Session 时调用）"""
        screen_size = config.get("screen_size", [1920, 1080])
        controller = await self.pool.acquire(screen_size)
        return {
            "controller": controller,
            "screen_size": screen_size
        }
    
    async def cleanup(self, worker_id: str, session_info: dict):
        """Session 清理（销毁 Session 时调用）"""
        controller = session_info["data"].get("controller")
        if controller:
            await controller.close()
    
    async def shutdown(self):
        """关闭（服务器关闭时调用）"""
        await self.pool.close()
    
    # ========================================================================
    # 工具方法（使用 @tool 装饰器标记）
    # ========================================================================
    
    @tool("vm:screenshot")
    async def screenshot(self, session_info: dict) -> dict:
        """截取屏幕截图"""
        controller = session_info["data"]["controller"]
        image = await controller.screenshot()
        return {"image": image}
    
    @tool("vm:click")
    async def click(self, x: int, y: int, session_info: dict) -> dict:
        """点击指定坐标"""
        controller = session_info["data"]["controller"]
        await controller.click(x, y)
        return {"clicked": [x, y]}
```

### @tool 装饰器

`@tool` 装饰器用于**标记**后端类中的方法为可注册的工具。

```python
from sandbox.server.core import tool

class MyBackend(Backend):
    name = "my"
    
    @tool("my:action")                    # 完整名称
    async def action(self, session_info: dict) -> dict:
        return {"result": "..."}
    
    @tool("other_action", resource_type="my")  # 自动添加前缀
    async def other_action(self, session_info: dict) -> dict:
        return {"result": "..."}
```

**工作原理**：

1. `@tool` 只做**标记**，不执行注册
2. `server.load_backend()` 调用 `scan_and_register()` 反射扫描
3. 扫描到带 `@tool` 标记的方法，注册到 `server._tools`

### 重资源代码示例

**注册后端**：

```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import VMBackend

server = HTTPServiceServer()

# 方式1：直接加载
vm_backend = VMBackend()
server.load_backend(vm_backend)

# 方式2：通过配置文件（推荐）
from sandbox.server.config_loader import create_server_from_config
server = create_server_from_config("configs/profiles/dev.json")
```

**客户端调用**：

```python
from sandbox import Sandbox

async with Sandbox() as sandbox:
    # 创建 Session（调用 backend.initialize）
    await sandbox.create_session("vm", {
        "screen_size": [1920, 1080],
        "custom_name": "my_vm"
    })
    
    # 执行工具
    result = await sandbox.execute("vm:screenshot", {})
    result = await sandbox.execute("vm:click", {"x": 100, "y": 200})
    
    # 销毁 Session（调用 backend.cleanup）
    await sandbox.destroy_session("vm")
```

---

## 轻资源工具注册

### 轻资源注册流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 1: 模块导入时，装饰器自动注册到全局表                              │
│                                                                         │
│  # websearch.py                                                         │
│  @register_api_tool("search", config_key="websearch")                  │
│  async def search(query: str, **config) -> dict:                       │
│      ...                                                                │
│                                                                         │
│  执行效果:                                                              │
│  _API_TOOLS["search"] = APIToolInfo(                                   │
│      name="search",                                                    │
│      func=search,                                                      │
│      config_key="websearch"                                            │
│  )                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 2: 服务器创建时，加载配置并注册                                    │
│                                                                         │
│  ConfigLoader._load_api_tools(server, apis_config)                     │
│                                                                         │
│  1. get_all_api_tools()  →  获取全局注册表                             │
│  2. for tool_info in api_tools:                                        │
│         tool_config = apis_config[tool_info.config_key]                │
│         server.register_api_tool(                                      │
│             name=tool_info.name,                                       │
│             func=tool_info.func,                                       │
│             config=tool_config  ← 配置注入                             │
│         )                                                               │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 3: server.register_api_tool() 创建包装函数                        │
│                                                                         │
│  @functools.wraps(func)                                                │
│  async def wrapper(*args, **kwargs):                                   │
│      merged_kwargs = {**config, **kwargs}  # 合并配置                  │
│      return await func(*args, **merged_kwargs)                         │
│                                                                         │
│  self.register_tool("search", wrapper, resource_type=None)             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 轻资源配置文件格式

```json
{
  "apis": {
    "websearch": {
      "serper_api_key": "${SERPER_API_KEY}",
      "jina_api_key": "${JINA_API_KEY}",
      "openai_api_key": "${OPENAI_API_KEY}",
      "default_llm_model": "gpt-4o-mini",
      "max_results": 10,
      "timeout": 30
    }
  }
}
```

**字段说明**：

- 配置键（如 `websearch`）对应装饰器中的 `config_key`
- 支持环境变量替换：`${VAR}` 或 `${VAR:-default}`
- 配置会自动注入到工具函数的 `**config` 参数

### @register_api_tool 装饰器

```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool(
    "search",                    # 工具名称
    config_key="websearch",      # 从 apis.websearch 读取配置
    description="搜索网页",       # 工具描述
    hidden=False                 # 是否隐藏
)
async def search(
    query: str,                  # 用户传入的参数
    max_results: int = 10,       # 可选参数
    **config                     # ← 配置自动注入到这里
) -> dict:
    """
    搜索网页
    
    配置会自动从 apis.websearch 注入到 **config:
    - config["serper_api_key"]
    - config["jina_api_key"]
    - config["timeout"]
    - ...
    """
    api_key = config.get("serper_api_key")
    timeout = config.get("timeout", 30)
    
    # 执行搜索逻辑
    results = await do_search(query, api_key, max_results, timeout)
    
    return {"query": query, "results": results}
```

**装饰器内部实现**：

```python
# sandbox/server/backends/tools/__init__.py

_API_TOOLS: Dict[str, APIToolInfo] = {}  # 全局注册表

def register_api_tool(name, *, config_key=None, description=None, hidden=False):
    """注册 API 工具的装饰器"""
    def decorator(func):
        tool_info = APIToolInfo(
            name=name,
            func=func,
            config_key=config_key,
            description=description or func.__doc__,
            hidden=hidden
        )
        _API_TOOLS[name] = tool_info  # 存入全局注册表
        return func
    return decorator

def get_all_api_tools() -> Dict[str, APIToolInfo]:
    """获取所有已注册的 API 工具"""
    return _API_TOOLS.copy()
```

### 轻资源代码示例

**定义工具**：

```python
# sandbox/server/backends/tools/websearch.py

from sandbox.server.backends.tools import register_api_tool

@register_api_tool("search", config_key="websearch")
async def search(query: str, max_results: int = 10, **config) -> dict:
    """搜索网页"""
    api_key = config.get("serper_api_key")
    # ... 实现逻辑
    return {"results": [...]}

@register_api_tool("visit", config_key="websearch")
async def visit(url: str, **config) -> dict:
    """访问网页"""
    jina_key = config.get("jina_api_key")
    # ... 实现逻辑
    return {"content": "..."}
```

**客户端调用**：

```python
from sandbox import Sandbox

async with Sandbox() as sandbox:
    # 直接调用，无需创建 Session
    result = await sandbox.execute("web:search", {"query": "Python tutorial"})
    
    result = await sandbox.execute("web:visit", {"url": "https://example.com"})
```

---

## 对比总结

| 特性 | 重资源后端 | 轻资源工具 |
|------|-----------|-----------|
| **有无状态** | 有状态 | 无状态 |
| **生命周期** | initialize → 使用 → cleanup | 无 |
| **注册 API** | `server.load_backend(backend)` | `server.register_api_tool(name, func, config)` |
| **工具标记** | `@tool("name")` | `@register_api_tool("name", config_key=...)` |
| **扫描方式** | 反射扫描 `scan_tools()` | 全局注册表 `_API_TOOLS` |
| **配置来源** | `resources.{name}.config` | `apis.{config_key}` |
| **配置访问** | `session_info["data"]` | `**config` 参数 |
| **资源前缀** | 有（如 `vm:`） | 无 |
| **Session 管理** | 需要 create/destroy | 不需要 |
| **适用场景** | VM、Browser、Bash | WebSearch、翻译 API |

---

## 边界案例与常见问题

### Q1: 需要 OAuth 鉴权的 API，应该用哪个？

**答案：大多数情况用 API Tool**

```python
# ✅ 推荐：API Tool + Token 刷新逻辑
@register_api_tool("github_api", config_key="github")
async def github_api(endpoint: str, **config) -> dict:
    token = config.get("access_token")
    
    # Token 过期检查和刷新可以在函数内处理
    if is_token_expired(token):
        token = await refresh_token(config.get("refresh_token"))
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com{endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

**例外：如果需要维护 Cookie-based Session**

```python
# ✅ 如果需要浏览器登录态，用 Backend
class AuthenticatedClientBackend(Backend):
    name = "auth_client"
    
    async def initialize(self, worker_id, config):
        # 登录并获取 Session Cookie
        session = aiohttp.ClientSession()
        await self._login(session, config)
        return {"session": session}
    
    async def cleanup(self, worker_id, session_info):
        await session_info["data"]["session"].close()
```

### Q2: 本地模型推理该用哪个？

**答案：Backend，但设置 `stateless=True` 共享模型**

```python
class LLMBackend(Backend):
    name = "llm"
    stateless = True  # 所有 worker 共享同一个模型
    
    async def warmup(self):
        # 服务器启动时加载模型（只加载一次）
        self.model = await load_model("llama-7b")
        self.tokenizer = await load_tokenizer("llama-7b")
    
    async def shutdown(self):
        # 服务器关闭时释放 GPU 内存
        del self.model
        torch.cuda.empty_cache()
    
    @tool("llm:generate")
    async def generate(self, prompt: str) -> dict:
        # 所有请求共享 self.model
        output = self.model.generate(prompt)
        return {"text": output}
```

### Q3: 我的工具既需要配置注入，又需要连接池，怎么办？

**答案：用 Backend，在 `warmup()` 中创建连接池**

```python
class DatabaseBackend(Backend):
    name = "db"
    stateless = True  # 共享连接池
    
    async def warmup(self):
        # 从 default_config 读取配置
        db_url = self.config.default_config.get("database_url")
        self.pool = await asyncpg.create_pool(db_url, min_size=5, max_size=20)
    
    async def shutdown(self):
        await self.pool.close()
    
    @tool("db:query")
    async def query(self, sql: str) -> dict:
        async with self.pool.acquire() as conn:
            result = await conn.fetch(sql)
            return {"rows": [dict(r) for r in result]}
```

### Q4: 如何从 API Tool 迁移到 Backend？

如果你的 API Tool 逐渐变得复杂（需要连接池、状态管理），可以迁移到 Backend：

**Before (API Tool):**
```python
@register_api_tool("redis_cache", config_key="redis")
async def redis_cache(key: str, value: str = None, **config) -> dict:
    # 每次都创建连接，效率低
    redis = await aioredis.from_url(config.get("redis_url"))
    if value:
        await redis.set(key, value)
    result = await redis.get(key)
    await redis.close()
    return {"value": result}
```

**After (Backend):**
```python
class RedisBackend(Backend):
    name = "redis"
    stateless = True
    
    async def warmup(self):
        url = self.config.default_config.get("redis_url")
        self.pool = await aioredis.from_url(url)
    
    async def shutdown(self):
        await self.pool.close()
    
    @tool("redis:get")
    async def get(self, key: str) -> dict:
        value = await self.pool.get(key)
        return {"value": value}
    
    @tool("redis:set")
    async def set(self, key: str, value: str) -> dict:
        await self.pool.set(key, value)
        return {"success": True}
```

### Q5: 什么时候用 `stateless=True`？

| `stateless` | Session 管理 | 适用场景 |
|-------------|-------------|---------|
| `False`（默认） | 每个 worker 独立资源 | VM、浏览器（各自独立） |
| `True` | 所有 worker 共享资源 | 模型推理、连接池（共享） |

```python
# stateless=False: 每个 worker 有自己的 VM
class VMBackend(Backend):
    name = "vm"
    stateless = False
    
    async def initialize(self, worker_id, config):
        # 每个 worker 创建自己的 VM
        return {"vm": await create_vm(config)}

# stateless=True: 所有 worker 共享模型
class EmbeddingBackend(Backend):
    name = "embedding"
    stateless = True
    
    async def warmup(self):
        # 只加载一次，所有 worker 共享
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
```

---

## 完整流程图

### 服务器启动时的注册流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ConfigLoader.create_server()                        │
└─────────────────────────────────────────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  创建 Server    │  │  加载重资源后端  │  │  加载轻资源工具  │
│                 │  │                 │  │                 │
│ HTTPService-    │  │ for res in      │  │ for tool in     │
│ Server(...)     │  │ resources:      │  │ api_tools:      │
└─────────────────┘  │                 │  │                 │
                     │ load_class()    │  │ get_all_api_-   │
                     │ → VMBackend     │  │ tools()         │
                     │                 │  │                 │
                     │ server.load_-   │  │ server.register │
                     │ backend()       │  │ _api_tool()     │
                     │                 │  │                 │
                     │ ├── bind_server │  │ ├── 创建包装    │
                     │ ├── register_-  │  │ │   函数        │
                     │ │   resource_-  │  │ │               │
                     │ │   type        │  │ └── register_-  │
                     │ └── scan_and_-  │  │     tool()      │
                     │     register    │  │                 │
                     └─────────────────┘  └─────────────────┘
                               │                   │
                               ▼                   ▼
                     ┌─────────────────────────────────────┐
                     │           server._tools             │
                     │                                     │
                     │  {                                  │
                     │    "vm:screenshot": func,          │
                     │    "vm:click": func,               │
                     │    "rag:search": func,             │
                     │    "search": func,      ← 轻资源   │
                     │    "visit": func,       ← 轻资源   │
                     │  }                                  │
                     └─────────────────────────────────────┘
```

### 请求执行时的调用流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Client: sandbox.execute("vm:screenshot", {})                          │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Server: ToolExecutor.execute("vm:screenshot", params, worker_id)      │
│                                                                         │
│  1. _resolve_tool("vm:screenshot")                                     │
│     └── 查找 _tools["vm:screenshot"] → func                            │
│                                                                         │
│  2. 检查资源类型: _tool_resource_types["vm:screenshot"] → "vm"         │
│                                                                         │
│  3. 有资源类型 → 需要 Session                                           │
│     └── ResourceRouter.get_session(worker_id, "vm")                    │
│         └── 返回 session_info                                          │
│                                                                         │
│  4. 执行工具函数                                                        │
│     └── result = await func(session_info=session_info, **params)       │
│                                                                         │
│  5. 返回结果                                                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  Client: sandbox.execute("web:search", {"query": "Python"})                │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Server: ToolExecutor.execute("web:search", params, worker_id)             │
│                                                                         │
│  1. _resolve_tool("search")                                            │
│     └── 查找 _tools["search"] → wrapper_func                           │
│                                                                         │
│  2. 检查资源类型: _tool_resource_types.get("search") → None            │
│                                                                         │
│  3. 无资源类型 → 不需要 Session                                         │
│                                                                         │
│  4. 执行包装函数                                                        │
│     └── wrapper_func(query="Python")                                   │
│         └── merged = {**config, **kwargs}  # 合并配置                  │
│         └── await search(query="Python", **merged)                     │
│                                                                         │
│  5. 返回结果                                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 快速参考

### 创建重资源后端

```python
from sandbox.server.backends import Backend, BackendConfig
from sandbox.server.core import tool

class MyBackend(Backend):
    name = "my"
    
    async def initialize(self, worker_id, config):
        return {"resource": create_resource()}
    
    async def cleanup(self, worker_id, session_info):
        session_info["data"]["resource"].close()
    
    @tool("my:action")
    async def action(self, session_info):
        resource = session_info["data"]["resource"]
        return {"result": resource.do_something()}
```

### 创建轻资源工具

```python
from sandbox.server.backends.tools import register_api_tool

@register_api_tool("my_tool", config_key="my_config")
async def my_tool(param: str, **config) -> dict:
    api_key = config.get("api_key")
    return {"result": "..."}
```

---

## CI/CD 配置预检

由于反射扫描增加了运行时不确定性，建议在 CI/CD 阶段进行配置预检。

### 命令行使用

```bash
# 验证单个配置
python -m sandbox server --config dev --validate

# 使用配置文件路径
python -m sandbox server --config configs/profiles/production.json --validate
```

### 验证内容

| 检查项 | 描述 |
|--------|------|
| `backend_class` 路径 | 确保所有后端类路径可解析（importlib） |
| `@tool` 装饰器 | 检查后端类中是否有工具方法 |
| `@register_api_tool` | 验证 API 工具的配置键是否存在 |
| 必填字段 | 检查 server.title 等必填配置 |

### Python API

当前版本不再提供独立的 `sandbox.server.validator` Python API。
如需预检配置，请调用 CLI：

```bash
python -m sandbox server --config configs/profiles/dev.json --validate
```

### GitHub Actions 示例

```yaml
# .github/workflows/validate.yml
name: Validate Configs

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
      
      - name: Validate dev configuration
        run: python -m sandbox server --config configs/profiles/dev.json --validate
```

---

*文档版本: 1.1*
*最后更新: 2026-01-12*

