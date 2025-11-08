# AgentFlow 开发者指南

本指南帮助开发者理解、扩展和贡献 AgentFlow 项目。

## 目录

1. [项目概述](#项目概述)
2. [架构设计](#架构设计)
3. [核心组件](#核心组件)
4. [开发环境设置](#开发环境设置)
5. [添加新工具](#添加新工具)
6. [创建新环境](#创建新环境)
7. [扩展基准测试](#扩展基准测试)
8. [测试](#测试)
9. [贡献指南](#贡献指南)
10. [故障排除](#故障排除)

## 项目概述

AgentFlow 是一个用于构建和评估 AI 智能体的模块化框架。它提供：

- **环境系统**: 不同智能体类型的模块化环境
- **工具系统**: 可扩展的智能体能力框架
- **基准测试系统**: 全面的评估框架
- **统一运行器**: 运行和评估智能体的单一接口

### 主要特性

- 🏗️ **模块化架构**: 清晰的关注点分离
- 🔧 **可扩展工具**: 易于添加新功能
- 📊 **全面评估**: 多种指标和基准测试
- 🚀 **统一接口**: 所有操作的单一命令
- 🧪 **测试框架**: 内置测试和验证

## 架构设计

```
AgentFlow/
├── src/
│   ├── envs/              # 环境类
│   │   ├── environment.py  # 基础Environment类
│   │   └── __init__.py
│   ├── tools/             # 工具实现
│   │   ├── calculator.py
│   │   ├── web_search.py
│   │   ├── web_visit.py
│   │   ├── rag_tools.py
|   |   ├── doc_tools.py
|   |   ├── mineru_vl_utils
│   │   └── __init__.py
│   ├── benchmark/         # 基准测试系统
│   │   ├── benchmark.py   # Benchmark类
│   │   └── __init__.py
│   ├── data/              # 示例数据集
│   ├── results/           # 输出文件
│   └── run.py            # 主执行脚本
├── requirements.txt
└── README.md
```

### 核心设计原则

1. **关注点分离**: 每个组件都有单一职责
2. **可扩展性**: 易于添加新工具、环境和基准测试
3. **可测试性**: 全面的测试框架
4. **模块化**: 组件可以独立使用
5. **一致性**: 所有组件间的统一接口

## 核心组件

### 1. 环境系统

环境系统为不同的智能体能力提供统一接口。

#### 基础环境类

```python
from envs import Environment

class CustomEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "custom"

    def _initialize_tools(self):
        # 在这里初始化你的工具
        self.register_tool(YourTool())
```

#### 内置环境

- **MathEnvironment**: 数学问题的计算器工具
- **PythonEnvironment**: 代码执行的 Python 解释器
- **WebEnvironment**: 网络搜索和浏览功能
- **RAGEnvironment**: 检索增强生成工具
- **DocEnvironment**: 文档理解与问答工具

### 2. 工具系统

工具是智能体能力的构建块。

#### 创建新工具

```python
from typing import Union, List, Dict, Any

class MyTool:
    name = "my_tool"
    description = "描述这个工具的功能"
    parameters = [
        {
            'name': 'input_param',
            'type': 'string',
            'description': '输入参数描述',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        # 你的工具逻辑在这里
        input_param = params.get("input_param")
        # 处理输入
        result = process_input(input_param)
        return result
```

#### 工具要求

1. **name**: 工具的唯一标识符
2. **description**: 人类可读的描述
3. **parameters**: 参数规范列表
4. **call()**: 主要执行方法

### 3. 基准测试系统

基准测试系统处理评估和测试。

#### 创建自定义基准测试

```python
from benchmark import Benchmark

class CustomBenchmark(Benchmark):
    def _parse_item(self, data: Dict[str, Any], line_num: int) -> BenchmarkItem:
        # 自定义解析逻辑
        return BenchmarkItem(
            id=data.get('custom_id'),
            question=data.get('query'),
            answer=data.get('response'),
            metadata={'line': line_num}
        )
```

#### 评估指标

内置指标：

- `exact_match`: 完全匹配
- `f1_score`: 基于词重叠的 F1 分数
- `similarity`: 字符串相似度
- `contains_answer`: 子字符串匹配
- `numeric_match`: 数值匹配

## 开发环境设置

### 前置条件

- Python 3.8+
- OpenAI API 密钥（完整功能需要）
- 可选：Serper API 密钥（网络搜索用）

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd AgentFlow

# 安装依赖
pip install -r requirements.txt

# 若使用 Doc Agent，参考 src/tools/mineru_vl_utils/pyproject.toml
pip install -U "mineru-vl-utils[transformers]"
# pip install -U "mineru-vl-utils[vllm]" # 可选

# 设置环境变量
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_URL="your-api-url"  # 可选
export SERPER_API_KEY="your-serper-key"  # 可选
```

### 项目结构

```
src/
├── envs/                  # 环境类
│   ├── environment.py     # 基础Environment + 实现
│   ├── example_usage.py   # 使用示例
│   └── __init__.py
├── tools/                 # 工具实现
│   ├── calculator.py      # 数学计算器
│   ├── web_search.py     # 网络搜索工具
│   ├── web_visit.py       # 网络浏览工具
│   ├── rag_tools.py       # RAG工具
|   ├── doc_tools.py        # 文档QA工具
|   ├── mineru_vl_utils     # MinerU2.5工具包
│   └── __init__.py
├── benchmark/             # 基准测试系统
│   ├── benchmark.py       # Benchmark类
│   ├── example_usage.py   # 使用示例
│   ├── integration_test.py # 集成测试
│   └── __init__.py
├── data/                  # 示例数据集
├── results/               # 输出文件
└── run.py                # 主执行脚本
```

## 添加新工具

### 步骤 1：创建工具类

```python
# src/tools/my_tool.py
from typing import Union, List, Dict, Any

class MyTool:
    name = "my_tool"
    description = "一个有用的工具"
    parameters = [
        {
            'name': 'input',
            'type': 'string',
            'description': '要处理的输入字符串',
            'required': True
        },
        {
            'name': 'options',
            'type': 'array',
            'array_type': 'string',
            'description': '可选配置',
            'required': False
        }
    ]

    def __init__(self, **kwargs):
        # 使用配置初始化
        self.config = kwargs

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            input_data = params.get("input")
            options = params.get("options", [])

            # 你的工具逻辑在这里
            result = self._process(input_data, options)
            return result

        except Exception as e:
            return f"错误: {str(e)}"

    def _process(self, input_data: str, options: List[str]) -> str:
        # 实现你的处理逻辑
        return f"已处理: {input_data}"
```

### 步骤 2：注册工具

```python
# src/tools/__init__.py
from .my_tool import MyTool

# 添加到导出
__all__ = [
    "CalculatorTool",
    "WebSearchTool",
    "WebVisitTool",
    "MyTool"  # 添加你的工具
]
```

### 步骤 3：创建环境

```python
# src/envs/environment.py
class MyEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "my_mode"

    def _initialize_tools(self):
        from tools.my_tool import MyTool
        self.register_tool(MyTool())
```

### 步骤 4：测试工具

```python
# test_my_tool.py
from tools.my_tool import MyTool

def test_my_tool():
    tool = MyTool()

    # 测试基本功能
    result = tool.call({"input": "test data"})
    assert "已处理: test data" in result

    # 测试带选项
    result = tool.call({
        "input": "test data",
        "options": ["option1", "option2"]
    })
    print(f"结果: {result}")

if __name__ == "__main__":
    test_my_tool()
```

## 创建新环境

### 步骤 1：定义环境类

```python
# src/envs/environment.py
class MyEnvironment(Environment):
    """特定用例的自定义环境。"""

    @property
    def mode(self) -> str:
        return "my_environment"

    def _initialize_tools(self):
        """初始化环境特定的工具。"""
        # 导入并注册你的工具
        from tools.my_tool import MyTool
        from tools.another_tool import AnotherTool

        self.register_tool(MyTool(config_param="value"))
        self.register_tool(AnotherTool())

    def custom_method(self):
        """添加此环境特定的自定义方法。"""
        pass
```

### 步骤 2：添加到工厂函数

```python
# src/envs/environment.py
def create_my_environment(**kwargs) -> MyEnvironment:
    """创建带有自定义工具的环境。"""
    return MyEnvironment(**kwargs)
```

### 步骤 3：更新主运行器

```python
# src/run.py
def setup_environment(self, mode: str, **kwargs) -> Environment:
    if mode == "my_environment":
        self.environment = MyEnvironment(**kwargs)
    # ... 其他模式
```

### 步骤 4：测试环境

```python
# test_my_environment.py
from envs import MyEnvironment

def test_my_environment():
    env = MyEnvironment()

    # 测试环境设置
    assert env.mode == "my_environment"
    assert len(env.list_tools()) > 0

    # 测试工具执行
    result = env.execute_tool("my_tool", {"input": "test"})
    print(f"工具结果: {result}")

if __name__ == "__main__":
    test_my_environment()
```

## 扩展基准测试

### 自定义数据格式

```python
# src/benchmark/benchmark.py
class CustomBenchmark(Benchmark):
    def _parse_item(self, data: Dict[str, Any], line_num: int) -> BenchmarkItem:
        """解析自定义数据格式。"""
        return BenchmarkItem(
            id=data.get('id', f'item_{line_num}'),
            question=data.get('question', ''),
            answer=data.get('answer', ''),
            metadata={
                'category': data.get('category'),
                'difficulty': data.get('difficulty'),
                'line': line_num
            }
        )
```

### 自定义评估指标

```python
# src/benchmark/benchmark.py
class CustomBenchmark(Benchmark):
    def _custom_metric(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """自定义评估指标。"""
        # 实现你的自定义逻辑
        return score

    def _get_metric_function(self, metric: str) -> Callable:
        """重写以添加自定义指标。"""
        if metric == "custom_metric":
            return self._custom_metric
        return super()._get_metric_function(metric)
```

### 自定义数据加载

```python
# src/benchmark/benchmark.py
class CustomBenchmark(Benchmark):
    def load_data(self, data_path: str):
        """重写自定义数据加载。"""
        if data_path.endswith('.csv'):
            self._load_csv(data_path)
        else:
            super().load_data(data_path)

    def _load_csv(self, file_path: str):
        """从CSV文件加载数据。"""
        import pandas as pd
        df = pd.read_csv(file_path)

        self.items = []
        for idx, row in df.iterrows():
            item = BenchmarkItem(
                id=row['id'],
                question=row['question'],
                answer=row['answer'],
                metadata=row.to_dict()
            )
            self.items.append(item)
```

## 测试

### 单元测试

```python
# tests/test_tools.py
import unittest
from tools.calculator import CalculatorTool

class TestCalculatorTool(unittest.TestCase):
    def setUp(self):
        self.tool = CalculatorTool()

    def test_basic_arithmetic(self):
        result = self.tool.call({"expressions": ["2+2"]})
        self.assertIn("4", result)

    def test_complex_expression(self):
        result = self.tool.call({"expressions": ["sqrt(16)"]})
        self.assertIn("4.0", result)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
# tests/test_integration.py
import unittest
from envs import MathEnvironment
from benchmark import create_benchmark

class TestIntegration(unittest.TestCase):
    def test_math_environment_with_benchmark(self):
        # 设置
        env = MathEnvironment()
        benchmark = create_benchmark("data/math_demo.jsonl")

        # 测试
        result = env.execute_tool("calculator", {"expressions": ["2+2"]})
        self.assertIsNotNone(result)

        # 评估
        predictions = {"aaa": result}
        results = benchmark.evaluate(predictions)
        self.assertEqual(len(results), 1)

if __name__ == '__main__':
    unittest.main()
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_tools.py

# 带覆盖率的测试
python -m pytest --cov=src tests/
```

## 贡献指南

### 开发工作流

1. **Fork 仓库**
2. **创建功能分支**
   ```bash
   git checkout -b feature/my-feature
   ```
3. **进行更改**
4. **添加测试**
5. **运行测试**
   ```bash
   python -m pytest tests/
   ```
6. **提交更改**
   ```bash
   git commit -m "添加我的功能"
   ```
7. **推送并创建 PR**

### 代码风格

- 遵循 PEP 8
- 使用类型提示
- 添加文档字符串
- 为新功能编写测试

### 拉取请求指南

1. **清晰的更改描述**
2. **新功能的测试**
3. **文档更新**
4. **向后兼容性考虑**

## 故障排除

### 常见问题

#### 1. 导入错误

```python
# 问题: ModuleNotFoundError
# 解决方案: 检查Python路径
import sys
sys.path.append('/path/to/AgentFlow/src')
```

#### 2. API 密钥问题

```python
# 问题: OpenAI API错误
# 解决方案: 检查环境变量
import os
print(os.environ.get("OPENAI_API_KEY"))
```

#### 3. 工具执行错误

```python
# 问题: 工具未找到
# 解决方案: 检查工具注册
env = MathEnvironment()
print(env.list_tools())  # 应该显示注册的工具
```

#### 4. 基准测试加载错误

```python
# 问题: 文件未找到
# 解决方案: 检查文件路径
import os
print(os.path.exists("data/math_demo.jsonl"))
```

### 调试模式

```python
# 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用调试输出运行
python src/run.py --mode math --data data/math_demo.jsonl
```

### 性能问题

1. **内存使用**: 在内存受限环境中使用`--max-workers 1`
2. **API 速率限制**: 在请求之间添加延迟
3. **大数据集**: 使用`--parallel`获得更好的性能

## 高级主题

### 自定义智能体运行器

```python
# src/run.py
class CustomAgentRunner(AgentRunner):
    def _run_conversation(self, question: str, task_id: str) -> List[Dict[str, Any]]:
        """重写自定义对话逻辑。"""
        # 你的自定义逻辑在这里
        pass
```

### 插件系统

```python
# src/plugins/plugin_manager.py
class PluginManager:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name: str, plugin):
        self.plugins[name] = plugin

    def execute_plugin(self, name: str, *args, **kwargs):
        if name in self.plugins:
            return self.plugins[name].execute(*args, **kwargs)
```

### 配置管理

```python
# src/config.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AgentConfig:
    model_name: str = "gpt-4"
    max_turns: int = 20
    custom_settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}
```

## 最佳实践

### 1. 工具开发

- **单一职责**: 每个工具应该做好一件事
- **错误处理**: 始终优雅地处理异常
- **文档**: 提供清晰的描述和示例
- **测试**: 编写全面的测试

### 2. 环境设计

- **一致性**: 遵循与内置环境相同的模式
- **配置**: 使环境可配置
- **可扩展性**: 为未来扩展而设计

### 3. 基准测试创建

- **数据质量**: 确保高质量的基准答案
- **多样性**: 包含多样化的测试用例
- **文档**: 记录数据格式和评估标准

### 4. 性能

- **分析**: 使用分析工具识别瓶颈
- **缓存**: 缓存昂贵的操作
- **并行化**: 在适当的地方使用并行处理

## 资源

- **文档**: [项目 README](README.md)
- **示例**: 查看示例文件
- **API 参考**: [代码文档](src/)
- **问题**: [GitHub Issues](https://github.com/your-repo/issues)

## 支持

如有问题和支持：

1. **查看文档**
2. **搜索现有问题**
3. **创建新问题**并提供详细信息
4. **加入社区**讨论

---

_本指南持续更新。请查看最新版本。_
