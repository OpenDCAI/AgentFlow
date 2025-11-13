# MMLongBench 快速开始指南

## 三步开始测试

### 步骤 1: 转换数据格式

```bash
cd AgentFlow/src/data
python load_mmlongbench.py --input /path/to/mmlongbench.json --output mmlongbench_demo.jsonl
```

### 步骤 2: 运行 Benchmark 测试

```bash
cd AgentFlow/src
python run.py \
    --mode doc \
    --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/mineru/model \
    --ocr-backend-type transformers \
    --metric numeric_match
```

### 步骤 3: 查看结果

```bash
# 查看评估结果
cat results/evaluation_mmlongbench_demo.json | python -m json.tool
```

## 常用命令

### 基本测试（顺序执行）

```bash
python src/run.py \
    --mode doc \
    --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model \
    --ocr-backend-type transformers
```

### 并行测试（更快）

```bash
python src/run.py \
    --mode doc \
    --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model \
    --ocr-backend-type transformers \
    --parallel \
    --max-workers 4
```

### 使用不同评估指标

```bash
# 数值匹配（推荐用于百分比、数量等）
python src/run.py --mode doc --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model --metric numeric_match

# F1 分数（推荐用于文本答案）
python src/run.py --mode doc --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model --metric f1_score

# LLM 判断（推荐用于复杂答案）
python src/run.py --mode doc --data data/mmlongbench_demo.jsonl \
    --ocr-model-path /path/to/model --metric llm_judgement
```

## 环境变量设置

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_URL="your-api-url"
```

## 测试转换脚本

```bash
# 测试数据转换和加载
python src/data/test_mmlongbench_benchmark.py
```

## 结果文件位置

- 任务结果: `results/result_mmlongbench_demo.jsonl`
- 评估结果: `results/evaluation_mmlongbench_demo.json`

## 更多信息

详细文档请参考: `README_MMLONGBENCH.md`

