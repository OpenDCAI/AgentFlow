# Sandbox 使用指南（模块内）

本指南聚焦 Sandbox 模块的使用方式与核心概念。

## 快速开始

### 方式一：自动启动（推荐）

```python
import asyncio
from sandbox import Sandbox

async def main():
    sandbox = Sandbox(
        server_url="http://127.0.0.1:18890",
        auto_start_server=True,
        server_config_path="sandbox/configs/profiles/dev.json"
    )
    await sandbox.start()

    result = await sandbox.execute("bash:run", {"command": "echo hello"})
    if result.get("code") == 0:
        print(result["data"])

    await sandbox.close()

asyncio.run(main())
```

> 注意：`Sandbox` 默认 `server_url` 为 `http://localhost:8080`，如果使用
> `bin/sandbox-server.sh` 启动，请显式设置为 `18890`。

### 方式二：手动启动服务器

```python
from sandbox.server.config_loader import create_server_from_config

server = create_server_from_config("sandbox/configs/profiles/dev.json")
server.run()
```

客户端连接：

```python
from sandbox import Sandbox

sandbox = Sandbox(server_url="http://127.0.0.1:18890", auto_start_server=False)
await sandbox.start()
```

### 方式三：连接现有服务器（不使用上下文管理器）

适用于需要手动管理连接生命周期的场景：

```python
import asyncio
from sandbox import Sandbox

async def main():
    # 连接到已运行的服务器
    sandbox = Sandbox(
        server_url="http://127.0.0.1:18890",
        auto_start_server=False
    )

    # 启动连接
    await sandbox.start()

    try:
        # 创建 Session（可传自定义名称）
        await sandbox.create_session("vm", {"custom_name": "my_vm"})

        # 执行多个操作
        result1 = await sandbox.execute("vm:screenshot", {})
        print(f"Screenshot result: {result1}")

        result2 = await sandbox.execute("bash:run", {"command": "ls -la"})
        if result2.get("code") == 0:
            print(f"Command output: {result2['data']}")

        # 销毁 Session
        await sandbox.destroy_session("vm")

    finally:
        # 确保关闭连接
        await sandbox.close()

asyncio.run(main())
```

> 提示：使用 `try-finally` 确保即使发生异常也能正确关闭连接。

## Warmup 预热

### 配置文件预热

```json
{
  "warmup": {
    "enabled": true,
    "resources": ["rag", "vm"]
  }
}
```

### 客户端显式预热

```python
async with Sandbox(server_url="http://127.0.0.1:18890") as sandbox:
    await sandbox.warmup(["rag", "vm"])
    status = await sandbox.get_warmup_status()
```

## Session 管理（简要）

- **显式 Session**：适合多次操作同一资源。
- **临时 Session**：执行有状态工具时自动创建，用完即销毁。

```python
async with Sandbox(server_url="http://127.0.0.1:18890") as sandbox:
    await sandbox.create_session("vm", {"custom_name": "my_vm"})
    await sandbox.execute("vm:screenshot", {})
    await sandbox.destroy_session("vm")
```

## 常用 API

| 方法 | 说明 |
|------|------|
| `await sandbox.start()` | 启动并连接服务器 |
| `await sandbox.close()` | 关闭客户端连接 |
| `await sandbox.warmup([...])` | 预热后端 |
| `await sandbox.execute(action, params)` | 执行工具 |
| `await sandbox.create_session(resource)` | 创建 Session（支持在 config 中传 `custom_name`） |
| `await sandbox.destroy_session(resource)` | 销毁 Session |

## 相关文档

- [系统架构](ARCHITECTURE.md)
- [后端开发详细指南](../development/BACKEND_DEVELOPMENT.md)

