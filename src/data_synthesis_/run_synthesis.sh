#!/bin/bash

# Web Agent 数据合成运行脚本
# 
# 使用方法:
#   ./run_synthesis.sh
# 
# 或者自定义参数:
#   ./run_synthesis.sh --max-depth 7 --branching-factor 3

echo "=================================="
echo "Web Agent 数据合成系统"
echo "=================================="
echo ""

export OPENAI_API_KEY='sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX'
export OPENAI_API_URL='http://123.129.219.111:3000/v1/'
export SERPER_API_KEY='ba84d16985e52118b112103fd7c97f5dad1db3f4'

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 未设置"
    echo "请设置: export OPENAI_API_KEY='your-key'"
fi

if [ -z "$OPENAI_API_URL" ] && [ -z "$OPENAI_API_BASE" ]; then
    echo "⚠️  警告: OPENAI_API_URL 或 OPENAI_API_BASE 未设置"
    echo "请设置: export OPENAI_API_URL='your-url'"
fi

if [ -z "$SERPER_API_KEY" ]; then
    echo "⚠️  警告: SERPER_API_KEY 未设置"
    echo "请设置: export SERPER_API_KEY='your-key'"
fi

echo ""
echo "开始运行数据合成..."
echo ""

# 运行数据合成
python web_agent.py \
    --seed-entities example_seed_entities.json \
    --model gpt-4.1-2025-04-14 \
    --max-depth 5 \
    --branching-factor 2 \
    --max-trajectories 5 \
    --min-depth 2 \
    --depth-threshold 1 \
    --web-search-top-k 3 \
    --output-dir synthesis_results \
    "$@"

echo ""
echo "=================================="
echo "运行完成!"
echo "=================================="
echo ""
echo "结果保存在: synthesis_results/"
echo "  - synthesized_qa_*.jsonl  : 合成的问答对"
echo "  - trajectories_*.json     : 轨迹数据"
echo "  - statistics_*.json       : 统计信息"
echo ""

