#!/bin/bash

# --- 1. 环境配置  ---
# 注意: 建议使用 export 命令，确保变量在子进程 (python run.py) 中可用。
export OPENAI_API_KEY="sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX"
export OPENAI_API_BASE="http://123.129.219.111:3000/v1"
export OPENAI_API_URL="http://123.129.219.111:3000/v1"

# 如果不设置，工具内部使用硬编码路径 (data/doc_demo/PDF 和 data/doc_demo/output)
pdf_root="src/data/doc_demo/PDF"
ocr_output_root="src/data/doc_demo/output"
temp-output-root="src/data/doc_demo/temp"


RESULTS_DIR="results"
DATA_PATH="src/data/doc_demo/doc_demo.jsonl"
MODEL_PATH="/mnt/dhwfile/doc_parse/wufan/cache/mineru2.5/mineru2.5_0916_e3" # 必须传递给 DocOCRTool

# --- 3. 执行 AgentFlow 命令 ---
echo "🚀 Starting Doc Agent Execution from CWD: $(pwd)"
echo "----------------------------------------------------"
# 打印硬编码路径信息以供参考
echo "Tool PDF Source (Hardcoded): ${PDF_DIR}"
echo "Tool JSON Output (Hardcoded): ${OUTPUT_ROOT}"
echo "Benchmark Data (Relative): ${DATA_PATH}"
echo "----------------------------------------------------"

python src/run.py \
    --mode doc \
    --data "${DATA_PATH}" \
    --output-dir "${RESULTS_DIR}" \
    --max-workers 1 \
    --no-eval \
    \
    --ocr-model-path "${MODEL_PATH}" \
    --ocr-backend-type "transformers"


# --- 4. 结束提示 ---
echo "----------------------------------------------------"
echo "✅ Execution command sent."