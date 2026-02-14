# Rollout - Agent Benchmark Execution Pipeline

Rollout 是一个用于在 benchmark 数据集上运行 Agent 的执行框架。它提供了配置驱动的方式来设置工具、运行任务、评估结果。

## 特性

- **配置驱动**: 通过 JSON/YAML 配置文件注册工具和设置参数
- **多种工具支持**: RAG、Web、VM、Bash、Code 等多种工具类型
- **多种评估指标**: exact_match、f1_score、contains_answer、numeric_match、llm_judgement
- **轨迹记录**: 完整记录对话轨迹，便于分析和调试
- **并行执行**: 支持并行运行多个任务
- **灵活集成**: 可与 sandbox 服务器无缝集成

## 快速开始

### 1. 简单 API 调用

```python
from rollout import rollout

# 使用配置文件运行
summary = rollout(
    config_path="configs/rollout/web_benchmark.json",
    data_path="benchmark/benchmark.jsonl"
)

print(f"Average score: {summary['average_score']}")
```

### 2. 单问题快速测试

```python
from rollout import quick_rollout

result = quick_rollout(
    "What is the capital of France?",
    tools=["web:search", "web:visit"]
)

print(f"Answer: {result['answer']}")
```

### 3. 命令行运行

```bash
# 使用配置文件
python quick_rollout.py --config configs/rollout/rag_benchmark.json

# 单问题测试
python quick_rollout.py --question "What is Python?" --tools web:search

# 覆盖参数
python quick_rollout.py --config configs/rollout/web_benchmark.json \
    --data my_data.jsonl \
    --output results/ \
    --max-tasks 10
```

### 4. 完整 Pipeline 控制

```python
from rollout import RolloutConfig, RolloutPipeline

# 加载配置
config = RolloutConfig.from_json("configs/rollout/rag_benchmark.json")

# 可选：修改配置
config.max_turns = 30
config.model_name = "gpt-4"

# 创建并运行 pipeline
pipeline = RolloutPipeline(config, output_dir="my_results")
summary = pipeline.run()
```

## 配置文件格式

```json
{
  "benchmark_name": "my_benchmark",
  "model_name": "gpt-4.1-2025-04-14",
  "base_url": "https://your-openai-compatible-endpoint/v1",
  
  "max_turns": 50,
  "max_retries": 3,
  
  "available_tools": ["web:search", "rag:search", "vm:*"],
  
  "system_prompt": "You are a helpful assistant...",
  
  "evaluate_results": true,
  "evaluation_metric": "f1_score",
  
  "resource_types": ["rag"],
  "resource_init_configs": {
    "rag": {"content": {"top_k": 10}}
  },
  
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": false,
  
  "data_path": "benchmark/benchmark.jsonl",
  "output_dir": "results/",
  
  "save_results": true,
  "save_trajectories": true
}
```

## Benchmark 数据格式

数据文件使用 JSONL 格式，每行一个任务：

```jsonl
{"id": "task_001", "question": "What is the capital of France?", "answer": "Paris"}
{"id": "task_002", "question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare"}
```

支持的字段别名：
- `id` / `task_id`
- `question` / `query` / `input`
- `answer` / `ground_truth` / `expected`

## 可用工具

### RAG 工具
- `rag_search` - 搜索本地知识库

### Web 工具
- `web_search` - 网页搜索
- `web_visit` - 访问网页提取内容

### VM 工具
- `vm_screenshot` - 截屏
- `vm_click` / `vm_double_click` - 点击
- `vm_type` - 输入文本
- `vm_key` / `vm_hotkey` - 按键
- `vm_scroll` / `vm_drag` / `vm_move` - 鼠标操作

## 评估指标

| 指标 | 描述 |
|-----|-----|
| `exact_match` | 规范化后精确匹配 |
| `f1_score` | Token 级 F1 分数 |
| `contains_answer` | 预测是否包含答案 |
| `numeric_match` | 数值匹配（带容差） |
| `llm_judgement` | 使用 LLM 判断正确性 |

## 输出文件

运行完成后会生成以下文件：

- `results_{name}_{timestamp}.jsonl` - 每个任务的结果
- `evaluation_{name}_{timestamp}.json` - 评估详情
- `summary_{name}_{timestamp}.json` - 运行摘要

## 目录结构

```
rollout/
├── __init__.py          # 模块入口
├── api.py               # 简单 API
├── pipeline.py          # 主 Pipeline
├── core/
│   ├── config.py        # 配置管理
│   ├── models.py        # 数据模型
│   ├── runner.py        # Agent 运行器
│   ├── evaluator.py     # 评估器
│   └── utils.py         # 工具函数
├── tools/
│   ├── __init__.py      # 工具 schema
│   └── __init__.py      # 工具 schema
├── tests/
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_evaluator.py
│   └── test_tools.py
└── README.md
```

## 环境变量

| 变量 | 描述 |
|-----|-----|
| `OPENAI_API_KEY` | OpenAI API Key |
| `OPENAI_API_BASE` | API Base URL |
| `LLM_MODEL_NAME` | 默认模型名称 |
| `OUTPUT_DIR` | 默认输出目录 |

> 如果在配置文件中设置了 `base_url`，会优先使用该值；否则回退到 `OPENAI_API_BASE` / `OPENAI_API_URL`。

## 运行测试

```bash
# 运行所有测试
pytest rollout/tests/ -v

# 运行特定测试
pytest rollout/tests/test_config.py -v
```

## 与 Synthesis 的区别

| 特性 | Synthesis | Rollout |
|-----|-----------|---------|
| 目标 | 生成训练数据 | 评估模型性能 |
| 输入 | Seed 数据 | Benchmark 任务 |
| 输出 | QA 对 + 轨迹 | 预测 + 评估结果 |
| 采样 | 树状探索 | 单一对话 |
| 评估 | 无 | 多种指标 |

## License

MIT License
