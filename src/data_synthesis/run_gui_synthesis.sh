#!/bin/bash
# GUI Agent 数据合成运行脚本
# 用法: ./run_gui_synthesis.sh [vm_path]

set -e

# 默认参数
DEFAULT_VM_PATH="/home/a1/sdb/zhy/GUIAgent/OSWorld/vmware_vm_data/Ubuntu0/Ubuntu.vmx"
DEFAULT_CONFIG="configs/osworld_config.json"
DEFAULT_SEEDS="example_seed_gui_tasks.json"
DEFAULT_OUTPUT="synthesis_results/gui"

# 从命令行参数获取VM路径，或使用默认值
VM_PATH=${1:-$DEFAULT_VM_PATH}

# 检查VM路径是否存在
if [ ! -f "$VM_PATH" ] && [ "$VM_PATH" != "/path/to/ubuntu.vmx" ]; then
    echo "错误: VM文件不存在: $VM_PATH"
    exit 1
fi

# 提示用户
echo "=================================="
echo "GUI Agent 数据合成"
echo "=================================="
echo "VM路径: $VM_PATH"
echo "配置文件: $DEFAULT_CONFIG"
echo "Seeds文件: $DEFAULT_SEEDS"
echo "输出目录: $DEFAULT_OUTPUT"
echo "=================================="
echo ""

# 检查配置文件是否存在
if [ ! -f "$DEFAULT_CONFIG" ]; then
    echo "错误: 配置文件不存在: $DEFAULT_CONFIG"
    echo "请先创建配置文件或使用正确的路径"
    exit 1
fi

# 检查seeds文件是否存在
if [ ! -f "$DEFAULT_SEEDS" ]; then
    echo "错误: Seeds文件不存在: $DEFAULT_SEEDS"
    echo "请先创建seeds文件或使用正确的路径"
    exit 1
fi

# 临时修改配置文件中的VM路径（如果提供了自定义路径）
if [ "$VM_PATH" != "/path/to/ubuntu.vmx" ]; then
    echo "更新配置文件中的VM路径..."
    # 创建临时配置文件
    TMP_CONFIG="configs/osworld_config_tmp.json"
    cp "$DEFAULT_CONFIG" "$TMP_CONFIG"
    
    # 使用sed替换VM路径
    # 注意：这个简单的替换假设path_to_vm在单独一行
    sed -i "s|\"path_to_vm\": \"[^\"]*\"|\"path_to_vm\": \"$VM_PATH\"|" "$TMP_CONFIG"
    
    CONFIG_TO_USE="$TMP_CONFIG"
else
    CONFIG_TO_USE="$DEFAULT_CONFIG"
    echo "警告: 使用默认VM路径 (请在配置文件中修改)"
fi

# 运行数据合成
echo "开始运行数据合成..."
echo ""

python synthesis_pipeline_multi.py \
    --config "$CONFIG_TO_USE" \
    --seeds "$DEFAULT_SEEDS" \
    --output-dir "$DEFAULT_OUTPUT"

# 清理临时文件
if [ "$CONFIG_TO_USE" == "$TMP_CONFIG" ]; then
    rm -f "$TMP_CONFIG"
fi

echo ""
echo "=================================="
echo "数据合成完成！"
echo "=================================="
echo "输出目录: $DEFAULT_OUTPUT"
echo "QA文件: $DEFAULT_OUTPUT/synthesized_qa_osworld.jsonl"
echo "轨迹文件: $DEFAULT_OUTPUT/trajectories_osworld.jsonl"
echo "=================================="

