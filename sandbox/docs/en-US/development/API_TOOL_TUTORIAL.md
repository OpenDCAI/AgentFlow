# API-Type Backend (Stateless Tool) Development Tutorial

This tutorial explains how to build a new API-type backend (stateless tool) in this project and quickly validate it with `quick_sandbox.py`.

With the `BaseApiTool` infrastructure, adding a new tool is now standardized and straightforward.

## 1) Create a config file

Create a config file under `configs/sandbox-server/`. A good starting point is
`configs/sandbox-server/web_config.json`, then create your own file
(for example, `my_api_sandbox.json`).

Example:

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

Notes:
- Values under `apis.<config_key>` are injected into the tool instance's `self._config` during registration.
- Read config in the tool via `self.get_config("key")`.

## 2) Implement the tool class

Use `sandbox/server/backends/tools/websearch.py` as a reference, then create your
own tool file under `sandbox/server/backends/tools/` (for example, `my_api_tool.py`).

### Standard implementation steps

1. Inherit from `BaseApiTool`
2. Implement `execute` (business logic only)
3. Register the instance via `register_api_tool`

```python
from typing import Any
from .base_tool import BaseApiTool, ToolBusinessError
from ..error_codes import ErrorCode
from . import register_api_tool

# 1. Inherit BaseApiTool
class MyApiTool(BaseApiTool):
    def __init__(self):
        # No args required. Registration auto-injects tool_name/resource_type/config.
        super().__init__()

    # 2. Implement execute
    async def execute(self, message: str, **kwargs) -> Any:
        """
        My API ping test

        Args:
            message: Input message
            **kwargs: Runtime params such as session_id and trace_id
        """
        api_key = self.get_config("api_key")
        if not api_key:
            raise ToolBusinessError("API Key missing", ErrorCode.EXECUTION_ERROR)

        try:
            result = f"PONG: {message} (Key: {api_key[:4]}***)"
            return {"result": result}
        except Exception as e:
            raise ToolBusinessError(f"Ping failed: {str(e)}")

# 3. Register tool instance
ping_tool = register_api_tool(
    name="my_api:ping",
    config_key="my_api",
    description="My API ping test"
)(MyApiTool())
```

## 3) Trigger auto-registration (module import)

Add an import in `sandbox/server/backends/tools/__init__.py`:

```python
from . import example_api_tool
```

Then `register_all_tools()` can auto-register this tool at startup.

## 4) Run with quick_sandbox.py (manual server startup)

`quick_sandbox.py` connects to an already running Sandbox Server. It does not auto-start the service.

### 4.1 Update script config

```python
CONFIG_PATH = "configs/sandbox-server/my_api_sandbox.json"
```

And execute your new tool:

```python
result = await sandbox.execute(
    "my_api:ping",
    {"message": "hello"}
)
```

### 4.2 Start server manually (CLI)

```bash
./start_sandbox_server.sh --config configs/sandbox-server/my_api_sandbox.json
```

Default port is `18890`, and `quick_sandbox.py` connects to `http://127.0.0.1:18890`.

### 4.3 Run script

```bash
python /home/a1/sdb/tzw/Synthesis/quick_sandbox.py
```

## Parameter mapping

### Call format

All tools share the same call format:

```python
await sandbox.execute(
    "tool_name",
    {"param_name": param_value}
)
```

### Mapping rule

The keys in `params` must match the `execute()` signature:

```python
# caller
await sandbox.execute("my_api:ping", {"message": "hello"})

# tool
async def execute(self, message: str, **kwargs) -> Any:
    ...
```

### How to read different parameter types

| Parameter Type | Access Method | Example |
|---------|---------|------|
| Business parameters | Direct function arguments | `message: str` |
| Config values | `self.get_config("key")` | `self.get_config("api_key")` |
| Runtime metadata | `kwargs.get("key")` | `kwargs.get("session_id")` |

Config access methods:
- `self.get_config("key")` supports default values, e.g. `self.get_config("timeout", 30)`
- `self.config` returns a read-only copy of full config
- `self._config` accesses internal config directly

### Multi-parameter example

```python
# caller
await sandbox.execute("visit", {
    "urls": ["https://example.com"],
    "goal": "Extract product prices"
})

# tool
async def execute(
    self,
    urls: Union[str, List[str]],
    goal: str,
    **kwargs
) -> Any:
    jina_api_key = self.get_config("jina_api_key")
    timeout = self.get_config("timeout", 30)
    ...
```

### Default argument example

```python
# caller can omit defaulted args
await sandbox.execute("example_api:echo", {"latency_ms": 500})

# tool signature with defaults
async def execute(
    self,
    response_body: Any = {"status": "ok"},
    latency_ms: int = 0,
    failure_rate: float = 0.0,
    **kwargs
) -> Any:
    ...
```

### Parameter error handling

Assume signature is `execute(self, message: str, **kwargs)`:

| Call Payload | Result | Description |
|---------|------|------|
| `{"message": "hi", "foo": "bar"}` | OK | extra fields are absorbed by `**kwargs` |
| `{"msg": "hi"}` | Error 5999 | wrong parameter name, missing `message` |
| `{}` | Error 5999 | required parameter `message` is missing |

Error code notes:
- `5999 UNEXPECTED_ERROR`: wrong/missing parameter name (Python `TypeError`)
- `5000 EXECUTION_ERROR`: tool explicitly raises `ToolBusinessError(...)`

Recommended pattern for friendlier required-param errors:

```python
async def execute(self, message: str = None, **kwargs) -> Any:
    if message is None:
        raise ToolBusinessError("Missing required parameter: 'message'")
    ...
```

## Tool naming convention

Recommended format:

`<resource_or_domain>:<action>`

Examples:
- `websearch:search`
- `rag:search`
- `my_api:ping`
- `my_api:get_user`

Recommended naming rules:
- Prefix: resource or business domain (`my_api`, `payment`, `notify`)
- Action: lowercase verbs (`search`, `fetch`, `list`, `ping`)
- Avoid overly generic names like `search` without a namespace

## Dependency reference

### Server core (required)

```bash
pip install fastapi uvicorn
```

### Existing tool dependencies

```bash
pip install requests openai
pip install crawl4ai  # optional
```

### Recommendation for heavy optional deps

```python
try:
    import heavy_package
    HEAVY_AVAILABLE = True
except ImportError:
    HEAVY_AVAILABLE = False

class MyTool(BaseApiTool):
    async def execute(self, **kwargs):
        if not HEAVY_AVAILABLE:
            raise ToolBusinessError("heavy_package not installed")
        ...
```

Note: API tool modules are imported at server startup. If heavy dependencies are imported unconditionally, startup time will increase even when the tool is not used.


