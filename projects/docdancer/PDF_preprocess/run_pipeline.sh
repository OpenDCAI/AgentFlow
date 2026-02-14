#!/bin/bash

# PDF文档处理流水线脚本
# 依次执行：PDF提取 -> 数据处理 -> 生成大纲和根节点

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置路径
PDF_INPUT_DIR="${SCRIPT_DIR}/test_PDF"
OCR_OUTPUT_DIR="${SCRIPT_DIR}/output/ocr_json"
PROCESSED_OUTPUT_DIR="${SCRIPT_DIR}/output/processed"
MODEL_PATH="${MODEL_PATH:-opendatalab/MinerU2.5-2509-1.2B}"  # 可通过环境变量覆盖
MAX_WORKERS="${MAX_WORKERS:-4}"  # 可通过环境变量覆盖

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查目录是否存在
check_directory() {
    if [ ! -d "$1" ]; then
        print_error "目录不存在: $1"
        exit 1
    fi
}

# 检查文件是否存在
check_file() {
    if [ ! -f "$1" ]; then
        print_error "文件不存在: $1"
        exit 1
    fi
}

# 打印配置信息
print_info "=========================================="
print_info "PDF文档处理流水线"
print_info "=========================================="
print_info "PDF输入目录: $PDF_INPUT_DIR"
print_info "OCR输出目录: $OCR_OUTPUT_DIR"
print_info "处理后输出目录: $PROCESSED_OUTPUT_DIR"
print_info "模型路径: $MODEL_PATH"
print_info "最大工作进程数: $MAX_WORKERS"
print_info "=========================================="
echo ""

# 检查输入目录
print_info "检查输入目录..."
check_directory "$PDF_INPUT_DIR"

# 检查PDF文件是否存在
PDF_COUNT=$(find "$PDF_INPUT_DIR" -maxdepth 1 -name "*.pdf" | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    print_error "在 $PDF_INPUT_DIR 中未找到PDF文件"
    exit 1
fi
print_success "找到 $PDF_COUNT 个PDF文件"

# 检查Python脚本
print_info "检查Python脚本..."
check_file "${SCRIPT_DIR}/1_run_pdf_extract.py"
check_file "${SCRIPT_DIR}/2_process_extracted_data.py"
check_file "${SCRIPT_DIR}/3_get_outline_and_root.py"
print_success "所有Python脚本检查通过"

# 创建输出目录
print_info "创建输出目录..."
mkdir -p "$OCR_OUTPUT_DIR"
mkdir -p "$PROCESSED_OUTPUT_DIR"
print_success "输出目录创建完成"

echo ""
print_info "=========================================="
print_info "步骤 1/3: PDF提取 (MinerU OCR)"
print_info "=========================================="
python "${SCRIPT_DIR}/1_run_pdf_extract.py" \
    --input_dir "$PDF_INPUT_DIR" \
    --output_dir "$OCR_OUTPUT_DIR" \
    --model_path "$MODEL_PATH"

if [ $? -ne 0 ]; then
    print_error "步骤1失败: PDF提取"
    exit 1
fi
print_success "步骤1完成: PDF提取"

echo ""
print_info "=========================================="
print_info "步骤 2/3: 数据处理和图像提取"
print_info "=========================================="
python "${SCRIPT_DIR}/2_process_extracted_data.py" \
    --input_root "$OCR_OUTPUT_DIR" \
    --output_root "$PROCESSED_OUTPUT_DIR" \
    --pdf_root "$PDF_INPUT_DIR" \
    --max_workers "$MAX_WORKERS"

if [ $? -ne 0 ]; then
    print_error "步骤2失败: 数据处理"
    exit 1
fi
print_success "步骤2完成: 数据处理"

echo ""
print_info "=========================================="
print_info "步骤 3/3: 生成大纲和根节点"
print_info "=========================================="
python "${SCRIPT_DIR}/3_get_outline_and_root.py" "$PROCESSED_OUTPUT_DIR"

if [ $? -ne 0 ]; then
    print_error "步骤3失败: 生成大纲"
    exit 1
fi
print_success "步骤3完成: 生成大纲"

echo ""
print_info "=========================================="
print_success "🎉 所有步骤完成！"
print_info "=========================================="
print_info "输出文件位置:"
print_info "  - OCR JSON: $OCR_OUTPUT_DIR"
print_info "  - 处理后数据: $PROCESSED_OUTPUT_DIR"
print_info "  - 每个PDF的处理结果在: $PROCESSED_OUTPUT_DIR/<PDF名称>/"
print_info "    * data.pkl: 结构化数据"
print_info "    * <PDF名称>.json: JSON格式数据"
print_info "    * outline.xml: 文档大纲"
print_info "    * all_content.xml: 完整内容"
print_info "    * figures/: 提取的图片"
print_info "    * tables/: 提取的表格"
print_info "    * page_images/: 页面图片"
print_info "=========================================="
