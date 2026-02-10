#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG Backend 完整测试脚本

包含两个测试阶段：
- 阶段 1：直接测试 RAGBackend（单元测试）
- 阶段 2：启动 Server 进行端到端测试（集成测试）

运行方式:
    python -m sandbox.tests.test_rag_backend
    
    # 指定配置文件
    python -m sandbox.tests.test_rag_backend --config sandbox/configs/profiles/dev.json
    
    # 指定查询数量
    python -m sandbox.tests.test_rag_backend --num-queries 30
"""

import asyncio
import argparse
import json
import time
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from threading import Thread
from enum import Enum

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志（INFO 级别以便查看详细信息）
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger("RAGTest")


# ============================================================================
# 响应解析（兼容新格式）
# ============================================================================

def is_success(response: Optional[Dict[str, Any]]) -> bool:
    return isinstance(response, dict) and response.get("code") == 0


def get_data(response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(response, dict):
        return {}
    data = response.get("data")
    return data if isinstance(data, dict) else {}


def get_error_message(response: Optional[Dict[str, Any]]) -> str:
    if not isinstance(response, dict):
        return "未知错误"
    message = response.get("message")
    if message:
        return message
    data = response.get("data", {})
    if isinstance(data, dict) and data.get("details"):
        return str(data.get("details"))
    return "未知错误"


# ============================================================================
# 预设测试查询
# ============================================================================

TEST_QUERIES = [
    # 技术类查询
    "如何使用 Python 进行文件读写操作？",
    "什么是机器学习中的梯度下降算法？",
    "解释一下 Docker 容器和虚拟机的区别",
    "如何在 Linux 中查看系统资源使用情况？",
    "什么是 RESTful API 设计原则？",
    
    # 概念类查询
    "深度学习和机器学习有什么区别？",
    "什么是分布式系统中的 CAP 定理？",
    "解释一下数据库的 ACID 特性",
    "什么是微服务架构的优缺点？",
    "如何理解面向对象编程的封装、继承、多态？",
    
    # 实践类查询
    "如何优化 Python 代码的性能？",
    "常见的 SQL 注入攻击如何防范？",
    "如何设计一个高可用的系统架构？",
    "Git 分支管理的最佳实践是什么？",
    "如何进行代码审查？",
    
    # 问题排查类查询
    "Python 内存泄漏如何排查？",
    "服务器 CPU 使用率过高怎么处理？",
    "数据库查询慢如何优化？",
    "网络延迟高的常见原因有哪些？",
    "如何调试分布式系统中的问题？",
    
    # 更多查询（用于并发测试）
    "什么是缓存穿透和缓存雪崩？",
    "如何实现分布式锁？",
    "消息队列的使用场景有哪些？",
    "什么是服务熔断和降级？",
    "如何保证分布式事务的一致性？",
    "什么是蓝绿部署和金丝雀发布？",
    "如何设计一个秒杀系统？",
    "什么是服务网格（Service Mesh）？",
    "如何实现全链路追踪？",
    "什么是云原生架构？",
]


# ============================================================================
# 数据结构
# ============================================================================

class TestStatus(Enum):
    PASSED = "✅"
    FAILED = "❌"
    SKIPPED = "⏭️"
    ERROR = "💥"


@dataclass
class TestResult:
    """单个测试结果"""
    name: str
    status: TestStatus
    message: str = ""
    duration_ms: float = 0.0


@dataclass
class QueryResult:
    """单条查询结果"""
    query: str
    result: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class PhaseReport:
    """阶段测试报告"""
    phase_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    total_time_ms: float
    results: List[TestResult] = field(default_factory=list)


# ============================================================================
# 测试运行器
# ============================================================================

class TestRunner:
    """测试运行器"""
    
    def __init__(self, config_path: str, num_queries: int = 10, top_k: Optional[int] = None):
        self.config_path = config_path
        self.num_queries = num_queries
        self.top_k = top_k
        self.config: Dict[str, Any] = {}
        self.rag_config: Dict[str, Any] = {}
        self.phases: List[PhaseReport] = []
        
    def load_config(self) -> bool:
        """加载配置文件"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            print(f"❌ 配置文件不存在: {self.config_path}")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.rag_config = self.config.get("resources", {}).get("rag", {}).get("config", {})
        if not self.rag_config:
            print("❌ 配置文件中未找到 rag 配置")
            return False
        
        return True
    
    def print_config_info(self):
        """打印配置信息"""
        from sandbox.server.backends.resources.rag import parse_device_config
        
        device_config = self.rag_config.get('device', 'cuda:0')
        encoder_device, index_device = parse_device_config(device_config)
        
        actual_top_k = self.top_k or self.rag_config.get('default_top_k', 5)
        
        print("=" * 70)
        print("📋 RAG Backend 完整测试")
        print("=" * 70)
        print(f"📄 配置文件: {self.config_path}")
        print(f"📦 模型: {self.rag_config.get('model_name')}")
        print(f"📂 索引: {self.rag_config.get('index_path')}")
        print(f"📂 语料: {self.rag_config.get('corpus_path')}")
        print(f"🖥️  设备配置: {device_config}")
        print(f"   → Encoder: {encoder_device}")
        print(f"   → Index: {index_device}")
        print(f"🔢 top_k: {actual_top_k}")
        print(f"📊 测试查询数: {self.num_queries}")
        print("=" * 70)
        print()
    
    def print_phase_report(self, report: PhaseReport):
        """打印阶段报告"""
        print()
        print(f"{'='*70}")
        print(f"📊 {report.phase_name} 报告")
        print(f"{'='*70}")
        print(f"  总测试数: {report.total_tests}")
        print(f"  通过: {report.passed} {TestStatus.PASSED.value}")
        print(f"  失败: {report.failed} {TestStatus.FAILED.value}")
        print(f"  跳过: {report.skipped} {TestStatus.SKIPPED.value}")
        print(f"  总耗时: {report.total_time_ms:.1f}ms")
        print()
    
    def print_final_summary(self):
        """打印最终汇总"""
        total_tests = sum(p.total_tests for p in self.phases)
        total_passed = sum(p.passed for p in self.phases)
        total_failed = sum(p.failed for p in self.phases)
        total_time = sum(p.total_time_ms for p in self.phases)
        
        print()
        print("=" * 70)
        print("🏁 最终测试汇总")
        print("=" * 70)
        
        for phase in self.phases:
            status = TestStatus.PASSED.value if phase.failed == 0 else TestStatus.FAILED.value
            print(f"  {status} {phase.phase_name}: {phase.passed}/{phase.total_tests} 通过")
        
        print("-" * 70)
        print(f"  总计: {total_passed}/{total_tests} 通过")
        print(f"  总耗时: {total_time/1000:.2f}s")
        
        if total_failed == 0:
            print()
            print("  🎉 所有测试通过！")
        else:
            print()
            print(f"  ⚠️  {total_failed} 个测试失败")
        
        print("=" * 70)

    # ========================================================================
    # 阶段 1：直接测试 RAGBackend
    # ========================================================================
    
    async def run_phase1_direct_test(self) -> PhaseReport:
        """阶段 1：直接测试 RAGBackend"""
        print()
        print("=" * 70)
        print("🔬 阶段 1：直接测试 RAGBackend")
        print("=" * 70)
        
        # 先清理可能残留的 GPU 显存
        print("\n🧹 清理可能残留的 GPU 显存...")
        self._cleanup_gpu_memory()
        
        results: List[TestResult] = []
        phase_start = time.time()
        
        # 1.1 创建并预热 Backend
        result = await self._test_backend_warmup()
        results.append(result)
        
        if result.status != TestStatus.PASSED:
            return self._create_phase_report("阶段 1: 直接测试", results, phase_start)
        
        # 1.2 单条查询测试
        result = await self._test_single_queries()
        results.append(result)
        
        # 1.3 批量顺序查询测试
        result = await self._test_batch_queries()
        results.append(result)
        
        # 1.4 并发查询测试
        result = await self._test_concurrent_queries()
        results.append(result)
        
        # 1.5 Batcher 统计
        result = await self._test_batcher_stats()
        results.append(result)
        
        # 1.6 关闭 Backend
        result = await self._test_backend_shutdown()
        results.append(result)
        
        return self._create_phase_report("阶段 1: 直接测试", results, phase_start)
    
    async def _test_backend_warmup(self) -> TestResult:
        """测试 Backend 预热"""
        print("\n📦 1.1 创建并预热 RAGBackend...")
        
        try:
            from sandbox.server.backends.resources.rag import RAGBackend
            from sandbox.server.backends.base import BackendConfig
            
            backend_config = BackendConfig(
                enabled=True,
                default_config=self.rag_config
            )
            
            self._backend = RAGBackend(backend_config)
            
            start = time.time()
            await self._backend.warmup()
            duration = (time.time() - start) * 1000
            
            assert self._backend._rag_index is not None
            index_size = self._backend._rag_index.index.ntotal
            corpus_size = len(self._backend._rag_index.corpus)
            
            return TestResult(
                "Backend 预热",
                TestStatus.PASSED,
                f"索引: {index_size:,} 向量, 语料: {corpus_size:,} 文档",
                duration
            )
        except Exception as e:
            return TestResult("Backend 预热", TestStatus.FAILED, str(e))
    
    async def _test_single_queries(self) -> TestResult:
        """测试单条查询"""
        print("\n🔍 1.2 单条查询测试 (5 条)...")
        
        try:
            queries = TEST_QUERIES[:5]
            actual_top_k = self.top_k or self.rag_config.get('default_top_k', 5)
            
            latencies = []
            start = time.time()
            
            assert self._backend._batcher is not None
            for i, query in enumerate(queries):
                q_start = time.time()
                result = await self._backend._batcher.submit(query, actual_top_k)
                latency = (time.time() - q_start) * 1000
                latencies.append(latency)
                print(f"    [{i+1}/5] {latency:.1f}ms - {query[:30]}...")
            
            total_duration = (time.time() - start) * 1000
            avg_latency = sum(latencies) / len(latencies)
            
            return TestResult(
                "单条查询测试",
                TestStatus.PASSED,
                f"平均延迟: {avg_latency:.1f}ms",
                total_duration
            )
        except Exception as e:
            return TestResult("单条查询测试", TestStatus.FAILED, str(e))
    
    async def _test_batch_queries(self) -> TestResult:
        """测试批量顺序查询"""
        print(f"\n📋 1.3 批量顺序查询测试 ({self.num_queries} 条)...")
        
        try:
            queries = TEST_QUERIES[:self.num_queries]
            actual_top_k = self.top_k or self.rag_config.get('default_top_k', 5)
            
            assert self._backend._batcher is not None
            latencies = []
            start = time.time()
            
            for query in queries:
                q_start = time.time()
                await self._backend._batcher.submit(query, actual_top_k)
                latencies.append((time.time() - q_start) * 1000)
            
            total_duration = (time.time() - start) * 1000
            avg_latency = sum(latencies) / len(latencies)
            qps = len(queries) / (total_duration / 1000)
            
            return TestResult(
                "批量顺序查询",
                TestStatus.PASSED,
                f"QPS: {qps:.1f}, 平均延迟: {avg_latency:.1f}ms",
                total_duration
            )
        except Exception as e:
            return TestResult("批量顺序查询", TestStatus.FAILED, str(e))
    
    async def _test_concurrent_queries(self) -> TestResult:
        """测试并发查询"""
        print(f"\n🚀 1.4 并发查询测试 ({self.num_queries} 条同时提交)...")
        
        try:
            queries = TEST_QUERIES[:self.num_queries]
            actual_top_k = self.top_k or self.rag_config.get('default_top_k', 5)
            
            assert self._backend._batcher is not None
            start = time.time()
            
            # 创建所有查询任务
            tasks = [
                self._backend._batcher.submit(q, actual_top_k)
                for q in queries
            ]
            
            # 并发执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_duration = (time.time() - start) * 1000
            
            # 统计成功/失败
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            fail_count = len(results) - success_count
            
            qps = len(queries) / (total_duration / 1000)
            
            if fail_count > 0:
                return TestResult(
                    "并发查询测试",
                    TestStatus.FAILED,
                    f"{fail_count}/{len(queries)} 失败",
                    total_duration
                )
            
            return TestResult(
                "并发查询测试",
                TestStatus.PASSED,
                f"QPS: {qps:.1f}, 全部 {success_count} 条成功",
                total_duration
            )
        except Exception as e:
            return TestResult("并发查询测试", TestStatus.FAILED, str(e))
    
    async def _test_batcher_stats(self) -> TestResult:
        """测试 Batcher 统计"""
        print("\n📈 1.5 Batcher 统计信息...")
        
        try:
            assert self._backend._batcher is not None
            stats = self._backend._batcher.get_stats()
            
            print(f"    总查询数: {stats.get('total_queries', 0)}")
            print(f"    总批次数: {stats.get('total_batches', 0)}")
            print(f"    平均批大小: {stats.get('avg_batch_size', 0):.2f}")
            
            return TestResult(
                "Batcher 统计",
                TestStatus.PASSED,
                f"批次: {stats.get('total_batches', 0)}, 平均批大小: {stats.get('avg_batch_size', 0):.2f}"
            )
        except Exception as e:
            return TestResult("Batcher 统计", TestStatus.FAILED, str(e))
    
    async def _test_backend_shutdown(self) -> TestResult:
        """测试 Backend 关闭"""
        print("\n🔌 1.6 关闭 Backend 并清理 GPU 显存...")
        
        try:
            start = time.time()
            await self._backend.shutdown()
            
            # 清除引用
            self._backend = None
            
            # 清理 GPU 显存
            self._cleanup_gpu_memory()
            
            duration = (time.time() - start) * 1000
            
            return TestResult("Backend 关闭", TestStatus.PASSED, "GPU 显存已清理", duration)
        except Exception as e:
            return TestResult("Backend 关闭", TestStatus.FAILED, str(e))

    # ========================================================================
    # 阶段 2：使用 Sandbox 类进行端到端测试（用户视角）
    # ========================================================================
    
    def _cleanup_gpu_memory(self):
        """清理 GPU 显存"""
        import gc
        
        # 强制垃圾回收
        gc.collect()
        
        try:
            import torch
            if torch.cuda.is_available():
                # 清空 CUDA 缓存
                torch.cuda.empty_cache()
                
                # 同步所有 GPU 设备
                for i in range(torch.cuda.device_count()):
                    try:
                        with torch.cuda.device(i):
                            torch.cuda.synchronize()
                    except Exception:
                        pass
                
                print("    ✅ GPU 显存已清理")
        except ImportError:
            pass
    
    async def _cleanup_existing_server(self, server_url: str) -> bool:
        """
        清理已有的服务器进程
        
        通过 HTTP API 关闭服务器，确保使用最新代码启动新服务器
        
        Args:
            server_url: 服务器地址
            
        Returns:
            是否成功关闭（或服务器不存在）
        """
        import httpx
        from sandbox.protocol import HTTPEndpoints
        
        print("\n🧹 2.0 检查并清理残留资源...")
        
        # 先清理可能残留的 GPU 显存（阶段 1 可能残留）
        print("    🔄 清理残留 GPU 显存...")
        self._cleanup_gpu_memory()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # 检查服务器是否在线
                try:
                    resp = await client.get(f"{server_url}/health")
                    if resp.status_code != 200:
                        print("    ✅ 服务器未运行，无需清理")
                        return True
                except httpx.ConnectError:
                    print("    ✅ 服务器未运行，无需清理")
                    return True
                
                # 服务器在线，尝试关闭
                print("    ⚠️ 检测到残留服务器，正在关闭...")
                try:
                    resp = await client.post(
                        f"{server_url}{HTTPEndpoints.SHUTDOWN}",
                        json={"force": True, "cleanup_sessions": True}
                    )
                    if resp.status_code == 200:
                        print("    ✅ 残留服务器已关闭")
                        # 等待服务器完全关闭
                        await asyncio.sleep(1.0)
                        return True
                    else:
                        print(f"    ❌ 关闭失败: HTTP {resp.status_code}")
                        return False
                except Exception as e:
                    print(f"    ⚠️ 关闭请求异常: {e}")
                    # 可能服务器已经关闭
                    await asyncio.sleep(0.5)
                    return True
                    
        except Exception as e:
            print(f"    ⚠️ 清理检查异常: {e}")
            return True  # 继续执行测试
    
    async def run_phase2_server_test(self) -> PhaseReport:
        """阶段 2：使用 Sandbox 类进行端到端测试"""
        print()
        print("=" * 70)
        print("🌐 阶段 2：Sandbox 端到端测试（用户视角）")
        print("=" * 70)
        
        results: List[TestResult] = []
        phase_start = time.time()
        
        sandbox = None
        server_url = "http://127.0.0.1:18890"
        
        try:
            # 2.0 清理残留服务器（确保使用最新代码）
            await self._cleanup_existing_server(server_url)
            
            # 2.1 创建 Sandbox 并启动
            result, sandbox = await self._test_sandbox_start()
            results.append(result)
            
            if result.status != TestStatus.PASSED or sandbox is None:
                return self._create_phase_report("阶段 2: Sandbox 测试", results, phase_start)
            
            # 2.2 预热 RAG Backend（使用 sandbox.warmup）
            result = await self._test_sandbox_warmup(sandbox)
            results.append(result)
            
            if result.status != TestStatus.PASSED:
                return self._create_phase_report("阶段 2: Sandbox 测试", results, phase_start)
            
            # 2.3 工具列表检查
            result = await self._test_sandbox_list_tools(sandbox)
            results.append(result)
            
            # 2.4 RAG 搜索测试
            result = await self._test_sandbox_rag_search(sandbox)
            results.append(result)
            
            # 2.5 RAG 批量搜索测试
            result = await self._test_sandbox_rag_batch_search(sandbox)
            results.append(result)
            
            # 2.6 RAG 统计测试
            result = await self._test_sandbox_rag_stats(sandbox)
            results.append(result)
            
            # 2.7 获取预热状态
            result = await self._test_sandbox_warmup_status(sandbox)
            results.append(result)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            results.append(TestResult("Sandbox 测试异常", TestStatus.ERROR, str(e)))
        finally:
            # 关闭 Sandbox 并停止服务器以释放 GPU 显存
            if sandbox:
                try:
                    # 先关闭服务器，这会触发 RAGBackend.shutdown() 释放 GPU 资源
                    print("\n🔌 2.8 关闭服务器并释放 GPU 显存...")
                    await sandbox.shutdown_server(cleanup_sessions=True)
                    await sandbox.close()
                    
                    # 额外的 GPU 显存清理
                    self._cleanup_gpu_memory()
                    
                    results.append(TestResult("Sandbox 关闭", TestStatus.PASSED, "服务器已停止，GPU 显存已释放"))
                except Exception as e:
                    results.append(TestResult("Sandbox 关闭", TestStatus.FAILED, str(e)))
                    # 即使关闭失败，也尝试清理 GPU 显存
                    self._cleanup_gpu_memory()
        
        return self._create_phase_report("阶段 2: Sandbox 测试", results, phase_start)
    
    async def _test_sandbox_start(self):
        """测试 Sandbox 启动"""
        print("\n🚀 2.1 启动 Sandbox...")
        
        try:
            from sandbox import Sandbox, SandboxConfig
            
            # 创建 Sandbox 配置，使用配置文件路径
            config = SandboxConfig(
                server_url="http://127.0.0.1:18890",
                auto_start_server=True,
                server_config_path=self.config_path,  # 使用配置文件路径
                server_startup_timeout=60.0,  # RAG 预热需要更长时间
                timeout=120.0
            )
            
            start = time.time()
            sandbox = Sandbox(config=config)
            await sandbox.start()
            duration = (time.time() - start) * 1000
            
            print(f"    ✅ Sandbox 启动成功，耗时: {duration:.1f}ms")
            
            return TestResult(
                "Sandbox 启动",
                TestStatus.PASSED,
                f"端口 18890",
                duration
            ), sandbox
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return TestResult("Sandbox 启动", TestStatus.FAILED, str(e)), None
    
    async def _test_sandbox_warmup(self, sandbox) -> TestResult:
        """测试 Sandbox 预热（用户 API）"""
        print("\n🔥 2.2 预热 RAG Backend (sandbox.warmup)...")
        
        try:
            start = time.time()
            result = await sandbox.warmup(["rag"])
            duration = (time.time() - start) * 1000
            
            warmup_results = result.get("results", {})
            warmup_errors = result.get("errors", {})
            rag_success = warmup_results.get("rag", False)
            
            print(f"    预热结果: {warmup_results}")
            print(f"    耗时: {duration:.1f}ms")
            
            # 如果有错误信息，打印详细错误
            if warmup_errors:
                print(f"    ⚠️ 错误详情:")
                for backend_name, error_msg in warmup_errors.items():
                    print(f"       [{backend_name}]: {error_msg}")
            
            if rag_success:
                return TestResult(
                    "RAG 预热",
                    TestStatus.PASSED,
                    f"预热成功",
                    duration
                )
            else:
                error_detail = warmup_errors.get("rag", "未知错误")
                # 截取错误信息的第一行
                first_line = error_detail.split('\n')[0] if error_detail else "预热失败"
                
                # 如果后端加载失败，尝试显示服务器日志
                if "Backend not found" in str(error_detail):
                    print("\n    📋 服务器启动日志:")
                    server_log = sandbox.get_server_log(tail_lines=50)
                    if server_log:
                        for line in server_log.strip().split('\n'):
                            print(f"       {line}")
                    else:
                        print("       (无法获取服务器日志)")
                
                return TestResult(
                    "RAG 预热",
                    TestStatus.FAILED,
                    first_line[:80],
                    duration
                )
        except Exception as e:
            return TestResult("RAG 预热", TestStatus.FAILED, str(e))
    
    async def _test_sandbox_list_tools(self, sandbox) -> TestResult:
        """测试工具列表"""
        print("\n📋 2.3 工具列表检查...")
        
        try:
            start = time.time()
            tools = await sandbox.get_tools()
            duration = (time.time() - start) * 1000
            
            # 调试输出所有工具（使用 full_name）
            all_tool_names = [t.get('full_name', t.get('name', 'unknown')) for t in tools]
            print(f"    所有工具 ({len(tools)}): {all_tool_names}")
            
            # 检查 RAG 工具（使用 full_name 来匹配）
            rag_tools = [t for t in tools if t.get('full_name', '').startswith('rag:')]
            tool_names = [t.get('full_name') for t in rag_tools]
            
            print(f"    RAG 工具: {tool_names}")
            
            expected = ['rag:search', 'rag:batch_search', 'rag:stats']
            missing = [t for t in expected if t not in tool_names]
            
            if missing:
                return TestResult(
                    "工具列表检查",
                    TestStatus.FAILED,
                    f"缺少工具: {missing}",
                    duration
                )
            
            return TestResult(
                "工具列表检查",
                TestStatus.PASSED,
                f"找到 {len(rag_tools)} 个 RAG 工具",
                duration
            )
        except Exception as e:
            return TestResult("工具列表检查", TestStatus.FAILED, str(e))
    
    async def _test_sandbox_rag_search(self, sandbox) -> TestResult:
        """测试 RAG 搜索"""
        print("\n🔍 2.4 RAG 搜索测试 (sandbox.execute)...")
        
        try:
            query = TEST_QUERIES[0]
            actual_top_k = self.top_k or self.rag_config.get('default_top_k', 5)
            
            start = time.time()
            result = await sandbox.execute("rag:search", {
                "query": query,
                "top_k": actual_top_k
            })
            duration = (time.time() - start) * 1000
            
            print(f"    查询: {query[:40]}...")
            print(f"    延迟: {duration:.1f}ms")
            
            if is_success(result):
                data = get_data(result)
                context = data.get("context", "")
                doc_count = context.count("---") + 1 if "---" in context else (1 if context else 0)
                print(f"    返回文档数: {doc_count}")
                
                return TestResult(
                    "RAG 搜索",
                    TestStatus.PASSED,
                    f"返回 {doc_count} 个文档",
                    duration
                )
            else:
                return TestResult(
                    "RAG 搜索",
                    TestStatus.FAILED,
                    get_error_message(result),
                    duration
                )
        except Exception as e:
            return TestResult("RAG 搜索", TestStatus.FAILED, str(e))
    
    async def _test_sandbox_rag_batch_search(self, sandbox) -> TestResult:
        """测试 RAG 批量搜索"""
        print("\n📋 2.5 RAG 批量搜索测试...")
        
        try:
            queries = TEST_QUERIES[:5]
            actual_top_k = self.top_k or self.rag_config.get('default_top_k', 5)
            
            start = time.time()
            result = await sandbox.execute("rag:batch_search", {
                "queries": queries,
                "top_k": actual_top_k
            })
            duration = (time.time() - start) * 1000
            
            if is_success(result):
                data = get_data(result)
                results_list = data.get("results", [])
                print(f"    批量查询: {len(queries)} 条")
                print(f"    返回结果: {len(results_list)} 条")
                print(f"    延迟: {duration:.1f}ms")
                
                return TestResult(
                    "RAG 批量搜索",
                    TestStatus.PASSED,
                    f"{len(results_list)} 条结果",
                    duration
                )
            else:
                return TestResult(
                    "RAG 批量搜索",
                    TestStatus.FAILED,
                    get_error_message(result),
                    duration
                )
        except Exception as e:
            return TestResult("RAG 批量搜索", TestStatus.FAILED, str(e))
    
    async def _test_sandbox_rag_stats(self, sandbox) -> TestResult:
        """测试 RAG 统计"""
        print("\n📈 2.6 RAG 统计测试...")
        
        try:
            start = time.time()
            result = await sandbox.execute("rag:stats", {})
            duration = (time.time() - start) * 1000
            
            if is_success(result):
                data = get_data(result)
                stats = data.get("stats", {})
                index_stats = stats.get("index", {})
                batcher_stats = stats.get("batcher", {})
                
                print(f"    索引向量数: {index_stats.get('index_size', 'N/A')}")
                print(f"    语料库大小: {index_stats.get('corpus_size', 'N/A')}")
                print(f"    Batcher 批次数: {batcher_stats.get('total_batches', 'N/A')}")
                
                return TestResult(
                    "RAG 统计",
                    TestStatus.PASSED,
                    f"索引: {index_stats.get('index_size', 0):,} 向量",
                    duration
                )
            else:
                return TestResult(
                    "RAG 统计",
                    TestStatus.FAILED,
                    get_error_message(result),
                    duration
                )
        except Exception as e:
            return TestResult("RAG 统计", TestStatus.FAILED, str(e))
    
    async def _test_sandbox_warmup_status(self, sandbox) -> TestResult:
        """测试预热状态查询"""
        print("\n📊 2.7 预热状态查询...")
        
        try:
            start = time.time()
            status = await sandbox.get_warmup_status()
            duration = (time.time() - start) * 1000
            
            summary = status.get("summary", {})
            print(f"    总后端数: {summary.get('total', 0)}")
            print(f"    已预热: {summary.get('warmed_up', 0)}")
            
            return TestResult(
                "预热状态查询",
                TestStatus.PASSED,
                f"已预热: {summary.get('warmed_up', 0)}/{summary.get('total', 0)}",
                duration
            )
        except Exception as e:
            return TestResult("预热状态查询", TestStatus.FAILED, str(e))

    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def _create_phase_report(self, phase_name: str, results: List[TestResult], start_time: float) -> PhaseReport:
        """创建阶段报告"""
        total_time = (time.time() - start_time) * 1000
        
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        
        report = PhaseReport(
            phase_name=phase_name,
            total_tests=len(results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            total_time_ms=total_time,
            results=results
        )
        
        # 打印每个测试结果
        print()
        for result in results:
            print(f"    {result.status.value} {result.name}: {result.message} ({result.duration_ms:.1f}ms)")
        
        self.phases.append(report)
        return report


# ============================================================================
# 主函数
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="RAG Backend 完整测试脚本")
    parser.add_argument(
        "--config",
        default="sandbox/configs/profiles/dev.json",
        help="配置文件路径 (默认: sandbox/configs/profiles/dev.json)"
    )
    parser.add_argument(
        "--num-queries",
        type=int,
        default=10,
        help="测试查询数量 (默认: 10)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="返回结果数 (不指定则使用配置文件中的 default_top_k)"
    )
    parser.add_argument(
        "--skip-server",
        action="store_true",
        help="跳过 Server 端到端测试"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(args.config, args.num_queries, args.top_k)
    
    try:
        # 加载配置
        if not runner.load_config():
            return
        
        # 检查文件是否存在
        index_path = Path(runner.rag_config.get('index_path', ''))
        corpus_path = Path(runner.rag_config.get('corpus_path', ''))
        
        if not index_path.exists():
            print(f"❌ 索引文件不存在: {index_path}")
            return
        
        if not corpus_path.exists():
            print(f"❌ 语料库文件不存在: {corpus_path}")
            return
        
        # 打印配置信息
        runner.print_config_info()
        
        # 阶段 1：直接测试
        report1 = await runner.run_phase1_direct_test()
        runner.print_phase_report(report1)
        
        # 阶段 2：Server 测试
        if not args.skip_server:
            report2 = await runner.run_phase2_server_test()
            runner.print_phase_report(report2)
        else:
            print("\n⏭️  跳过阶段 2: Server 测试 (--skip-server)")
        
        # 最终汇总
        runner.print_final_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 最终的 GPU 显存清理，确保任何情况下都能释放
        print("\n🧹 执行最终 GPU 显存清理...")
        _final_gpu_cleanup()


def _final_gpu_cleanup():
    """最终的 GPU 显存清理"""
    import gc
    gc.collect()
    
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            # 同步所有 GPU 设备
            for i in range(torch.cuda.device_count()):
                try:
                    with torch.cuda.device(i):
                        torch.cuda.synchronize()
                except Exception:
                    pass
            print("    ✅ 最终 GPU 显存清理完成")
    except ImportError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
