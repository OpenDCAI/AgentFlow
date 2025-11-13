#!/usr/bin/env python
"""
MMLongBench Benchmark 测试脚本

使用方法:
1. 首先转换数据: python load_mmlongbench.py --input your_data.json --output mmlongbench_demo.jsonl
2. 然后运行此脚本: python test_mmlongbench_benchmark.py
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark import create_benchmark


def test_benchmark_loading():
    """测试 benchmark 加载"""
    print("=" * 60)
    print("测试 1: Benchmark 加载")
    print("=" * 60)
    
    # 使用测试数据
    data_path = os.path.join(os.path.dirname(__file__), "test_mmlongbench_output.jsonl")
    
    if not os.path.exists(data_path):
        print(f"❌ 数据文件不存在: {data_path}")
        print("请先运行: python load_mmlongbench.py --input test_mmlongbench.json --output test_mmlongbench_output.jsonl")
        return None
    
    benchmark = create_benchmark(
        data_path=data_path,
        name="MMLongBench Test",
        description="MMLongBench 测试数据集"
    )
    
    print(f"✓ 成功加载 {len(benchmark.items)} 条数据")
    print(f"✓ Benchmark 名称: {benchmark.name}")
    
    # 显示第一条数据
    if benchmark.items:
        item = benchmark.items[0]
        print(f"\n第一条数据:")
        print(f"  ID: {item.id}")
        print(f"  问题: {item.question[:60]}...")
        print(f"  答案: {item.answer}")
        if item.metadata:
            print(f"  元数据字段: {list(item.metadata.keys())}")
            print(f"  文档类型: {item.metadata.get('doc_type')}")
            print(f"  答案格式: {item.metadata.get('answer_format')}")
    
    return benchmark


def test_evaluation(benchmark):
    """测试评估功能"""
    print("\n" + "=" * 60)
    print("测试 2: 评估功能")
    print("=" * 60)
    
    if not benchmark:
        print("❌ Benchmark 未加载，跳过评估测试")
        return
    
    # 创建一些预测（这里使用正确答案作为示例）
    predictions = {}
    for item in benchmark.items:
        predictions[item.id] = item.answer  # 使用正确答案，应该得到满分
    
    # 测试不同的评估指标
    metrics = ["exact_match", "f1_score", "similarity"]
    
    for metric in metrics:
        print(f"\n使用指标: {metric}")
        results = benchmark.evaluate(predictions, metric=metric)
        
        scores = [r.score for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        perfect_matches = sum(1 for s in scores if s == 1.0)
        
        print(f"  平均分数: {avg_score:.3f}")
        print(f"  完美匹配: {perfect_matches}/{len(results)}")
        
        # 显示每个结果的分数
        for result in results:
            status = "✓" if result.score == 1.0 else "✗"
            print(f"  {status} {result.item_id}: {result.score:.3f}")


def test_wrong_predictions(benchmark):
    """测试错误预测的评估"""
    print("\n" + "=" * 60)
    print("测试 3: 错误预测评估")
    print("=" * 60)
    
    if not benchmark:
        print("❌ Benchmark 未加载，跳过错误预测测试")
        return
    
    # 创建错误的预测
    wrong_predictions = {}
    for item in benchmark.items:
        # 故意给出错误答案
        wrong_predictions[item.id] = "错误的答案"
    
    # 使用 exact_match 评估
    results = benchmark.evaluate(wrong_predictions, metric="exact_match")
    
    scores = [r.score for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    print(f"错误预测的平均分数: {avg_score:.3f} (应该接近 0)")
    print(f"完美匹配: {sum(1 for s in scores if s == 1.0)}/{len(results)} (应该为 0)")


def test_summary(benchmark):
    """测试摘要功能"""
    print("\n" + "=" * 60)
    print("测试 4: 摘要功能")
    print("=" * 60)
    
    if not benchmark:
        print("❌ Benchmark 未加载，跳过摘要测试")
        return
    
    # 先进行一次评估
    predictions = {item.id: item.answer for item in benchmark.items}
    benchmark.evaluate(predictions, metric="exact_match")
    
    # 获取摘要
    summary = benchmark.get_summary()
    
    print("Benchmark 摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main():
    """主函数"""
    print("🚀 开始 MMLongBench Benchmark 测试\n")
    
    # 测试 1: 加载
    benchmark = test_benchmark_loading()
    
    # 测试 2: 评估
    test_evaluation(benchmark)
    
    # 测试 3: 错误预测
    test_wrong_predictions(benchmark)
    
    # 测试 4: 摘要
    test_summary(benchmark)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 转换你的 MMLongBench 数据:")
    print("   python load_mmlongbench.py --input your_data.json --output mmlongbench_demo.jsonl")
    print("\n2. 运行完整的 benchmark 测试:")
    print("   python ../run.py --mode doc --data mmlongbench_demo.jsonl \\")
    print("       --ocr-model-path /path/to/model --ocr-backend-type transformers")


if __name__ == "__main__":
    main()

