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

