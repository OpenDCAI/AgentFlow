#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick verification script for mock capabilities.

This lightweight script does not start the server. It only verifies:
1. Module imports
2. Backend instantiation
3. Tool registration
4. Basic function calls

Run:
    python -m sandbox.tests.test_quick_verify
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path.
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test module imports."""
    print("📦 测试模块导入...")
    
    try:
        from sandbox.server import HTTPServiceServer
        from sandbox.server.backends.resources import (
            VMBackend, BashBackend, BrowserBackend,
            CodeExecutorBackend, RAGBackend
        )
        from sandbox.server.backends.tools.websearch import (
            search, visit
        )
        print("  [OK] 所有模块导入成功")
        return True
    except Exception as e:
        print(f"  [FAIL] 导入失败: {e}")
        return False


def test_backend_instantiation():
    """Test backend instantiation."""
    print("\n🔧 测试后端实例化...")
    
    try:
        from sandbox.server.backends.resources import (
            VMBackend, BashBackend, BrowserBackend,
            CodeExecutorBackend, RAGBackend
        )
        
        backends = [
            ("VMBackend", VMBackend),
            ("BashBackend", BashBackend),
            ("BrowserBackend", BrowserBackend),
            ("CodeExecutorBackend", CodeExecutorBackend),
            ("RAGBackend", RAGBackend),
        ]
        
        for name, BackendClass in backends:
            backend = BackendClass()
            assert hasattr(backend, 'name'), f"{name} 缺少 name 属性"
            print(f"  [OK] {name}: {backend.name}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 实例化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_load_backends():
    """Test server backend loading."""
    print("\n🖥️ 测试服务器加载后端...")
    
    try:
        from sandbox.server import HTTPServiceServer
        from sandbox.server.backends.resources import (
            VMBackend, BashBackend, BrowserBackend,
            CodeExecutorBackend, RAGBackend
        )
        
        server = HTTPServiceServer(host="127.0.0.1", port=9999)
        
        backends = [
            ("vm", VMBackend()),
            ("bash", BashBackend()),
            ("browser", BrowserBackend()),
            ("code", CodeExecutorBackend()),
            ("rag", RAGBackend()),
        ]
        
        total_tools = 0
        for name, backend in backends:
            tools = server.load_backend(backend)
            total_tools += len(tools)
            print(f"  [OK] {name}: {len(tools)} 工具")
        
        all_tools = server.list_tools()
        print(f"  [OK] 已注册工具总数: {len(all_tools)}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_backend_lifecycle():
    """Test backend lifecycle."""
    print("\n🔄 测试后端生命周期...")
    
    try:
        from sandbox.server.backends.resources import (
            VMBackend, BashBackend, BrowserBackend,
            CodeExecutorBackend, RAGBackend
        )
        
        test_worker_id = "test_worker"
        
        backends_with_config = [
            ("VMBackend", VMBackend(), {"screen_size": [1920, 1080]}),
            ("BashBackend", BashBackend(), {"shell_type": "local"}),
            ("BrowserBackend", BrowserBackend(), {"browser_type": "chromium"}),
            ("CodeExecutorBackend", CodeExecutorBackend(), {"runtime": "python:3.10"}),
            ("RAGBackend", RAGBackend(), {}),
        ]
        
        for name, backend, config in backends_with_config:
            # Test initialize.
            result = await backend.initialize(test_worker_id, config)
            assert isinstance(result, dict), f"{name}.initialize() 应返回 dict"
            
            # Test cleanup.
            session_info = {
                "session_name": f"{backend.name}_session",
                "data": result
            }
            await backend.cleanup(test_worker_id, session_info)
            
            print(f"  [OK] {name}: initialize/cleanup")
        
        # Test RAG warmup.
        rag = RAGBackend()
        await rag.warmup()
        print(f"  [OK] RAGBackend: warmup")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 生命周期测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websearch_tools():
    """Test WebSearch tools."""
    print("\n🔍 测试 WebSearch 工具...")
    
    try:
        from sandbox.server.backends.tools.websearch import (
            search, visit
        )
        
        # Test search.
        result = await search(query="Python tutorial", max_results=5)
        assert result.get("code") == 0, f"search 失败: {result.get('message')}"
        data = result.get("data", {})
        assert "result" in data, "search 应返回 data.result"
        print(f"  [OK] search: {len(data.get('result', ''))} 字符")
        
        # Test visit.
        result = await visit(urls="https://example.com", goal="Extract main content")
        assert result.get("code") == 0, f"visit 失败: {result.get('message')}"
        data = result.get("data", {})
        assert "result" in data, "visit 应返回 data.result"
        print(f"  [OK] visit: 成功")
        
        return True
    except Exception as e:
        print(f"  [FAIL] WebSearch 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entrypoint."""
    # Configure stdout/stderr encoding (Windows compatibility).
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("""
======================================================================
          Sandbox Mock Quick Verification
======================================================================
  Verification items:
    - Module imports
    - Backend instantiation
    - Server backend loading
    - Backend lifecycle
    - WebSearch tools
======================================================================
""")
    
    results = []
    
    # 1. Import test.
    results.append(("模块导入", test_imports()))
    
    # 2. Instantiation test.
    results.append(("后端实例化", test_backend_instantiation()))
    
    # 3. Server loading test.
    results.append(("服务器加载", test_server_load_backends()))
    
    # 4. Lifecycle test.
    results.append(("后端生命周期", await test_backend_lifecycle()))
    
    # 5. WebSearch test.
    results.append(("WebSearch 工具", await test_websearch_tools()))
    
    # Print summary.
    print(f"\n{'='*70}")
    print(f"验证结果")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\n  通过: {passed}/{total}")
    print(f"{'='*70}\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] 验证被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

