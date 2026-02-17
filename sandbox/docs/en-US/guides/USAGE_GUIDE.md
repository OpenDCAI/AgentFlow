# Sandbox Usage Guide (Module-level)

This guide focuses on the usage patterns and core concepts of the Sandbox module.

## Quick Start

### Method 1: Auto-start (Recommended)

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

> Note: `Sandbox` defaults `server_url` to `http://localhost:8080`. If using
> `bin/sandbox-server.sh` to start, explicitly set it to `18890`.

### Method 2: Manual Server Startup

```python
from sandbox.server.config_loader import create_server_from_config

server = create_server_from_config("sandbox/configs/profiles/dev.json")
server.run()
```

Client connection:

```python
from sandbox import Sandbox

sandbox = Sandbox(server_url="http://127.0.0.1:18890", auto_start_server=False)
await sandbox.start()
```

### Method 3: Connect to Existing Server (Without Context Manager)

Suitable for scenarios requiring manual connection lifecycle management:

```python
import asyncio
from sandbox import Sandbox

async def main():
    # Connect to running server
    sandbox = Sandbox(
        server_url="http://127.0.0.1:18890",
        auto_start_server=False
    )

    # Start connection
    await sandbox.start()

    try:
        # Create Session (can pass custom name)
        await sandbox.create_session("vm", {"custom_name": "my_vm"})

        # Execute multiple operations
        result1 = await sandbox.execute("vm:screenshot", {})
        print(f"Screenshot result: {result1}")

        result2 = await sandbox.execute("bash:run", {"command": "ls -la"})
        if result2.get("code") == 0:
            print(f"Command output: {result2['data']}")

        # Destroy Session
        await sandbox.destroy_session("vm")

    finally:
        # Ensure connection is closed
        await sandbox.close()

asyncio.run(main())
```

> Tip: Use `try-finally` to ensure connection is properly closed even if exceptions occur.

## Warmup

### Configuration File Warmup

```json
{
  "warmup": {
    "enabled": true,
    "resources": ["rag", "vm"]
  }
}
```

### Client Explicit Warmup

```python
async with Sandbox(server_url="http://127.0.0.1:18890") as sandbox:
    await sandbox.warmup(["rag", "vm"])
    status = await sandbox.get_warmup_status()
```

## Session Management (Brief)

- **Explicit Session**: Suitable for multiple operations on the same resource.
- **Temporary Session**: Automatically created when executing stateful tools, destroyed after use.

```python
async with Sandbox(server_url="http://127.0.0.1:18890") as sandbox:
    await sandbox.create_session("vm", {"custom_name": "my_vm"})
    await sandbox.execute("vm:screenshot", {})
    await sandbox.destroy_session("vm")
```

## Common APIs

| Method | Description |
|--------|-------------|
| `await sandbox.start()` | Start and connect to server |
| `await sandbox.close()` | Close client connection |
| `await sandbox.warmup([...])` | Warm up backends |
| `await sandbox.execute(action, params)` | Execute tool |
| `await sandbox.create_session(resource)` | Create Session (supports passing `custom_name` in config) |
| `await sandbox.destroy_session(resource)` | Destroy Session |

## Related Documentation

- [System Architecture](ARCHITECTURE.md)
- [Backend Development Guide](../development/BACKEND_DEVELOPMENT.md)

