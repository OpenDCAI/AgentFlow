#!/bin/bash

# 通用Agent数据合成运行脚本
# 
# 使用方法:
#   ./run_generic_synthesis.sh web      # 使用Web配置
#   ./run_generic_synthesis.sh math     # 使用Math配置
#   ./run_generic_synthesis.sh python   # 使用Python配置
#   ./run_generic_synthesis.sh rag      # 使用RAG配置
#   ./run_generic_synthesis.sh custom path/to/config.json  # 使用自定义配置

echo "=========================================="
echo "通用Agent数据合成系统"
echo "=========================================="
echo ""

# 设置环境变量
export OPENAI_API_KEY='sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX'
export OPENAI_API_URL='http://123.129.219.111:3000/v1/'
export SERPER_API_KEY='ba84d16985e52118b112103fd7c97f5dad1db3f4'

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 未设置"
fi

if [ -z "$OPENAI_API_URL" ]; then
    echo "⚠️  警告: OPENAI_API_URL 未设置"
fi

# 确定使用哪个配置文件
# CONFIG_TYPE=${1:-"web"}
CONFIG_TYPE=${1:-"rag"}
SEED_FILE=${2:-"example_seed_entities.json"}
OUTPUT_DIR=${3:-"synthesis_results"}

case $CONFIG_TYPE in
    web)
        CONFIG_FILE="configs/web_config.json"
        echo "使用配置: Web环境 (web_search + web_visit)"
        ;;
    math)
        CONFIG_FILE="configs/math_config.json"
        echo "使用配置: Math环境 (calculator)"
        ;;
    python|py)
        CONFIG_FILE="configs/python_config.json"
        echo "使用配置: Python环境 (python_interpreter)"
        ;;
    rag)
        CONFIG_FILE="configs/rag_config.json"
        echo "使用配置: RAG环境 (local_search)"
        echo "⚠️  注意: 请确保在配置文件中设置了正确的 rag_index 路径"
        ;;
    custom)
        CONFIG_FILE=$2
        SEED_FILE=${3:-"example_seed_entities.json"}
        OUTPUT_DIR=${4:-"synthesis_results"}
        if [ ! -f "$CONFIG_FILE" ]; then
            echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
            exit 1
        fi
        echo "使用配置: 自定义配置文件 ($CONFIG_FILE)"
        ;;
    *)
        echo "❌ 错误: 未知的配置类型: $CONFIG_TYPE"
        echo ""
        echo "用法:"
        echo "  $0 web [seed_file] [output_dir]       # Web环境"
        echo "  $0 math [seed_file] [output_dir]      # Math环境"
        echo "  $0 python [seed_file] [output_dir]    # Python环境"
        echo "  $0 rag [seed_file] [output_dir]       # RAG环境"
        echo "  $0 custom config_file [seed_file] [output_dir]  # 自定义配置"
        echo ""
        exit 1
        ;;
esac

# 检查文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

if [ ! -f "$SEED_FILE" ]; then
    echo "❌ 错误: Seed数据文件不存在: $SEED_FILE"
    exit 1
fi

echo "配置文件: $CONFIG_FILE"
echo "Seed文件: $SEED_FILE"
echo "输出目录: $OUTPUT_DIR"
echo ""
echo "开始运行数据合成..."
echo ""

# 运行数据合成
python synthesis_pipeline.py \
    --config "$CONFIG_FILE" \
    --seeds "$SEED_FILE" \
    --output-dir "$OUTPUT_DIR"

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 运行完成!"
    echo "=========================================="
    echo ""
    echo "结果保存在: $OUTPUT_DIR/"
    echo "  - synthesized_qa_*.jsonl  : 合成的问答对"
    echo "  - trajectories_*.json     : 轨迹数据"
    echo "  - statistics_*.json       : 统计信息"
else
    echo "❌ 运行失败! (退出码: $EXIT_CODE)"
    echo "=========================================="
fi
echo ""


