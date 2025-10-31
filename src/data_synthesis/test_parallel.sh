#!/bin/bash

# 并行处理功能测试脚本

echo "=========================================="
echo "测试并行数据合成功能"
echo "=========================================="
echo ""

# 创建测试seeds文件（只有2个seeds用于快速测试）
cat > test_seeds.json << 'EOF'
[
  "Apple Inc",
  "Tesla Inc"
]
EOF

echo "✓ 创建测试seeds文件: test_seeds.json (2个seeds)"
echo ""

# 测试1: 串行模式
echo "测试 1/2: 串行模式 (max_workers=1)"
echo "--------------------------------------"

cat > test_config_serial.json << 'EOF'
{
  "environment_mode": "web",
  "environment_kwargs": {
    "web_search_top_k": 2
  },
  "available_tools": ["web_search", "web_visit"],
  "sampling_tips": "简单探索，收集基础信息",
  "synthesis_tips": "生成简单的QA对",
  "seed_description": "公司名称",
  "model_name": "gpt-4.1-mini-2025-04-14",
  "max_depth": 3,
  "branching_factor": 2,
  "depth_threshold": 2,
  "max_trajectories": 2,
  "min_depth": 2,
  "max_selected_traj": 2,
  "max_retries": 3,
  "max_workers": 1
}
EOF

echo "开始串行测试..."
time python synthesis_pipeline_multi.py \
    --config test_config_serial.json \
    --seeds test_seeds.json \
    --output-dir test_results_serial

echo ""
echo "串行测试完成！"
echo ""

# 测试2: 并行模式
echo "测试 2/2: 并行模式 (max_workers=2)"
echo "--------------------------------------"

cat > test_config_parallel.json << 'EOF'
{
  "environment_mode": "web",
  "environment_kwargs": {
    "web_search_top_k": 2
  },
  "available_tools": ["web_search", "web_visit"],
  "sampling_tips": "简单探索，收集基础信息",
  "synthesis_tips": "生成简单的QA对",
  "seed_description": "公司名称",
  "model_name": "gpt-4.1-mini-2025-04-14",
  "max_depth": 3,
  "branching_factor": 2,
  "depth_threshold": 2,
  "max_trajectories": 2,
  "min_depth": 2,
  "max_selected_traj": 2,
  "max_retries": 3,
  "max_workers": 2
}
EOF

echo "开始并行测试..."
time python synthesis_pipeline_multi.py \
    --config test_config_parallel.json \
    --seeds test_seeds.json \
    --output-dir test_results_parallel

echo ""
echo "并行测试完成！"
echo ""

# 比较结果
echo "=========================================="
echo "测试结果对比"
echo "=========================================="
echo ""

echo "串行模式结果:"
echo "  QA文件: $(ls test_results_serial/synthesized_qa_*.jsonl 2>/dev/null | head -1)"
echo "  QA数量: $(wc -l test_results_serial/synthesized_qa_*.jsonl 2>/dev/null | awk '{print $1}')"
echo ""

echo "并行模式结果:"
echo "  QA文件: $(ls test_results_parallel/synthesized_qa_*.jsonl 2>/dev/null | head -1)"
echo "  QA数量: $(wc -l test_results_parallel/synthesized_qa_*.jsonl 2>/dev/null | awk '{print $1}')"
echo ""

# 清理测试文件
echo "清理测试文件..."
rm -f test_seeds.json test_config_serial.json test_config_parallel.json
# 保留结果目录供检查: test_results_serial/ test_results_parallel/

echo ""
echo "=========================================="
echo "✅ 测试完成！"
echo "=========================================="
echo ""
echo "测试结果已保存到:"
echo "  - test_results_serial/     (串行模式结果)"
echo "  - test_results_parallel/   (并行模式结果)"
echo ""
echo "你可以对比两个目录的输出文件，验证并行功能是否正常工作。"
echo ""

