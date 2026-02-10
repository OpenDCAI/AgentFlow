#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Synthesis - 多工具调用与结果格式化示例

演示如何在 rag_synthesis 模块中使用 sandbox 客户端进行多工具调用，
并使用 format_tool_result 将结果转化为合适的格式。

功能:
1. 使用 Sandbox 实例连接到 Sandbox 服务器
2. 调用多种工具 (WebSearch, WebVisit, RAG Search)
3. 使用 format_tool_result 格式化每个工具的返回结果
4. 打印每一步的原始输出和格式化后的输出，展示过滤效果

运行方式:
    python -m rag_synthesis.examples.multi_tool_demo
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入 Sandbox 客户端和结果格式化器
from sandbox.sandbox import Sandbox
from sandbox.sandbox.result_formatter import format_tool_result, ResultFormatter


# ============================================================================
# 工具调用与结果展示
# ============================================================================

def print_separator(title: str = "", char: str = "=", width: int = 80):
    """打印分隔线"""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(f"\n{char * width}")


def print_raw_response(response: Dict[str, Any], max_length: int = 500):
    """仅打印工具返回的 data 结构（截断显示）"""
    print("\n📦 原始数据结构 (data):")
    print("─" * 80)

    data = response.get("data", {})
    data_str = json.dumps(data, indent=2, ensure_ascii=False)

    if len(data_str) > max_length:
        print(f"{data_str[:max_length]}...")
        print(f"... (总长度: {len(data_str)} 字符)")
    else:
        print(data_str)


def print_formatted_result(formatted: str, max_length: int = 500):
    """打印格式化后的结构"""
    print("\n✨ 格式化结构 (formatted):")
    print("─" * 80)

    if len(formatted) > max_length:
        print(formatted[:max_length])
        print(f"... (总长度: {len(formatted)} 字符)")
    else:
        print(formatted)


# 不再输出对比信息，只展示结构
# ============================================================================
# 工具调用示例
# ============================================================================

async def demo_websearch(sandbox: Sandbox):
    """示例 1: WebSearch 工具"""
    print_separator("示例 1: WebSearch 工具", "=")

    print("\n🔍 调用 WebSearch 工具...")
    print("   查询: 'Python asyncio tutorial'")

    # 调用工具
    response = await sandbox.execute("search", {
        "query": "Python asyncio tutorial"
    })

    # 打印原始响应
    print_raw_response(response)

    # 格式化结果（简洁模式）
    formatted_simple = format_tool_result(response, verbose=False)
    print_formatted_result(formatted_simple)

    return response, formatted_simple


async def demo_webvisit(sandbox: Sandbox):
    """示例 2: WebVisit 工具"""
    print_separator("示例 2: WebVisit 工具", "=")

    print("\n🌐 调用 WebVisit 工具...")
    print("   URL: 'https://www.baidu.com'")
    print("   目标: '获取百度首页内容'")

    # 调用工具
    response = await sandbox.execute("visit", {
        "urls": "https://www.baidu.com",
        "goal": "获取百度首页内容"
    })

    # 打印原始响应
    print_raw_response(response)

    # 格式化结果
    formatted = format_tool_result(response, verbose=False)
    print_formatted_result(formatted)

    return response, formatted


async def demo_rag_search(sandbox: Sandbox):
    """示例 3: RAG Search 工具"""
    print_separator("示例 3: RAG Search 工具", "=")

    print("\n📚 调用 RAG Search 工具...")
    print("   查询: '什么是机器学习？'")
    print("   Top K: 5")

    # 调用工具
    response = await sandbox.execute("rag:search", {
        "query": "什么是机器学习？",
        "top_k": 5
    })

    # 打印原始响应
    print_raw_response(response)

    # 格式化结果（简洁模式）
    formatted_simple = format_tool_result(response, verbose=False)
    print_formatted_result(formatted_simple)

    return response, formatted_simple


async def demo_mixed_workflow(sandbox: Sandbox):
    """示例 4: 混合工作流 - 组合使用多个工具"""
    print_separator("示例 4: 混合工作流", "=")

    print("\n🔄 执行混合工作流...")
    print("   步骤 1: WebSearch 搜索 'RAG technology'")
    print("   步骤 2: RAG Search 检索本地知识库")
    print("   步骤 3: WebVisit 访问相关页面")

    results = []

    # 步骤 1: WebSearch
    print("\n" + "─" * 80)
    print("📍 步骤 1/3: WebSearch")
    print("─" * 80)

    search_response = await sandbox.execute("search", {
        "query": "RAG retrieval augmented generation"
    })

    search_formatted = format_tool_result(search_response, verbose=False)

    print("\n✅ WebSearch 完成")
    print_raw_response(search_response)
    print_formatted_result(search_formatted)

    results.append({
        "tool": "WebSearch",
        "response": search_response,
        "formatted": search_formatted
    })

    # 步骤 2: RAG Search
    print("\n" + "─" * 80)
    print("📍 步骤 2/3: RAG Search")
    print("─" * 80)

    rag_response = await sandbox.execute("rag:search", {
        "query": "RAG 检索增强生成技术",
        "top_k": 3
    })

    rag_formatted = format_tool_result(rag_response, verbose=False)

    print("\n✅ RAG Search 完成")
    print_raw_response(rag_response)
    print_formatted_result(rag_formatted)

    results.append({
        "tool": "RAG Search",
        "response": rag_response,
        "formatted": rag_formatted
    })

    # 步骤 3: WebVisit
    print("\n" + "─" * 80)
    print("📍 步骤 3/3: WebVisit")
    print("─" * 80)

    visit_response = await sandbox.execute("visit", {
        "urls": "https://www.baidu.com",
        "goal": "获取百度首页内容"
    })

    visit_formatted = format_tool_result(visit_response, verbose=False)

    print("\n✅ WebVisit 完成")
    print_raw_response(visit_response)
    print_formatted_result(visit_formatted)

    results.append({
        "tool": "WebVisit",
        "response": visit_response,
        "formatted": visit_formatted
    })

    # 打印工作流总结
    return results


async def demo_parallel_tools(sandbox: Sandbox):
    """示例 5: 并行调用多个工具"""
    print_separator("示例 5: 并行调用多个工具", "=")

    print("\n⚡ 并行执行多个工具...")
    print("   工具 1: WebSearch - 'Python programming'")
    print("   工具 2: RAG Search - 'Python 编程基础'")
    print("   工具 3: WebVisit - 'https://www.python.org'")

    # 并行执行
    tasks = [
        sandbox.execute("search", {"query": "Python programming"}),
        sandbox.execute("rag:search", {"query": "Python 编程基础", "top_k": 3}),
        sandbox.execute("visit", {
            "urls": "https://www.python.org",
            "goal": "Get Python overview"
        })
    ]

    print("\n⏳ 等待所有工具完成...")
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    print("\n" + "=" * 80)
    print("📊 并行执行结果")
    print("=" * 80)

    tool_names = ["WebSearch", "RAG Search", "WebVisit"]

    for i, (tool_name, response) in enumerate(zip(tool_names, responses), 1):
        print(f"\n{i}. {tool_name}:")

        if isinstance(response, Exception):
            print(f"   ❌ 错误: {response}")
            continue
        if not isinstance(response, dict):
            print(f"   ❌ 错误: 非预期响应类型 {type(response)}")
            continue

        # 格式化结果
        formatted = format_tool_result(response, verbose=False)

        print_raw_response(response)
        print_formatted_result(formatted)


async def demo_formatter_details(sandbox: Sandbox):
    """示例 6: 展示格式化器的详细功能"""
    print_separator("示例 6: 格式化器详细功能", "=")

    print("\n🔧 演示 ResultFormatter 的高级功能...")

    # 调用一个工具
    response = await sandbox.execute("rag:search", {
        "query": "深度学习",
        "top_k": 3
    })

    print("\n1️⃣ 使用工厂类获取格式化器实例:")
    print("─" * 80)

    formatter = ResultFormatter.format(response)

    print(f"   格式化器类型: {type(formatter).__name__}")
    print(f"   工具名称: {formatter.tool_name}")
    print(f"   执行时间: {formatter.execution_time:.2f}ms")
    print(f"   是否成功: {formatter.success}")

    print("\n2️⃣ 获取原始数据:")
    print("─" * 80)

    raw_data = formatter.raw_data
    print(f"   原始数据类型: {type(raw_data)}")
    if isinstance(raw_data, dict):
        print(f"   原始数据键: {list(raw_data.keys())}")

    print("\n3️⃣ 生成格式化结构:")
    print("─" * 80)

    simple = formatter.to_str(verbose=False)
    print(f"   {simple[:200]}...")


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "RAG Synthesis - 多工具调用与结果格式化示例" + " " * 16 + "║")
    print("╚" + "=" * 78 + "╝")

    print("\n📝 说明:")
    print("   本示例演示如何在 rag_synthesis 模块中:")
    print("   1. 使用 Sandbox 实例连接到 Sandbox 服务器")
    print("   2. 调用多种工具 (WebSearch, WebVisit, RAG Search)")
    print("   3. 使用 format_tool_result 格式化结果")
    print("   4. 展示原始输出和格式化后的输出对比")

    # 连接到 Sandbox 服务器
    print_separator("连接到 Sandbox 服务器", "=")

    print("\n🔌 连接到 Sandbox 服务器...")
    print("   URL: http://localhost:18890")

    try:
        async with Sandbox(server_url="http://localhost:18890") as sandbox:
            print("✅ 连接成功!")

            # 运行示例
            await demo_websearch(sandbox)
            await demo_webvisit(sandbox)
            await demo_rag_search(sandbox)
            await demo_mixed_workflow(sandbox)
            await demo_parallel_tools(sandbox)
            await demo_formatter_details(sandbox)

            print_separator("所有示例完成", "=")
            print("\n✅ 所有示例执行完成!")
            print("\n💡 关键要点:")
            print("   1. format_tool_result() 自动识别工具类型并应用对应格式化器")
            print("   2. 格式化后的结果过滤了冗余信息，只保留关键内容")
            print("   3. 支持简洁模式和详细模式，适应不同使用场景")
            print("   4. 可以直接用于 Agent 的 tool response")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 提示:")
        print("   1. 确保 Sandbox 服务器正在运行")
        print("   2. 检查服务器地址是否正确 (默认: http://localhost:18890)")
        print("   3. 确认服务器已加载相应的工具后端")

        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
