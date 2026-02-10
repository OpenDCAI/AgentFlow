#!/usr/bin/env python3
# sandbox/tests/test_mock_backends.py
"""
Mock 后端综合测试

测试所有 Mock 后端是否可以正常加载和工作：
- VMBackend - 虚拟机/桌面自动化
- BashBackend - 命令行终端
- BrowserBackend - 浏览器自动化
- CodeExecutorBackend - 代码执行沙箱
- RAGBackend - 文档检索
- WebSearch Tools - 网页搜索 API

运行方式:
    python -m sandbox.tests.test_mock_backends
    
或者带参数:
    python -m sandbox.tests.test_mock_backends --verbose
    python -m sandbox.tests.test_mock_backends --test backend   # 只测试后端加载
    python -m sandbox.tests.test_mock_backends --test tools     # 只测试工具功能
"""

import sys
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 默认只显示警告和错误
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MockBackendTest")


class TestStatus(Enum):
    PASSED = "✅"
    FAILED = "❌"
    SKIPPED = "⏭️"
    ERROR = "💥"


@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str = ""
    duration_ms: float = 0


class TestRunner:
    """测试运行器"""
    
    def __init__(self, verbose: bool = False):
        self.results: List[TestResult] = []
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.INFO)
    
    def add_result(self, result: TestResult):
        self.results.append(result)
        icon = result.status.value
        name = result.name
        
        if result.status == TestStatus.PASSED:
            print(f"  {icon} {name} ({result.duration_ms:.1f}ms)")
        else:
            print(f"  {icon} {name}: {result.message}")
    
    def summary(self) -> bool:
        """打印测试摘要，返回是否全部通过"""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        total = len(self.results)
        
        print(f"\n{'='*60}")
        print(f"📊 测试结果摘要")
        print(f"{'='*60}")
        print(f"  ✅ 通过: {passed}")
        print(f"  ❌ 失败: {failed}")
        print(f"  💥 错误: {errors}")
        print(f"  ⏭️ 跳过: {skipped}")
        print(f"  📦 总计: {total}")
        
        if failed > 0 or errors > 0:
            print(f"\n❌ 失败/错误的测试:")
            for r in self.results:
                if r.status in (TestStatus.FAILED, TestStatus.ERROR):
                    print(f"   - {r.name}: {r.message}")
        
        print(f"{'='*60}\n")
        
        return failed == 0 and errors == 0


# ============================================================================
# 后端加载测试
# ============================================================================

async def test_backend_imports(runner: TestRunner):
    """测试后端模块导入"""
    print("\n📦 测试后端模块导入...")
    
    import time
    
    # 测试 resources 后端导入
    start = time.time()
    try:
        from sandbox.server.backends.resources import (
            VMBackend,
            BashBackend,
            BrowserBackend,
            CodeExecutorBackend,
            RAGBackend
        )
        duration = (time.time() - start) * 1000
        runner.add_result(TestResult(
            "导入 resources 后端",
            TestStatus.PASSED,
            duration_ms=duration
        ))
    except ImportError as e:
        runner.add_result(TestResult(
            "导入 resources 后端",
            TestStatus.ERROR,
            str(e)
        ))
        return
    
    # 测试 tools 后端导入
    start = time.time()
    try:
        from sandbox.server.backends.tools import (
            register_api_tool,
            get_all_api_tools,
            register_all_tools
        )
        duration = (time.time() - start) * 1000
        runner.add_result(TestResult(
            "导入 tools 模块",
            TestStatus.PASSED,
            duration_ms=duration
        ))
    except ImportError as e:
        runner.add_result(TestResult(
            "导入 tools 模块",
            TestStatus.ERROR,
            str(e)
        ))


async def test_backend_instantiation(runner: TestRunner):
    """测试后端实例化"""
    print("\n🔧 测试后端实例化...")
    
    import time
    
    from sandbox.server.backends.resources import (
        VMBackend,
        BashBackend,
        BrowserBackend,
        CodeExecutorBackend,
        RAGBackend
    )
    
    backends = [
        ("VMBackend", VMBackend),
        ("BashBackend", BashBackend),
        ("BrowserBackend", BrowserBackend),
        ("CodeExecutorBackend", CodeExecutorBackend),
        ("RAGBackend", RAGBackend),
    ]
    
    for name, BackendClass in backends:
        start = time.time()
        try:
            backend = BackendClass()
            duration = (time.time() - start) * 1000
            
            # 验证基本属性
            assert hasattr(backend, 'name'), f"{name} 缺少 name 属性"
            assert hasattr(backend, 'description'), f"{name} 缺少 description 属性"
            
            runner.add_result(TestResult(
                f"实例化 {name}",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"实例化 {name}",
                TestStatus.ERROR,
                str(e)
            ))


async def test_server_load_backends(runner: TestRunner):
    """测试服务器加载后端"""
    print("\n🖥️ 测试服务器加载后端...")
    
    import time
    
    from sandbox.server import HTTPServiceServer
    from sandbox.server.backends.resources import (
        VMBackend,
        BashBackend,
        BrowserBackend,
        CodeExecutorBackend,
        RAGBackend
    )
    
    server = HTTPServiceServer(
        host="127.0.0.1",
        port=9999,  # 使用非标准端口避免冲突
        title="Mock Backend Test Server"
    )
    
    backends = [
        ("vm", VMBackend),
        ("bash", BashBackend),
        ("browser", BrowserBackend),
        ("code", CodeExecutorBackend),
        ("rag", RAGBackend),
    ]
    
    for name, BackendClass in backends:
        start = time.time()
        try:
            backend = BackendClass()
            tools = server.load_backend(backend)
            duration = (time.time() - start) * 1000
            
            runner.add_result(TestResult(
                f"加载 {name} 后端 ({len(tools)} 工具)",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"加载 {name} 后端",
                TestStatus.ERROR,
                str(e)
            ))
    
    # 验证工具总数
    all_tools = server.list_tools()
    print(f"  📊 已注册工具总数: {len(all_tools)}")
    
    return server


# ============================================================================
# 后端初始化和清理测试
# ============================================================================

async def test_backend_lifecycle(runner: TestRunner):
    """测试后端生命周期 (initialize/cleanup)"""
    print("\n🔄 测试后端生命周期...")
    
    import time
    
    from sandbox.server.backends.resources import (
        VMBackend,
        BashBackend,
        BrowserBackend,
        CodeExecutorBackend,
        RAGBackend
    )
    
    test_worker_id = "test_worker_001"
    
    backends_with_config = [
        ("VMBackend", VMBackend(), {"screen_size": [1920, 1080]}),
        ("BashBackend", BashBackend(), {"shell_type": "local"}),
        ("BrowserBackend", BrowserBackend(), {"browser_type": "chromium", "headless": True}),
        ("CodeExecutorBackend", CodeExecutorBackend(), {"runtime": "python:3.10"}),
        ("RAGBackend", RAGBackend(), {"model_name": "e5-base"}),
    ]
    
    for name, backend, config in backends_with_config:
        # 测试 initialize
        start = time.time()
        try:
            result = await backend.initialize(test_worker_id, config)
            duration = (time.time() - start) * 1000
            
            assert isinstance(result, dict), f"{name}.initialize() 应返回 dict"
            
            runner.add_result(TestResult(
                f"{name}.initialize()",
                TestStatus.PASSED,
                duration_ms=duration
            ))
            
            # 测试 cleanup
            session_info = {
                "session_name": f"{backend.name}_session_001",
                "data": result
            }
            start = time.time()
            await backend.cleanup(test_worker_id, session_info)
            duration = (time.time() - start) * 1000
            
            runner.add_result(TestResult(
                f"{name}.cleanup()",
                TestStatus.PASSED,
                duration_ms=duration
            ))
            
        except Exception as e:
            runner.add_result(TestResult(
                f"{name} 生命周期",
                TestStatus.ERROR,
                str(e)
            ))


# ============================================================================
# 工具功能测试
# ============================================================================

async def test_vm_tools(runner: TestRunner):
    """测试 VM 后端工具"""
    print("\n🖥️ 测试 VM 工具...")
    
    import time
    
    from sandbox.server.backends.resources import VMBackend
    
    backend = VMBackend()
    worker_id = "vm_test_worker"
    
    # 初始化
    session_data = await backend.initialize(worker_id, {"screen_size": [1920, 1080]})
    session_info = {"session_name": "vm_test_session", "data": session_data}
    
    controller = session_data.get("controller")
    
    # 测试各个工具方法
    tool_tests = [
        ("screenshot", lambda: controller.screenshot()),
        ("click", lambda: controller.click(100, 200, "left")),
        ("double_click", lambda: controller.double_click(100, 200)),
        ("type_text", lambda: controller.type_text("Hello Mock", 0.0)),
        ("press_key", lambda: controller.press_key("enter")),
        ("hotkey", lambda: controller.hotkey("ctrl", "c")),
        ("scroll", lambda: controller.scroll(100, 200, 3)),
        ("drag", lambda: controller.drag(0, 0, 100, 100)),
        ("move", lambda: controller.move(500, 500)),
    ]
    
    for name, test_func in tool_tests:
        start = time.time()
        try:
            result = await test_func()
            duration = (time.time() - start) * 1000
            runner.add_result(TestResult(
                f"vm:{name}",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"vm:{name}",
                TestStatus.ERROR,
                str(e)
            ))
    
    # 清理
    await backend.cleanup(worker_id, session_info)


async def test_browser_tools(runner: TestRunner):
    """测试 Browser 后端工具"""
    print("\n🌐 测试 Browser 工具...")
    
    import time
    
    from sandbox.server.backends.resources import BrowserBackend
    
    backend = BrowserBackend()
    worker_id = "browser_test_worker"
    
    # 初始化
    session_data = await backend.initialize(worker_id, {
        "browser_type": "chromium",
        "headless": True
    })
    session_info = {"session_name": "browser_test_session", "data": session_data}
    
    browser = session_data.get("browser")
    page = browser.current_page
    
    # 测试各个工具方法
    tool_tests = [
        ("goto", lambda: page.goto("https://example.com")),
        ("screenshot", lambda: page.screenshot(False)),
        ("click", lambda: page.click("#button")),
        ("fill", lambda: page.fill("#input", "test value")),
        ("type_text", lambda: page.type_text("#input", "typed text", 0)),
        ("press", lambda: page.press("Enter")),
        ("select_option", lambda: page.select_option("#select", "option1")),
        ("get_content", lambda: page.get_content()),
        ("get_text", lambda: page.get_text(".content")),
        ("evaluate", lambda: page.evaluate("return document.title")),
        ("wait_for_selector", lambda: page.wait_for_selector("#element")),
        ("scroll", lambda: page.scroll(0, 500)),
    ]
    
    for name, test_func in tool_tests:
        start = time.time()
        try:
            result = await test_func()
            duration = (time.time() - start) * 1000
            runner.add_result(TestResult(
                f"browser:{name}",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"browser:{name}",
                TestStatus.ERROR,
                str(e)
            ))
    
    # 清理
    await backend.cleanup(worker_id, session_info)


async def test_bash_tools(runner: TestRunner):
    """测试 Bash 后端工具"""
    print("\n💻 测试 Bash 工具...")
    
    import time
    
    from sandbox.server.backends.resources import BashBackend
    
    backend = BashBackend()
    worker_id = "bash_test_worker"
    
    # 初始化
    session_data = await backend.initialize(worker_id, {"shell_type": "local"})
    session_info = {"session_name": "bash_test_session", "data": session_data}
    
    session = session_data.get("session")  # 后端返回 "session" 而不是 "terminal"
    
    # 测试各个工具方法（使用 BashSession 的实际方法）
    tool_tests = [
        ("run_command", lambda: session.run_command("echo 'Hello Mock'")),
        ("run_pwd", lambda: session.run_command("pwd")),
        ("run_cd", lambda: session.run_command("cd /tmp")),
    ]
    
    for name, test_func in tool_tests:
        start = time.time()
        try:
            result = await test_func()
            duration = (time.time() - start) * 1000
            runner.add_result(TestResult(
                f"bash:{name}",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"bash:{name}",
                TestStatus.ERROR,
                str(e)
            ))
    
    # 清理
    await backend.cleanup(worker_id, session_info)


async def test_code_executor_tools(runner: TestRunner):
    """测试 CodeExecutor 后端工具"""
    print("\n🐍 测试 CodeExecutor 工具...")
    
    import time
    
    from sandbox.server.backends.resources import CodeExecutorBackend
    
    backend = CodeExecutorBackend()
    worker_id = "code_test_worker"
    
    # 初始化
    session_data = await backend.initialize(worker_id, {"runtime": "python:3.10"})
    session_info = {"session_name": "code_test_session", "data": session_data}
    
    environment = session_data.get("environment")  # 后端返回 "environment" 而不是 "executor"
    
    # 测试各个工具方法（使用 MockExecutionEnvironment 的实际方法）
    tool_tests = [
        ("execute", lambda: environment.execute("x = 1 + 2\nprint(x)")),
        ("get_variable", lambda: environment.get_variable("x")),
        ("set_variable", lambda: environment.set_variable("y", 42)),
        ("reset", lambda: environment.reset()),
        ("install_package", lambda: environment.install_package("numpy")),
    ]
    
    for name, test_func in tool_tests:
        start = time.time()
        try:
            result = await test_func()
            duration = (time.time() - start) * 1000
            runner.add_result(TestResult(
                f"code:{name}",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"code:{name}",
                TestStatus.ERROR,
                str(e)
            ))
    
    # 清理
    await backend.cleanup(worker_id, session_info)


async def test_rag_tools(runner: TestRunner):
    """测试 RAG 后端工具"""
    print("\n📚 测试 RAG 工具...")
    
    import time
    
    from sandbox.server.backends.resources import RAGBackend
    
    backend = RAGBackend()
    
    # RAG 是共享后端，使用 warmup 而不是 initialize
    start = time.time()
    try:
        await backend.warmup()
        duration = (time.time() - start) * 1000
        runner.add_result(TestResult(
            "rag:warmup",
            TestStatus.PASSED,
            duration_ms=duration
        ))
    except Exception as e:
        runner.add_result(TestResult(
            "rag:warmup",
            TestStatus.ERROR,
            str(e)
        ))
        return
    
    # 测试各个工具方法（使用 backend 的实际方法）
    tool_tests = [
        ("search", lambda: backend.index.search([0.1] * 768, 5)),
        ("add_documents", lambda: backend.index.add([
            {"id": "doc1", "text": "Test document 1"},
            {"id": "doc2", "text": "Test document 2"}
        ], [[0.1] * 768, [0.2] * 768])),
        ("clear", lambda: backend.index.clear()),
    ]
    
    for name, test_func in tool_tests:
        start = time.time()
        try:
            result = await test_func()
            duration = (time.time() - start) * 1000
            runner.add_result(TestResult(
                f"rag:{name}",
                TestStatus.PASSED,
                duration_ms=duration
            ))
        except Exception as e:
            runner.add_result(TestResult(
                f"rag:{name}",
                TestStatus.ERROR,
                str(e)
            ))
    
    # 清理
    await backend.shutdown()


async def test_websearch_tools(runner: TestRunner):
    """测试 WebSearch API 工具"""
    print("\n🔍 测试 WebSearch 工具...")
    
    import time
    
    # 直接导入并测试工具函数
    from sandbox.server.backends.tools.websearch import (
        search,
        visit
    )
    
    # 测试 search
    start = time.time()
    try:
        result = await search(
            query="Python tutorial",
            max_results=5
        )
        duration = (time.time() - start) * 1000
        
        assert result.get("code") == 0, f"search 失败: {result.get('message')}"
        data = result.get("data", {})
        assert "result" in data, "search 结果缺少 data.result"
        
        runner.add_result(TestResult(
            "search",
            TestStatus.PASSED,
            duration_ms=duration
        ))
    except Exception as e:
        runner.add_result(TestResult(
            "search",
            TestStatus.ERROR,
            str(e)
        ))
    
    # 测试 visit
    start = time.time()
    try:
        result = await visit(url="https://example.com", goal="Extract main content")
        duration = (time.time() - start) * 1000
        
        assert result.get("code") == 0, f"visit 失败: {result.get('message')}"
        data = result.get("data", {})
        assert "result" in data, "visit 结果缺少 data.result"
        
        runner.add_result(TestResult(
            "visit",
            TestStatus.PASSED,
            duration_ms=duration
        ))
    except Exception as e:
        runner.add_result(TestResult(
            "visit",
            TestStatus.ERROR,
            str(e)
        ))
    
# ============================================================================
# 配置加载测试
# ============================================================================

async def test_config_loader(runner: TestRunner):
    """测试配置加载"""
    print("\n📋 测试配置加载...")
    
    import time
    from pathlib import Path
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    dev_config_path = project_root / "sandbox" / "configs" / "profiles" / "dev.json"
    
    if not dev_config_path.exists():
        runner.add_result(TestResult(
            "加载 dev.json",
            TestStatus.SKIPPED,
            f"配置文件不存在: {dev_config_path}"
        ))
        return
    
    start = time.time()
    try:
        from sandbox.server.config_loader import ConfigLoader
        
        loader = ConfigLoader()
        config = loader.load(str(dev_config_path))
        duration = (time.time() - start) * 1000
        
        assert config is not None, "配置加载结果为 None"
        
        runner.add_result(TestResult(
            "加载 dev.json",
            TestStatus.PASSED,
            duration_ms=duration
        ))
    except Exception as e:
        runner.add_result(TestResult(
            "加载 dev.json",
            TestStatus.ERROR,
            str(e)
        ))


# ============================================================================
# 主函数
# ============================================================================

async def run_all_tests(verbose: bool = False) -> bool:
    """运行所有测试"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Mock Backend 综合测试                               ║
╠══════════════════════════════════════════════════════════════╣
║  测试项目:                                                    ║
║    - 后端模块导入                                             ║
║    - 后端实例化                                               ║
║    - 服务器加载后端                                           ║
║    - 后端生命周期 (initialize/cleanup)                        ║
║    - VM/Browser/Bash/Code/RAG 工具                           ║
║    - WebSearch API 工具                                       ║
║    - 配置文件加载                                             ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    runner = TestRunner(verbose=verbose)
    
    # 后端加载测试
    await test_backend_imports(runner)
    await test_backend_instantiation(runner)
    await test_server_load_backends(runner)
    
    # 生命周期测试
    await test_backend_lifecycle(runner)
    
    # 工具功能测试
    await test_vm_tools(runner)
    await test_browser_tools(runner)
    await test_bash_tools(runner)
    await test_code_executor_tools(runner)
    await test_rag_tools(runner)
    await test_websearch_tools(runner)
    
    # 配置测试
    await test_config_loader(runner)
    
    # 打印摘要
    return runner.summary()


async def run_backend_tests(verbose: bool = False) -> bool:
    """只运行后端加载测试"""
    print("\n📦 后端加载测试...")
    
    runner = TestRunner(verbose=verbose)
    
    await test_backend_imports(runner)
    await test_backend_instantiation(runner)
    await test_server_load_backends(runner)
    await test_backend_lifecycle(runner)
    
    return runner.summary()


async def run_tool_tests(verbose: bool = False) -> bool:
    """只运行工具功能测试"""
    print("\n🛠️ 工具功能测试...")
    
    runner = TestRunner(verbose=verbose)
    
    await test_vm_tools(runner)
    await test_browser_tools(runner)
    await test_bash_tools(runner)
    await test_code_executor_tools(runner)
    await test_rag_tools(runner)
    await test_websearch_tools(runner)
    
    return runner.summary()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mock Backend 综合测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--test", choices=["all", "backend", "tools"], default="all",
                       help="运行指定测试类型")
    args = parser.parse_args()
    
    if args.test == "all":
        success = asyncio.run(run_all_tests(args.verbose))
    elif args.test == "backend":
        success = asyncio.run(run_backend_tests(args.verbose))
    elif args.test == "tools":
        success = asyncio.run(run_tool_tests(args.verbose))
    else:
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

