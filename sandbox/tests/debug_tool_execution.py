#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试工具执行 - 直接测试后端工具方法

这个脚本直接测试后端的工具方法，跳过 HTTP 层，
帮助定位工具执行失败的根本原因。

运行方式:
    python3 -m sandbox.tests.debug_tool_execution
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def test_bash_backend():
    """直接测试 Bash 后端"""
    print_section("测试 Bash 后端")
    
    try:
        from sandbox.server.backends.resources import BashBackend
        
        backend = BashBackend()
        worker_id = "debug_worker"
        config = {"shell_type": "local"}
        
        print("1. 初始化后端...")
        init_result = await backend.initialize(worker_id, config)
        print(f"   初始化结果: {list(init_result.keys())}")
        
        # 构造 session_info（模拟 ResourceRouter 的行为）
        session_info = {
            "session_id": "debug_session_001",
            "session_name": "bash_debug_001",
            "worker_id": worker_id,
            "resource_type": "bash",
            "status": "active",
            "data": init_result  # initialize() 的返回值
        }
        
        print(f"\n2. Session Info 结构:")
        print(f"   - session_id: {session_info['session_id']}")
        print(f"   - status: {session_info['status']}")
        print(f"   - data keys: {list(session_info['data'].keys())}")
        
        print(f"\n3. 测试工具方法...")
        
        # 测试 bash:pwd
        print("\n   测试 bash:pwd...")
        try:
            result = await backend.get_cwd(session_info=session_info)
            print(f"   ✅ bash:pwd 成功: {result}")
        except Exception as e:
            print(f"   ❌ bash:pwd 失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试 bash:run
        print("\n   测试 bash:run...")
        try:
            result = await backend.run_command(
                command="echo 'Hello World'",
                session_info=session_info
            )
            print(f"   ✅ bash:run 成功: {result}")
        except Exception as e:
            print(f"   ❌ bash:run 失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 清理
        print("\n4. 清理...")
        await backend.cleanup(worker_id, session_info)
        print("   ✅ 清理完成")
        
    except Exception as e:
        print(f"❌ Bash 后端测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_vm_backend():
    """直接测试 VM 后端"""
    print_section("测试 VM 后端")
    
    try:
        from sandbox.server.backends.resources import VMBackend
        
        backend = VMBackend()
        worker_id = "debug_worker"
        config = {"screen_size": [1920, 1080]}
        
        print("1. 初始化后端...")
        init_result = await backend.initialize(worker_id, config)
        print(f"   初始化结果: {list(init_result.keys())}")
        
        session_info = {
            "session_id": "debug_session_001",
            "session_name": "vm_debug_001",
            "worker_id": worker_id,
            "resource_type": "vm",
            "status": "active",
            "data": init_result
        }
        
        print(f"\n2. Session Info 结构:")
        print(f"   - data keys: {list(session_info['data'].keys())}")
        
        print(f"\n3. 测试工具方法...")
        
        # 测试 vm:screenshot
        print("\n   测试 vm:screenshot...")
        try:
            result = await backend.screenshot(session_info=session_info)
            print(f"   ✅ vm:screenshot 成功: 返回了 {len(result.get('image', ''))} 字节的图像数据")
        except Exception as e:
            print(f"   ❌ vm:screenshot 失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 清理
        print("\n4. 清理...")
        await backend.cleanup(worker_id, session_info)
        print("   ✅ 清理完成")
        
    except Exception as e:
        print(f"❌ VM 后端测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_tool_registration():
    """测试工具注册"""
    print_section("测试工具注册")
    
    try:
        from sandbox.server import HTTPServiceServer
        from sandbox.server.backends.resources import BashBackend, VMBackend
        
        server = HTTPServiceServer(host="127.0.0.1", port=19999)
        
        # 加载后端
        bash_backend = BashBackend()
        vm_backend = VMBackend()
        
        print("1. 加载 Bash 后端...")
        bash_tools = server.load_backend(bash_backend)
        print(f"   注册的工具: {bash_tools}")
        
        print("\n2. 加载 VM 后端...")
        vm_tools = server.load_backend(vm_backend)
        print(f"   注册的工具: {vm_tools}")
        
        print("\n3. 检查工具资源类型映射...")
        for tool_name in ["bash:pwd", "bash:run", "vm:screenshot", "vm:click"]:
            resource_type = server._tool_resource_types.get(tool_name)
            print(f"   {tool_name} -> resource_type: {resource_type}")
        
        print("\n✅ 工具注册测试完成")
        
    except Exception as e:
        print(f"❌ 工具注册测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    print("\n" + "="*60)
    print("           调试工具执行")
    print("="*60)
    
    await test_tool_registration()
    await test_bash_backend()
    await test_vm_backend()
    
    print("\n" + "="*60)
    print("           测试完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

