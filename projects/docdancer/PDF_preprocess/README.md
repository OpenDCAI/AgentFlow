# PDF文档处理流水线

本项目的文档结构化提取基于 [mineru-vl-utils](https://github.com/opendatalab/mineru-vl-utils/tree/main/mineru_vl_utils) 实现。**具体环境依赖建议参考官方github文档说明，pip包及依赖、模型部署等细节以官方为准。**

该流水线结合 MinerU 模型，完成 OCR 提取、数据处理与结构化输出。

## 📋 功能概述

流水线包含如下三个主要步骤：

1. **PDF提取** (`1_run_pdf_extract.py`): 调用 MinerU VLM 与 vLLM 引擎批量提取PDF OCR结果
2. **数据处理** (`2_process_extracted_data.py`): 处理上步结果，裁剪/保存图片和表格，生成图像描述，输出结构化数据
3. **生成大纲** (`3_get_outline_and_root.py`): 基于处理结果生成文档大纲和完整内容XML文件

## 🚀 快速开始

### 前置要求

1. **Python环境**: Python 3.8+
2. **依赖包安装**（参见[mineru-vl-utils官方环境说明](https://github.com/opendatalab/mineru-vl-utils/tree/main/mineru_vl_utils)，以下仅为常见依赖举例）:
   ```bash
   pip install 'mineru-vl-utils[vllm]' pdf2image Pillow PyMuPDF pandas numpy openai tqdm
   ```
3. **vLLM**: 请确保已正确安装 vLLM 引擎及 MinerU 权重，详见官方 repo
4. **PDF文件**: 待处理PDF文件请置于 `test_PDF/` 目录下

### 使用方法

#### 方法1: 使用 Bash 脚本（推荐）

```bash
# 赋予执行权限
chmod +x run_pipeline.sh

# 一键运行完整流程
./run_pipeline.sh
```

#### 方法2: 手动依次运行各步骤

```bash
# 步骤1: PDF提取
python 1_run_pdf_extract.py \
    --input_dir test_PDF \
    --output_dir output/ocr_json \
    --model_path opendatalab/MinerU2.5-2509-1.2B

# 步骤2: 数据处理
python 2_process_extracted_data.py \
    --input_root output/ocr_json \
    --output_root output/processed \
    --pdf_root test_PDF \
    --max_workers 4

# 步骤3: 生成大纲
python 3_get_outline_and_root.py output/processed
```

## ⚙️ 配置选项

### 环境变量

通过环境变量自定义主要配置：

```bash
# 设置模型路径
export MODEL_PATH="opendatalab/MinerU2.5-2509-1.2B"

# 设置最大进程数
export MAX_WORKERS=4

# 运行脚本
./run_pipeline.sh
```

### 脚本参数说明

#### 1_run_pdf_extract.py
- `--input_dir`: PDF文件目录（必需）
- `--output_dir`: OCR JSON输出目录（必需）
- `--model_path`: MinerU模型repo或ckpt（可选，默认: `opendatalab/MinerU2.5-2509-1.2B`）

#### 2_process_extracted_data.py
- `--input_root`: OCR JSON 输入目录（必需）
- `--output_root`: 结构化输出目录（必需）
- `--pdf_root`: 源PDF文件目录（必需）
- `--max_workers`: 最大并行工作数（可选，默认: 4）

#### 3_get_outline_and_root.py
- `prepress_root_path`: 已处理数据的根目录（位置参数，必需）

## 📁 输出结构

处理完成后，输出结构如下：

```
output/
├── ocr_json/                    # 步骤1输出
│   ├── PDF1_ocr.json
│   └── PDF2_ocr.json
│
└── processed/                   # 步骤2和3输出
    ├── PDF1/
    │   ├── data.pkl            # 结构化数据（DataFrame）
    │   ├── PDF1.json           # JSON格式数据
    │   ├── outline.xml         # 文档大纲
    │   ├── all_content.xml     # 完整内容
    │   ├── figures/            # 提取图片
    │   │   ├── image_0.png
    │   │   └── ...
    │   ├── tables/             # 提取表格
    │   │   ├── table_0.png
    │   │   └── ...
    │   └── page_images/        # 页面图片
    │       ├── page_0000.png
    │       └── ...
    └── PDF2/
        └── ...
```

## 🔍 输出文件说明

### data.pkl
包含所有提取内容的 pandas DataFrame，包括（但不限于）：
- `para_text`: 文本内容或图片/表格信息
- `table_id`: 表格/图片ID
- `style`: 内容类型（如 Title, Heading 1-6, Text, Image, Table, Caption等）

### outline.xml
文档大纲 XML，含：
- 文档结构（Section分层）
- 标题（Heading）
- 段落首句（Paragraph first_sentence）
- 图片描述首句（Image first_sentence_of_image_description）
- 表格位置信息

### all_content.xml
完整内容 XML，含全部结构化的文本、图片和表格信息
