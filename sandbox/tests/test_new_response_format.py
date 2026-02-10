#!/usr/bin/env python3
"""
验证新响应格式的测试脚本

运行此脚本以验证工具是否正确返回新的 Code/Message/Data/Meta 格式
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径（避免直接运行时相对导入失败）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sandbox import Sandbox


async def test_new_format():
    """测试新格式工具"""
    print("=" * 80)
    print("测试新响应格式")
    print("=" * 80)

    async with Sandbox(server_url="http://127.0.0.1:18890") as sandbox:
        # 测试 search 工具
        print("\n1. 测试 search 工具")
        print("-" * 80)
        result = await sandbox.execute("web:search", {"query": "Python tutorial"})

        print(f"✓ 返回结果包含的键: {list(result.keys())}")

        # 验证新格式
        assert "code" in result, "❌ 缺少 'code' 字段"
        assert "message" in result, "❌ 缺少 'message' 字段"
        assert "data" in result, "❌ 缺少 'data' 字段"
        assert "meta" in result, "❌ 缺少 'meta' 字段"

        print(f"✓ code: {result['code']}")
        print(f"✓ message: {result['message']}")
        print(f"✓ data keys: {list(result['data'].keys())}")
        print(f"✓ meta keys: {list(result['meta'].keys())}")

        # 验证不应该有旧格式的 success 字段
        if "success" in result:
            print("⚠️  警告: 响应中仍然包含 'success' 字段（应该已被移除）")
        else:
            print("✓ 没有旧的 'success' 字段")

        # 验证 meta 字段内容
        assert result["meta"]["tool"] == "web:search", "❌ meta.tool 不正确"
        assert "execution_time_ms" in result["meta"], "❌ 缺少 execution_time_ms"
        assert "trace_id" in result["meta"], "❌ 缺少 trace_id"

        print("\n✅ search 工具测试通过！")

        # 测试 rag:search 工具
        print("\n2. 测试 rag:search 工具")
        print("-" * 80)

        # 先预热 RAG
        await sandbox.warmup(["rag"])

        result = await sandbox.execute("rag:search", {
            "query": "什么是机器学习？",
            "top_k": 3
        })

        print(f"✓ 返回结果包含的键: {list(result.keys())}")

        # 验证新格式
        assert "code" in result, "❌ 缺少 'code' 字段"
        assert "message" in result, "❌ 缺少 'message' 字段"
        assert "data" in result, "❌ 缺少 'data' 字段"
        assert "meta" in result, "❌ 缺少 'meta' 字段"

        print(f"✓ code: {result['code']}")
        print(f"✓ message: {result['message']}")
        print(f"✓ data keys: {list(result['data'].keys())}")
        print(f"✓ meta keys: {list(result['meta'].keys())}")

        # 验证不应该有旧格式的 success 字段
        if "success" in result:
            print("⚠️  警告: 响应中仍然包含 'success' 字段（应该已被移除）")
        else:
            print("✓ 没有旧的 'success' 字段")

        # 验证 meta 字段内容
        assert result["meta"]["tool"] == "rag:search", "❌ meta.tool 不正确"
        assert "execution_time_ms" in result["meta"], "❌ 缺少 execution_time_ms"
        assert "trace_id" in result["meta"], "❌ 缺少 trace_id"

        print("\n✅ rag:search 工具测试通过！")

        # 测试 visit 工具
        print("\n3. 测试 visit 工具")
        print("-" * 80)
        result = await sandbox.execute("web:visit", {
            "urls": "https://www.baidu.com",
            "goal": "获取首页标题"
        })

        print(f"✓ 返回结果包含的键: {list(result.keys())}")

        # 验证新格式
        assert "code" in result, "❌ 缺少 'code' 字段"
        assert "message" in result, "❌ 缺少 'message' 字段"
        assert "data" in result, "❌ 缺少 'data' 字段"
        assert "meta" in result, "❌ 缺少 'meta' 字段"

        print(f"✓ code: {result['code']}")
        print(f"✓ message: {result['message']}")
        print(f"✓ data keys: {list(result['data'].keys())}")
        print(f"✓ meta keys: {list(result['meta'].keys())}")

        # 验证不应该有旧格式的 success 字段
        if "success" in result:
            print("⚠️  警告: 响应中仍然包含 'success' 字段（应该已被移除）")
        else:
            print("✓ 没有旧的 'success' 字段")

        # 验证 meta 字段内容
        assert result["meta"]["tool"] == "web:visit", "❌ meta.tool 不正确"
        assert "execution_time_ms" in result["meta"], "❌ 缺少 execution_time_ms"
        assert "trace_id" in result["meta"], "❌ 缺少 trace_id"

        print("\n✅ visit 工具测试通过！")

    print("\n" + "=" * 80)
    print("🎉 所有测试通过！新响应格式工作正常！")
    print("=" * 80)


async def test_error_format():
    """测试错误响应格式"""
    print("\n" + "=" * 80)
    print("测试错误响应格式")
    print("=" * 80)

    async with Sandbox() as sandbox:
        # 测试无效查询（应该返回错误）
        print("\n测试错误响应")
        print("-" * 80)

        # 这里可以添加一些会触发错误的测试
        # 例如：无效的参数、API 错误等

        print("✓ 错误响应格式测试（待实现）")


def main():
    """主函数"""
    try:
        asyncio.run(test_new_format())
        # asyncio.run(test_error_format())
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
