# AgentFlow Developer Guide

This comprehensive guide helps developers understand, extend, and contribute to the AgentFlow project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Adding New Tools](#adding-new-tools)
6. [Creating New Environments](#creating-new-environments)
7. [Extending Benchmarks](#extending-benchmarks)
8. [Testing](#testing)
9. [Contributing](#contributing)
10. [Troubleshooting](#troubleshooting)

## Project Overview

AgentFlow is a modular framework for building and evaluating AI agents with different capabilities. It provides:

- **Environment System**: Modular environments for different agent types (math, web, RAG, etc.)
- **Tool System**: Extensible tool framework for agent capabilities
- **Benchmark System**: Comprehensive evaluation framework
- **Unified Runner**: Single interface for running and evaluating agents

### Key Features

- 🏗️ **Modular Architecture**: Clean separation of concerns
- 🔧 **Extensible Tools**: Easy to add new capabilities
- 📊 **Comprehensive Evaluation**: Multiple metrics and benchmarks
- 🚀 **Unified Interface**: Single command for all operations
- 🧪 **Testing Framework**: Built-in testing and validation

## Architecture

```
AgentFlow/
├── src/
│   ├── envs/              # Environment classes
│   │   ├── environment.py  # Base Environment class
│   │   └── __init__.py
│   ├── tools/             # Tool implementations
│   │   ├── calculator.py
│   │   ├── web_search.py
│   │   ├── web_visit.py
│   │   ├── rag_tools.py
│   │   └── __init__.py
│   ├── benchmark/         # Benchmark system
│   │   ├── benchmark.py   # Benchmark class
│   │   └── __init__.py
│   ├── data/              # Sample datasets
│   ├── results/           # Output files
│   └── run.py            # Main execution script
├── requirements.txt
└── README.md
```

### Core Design Principles

1. **Separation of Concerns**: Each component has a single responsibility
2. **Extensibility**: Easy to add new tools, environments, and benchmarks
3. **Testability**: Comprehensive testing framework
4. **Modularity**: Components can be used independently
5. **Consistency**: Uniform interfaces across all components

## Core Components

### 1. Environment System

The Environment system provides a unified interface for different agent capabilities.

#### Base Environment Class

```python
from envs import Environment

class CustomEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "custom"

    def _initialize_tools(self):
        # Initialize your tools here
        self.register_tool(YourTool())
```

#### Built-in Environments

- **MathEnvironment**: Calculator tools for mathematical problems
- **PythonEnvironment**: Python interpreter for code execution
- **WebEnvironment**: Web search and browsing capabilities
- **RAGEnvironment**: Retrieval-augmented generation tools

### 2. Tool System

Tools are the building blocks of agent capabilities.

#### Creating a New Tool

```python
from typing import Union, List, Dict, Any

class MyTool:
    name = "my_tool"
    description = "Description of what this tool does"
    parameters = [
        {
            'name': 'input_param',
            'type': 'string',
            'description': 'Input parameter description',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        # Your tool logic here
        input_param = params.get("input_param")
        # Process the input
        result = process_input(input_param)
        return result
```

#### Tool Requirements

1. **name**: Unique identifier for the tool
2. **description**: Human-readable description
3. **parameters**: List of parameter specifications
4. **call()**: Main execution method

### 3. Benchmark System

The Benchmark system handles evaluation and testing.

#### Creating a Custom Benchmark

```python
from benchmark import Benchmark

class CustomBenchmark(Benchmark):
    def _parse_item(self, data: Dict[str, Any], line_num: int) -> BenchmarkItem:
        # Custom parsing logic
        return BenchmarkItem(
            id=data.get('custom_id'),
            question=data.get('query'),
            answer=data.get('response'),
            metadata={'line': line_num}
        )
```

#### Evaluation Metrics

Built-in metrics:

- `exact_match`: Exact string matching
- `f1_score`: F1 score based on word overlap
- `similarity`: String similarity
- `contains_answer`: Substring matching
- `numeric_match`: Numeric value matching

## Development Setup

### Prerequisites

- Python 3.8+
- OpenAI API key (for full functionality)
- Optional: Serper API key (for web search)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AgentFlow

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_URL="your-api-url"  # Optional
export SERPER_API_KEY="your-serper-key"  # Optional
```

### Project Structure

```
src/
├── envs/                  # Environment classes
│   ├── environment.py     # Base Environment + implementations
│   ├── example_usage.py  # Usage examples
│   └── __init__.py
├── tools/                 # Tool implementations
│   ├── calculator.py      # Math calculator
│   ├── web_search.py     # Web search tool
│   ├── web_visit.py      # Web browsing tool
│   ├── rag_tools.py      # RAG tools
│   └── __init__.py
├── benchmark/             # Benchmark system
│   ├── benchmark.py       # Benchmark class
│   ├── example_usage.py  # Usage examples
│   ├── integration_test.py # Integration tests
│   └── __init__.py
├── data/                  # Sample datasets
├── results/               # Output files
└── run.py                # Main execution script
```

## Adding New Tools

### Step 1: Create Tool Class

```python
# src/tools/my_tool.py
from typing import Union, List, Dict, Any

class MyTool:
    name = "my_tool"
    description = "A tool that does something useful"
    parameters = [
        {
            'name': 'input',
            'type': 'string',
            'description': 'Input string to process',
            'required': True
        },
        {
            'name': 'options',
            'type': 'array',
            'array_type': 'string',
            'description': 'Optional configuration',
            'required': False
        }
    ]

    def __init__(self, **kwargs):
        # Initialize with configuration
        self.config = kwargs

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            input_data = params.get("input")
            options = params.get("options", [])

            # Your tool logic here
            result = self._process(input_data, options)
            return result

        except Exception as e:
            return f"Error: {str(e)}"

    def _process(self, input_data: str, options: List[str]) -> str:
        # Implement your processing logic
        return f"Processed: {input_data}"
```

### Step 2: Register Tool

```python
# src/tools/__init__.py
from .my_tool import MyTool

# Add to exports
__all__ = [
    "CalculatorTool",
    "WebSearchTool",
    "WebVisitTool",
    "MyTool"  # Add your tool
]
```

### Step 3: Create Environment

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

### Step 4: Test Tool

```python
# test_my_tool.py
from tools.my_tool import MyTool

def test_my_tool():
    tool = MyTool()

    # Test basic functionality
    result = tool.call({"input": "test data"})
    assert "Processed: test data" in result

    # Test with options
    result = tool.call({
        "input": "test data",
        "options": ["option1", "option2"]
    })
    print(f"Result: {result}")

if __name__ == "__main__":
    test_my_tool()
```

## Creating New Environments

### Step 1: Define Environment Class

```python
# src/envs/environment.py
class MyEnvironment(Environment):
    """Custom environment for specific use cases."""

    @property
    def mode(self) -> str:
        return "my_environment"

    def _initialize_tools(self):
        """Initialize environment-specific tools."""
        # Import and register your tools
        from tools.my_tool import MyTool
        from tools.another_tool import AnotherTool

        self.register_tool(MyTool(config_param="value"))
        self.register_tool(AnotherTool())

    def custom_method(self):
        """Add custom methods specific to this environment."""
        pass
```

### Step 2: Add to Factory Functions

```python
# src/envs/environment.py
def create_my_environment(**kwargs) -> MyEnvironment:
    """Create a my environment with custom tools."""
    return MyEnvironment(**kwargs)
```

### Step 3: Update Main Runner

```python
# src/run.py
def setup_environment(self, mode: str, **kwargs) -> Environment:
    if mode == "my_environment":
        self.environment = MyEnvironment(**kwargs)
    # ... other modes
```

### Step 4: Test Environment

```python
# test_my_environment.py
from envs import MyEnvironment

def test_my_environment():
    env = MyEnvironment()

    # Test environment setup
    assert env.mode == "my_environment"
    assert len(env.list_tools()) > 0

    # Test tool execution
    result = env.execute_tool("my_tool", {"input": "test"})
    print(f"Tool result: {result}")

if __name__ == "__main__":
    test_my_environment()
```

## Extending Benchmarks

### Custom Data Formats

```python
# src/benchmark/benchmark.py
class CustomBenchmark(Benchmark):
    def _parse_item(self, data: Dict[str, Any], line_num: int) -> BenchmarkItem:
        """Parse custom data format."""
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

### Custom Evaluation Metrics

```python
# src/benchmark/benchmark.py
class CustomBenchmark(Benchmark):
    def _custom_metric(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """Custom evaluation metric."""
        # Implement your custom logic
        return score

    def _get_metric_function(self, metric: str) -> Callable:
        """Override to add custom metrics."""
        if metric == "custom_metric":
            return self._custom_metric
        return super()._get_metric_function(metric)
```

### Custom Data Loading

```python
# src/benchmark/benchmark.py
class CustomBenchmark(Benchmark):
    def load_data(self, data_path: str):
        """Override for custom data loading."""
        if data_path.endswith('.csv'):
            self._load_csv(data_path)
        else:
            super().load_data(data_path)

    def _load_csv(self, file_path: str):
        """Load data from CSV file."""
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

## Testing

### Unit Tests

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

### Integration Tests

```python
# tests/test_integration.py
import unittest
from envs import MathEnvironment
from benchmark import create_benchmark

class TestIntegration(unittest.TestCase):
    def test_math_environment_with_benchmark(self):
        # Setup
        env = MathEnvironment()
        benchmark = create_benchmark("data/math_demo.jsonl")

        # Test
        result = env.execute_tool("calculator", {"expressions": ["2+2"]})
        self.assertIsNotNone(result)

        # Evaluate
        predictions = {"aaa": result}
        results = benchmark.evaluate(predictions)
        self.assertEqual(len(results), 1)

if __name__ == '__main__':
    unittest.main()
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_tools.py

# Run with coverage
python -m pytest --cov=src tests/
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make changes**
4. **Add tests**
5. **Run tests**
   ```bash
   python -m pytest tests/
   ```
6. **Commit changes**
   ```bash
   git commit -m "Add my feature"
   ```
7. **Push and create PR**

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

### Pull Request Guidelines

1. **Clear description** of changes
2. **Tests** for new functionality
3. **Documentation** updates
4. **Backward compatibility** considerations

## Troubleshooting

### Common Issues

#### 1. Import Errors

```python
# Problem: ModuleNotFoundError
# Solution: Check Python path
import sys
sys.path.append('/path/to/AgentFlow/src')
```

#### 2. API Key Issues

```python
# Problem: OpenAI API errors
# Solution: Check environment variables
import os
print(os.environ.get("OPENAI_API_KEY"))
```

#### 3. Tool Execution Errors

```python
# Problem: Tool not found
# Solution: Check tool registration
env = MathEnvironment()
print(env.list_tools())  # Should show registered tools
```

#### 4. Benchmark Loading Errors

```python
# Problem: File not found
# Solution: Check file path
import os
print(os.path.exists("data/math_demo.jsonl"))
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
python src/run.py --mode math --data data/math_demo.jsonl
```

### Performance Issues

1. **Memory Usage**: Use `--max-workers 1` for memory-constrained environments
2. **API Rate Limits**: Add delays between requests
3. **Large Datasets**: Use `--parallel` for better performance

## Advanced Topics

### Custom Agent Runner

```python
# src/run.py
class CustomAgentRunner(AgentRunner):
    def _run_conversation(self, question: str, task_id: str) -> List[Dict[str, Any]]:
        """Override for custom conversation logic."""
        # Your custom logic here
        pass
```

### Plugin System

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

### Configuration Management

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

## Best Practices

### 1. Tool Development

- **Single Responsibility**: Each tool should do one thing well
- **Error Handling**: Always handle exceptions gracefully
- **Documentation**: Provide clear descriptions and examples
- **Testing**: Write comprehensive tests

### 2. Environment Design

- **Consistency**: Follow the same patterns as built-in environments
- **Configuration**: Make environments configurable
- **Extensibility**: Design for future extensions

### 3. Benchmark Creation

- **Data Quality**: Ensure high-quality ground truth
- **Diversity**: Include diverse test cases
- **Documentation**: Document data format and evaluation criteria

### 4. Performance

- **Profiling**: Use profiling tools to identify bottlenecks
- **Caching**: Cache expensive operations
- **Parallelization**: Use parallel processing where appropriate

## Resources

- **Documentation**: [Project README](README.md)
- **Examples**: [Usage Examples](src/envs/example_usage.py)
- **API Reference**: [Code Documentation](src/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## Support

For questions and support:

1. **Check the documentation**
2. **Search existing issues**
3. **Create a new issue** with detailed information
4. **Join the community** discussions

---

_This guide is continuously updated. Please check for the latest version._
