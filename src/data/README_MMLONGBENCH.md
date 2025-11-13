# MMLongBench Benchmark 使用指南

本指南介绍如何使用 MMLongBench 数据集进行 AgentFlow 的 benchmark 测试。

## 1. 数据转换

首先，将 MMLongBench 数据转换为 AgentFlow 格式：

### 从本地文件转换

```bash
cd AgentFlow/src/data
python load_mmlongbench.py --input /path/to/mmlongbench.json --output mmlongbench_demo.jsonl
```

### 从 HuggingFace 加载（如果可用）

```bash
python load_mmlongbench.py --dataset THUDM/MMLongBench --split test --output mmlongbench_demo.jsonl
```

### 转换选项

- `--input`: 本地 JSON/JSONL 文件路径
- `--output`: 输出文件路径（默认：`mmlongbench_demo.jsonl`）
- `--dataset`: HuggingFace 数据集名称
- `--split`: 数据集分割（默认：`test`）
- `--use-index-as-id`: 使用索引作为 ID（而不是 doc_id）

## 2. 运行 Benchmark 测试

MMLongBench 涉及文档处理，需要使用 `doc` 模式。

### 基本使用

```bash
cd AgentFlow/src
python run.py \
    --mode doc \
    --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/mineru/model \
    --ocr-backend-type transformers
```

### 完整参数示例

```bash
python run.py \
    --mode doc \
    --data data/mmlongbench_demo.jsonl \
    --model gpt-4.1-2025-04-14 \
    --ocr-model-path /path/to/mineru/model \
    --ocr-backend-type transformers \
    --max-turns 100 \
    --max-retries 3 \
    --max-workers 1 \
    --output-dir results \
    --metric exact_match \
    --parallel
```

### 参数说明

#### 必需参数
- `--mode doc`: 使用文档处理模式
- `--data`: 转换后的 MMLongBench 数据文件路径
- `--ocr-model-path`: MinerU OCR 模型路径

#### 可选参数
- `--model`: 使用的 LLM 模型（默认：`gpt-4.1-2025-04-14`）
- `--ocr-backend-type`: OCR 后端类型（`transformers` 或 `vllm-engine`，默认：`transformers`）
- `--max-turns`: 最大对话轮数（默认：100）
- `--max-retries`: 每轮最大重试次数（默认：3）
- `--max-workers`: 并行工作进程数（默认：1）
- `--output-dir`: 结果输出目录（默认：`results`）
- `--metric`: 评估指标（`exact_match`, `f1_score`, `similarity`, `contains_answer`, `numeric_match`, `llm_judgement`，默认：`exact_match`）
- `--parallel`: 启用并行执行
- `--no-eval`: 跳过评估
- `--no-save`: 跳过保存结果

## 3. 评估指标

AgentFlow 支持多种评估指标：

- **exact_match**: 精确匹配（默认）
- **f1_score**: F1 分数（基于词重叠）
- **similarity**: 字符串相似度
- **contains_answer**: 检查预测是否包含正确答案
- **numeric_match**: 数值匹配
- **llm_judgement**: 使用 LLM 进行判断

### 选择评估指标

对于 MMLongBench，建议根据答案类型选择：

- **数值答案**（如百分比、数量）：使用 `numeric_match` 或 `exact_match`
- **文本答案**：使用 `f1_score` 或 `similarity`
- **复杂答案**：使用 `llm_judgement`

```bash
# 使用数值匹配
python run.py --mode doc --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model --metric numeric_match

# 使用 LLM 判断
python run.py --mode doc --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model --metric llm_judgement
```

## 4. 结果查看

运行完成后，结果会保存在 `results/` 目录下：

- `result_<benchmark_name>.jsonl`: 每个任务的详细结果
- `evaluation_<benchmark_name>.json`: 评估结果摘要

### 查看结果

```bash
# 查看任务结果
cat results/result_mmlongbench_demo.jsonl | head -n 1 | python -m json.tool

# 查看评估摘要
cat results/evaluation_mmlongbench_demo.json | python -m json.tool
```

## 5. 在 Python 代码中使用

### 方式 1: 使用 AgentRunner（完整流程）

```python
from run import AgentRunner, AgentConfig

# 创建配置
config = AgentConfig(
    model_name="gpt-4.1-2025-04-14",
    max_turns=100,
    evaluation_metric="exact_match"
)

# 创建 runner
runner = AgentRunner(config)

# 运行测试
summary = runner.run(
    mode="doc",
    data_path="data/mmlongbench_demo.jsonl",
    ocr_model_path="/path/to/mineru/model",
    ocr_backend_type="transformers",
    output_dir="results"
)

print(f"评估结果: {summary['evaluation']}")
```

### 方式 2: 仅使用 Benchmark 类（仅评估）

```python
from benchmark import create_benchmark

# 加载 benchmark
benchmark = create_benchmark(
    data_path="data/mmlongbench_demo.jsonl",
    name="MMLongBench Test"
)

# 准备预测结果（字典格式：{item_id: prediction}）
predictions = {
    "Independents-Report.pdf": "18.29%",
    "Test-Document-2.pdf": "Climate change impacts",
    # ... 更多预测
}

# 评估
results = benchmark.evaluate(predictions, metric="exact_match")

# 获取摘要
summary = benchmark.get_summary()
print(f"平均分数: {summary['average_score']}")
print(f"完美匹配: {summary['perfect_matches']}/{summary['total_items']}")

# 保存评估结果
benchmark.save_results("evaluation_results.json")
```

### 方式 3: 访问元数据

转换后的数据保留了所有原始字段，可以通过 metadata 访问：

```python
from benchmark import create_benchmark

benchmark = create_benchmark("data/mmlongbench_demo.jsonl")

for item in benchmark.items:
    print(f"ID: {item.id}")
    print(f"问题: {item.question}")
    print(f"答案: {item.answer}")
    
    # 访问元数据
    if item.metadata:
        print(f"文档类型: {item.metadata.get('doc_type')}")
        print(f"证据页码: {item.metadata.get('evidence_pages')}")
        print(f"答案格式: {item.metadata.get('answer_format')}")
```

## 6. 环境变量设置

确保设置了必要的环境变量：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_URL="your-api-url"  # 或 OPENAI_API_BASE
```

## 7. 故障排除

### 问题：找不到 OCR 模型

**解决方案**：确保 `--ocr-model-path` 指向正确的模型路径。

### 问题：评估指标不匹配

**解决方案**：根据答案类型选择合适的评估指标。对于 MMLongBench，建议：
- 数值答案：`numeric_match`
- 文本答案：`f1_score` 或 `similarity`
- 复杂答案：`llm_judgement`

### 问题：并行执行出错

**解决方案**：如果遇到并发问题，可以：
1. 减少 `--max-workers` 数量
2. 不使用 `--parallel` 标志（顺序执行）

## 8. 示例脚本

创建一个简单的测试脚本 `test_mmlongbench.py`：

```python
#!/usr/bin/env python
"""测试 MMLongBench benchmark"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import AgentRunner, AgentConfig

def main():
    # 配置
    config = AgentConfig(
        model_name="gpt-4.1-2025-04-14",
        max_turns=100,
        max_retries=3,
        max_workers=1,
        evaluation_metric="numeric_match"  # 根据答案类型选择
    )
    
    # 创建 runner
    runner = AgentRunner(config)
    
    # 运行测试
    summary = runner.run(
        mode="doc",
        data_path="data/mmlongbench_demo.jsonl",
        ocr_model_path=os.getenv("OCR_MODEL_PATH", "/path/to/model"),
        ocr_backend_type="transformers",
        output_dir="results"
    )
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print(f"总任务数: {summary['total_tasks']}")
    print(f"成功: {summary['successful_tasks']}")
    print(f"失败: {summary['failed_tasks']}")
    if summary['evaluation']:
        print(f"平均分数: {summary['evaluation'].get('average_score', 0):.3f}")
    print(f"结果文件: {summary['output_file']}")

if __name__ == "__main__":
    main()
```

运行：

```bash
python test_mmlongbench.py
```

## 9. 数据格式说明

### 输入格式（MMLongBench）

```json
{
    "doc_id": "Independents-Report.pdf",
    "doc_type": "Research report / Introduction",
    "question": "What's the percentage...",
    "answer": "18.29%",
    "evidence_pages": "[3, 5]",
    "evidence_sources": "['Pure-text (Plain-text)']",
    "answer_format": "Float"
}
```

### 输出格式（AgentFlow）

```json
{
    "id": "Independents-Report.pdf",
    "question": "What's the percentage...",
    "answer": "18.29%",
    "doc_type": "Research report / Introduction",
    "evidence_pages": "[3, 5]",
    "evidence_sources": "['Pure-text (Plain-text)']",
    "answer_format": "Float"
}
```

所有原始字段都会被保留，可以通过 `item.metadata` 访问额外字段。

