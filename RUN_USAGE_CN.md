# AgentFlow 运行脚本使用指南

本文档描述了如何使用集成了 Environment 和 Benchmark 模块的新`run.py`脚本。

## 概述

新的`run.py`脚本为使用 Environment 和 Benchmark 类在不同基准测试上运行智能体提供了统一接口。它用更模块化和可扩展的架构替换了旧的基于模式的方法。

## 主要特性

- **统一接口**: 所有环境类型的单一脚本
- **模块化架构**: 使用 Environment 和 Benchmark 类
- **灵活配置**: 丰富的命令行选项
- **内置评估**: 多种指标的自动评估
- **并行执行**: 并行任务处理支持
- **结果管理**: 结果的自动保存和加载

## 基本使用

### 命令行界面

```bash
python src/run.py --mode <环境类型> --data <数据路径> [选项]
```

### 必需参数

- `--mode`: 环境类型（`math`, `py`, `rag`, `web`）
- `--data`: 基准测试数据文件路径

### 可选参数

- `--model`: OpenAI 模型名称（默认：`gpt-4.1-2025-04-14`）
- `--max-turns`: 最大对话轮数（默认：20）
- `--max-retries`: 每轮最大重试次数（默认：3）
- `--max-workers`: 最大并行工作进程（默认：1）
- `--output-dir`: 结果输出目录（默认：`results`）
- `--no-eval`: 跳过评估
- `--no-save`: 跳过保存结果
- `--parallel`: 并行运行任务
- `--metric`: 评估指标（默认：`exact_match`）

## 示例

### 数学环境

```bash
# 基本数学基准测试
python src/run.py --mode math --data src/data/math_demo.jsonl

# 自定义模型和评估
python src/run.py --mode math --data src/data/math_demo.jsonl --model gpt-4 --metric f1_score

# 并行执行
python src/run.py --mode math --data src/data/math_demo.jsonl --parallel --max-workers 4
```

### Python 环境

```bash
# Python解释器基准测试
python src/run.py --mode py --data src/data/python_interpreter_demo.jsonl

# 自定义配置
python src/run.py --mode py --data src/data/python_interpreter_demo.jsonl --max-turns 10
```

### Web 环境

```bash
# Web智能体基准测试
python src/run.py --mode web --data src/data/webagent_demo.jsonl

# 带Web特定选项
python src/run.py --mode web --data src/data/webagent_demo.jsonl \
  --web-search-top-k 10 --web-search-type news
```

### RAG 环境

```bash
# 带知识库的RAG基准测试
python src/run.py --mode rag --data src/data/rag_queries.jsonl --kb-path src/data/knowledge_base.json
```

## 配置

### 环境特定选项

#### Web 环境

- `--web-search-top-k`: 搜索结果数量（默认：5）
- `--web-search-type`: 搜索类型（`search`, `news`, `images`）

#### RAG 环境

- `--kb-path`: 知识库文件路径

### 评估指标

可用指标：

- `exact_match`: 精确字符串匹配
- `f1_score`: 基于词重叠的 F1 分数
- `similarity`: 使用 difflib 的字符串相似度
- `contains_answer`: 检查预测是否包含基准答案
- `numeric_match`: 提取并比较数值

## 输出

### 结果文件

脚本生成几个输出文件：

1. **结果文件**: `results/result_<基准测试名称>.jsonl`

   - 包含对话日志和最终答案
   - 每行一个 JSON 对象

2. **评估文件**: `results/evaluation_<基准测试名称>.json`
   - 包含评估结果和指标
   - 性能的详细分析

### 结果格式

```json
{
  "task_id": "item_1",
  "question": "2+2等于多少？",
  "answer": "答案是4。",
  "messages": [...],
  "success": true,
  "error": null
}
```

## 程序化使用

### 使用 AgentRunner 类

```python
from run import AgentRunner, AgentConfig
from envs import MathEnvironment
from benchmark import create_benchmark

# 创建配置
config = AgentConfig(
    model_name="gpt-4",
    max_turns=10,
    evaluate_results=True,
    evaluation_metric="f1_score"
)

# 创建运行器
runner = AgentRunner(config)

# 设置环境
runner.setup_environment("math")

# 加载基准测试
runner.load_benchmark("data/math_demo.jsonl")

# 运行基准测试
results = runner.run_benchmark(parallel=True)

# 评估结果
evaluation = runner.evaluate_results()

# 保存结果
runner.save_results("output/")
```

### 自定义环境集成

```python
from run import AgentRunner, AgentConfig
from envs import MathEnvironment

# 创建自定义环境
env = MathEnvironment(model_name="gpt-4")

# 使用自定义环境创建运行器
runner = AgentRunner(AgentConfig())
runner.environment = env

# 继续正常工作流...
```

## 错误处理

脚本包含全面的错误处理：

- **API 错误**: 带指数退避的自动重试
- **工具错误**: 工具执行故障的优雅处理
- **数据错误**: 输入数据和文件格式的验证
- **配置错误**: 无效选项的清晰错误消息

## 性能提示

1. **并行执行**: 对大数据集使用`--parallel`
2. **工作进程数**: 根据系统调整`--max-workers`
3. **轮数限制**: 为用例设置适当的`--max-turns`
4. **评估**: 开发期间使用`--no-eval`获得更快执行

## 故障排除

### 常见问题

1. **API 密钥未设置**

   ```
   Warning: OPENAI_API_KEY is not set
   ```

   解决方案: 设置`OPENAI_API_KEY`环境变量

2. **文件未找到**

   ```
   FileNotFoundError: Data file not found
   ```

   解决方案: 检查数据文件路径

3. **工具执行错误**
   ```
   Error: Tool calculator not found
   ```
   解决方案: 确保环境正确设置

### 调试模式

要调试，可以修改脚本以添加更详细的日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 从旧脚本迁移

新脚本与旧命令行界面向后兼容：

### 旧命令

```bash
python src/run.py --mode math --data math_demo
```

### 新命令

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl
```

主要差异：

- 数据路径现在包含完整文件路径
- 更多配置选项可用
- 更好的错误处理和日志记录
- 集成的评估和结果管理
