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
> `start_sandbox_server.sh` to start, explicitly set it to `18890`.

### Method 2: Manual Server Startup (Standard)

Use the project-root script `start_sandbox_server.sh` and explicitly pass a config
from `configs/sandbox-server`:

```bash
# Run from project root
./start_sandbox_server.sh --config configs/sandbox-server/rag_config.json
```

You can switch to other configs as needed:

```bash
./start_sandbox_server.sh --config configs/sandbox-server/web_config.json
./start_sandbox_server.sh --config configs/sandbox-server/text2sql_config.json
./start_sandbox_server.sh --config configs/sandbox-server/vm_config.json
```

> Note: this script resolves host/port from `server.url` / `server.port` in config,
> and ignores CLI `--host` / `--port` to avoid conflicting inputs.

Client connection:

```python
from sandbox import Sandbox

sandbox = Sandbox(server_url="http://127.0.0.1:18890", auto_start_server=False)
await sandbox.start()
```

### Config Parameters (`configs/sandbox-server/`)

Typical structure (fields may vary by scenario):

```json
{
  "server": {},
  "resources": {},
  "apis": {},
  "warmup": {}
}
```

Key fields:

- `server`
  - `url`: service address (e.g., `http://127.0.0.1:18890`), preferred for host/port resolution.
  - `port`: fallback port when `url` does not include one.
  - `session_ttl`: session expiration in seconds.
- `resources`
  - Stateful backends (e.g., `vm`, `rag`).
  - Typical per-backend fields:
    - `enabled`: whether this backend is enabled.
    - `backend_class`: import path of backend implementation.
    - `config`: backend init params (model path, screen size, etc.).
- `apis`
  - Stateless API tool configs (e.g., `websearch`, `text2sql`).
  - Values are injected into corresponding tool instances (API keys, DB paths, timeout, etc.).
- `warmup`
  - `enabled`: whether to warm up at startup.
  - `resources`: list of resources to warm up (e.g., `["rag"]`, `["vm"]`).

Config selection:

- RAG retrieval: `configs/sandbox-server/rag_config.json`
- Web search/visit: `configs/sandbox-server/web_config.json`
- Text2SQL: `configs/sandbox-server/text2sql_config.json`
- VM only: `configs/sandbox-server/vm_config.json`

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

