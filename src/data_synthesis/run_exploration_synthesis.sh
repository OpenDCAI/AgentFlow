#!/bin/bash
# GUI探索式数据合成运行脚本

set -e

# 默认参数
export OPENAI_API_KEY='sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX'
export OPENAI_API_URL='http://123.129.219.111:3000/v1/'

DEFAULT_VM_PATH="/home/a1/sdb/zhy/GUIAgent/OSWorld/vmware_vm_data/Ubuntu0/Ubuntu.vmx"
DEFAULT_CONFIG="configs/osworld_exploration_config.json"
DEFAULT_SEEDS="example_seed_exploration.json"
DEFAULT_OUTPUT="exploration_results"

# 从命令行参数获取VM路径
VM_PATH=${1:-$DEFAULT_VM_PATH}

# 提示用户
echo "=================================="
echo "GUI探索式数据合成"
echo "=================================="
echo "VM路径: $VM_PATH"
echo "配置文件: $DEFAULT_CONFIG"
echo "探索方向: $DEFAULT_SEEDS"
echo "输出目录: $DEFAULT_OUTPUT"
echo "=================================="
echo ""

# 检查配置文件
if [ ! -f "$DEFAULT_CONFIG" ]; then
    echo "错误: 配置文件不存在: $DEFAULT_CONFIG"
    exit 1
fi

# 检查seeds文件
if [ ! -f "$DEFAULT_SEEDS" ]; then
    echo "错误: Seeds文件不存在: $DEFAULT_SEEDS"
    exit 1
fi

# 更新配置文件中的VM路径（如果提供了自定义路径）
if [ "$VM_PATH" != "/path/to/ubuntu.vmx" ]; then
    echo "更新配置文件中的VM路径..."
    TMP_CONFIG="configs/osworld_exploration_config_tmp.json"
    cp "$DEFAULT_CONFIG" "$TMP_CONFIG"
    sed -i "s|\"path_to_vm\": \"[^\"]*\"|\"path_to_vm\": \"$VM_PATH\"|" "$TMP_CONFIG"
    CONFIG_TO_USE="$TMP_CONFIG"
else
    CONFIG_TO_USE="$DEFAULT_CONFIG"
    echo "警告: 使用默认VM路径（请在配置文件中修改）"
fi

# 运行探索式数据合成
echo "开始运行探索式数据合成..."
echo ""

python exploration_pipeline.py \
    --config "$CONFIG_TO_USE" \
    --seeds "$DEFAULT_SEEDS" \
    --output-dir "$DEFAULT_OUTPUT"

# 清理临时文件
if [ "$CONFIG_TO_USE" == "$TMP_CONFIG" ]; then
    rm -f "$TMP_CONFIG"
fi

echo ""
echo "=================================="
echo "探索式数据合成完成！"
echo "=================================="
echo "输出目录: $DEFAULT_OUTPUT"
echo "任务/QA文件: $DEFAULT_OUTPUT/exploration_tasks.jsonl 或 exploration_qa.jsonl"
echo "探索树文件: $DEFAULT_OUTPUT/tree_explore_*.json"
echo "=================================="

