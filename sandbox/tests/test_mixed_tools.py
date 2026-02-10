#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合工具测试脚本

测试范围:
1. WebSearch 工具 (search)
2. WebVisit 工具 (visit)
3. RAG 检索工具 (rag:search)
4. 混合使用场景测试

运行方式:
    python -m sandbox.tests.test_mixed_tools

    # 指定配置文件
    python -m sandbox.tests.test_mixed_tools --config sandbox/configs/profiles/dev.json

    # 详细模式
    python -m sandbox.tests.test_mixed_tools --verbose
"""

import sys
import os
import asyncio
import logging
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sandbox import Sandbox, SandboxConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MixedToolsTest")


# ============================================================================
# 测试状态和结果
# ============================================================================

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
    duration_ms: float = 0.0
    details: Optional[Dict[str, Any]] = None


class TestRunner:
    """测试运行器"""

    def __init__(self, verbose: bool = False):
        self.results: List[TestResult] = []
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    def add_result(self, result: TestResult):
        self.results.append(result)
        icon = result.status.value
        name = result.name

        if result.status == TestStatus.PASSED:
            print(f"  {icon} {name} ({result.duration_ms:.1f}ms)")
            if self.verbose and result.details:
                print(f"      详情: {result.details}")
        elif result.status == TestStatus.SKIPPED:
            print(f"  {icon} {name}: {result.message}")
        else:
            print(f"  {icon} {name}: {result.message}")
            if result.details:
                print(f"      详情: {result.details}")

    def summary(self) -> bool:
        """打印测试摘要，返回是否全部通过"""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        total = len(self.results)

        print(f"\n{'='*70}")
        print(f"📊 测试结果摘要")
        print(f"{'='*70}")
        print(f"  ✅ 通过: {passed}/{total}")
        print(f"  ❌ 失败: {failed}/{total}")
        print(f"  💥 错误: {errors}/{total}")
        print(f"  ⏭️ 跳过: {skipped}/{total}")

        if failed > 0 or errors > 0:
            print(f"\n❌ 失败/错误的测试:")
            for r in self.results:
                if r.status in (TestStatus.FAILED, TestStatus.ERROR):
                    print(f"   - {r.name}: {r.message}")

        print(f"{'='*70}\n")

        return failed == 0 and errors == 0


# ============================================================================
# 结果记录（支持 verbose 附加原始响应）
# ============================================================================

def record_result(
    runner: TestRunner,
    result: TestResult,
    response: Optional[Any] = None,
    response_key: str = "raw_response"
):
    if runner.verbose and response is not None:
        details = result.details or {}
        if response_key not in details:
            details[response_key] = response
        result.details = details
    runner.add_result(result)


# ============================================================================
# 响应解析（兼容新格式）
# ============================================================================

def is_success(response: Any) -> bool:
    return isinstance(response, dict) and response.get("code") == 0


def get_data(response: Any) -> Dict[str, Any]:
    if not isinstance(response, dict):
        return {}
    data = response.get("data")
    return data if isinstance(data, dict) else {}


def get_error_message(response: Any) -> str:
    if not isinstance(response, dict):
        return "Unknown error"
    message = response.get("message")
    if message:
        return message
    data = response.get("data", {})
    if isinstance(data, dict) and data.get("details"):
        return str(data.get("details"))
    return "Unknown error"


# ============================================================================
# 测试用例
# ============================================================================

async def test_websearch_single_query(sandbox: Sandbox, runner: TestRunner):
    """测试 WebSearch - 单个查询"""
    print("\n🔍 测试 WebSearch 工具 - 单个查询...")

    start_time = time.time()
    try:
        result = await sandbox.execute("web:search", {
            "query": "Python asyncio tutorial"
        })
        duration = (time.time() - start_time) * 1000

        if is_success(result):
            data = get_data(result)
            result_text = data.get("result", "")
            record_result(runner, TestResult(
                "WebSearch - 单个查询",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"result_length": len(result_text), "query": "Python asyncio tutorial"}
            ), response=result)
        else:
            record_result(runner, TestResult(
                "WebSearch - 单个查询",
                TestStatus.FAILED,
                f"搜索失败: {get_error_message(result)}",
                duration_ms=duration
            ), response=result)
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "WebSearch - 单个查询",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_websearch_multiple_queries(sandbox: Sandbox, runner: TestRunner):
    """测试 WebSearch - 多个查询"""
    print("\n🔍 测试 WebSearch 工具 - 多个查询...")

    start_time = time.time()
    try:
        queries = [
            "机器学习基础",
            "深度学习框架",
            "自然语言处理"
        ]

        result = await sandbox.execute("web:search", {
            "query": queries
        })
        duration = (time.time() - start_time) * 1000

        if is_success(result):
            data = get_data(result)
            result_text = data.get("result", "")
            record_result(runner, TestResult(
                "WebSearch - 多个查询",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"result_length": len(result_text), "num_queries": len(queries)}
            ), response=result)
        else:
            record_result(runner, TestResult(
                "WebSearch - 多个查询",
                TestStatus.FAILED,
                f"搜索失败: {get_error_message(result)}",
                duration_ms=duration
            ), response=result)
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "WebSearch - 多个查询",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_webvisit_single_url(sandbox: Sandbox, runner: TestRunner):
    """测试 WebVisit - 单个 URL"""
    print("\n🌐 测试 WebVisit 工具 - 单个 URL...")

    start_time = time.time()
    try:
        result = await sandbox.execute("web:visit", {
            "urls": "https://www.python.org",
            "goal": "Extract main content about Python programming language"
        })
        duration = (time.time() - start_time) * 1000

        if is_success(result):
            data = get_data(result)
            result_text = data.get("result", "")
            record_result(runner, TestResult(
                "WebVisit - 单个 URL",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"result_length": len(result_text), "url": "https://www.python.org"}
            ), response=result)
        else:
            record_result(runner, TestResult(
                "WebVisit - 单个 URL",
                TestStatus.FAILED,
                f"访问失败: {get_error_message(result)}",
                duration_ms=duration
            ), response=result)
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "WebVisit - 单个 URL",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_webvisit_multiple_urls(sandbox: Sandbox, runner: TestRunner):
    """测试 WebVisit - 多个 URL"""
    print("\n🌐 测试 WebVisit 工具 - 多个 URL...")

    start_time = time.time()
    try:
        urls = [
            "https://docs.python.org/3/",
            "https://www.python.org/about/"
        ]

        result = await sandbox.execute("web:visit", {
            "urls": urls,
            "goal": "Summarize Python documentation and information"
        })
        duration = (time.time() - start_time) * 1000

        if is_success(result):
            data = get_data(result)
            result_text = data.get("result", "")
            record_result(runner, TestResult(
                "WebVisit - 多个 URL",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"result_length": len(result_text), "num_urls": len(urls)}
            ), response=result)
        else:
            record_result(runner, TestResult(
                "WebVisit - 多个 URL",
                TestStatus.FAILED,
                f"访问失败: {get_error_message(result)}",
                duration_ms=duration
            ), response=result)
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "WebVisit - 多个 URL",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_rag_search_single(sandbox: Sandbox, runner: TestRunner):
    """测试 RAG Search - 单个查询"""
    print("\n📚 测试 RAG Search 工具 - 单个查询...")

    start_time = time.time()
    try:
        result = await sandbox.execute("rag:search", {
            "query": "什么是机器学习？",
            "top_k": 5
        })
        duration = (time.time() - start_time) * 1000

        if is_success(result):
            data = get_data(result)
            context = data.get("context", "")
            record_result(runner, TestResult(
                "RAG Search - 单个查询",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"context_length": len(context), "query": "什么是机器学习？"}
            ), response=result)
        else:
            record_result(runner, TestResult(
                "RAG Search - 单个查询",
                TestStatus.FAILED,
                f"检索失败: {get_error_message(result)}",
                duration_ms=duration
            ), response=result)
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "RAG Search - 单个查询",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_rag_search_concurrent(sandbox: Sandbox, runner: TestRunner):
    """测试 RAG Search - 并发查询"""
    print("\n📚 测试 RAG Search 工具 - 并发查询...")

    start_time = time.time()
    try:
        queries = [
            "Python 异步编程",
            "深度学习框架",
            "自然语言处理",
            "分布式系统",
            "微服务架构"
        ]

        # 并发执行多个查询
        tasks = [
            sandbox.execute("rag:search", {"query": q, "top_k": 3})
            for q in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = (time.time() - start_time) * 1000

        # 检查结果
        success_count = sum(1 for r in results if is_success(r))

        if success_count == len(queries):
            record_result(
                runner,
                TestResult(
                "RAG Search - 并发查询",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"num_queries": len(queries), "success_count": success_count}
                ),
                response=results,
                response_key="raw_responses"
            )
        else:
            record_result(
                runner,
                TestResult(
                "RAG Search - 并发查询",
                TestStatus.FAILED,
                f"部分查询失败: {success_count}/{len(queries)} 成功",
                duration_ms=duration
                ),
                response=results,
                response_key="raw_responses"
            )
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "RAG Search - 并发查询",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_mixed_workflow(sandbox: Sandbox, runner: TestRunner):
    """测试混合工作流 - 组合使用所有工具"""
    print("\n🔄 测试混合工作流 - 组合使用所有工具...")

    start_time = time.time()
    try:
        # 步骤 1: 使用 WebSearch 搜索相关信息
        search_result = await sandbox.execute("web:search", {
            "query": "RAG retrieval augmented generation"
        })

        if not is_success(search_result):
            raise Exception(f"WebSearch 失败: {get_error_message(search_result)}")

        # 步骤 2: 使用 RAG Search 检索本地知识库
        rag_result = await sandbox.execute("rag:search", {
            "query": "RAG 检索增强生成技术",
            "top_k": 3
        })

        if not is_success(rag_result):
            raise Exception(f"RAG Search 失败: {get_error_message(rag_result)}")

        # 步骤 3: 使用 WebVisit 访问特定 URL（可选，如果有搜索结果）
        # 这里使用一个示例 URL
        visit_result = await sandbox.execute("web:visit", {
            "urls": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
            "goal": "Extract information about RAG technology"
        })

        duration = (time.time() - start_time) * 1000

        # 检查所有步骤是否成功
        all_success = (
            is_success(search_result) and
            is_success(rag_result) and
            is_success(visit_result)
        )

        if all_success:
            record_result(
                runner,
                TestResult(
                "混合工作流 - 组合使用",
                TestStatus.PASSED,
                duration_ms=duration,
                details={
                    "websearch_length": len(get_data(search_result).get("result", "")),
                    "rag_context_length": len(get_data(rag_result).get("context", "")),
                    "webvisit_length": len(get_data(visit_result).get("result", ""))
                }
                ),
                response={
                    "search": search_result,
                    "rag": rag_result,
                    "visit": visit_result
                },
                response_key="raw_responses"
            )
        else:
            record_result(
                runner,
                TestResult(
                "混合工作流 - 组合使用",
                TestStatus.FAILED,
                "部分工具执行失败",
                duration_ms=duration,
                details={
                    "websearch_success": is_success(search_result),
                    "rag_success": is_success(rag_result),
                    "webvisit_success": is_success(visit_result)
                }
                ),
                response={
                    "search": search_result,
                    "rag": rag_result,
                    "visit": visit_result
                },
                response_key="raw_responses"
            )
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "混合工作流 - 组合使用",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


async def test_parallel_mixed_tools(sandbox: Sandbox, runner: TestRunner):
    """测试并行混合工具调用"""
    print("\n⚡ 测试并行混合工具调用...")

    start_time = time.time()
    try:
        # 并行执行不同类型的工具
        tasks = [
            sandbox.execute("web:search", {"query": "Python programming"}),
            sandbox.execute("rag:search", {"query": "Python 编程基础", "top_k": 3}),
            sandbox.execute("web:visit", {
                "urls": "https://www.python.org",
                "goal": "Get Python overview"
            })
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = (time.time() - start_time) * 1000

        # 检查结果
        success_count = sum(1 for r in results if is_success(r))

        if success_count == len(tasks):
            record_result(
                runner,
                TestResult(
                "并行混合工具调用",
                TestStatus.PASSED,
                duration_ms=duration,
                details={"num_tools": len(tasks), "success_count": success_count}
                ),
                response=results,
                response_key="raw_responses"
            )
        else:
            record_result(
                runner,
                TestResult(
                "并行混合工具调用",
                TestStatus.FAILED,
                f"部分工具失败: {success_count}/{len(tasks)} 成功",
                duration_ms=duration
                ),
                response=results,
                response_key="raw_responses"
            )
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        record_result(runner, TestResult(
            "并行混合工具调用",
            TestStatus.ERROR,
            str(e),
            duration_ms=duration
        ))


# ============================================================================
# 主测试流程
# ============================================================================

async def run_all_tests(config_path: str, verbose: bool = False):
    """运行所有测试"""
    runner = TestRunner(verbose=verbose)

    print("="*70)
    print("🧪 混合工具测试套件")
    print("="*70)
    print(f"配置文件: {config_path}")
    print(f"详细模式: {verbose}")
    print("="*70)

    # 创建 Sandbox 实例
    sandbox = None
    try:
        print("\n🚀 启动 Sandbox...")
        sandbox = Sandbox(config=SandboxConfig(
            server_url="http://127.0.0.1:18890",
            auto_start_server=False,
            server_config_path=config_path,
            timeout=120,
            warmup_resources=["rag"]  # 预热 RAG Backend
        ))

        await sandbox.start()
        print("✅ Sandbox 启动成功")

        # 运行测试
        await test_websearch_single_query(sandbox, runner)
        await test_websearch_multiple_queries(sandbox, runner)
        await test_webvisit_single_url(sandbox, runner)
        await test_webvisit_multiple_urls(sandbox, runner)
        await test_rag_search_single(sandbox, runner)
        await test_rag_search_concurrent(sandbox, runner)
        await test_mixed_workflow(sandbox, runner)
        await test_parallel_mixed_tools(sandbox, runner)

    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        logger.exception("测试执行异常")
    finally:
        if sandbox:
            print("\n🔌 关闭 Sandbox...")
            await sandbox.close()
            print("✅ Sandbox 已关闭")

    # 打印摘要
    success = runner.summary()
    return 0 if success else 1


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="混合工具测试脚本")
    parser.add_argument(
        "--config",
        default="sandbox/configs/profiles/dev.json",
        help="配置文件路径 (默认: sandbox/configs/profiles/dev.json)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="启用详细输出"
    )

    args = parser.parse_args()

    # 检查配置文件是否存在
    config_path = Path(args.config)

    # 如果是相对路径，尝试从项目根目录解析
    if not config_path.is_absolute() and not config_path.exists():
        config_path = project_root / args.config

    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print(f"提示: 请确保配置文件路径正确，或使用绝对路径")
        return 1

    # 运行测试
    exit_code = asyncio.run(run_all_tests(str(config_path), args.verbose))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
