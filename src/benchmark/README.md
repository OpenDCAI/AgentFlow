
# AgentFlow Benchmark

这个模块提供了 `Benchmark` 类，用于加载标准化测试集并评估 Agent 的性能。它不仅支持简单的问答评估，还支持复杂的元数据管理和自定义评测逻辑。

## 功能特性

  * **数据加载**: 原生支持 JSON 和 JSONL 格式，自动识别列表或流式结构。
  * **双模开发**: 支持“零代码”标准模式和“继承扩展”自定义模式。
  * **多种评估指标**: 内置 `exact_match`, `F1`, `BLEU`, `ROUGE`, 数值匹配及 LLM 裁判等。
  * **元数据管理**: 自动将非核心字段解析为 `metadata`，支持 OSWorld 等复杂环境配置。
  * **结果持久化**: 支持保存和加载详细的评估报告。

-----

## 开发指南 (Development Guide)

根据数据格式的复杂度，Benchmark 开发分为两种模式：

### 模式 A：标准模式（零代码）

如果您的数据文件是标准的 JSON/JSONL，且字段能直接映射到 `question` 和 `answer`，则不需要编写任何代码。

直接使用工厂函数加载：

```python
from benchmark import create_benchmark

# 自动加载并解析
benchmark = create_benchmark(
    data_path="data/math_test.jsonl",
    name="Math Test",
    description="标准数学测试集"
)
```

### 模式 B：自定义模式（继承扩展）

如果数据结构特殊（例如字段名为 `problem`/`solution`），或者需要清洗数据，请继承 `Benchmark` 类并重写 `_parse_item`。

```python
from benchmark import Benchmark, BenchmarkItem

class CustomBenchmark(Benchmark):
    def _parse_item(self, data: dict, line_num: int) -> BenchmarkItem:
        # 自定义解析逻辑：将原始字段映射到标准字段
        return BenchmarkItem(
            id=str(data.get('custom_id', line_num)),
            question=data.get('problem_text'),      # 映射 question
            answer=str(data.get('ground_truth')),   # 映射 answer
            metadata={"difficulty": data.get("level")} # 其他存入 metadata
        )
```

-----

## 数据结构说明 (Data Structure)

Benchmark 的核心单元是 `BenchmarkItem`。理解其字段含义对于正确构建数据集至关重要。

```python
@dataclass
class BenchmarkItem:
    id: str
    question: str
    answer: str
    metadata: Optional[Dict[str, Any]] = None
```

### 字段详细说明

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| **id** | `str` | 否 | **唯一标识符**。<br>用于在日志和结果中追踪任务。若数据中缺失，框架会自动生成 `item_{行号}`。 |
| **question** | `str` | **是** | **Agent 输入指令**。<br>告诉 Agent 需要完成什么任务（如 `"Calculate 2+2"` 或 `"Install Spotify"`）。 |
| **answer** | `str` | 否 | **标准答案 (Ground Truth)**。<br>用于文本比对评测。框架会强制将其转换为字符串。<br>*注：对于 OSWorld 等基于状态评测的任务，此字段可为空，评测逻辑存放在 metadata 中。* |
| **metadata** | `dict` | 否 | **元数据/配置容器**。<br>存储所有非核心字段。常用于存放：<br>1. `evaluator`: 评测器配置 (OSWorld 必需)<br>2. `config`: 环境初始化配置<br>3. `difficulty`/`source`: 任务标签 |

-----

## 快速开始

### 1\. 准备数据

**JSONL 格式 (推荐):**

```jsonl
{"id": "q1", "question": "What is 2+2?", "answer": "4", "difficulty": "easy"}
{"id": "q2", "question": "What is 3*3?", "answer": "9", "difficulty": "medium"}
```

### 2\. 加载与评估

```python
from benchmark import create_benchmark

# 1. 加载
benchmark = create_benchmark(data_path="data/math_demo.jsonl")

# 2. 获取数据（模拟 Agent 执行）
questions = benchmark.get_questions()

# 3. 准备预测结果
predictions = {
    "q1": "4", 
    "q2": "9"
}

# 4. 执行评估
# 支持 metric: exact_match, f1_score, contains_answer, numeric_match 等
results = benchmark.evaluate(predictions, metric="exact_match")

# 5. 查看摘要
print(benchmark.get_summary())
# Output: {'average_score': 1.0, 'total_items': 2, ...}
```

-----

## API 参考

### 主要方法

  * **`load_data(data_path)`**: 加载并解析数据文件。
  * **`get_items()`**: 返回所有 `BenchmarkItem` 对象列表。
  * **`evaluate(predictions, metric=...)`**: 核心评估方法。
      * `predictions`: 字典 `{id: prediction}` 或 列表 `[prediction]`。
      * `metric`: 指定评估指标字符串。
  * **`save_results(file_path)`**: 将评估详情和摘要保存为 JSON。

### 内置评估指标

| 指标名称 | 说明 | 适用场景 |
| :--- | :--- | :--- |
| **exact\_match** | 字符串完全相等（去除首尾空格） | 数学、选择题、短文本 |
| **f1\_score** | 基于词袋模型的重叠度 F1 分数 | 阅读理解、长文本生成 |
| **contains\_answer** | 检查预测是否包含标准答案 | 宽松匹配、检索任务 |
| **numeric\_match** | 提取文本中的数字进行数值比对 | 数学计算 (忽略单位/文字) |
| **similarity** | Python `difflib` 字符串相似度 | 模糊匹配 |
| **llm\_judgement** | 调用 GPT-4 进行语义判定 | 开放式问答、复杂逻辑 |

-----

## 高级用法

### 自定义评估指标

如果内置指标不满足需求，可以动态注册新指标：

```python
def my_custom_metric(ground_truth, prediction, **kwargs):
    # 自定义逻辑：例如检查是否是合法的 Python 代码
    return 1.0 if "def " in prediction else 0.0

# 临时注册并使用
benchmark._get_metric_function = lambda metric: {
    'code_check': my_custom_metric
}.get(metric, benchmark._get_metric_function(metric))

benchmark.evaluate(predictions, metric="code_check")
```

-----

## 注意事项

1.  **ID 匹配**: `evaluate` 方法依赖 `id` 来对齐预测结果和标准答案。请确保 Agent 返回的结果中包含正确的 Task ID。
2.  **Answer 类型**: 无论原始 JSON 中的 answer 是数字还是布尔值，在 `BenchmarkItem` 中都会被转换为 `str`。
3.  **并发评估**: `evaluate` 默认开启多线程 (`concurrent=True`) 以加速大量数据的评测。