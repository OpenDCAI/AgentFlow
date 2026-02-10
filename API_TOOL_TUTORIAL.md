# API 类型后端（无状态工具）开发教程

本教程介绍如何在本项目中开发一个新的 API 类型后端（无状态工具），并通过 `quick_sandbox.py` 进行快速验证。

得益于 `BaseApiTool` 基础设施，现在开发一个新工具变得极其简单和标准化。

## 1) 新建配置文件

在项目根目录的 `configs/` 下创建一个配置文件，例如：

`configs/server/my_api_sandbox.json`

示例：

```json
{
  "server": {
    "title": "My API Sandbox",
    "session_ttl": 300
  },
  "resources": {},
  "apis": {
    "my_api": {
      "api_key": "YOUR_KEY",
      "base_url": "https://example.com",
      "timeout": 10
    }
  }
}
```

说明：
- `apis.<config_key>` 下的内容会在注册时自动注入到工具实例的 `self._config` 中，通过 `self.get_config("key")` 获取。

## 2) 开发工具类

在 `sandbox/server/backends/tools/` 新建文件，例如：

`sandbox/server/backends/tools/example_api_tool.py`

### 标准实现步骤：

1.  继承 `BaseApiTool`
2.  实现 `execute` 方法（纯业务逻辑）
3.  使用 `register_api_tool` 注册实例

```python
from typing import Any
from .base_tool import BaseApiTool, ToolBusinessError
from ..error_codes import ErrorCode
from . import register_api_tool

# 1. 继承 BaseApiTool
class MyApiTool(BaseApiTool):
    def __init__(self):
        # 无需传递任何参数，注册时会自动注入 tool_name、resource_type 和 config
        super().__init__()

    # 2. 实现 execute 方法
    async def execute(self, message: str, **kwargs) -> Any:
        """
        My API ping test
        
        Args:
            message: 输入消息
            **kwargs: 包含 session_id, trace_id 等运行时参数
        """
        # 从类内部配置获取 (注册时自动注入到 self._config)
        api_key = self.get_config("api_key")
        if not api_key:
            # 抛出业务异常 (自动转换为标准错误响应)
            raise ToolBusinessError("API Key missing", ErrorCode.EXECUTION_ERROR)

        try:
            # 模拟业务逻辑
            result = f"PONG: {message} (Key: {api_key[:4]}***)"
            
            # 直接返回业务数据 (BaseApiTool 会自动包装成标准响应格式)
            return {"result": result}
            
        except Exception as e:
            # 捕获特定业务异常
            raise ToolBusinessError(f"Ping failed: {str(e)}")

# 3. 注册工具实例
# name: 工具调用名称 (如 "my_api:ping")
# config_key: 对应配置文件中的 apis.my_api（会注入到实例的 self._config）
ping_tool = register_api_tool(
    name="my_api:ping", 
    config_key="my_api", 
    description="My API ping test"
)(MyApiTool())
```

## 3) 触发自动注册（导入模块）

在 `sandbox/server/backends/tools/__init__.py` 中添加导入：

```python
from . import example_api_tool
```

这样启动时 `register_all_tools()` 会自动注册该工具。

## 4) 使用 quick_sandbox.py 运行（手动启动服务器）

`quick_sandbox.py` 连接到已运行的 Sandbox Server，不再自动拉起服务。

### 4.1 修改脚本配置

```python
CONFIG_PATH = "configs/server/my_api_sandbox.json"
```

并将执行命令改为你的工具：

```python
result = await sandbox.execute(
    "my_api:ping",
    {"message": "hello"}
)
```

### 4.2 手动启动服务器（CLI）

```bash
python3 bin/sandbox-server.py --config my_api_sandbox.json
```

> 说明：默认端口为 `18890`，`quick_sandbox.py` 会连接 `http://127.0.0.1:18890`。

### 4.3 运行脚本

```bash
python /home/a1/sdb/tzw/Synthesis/quick_sandbox.py
```

## 参数传递格式说明

### 调用格式

所有工具（无论是 API Tools 还是 Resource Tools）的调用格式统一：

```python
await sandbox.execute(
    "工具名称",           # str: 如 "my_api:ping", "search", "vm:click"
    {"参数名": 参数值}    # Dict[str, Any]: 业务参数字典
)
```

### 参数对应关系

调用方传入的 `params` 字典的 **key 必须与 `execute()` 方法的形参名称一致**：

```python
# 调用方
await sandbox.execute("my_api:ping", {"message": "hello"})
#                                       ↓
# 工具方
async def execute(self, message: str, **kwargs) -> Any:
#                       ↑ key 名必须匹配
```

### 完整数据流

```
┌─────────────────────────────────────────────────────────────────────────┐
│  调用方                      配置文件                      工具方       │
│                                                                         │
│  sandbox.execute(           apis.my_api:                                │
│    "my_api:ping",             api_key: "YOUR_KEY"                       │
│    {"message": "hello"}       base_url: "..."                           │
│  )                            timeout: 10                               │
│       │                           │                                     │
│       │                           │                                     │
│       │                           ↓                                     │
│       │              ┌────────────────────────────┐                     │
│       │              │  注册时注入到实例内部:      │                     │
│       │              │  self._config = {          │                     │
│       │              │    "api_key": "YOUR_KEY",  │                     │
│       │              │    "base_url": "...",      │                     │
│       │              │    "timeout": 10           │                     │
│       │              │  }                         │                     │
│       │              └────────────────────────────┘                     │
│       │                                                                 │
│       └──────────────────────────────────────────────┐                  │
│                                                      ↓                  │
│                                    execute 的 kwargs:                   │
│                                    {                                    │
│                                      "message": "hello",    ← params    │
│                                      "session_id": "xxx",   ← 系统注入  │
│                                      "trace_id": "zzz",     ← 系统注入  │
│                                    }                                    │
│                                          ↓                              │
│                          execute(self, message: str, **kwargs)          │
│                                    ↑              ↑                     │
│                              显式形参        运行时参数                  │
│                                                                         │
│                          配置获取: self.get_config("api_key")           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 参数获取方式

| 参数类型 | 获取方式 | 示例 |
|---------|---------|------|
| 业务参数 | 直接作为函数形参 | `message: str` |
| 配置项 | `self.get_config("key")` | `self.get_config("api_key")` |
| 系统元数据 | `kwargs.get("key")` | `kwargs.get("session_id")` |

> **配置获取方法**：
> - `self.get_config("key")` - 获取单个配置项，支持默认值：`self.get_config("timeout", 30)`
> - `self.config` - 获取完整配置字典（只读副本）
> - `self._config` - 直接访问配置字典

### 多参数示例

```python
# 调用方 - 多个参数
await sandbox.execute("visit", {
    "urls": ["https://example.com"],
    "goal": "Extract product prices"
})

# 工具方 - 对应的 execute 签名
async def execute(
    self,
    urls: Union[str, List[str]],  # ← 对应 params["urls"]
    goal: str,                     # ← 对应 params["goal"]
    **kwargs
) -> Any:
    # 从实例内部获取配置
    jina_api_key = self.get_config("jina_api_key")
    timeout = self.get_config("timeout", 30)
    ...
```

### 带默认值的参数

```python
# 调用方 - 可以省略有默认值的参数
await sandbox.execute("example_api:echo", {"latency_ms": 500})

# 工具方 - 带默认值的形参
async def execute(
    self,
    response_body: Any = {"status": "ok"},  # 有默认值，可省略
    latency_ms: int = 0,                     # 有默认值，可省略
    failure_rate: float = 0.0,               # 有默认值，可省略
    **kwargs
) -> Any:
    ...
```

### 参数错误处理

假设 `execute` 签名为 `execute(self, message: str, **kwargs)`：

| 调用示例 | 结果 | 说明 |
|---------|------|------|
| `{"message": "hi", "foo": "bar"}` | ✅ 正常 | 多余参数被 `**kwargs` 吸收 |
| `{"msg": "hi"}` | ❌ 错误 5999 | 参数名错误，`message` 缺失 |
| `{}` | ❌ 错误 5999 | 缺少必需参数 `message` |

**错误码说明**：
- `5999 UNEXPECTED_ERROR`：参数名错误或缺失（Python TypeError）
- `5000 EXECUTION_ERROR`：开发者主动 `raise ToolBusinessError(...)`

**建议**：对必需参数使用默认值 `None`，然后手动校验以提供更友好的错误信息：

```python
async def execute(self, message: str = None, **kwargs) -> Any:
    if message is None:
        raise ToolBusinessError("Missing required parameter: 'message'")
    # 业务逻辑...
```

## 工具名称规范

建议统一使用：

```
<resource_or_domain>:<action>
```

示例：
- `websearch:search`
- `rag:search`
- `my_api:ping`
- `my_api:get_user`

建议规则：
- 前缀使用"资源或业务域名"（如 `my_api`、`payment`、`notify`）
- 动作使用小写动词（如 `search`、`fetch`、`list`、`ping`）
- 避免只用通用动词（如 `search`）以防命名冲突

## 依赖包参考

### 服务端核心（必需）

```bash
pip install fastapi uvicorn
```

| 包名 | 用途 |
|------|------|
| `fastapi` | Web 框架 |
| `uvicorn` | ASGI 服务器 |

### 现有工具依赖

| 包名 | 用途 | 使用工具 |
|------|------|---------|
| `requests` | HTTP 请求 | `websearch.py` |
| `openai` | LLM 调用 | `websearch.py` |
| `crawl4ai` | 网页爬取（可选） | `websearch.py` |

```bash
# 安装现有工具依赖
pip install requests openai

# 可选依赖
pip install crawl4ai
```

### 新工具依赖建议

如果新工具引入重型依赖，建议使用可选导入模式：

```python
# 推荐：可选依赖处理
try:
    import heavy_package
    HEAVY_AVAILABLE = True
except ImportError:
    HEAVY_AVAILABLE = False

class MyTool(BaseApiTool):
    async def execute(self, **kwargs):
        if not HEAVY_AVAILABLE:
            raise ToolBusinessError("heavy_package not installed")
        # 业务逻辑...
```

> **注意**：API Tools 模块在服务启动时会全部导入，即使配置中未使用。重型依赖若不做可选处理会影响启动速度。
