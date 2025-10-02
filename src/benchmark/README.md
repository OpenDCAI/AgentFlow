# AgentFlow Benchmark

这个模块提供了 Benchmark 类用于加载和评估基准测试数据集。

## 功能特性

- **数据加载**: 支持 JSON 和 JSONL 格式的数据文件
- **多种评估指标**: 提供 exact_match、F1、BLEU、ROUGE、相似度等多种评估指标
- **灵活的数据结构**: 支持不同的数据格式和自定义解析
- **结果管理**: 支持保存和加载评估结果
- **详细统计**: 提供完整的评估统计信息

## 快速开始

### 基本使用

```python
from benchmark import create_benchmark

# 创建基准测试
benchmark = create_benchmark(
    data_path="data/math_demo.jsonl",
    name="Math Demo",
    description="数学计算基准测试"
)

# 获取问题和答案
questions = benchmark.get_questions()
answers = benchmark.get_answers()

# 评估预测结果
predictions = {"item_id": "predicted_answer"}
results = benchmark.evaluate(predictions, metric="exact_match")

# 获取评估摘要
summary = benchmark.get_summary()
print(summary)
```

### 数据格式

支持两种数据格式：

#### JSONL 格式

```jsonl
{"id": "q1", "question": "What is 2+2?", "answer": "4"}
{"id": "q2", "question": "What is 3*3?", "answer": "9"}
```

#### JSON 格式

```json
[
  { "id": "q1", "question": "What is 2+2?", "answer": "4" },
  { "id": "q2", "question": "What is 3*3?", "answer": "9" }
]
```

或者结构化格式：

```json
{
  "name": "Math Test",
  "items": [
    { "id": "q1", "question": "What is 2+2?", "answer": "4" },
    { "id": "q2", "question": "What is 3*3?", "answer": "9" }
  ]
}
```

## API 参考

### Benchmark 类

#### 构造函数

```python
Benchmark(
    data_path: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None
)
```

#### 主要方法

- `load_data(data_path: str)`: 加载数据文件
- `get_item(item_id: str)`: 获取指定 ID 的项目
- `get_items() -> List[BenchmarkItem]`: 获取所有项目
- `get_questions() -> List[str]`: 获取所有问题
- `get_answers() -> List[str]`: 获取所有答案
- `evaluate(predictions, metric="exact_match")`: 评估预测结果
- `get_summary() -> Dict[str, Any]`: 获取评估摘要
- `save_results(file_path: str)`: 保存评估结果
- `load_results(file_path: str)`: 加载评估结果

### 评估指标

#### 内置指标

1. **exact_match**: 完全匹配

   - 检查预测结果是否与标准答案完全一致

2. **f1_score**: F1 分数

   - 基于词重叠的 F1 分数

3. **bleu_score**: BLEU 分数

   - 基于 n-gram 重叠的 BLEU 分数

4. **rouge_score**: ROUGE 分数

   - 基于最长公共子序列的 ROUGE-L 分数

5. **similarity**: 字符串相似度

   - 使用 difflib 计算字符串相似度

6. **contains_answer**: 包含答案

   - 检查预测结果是否包含标准答案

7. **numeric_match**: 数值匹配
   - 提取并比较数值答案

#### 使用示例

```python
# 使用不同指标评估
results = benchmark.evaluate(predictions, metric="exact_match")
results = benchmark.evaluate(predictions, metric="f1_score")
results = benchmark.evaluate(predictions, metric="similarity")
```

### 数据结构

#### BenchmarkItem

```python
@dataclass
class BenchmarkItem:
    id: str
    question: str
    answer: str
    metadata: Optional[Dict[str, Any]] = None
```

#### EvaluationResult

```python
@dataclass
class EvaluationResult:
    item_id: str
    question: str
    ground_truth: str
    prediction: str
    score: float
    metric_name: str
    details: Optional[Dict[str, Any]] = None
```

## 高级用法

### 自定义数据解析

```python
class CustomBenchmark(Benchmark):
    def _parse_item(self, data: Dict[str, Any], line_num: int) -> BenchmarkItem:
        # 自定义解析逻辑
        item_id = data.get('question_id', f'item_{line_num}')
        question = data.get('query', '')
        answer = data.get('response', '')

        return BenchmarkItem(
            id=item_id,
            question=question,
            answer=answer,
            metadata={'line': line_num}
        )
```

### 自定义评估指标

```python
def custom_metric(ground_truth: str, prediction: str, **kwargs) -> float:
    # 自定义评估逻辑
    return score

# 注册自定义指标
benchmark._get_metric_function = lambda metric: {
    'custom': custom_metric
}.get(metric, benchmark._get_metric_function(metric))
```

### 批量评估

```python
# 使用字典格式的预测结果
predictions = {
    "q1": "answer1",
    "q2": "answer2",
    "q3": "answer3"
}
results = benchmark.evaluate(predictions, metric="exact_match")

# 使用列表格式的预测结果（按顺序）
predictions = ["answer1", "answer2", "answer3"]
results = benchmark.evaluate(predictions, metric="exact_match")
```

## 示例

查看 `example_usage.py` 文件获取更多使用示例。

## 注意事项

1. 确保数据文件格式正确
2. 预测结果的 ID 必须与基准测试中的 ID 匹配
3. 评估指标的选择应根据任务类型决定
4. 大量数据评估时建议使用批处理方式
