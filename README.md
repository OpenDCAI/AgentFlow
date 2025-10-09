# AgentFlow

A modular framework for building and evaluating AI agents with different capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys
export OPENAI_API_KEY="your-api-key"

# Run your first agent
python src/run.py --mode math --data src/data/math_demo.jsonl
```

## 📚 Documentation

### English

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Comprehensive development documentation
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Run Usage Guide](RUN_USAGE.md)** - Detailed usage instructions

### 中文

- **[快速入门指南](QUICKSTART_CN.md)** - 5 分钟快速上手
- **[开发者指南](DEVELOPER_GUIDE_CN.md)** - 全面开发文档
- **[API 参考](API_REFERENCE_CN.md)** - 完整 API 文档
- **[运行使用指南](RUN_USAGE_CN.md)** - 详细使用说明
- **[文档索引](DOCS_INDEX_CN.md)** - 中文文档导航

## 🏗️ Architecture

AgentFlow provides a modular architecture with three core components:

### Environment System

- **MathEnvironment**: Calculator tools for mathematical problems
- **PythonEnvironment**: Python interpreter for code execution
- **WebEnvironment**: Web search and browsing capabilities
- **RAGEnvironment**: Retrieval-augmented generation tools

### Tool System

- **Extensible**: Easy to add new capabilities
- **Modular**: Each tool has a single responsibility
- **Testable**: Built-in testing framework

### Benchmark System

- **Multiple Formats**: JSON, JSONL support
- **Various Metrics**: Exact match, F1, similarity, etc.
- **Flexible Evaluation**: Custom metrics and evaluation logic

## 🛠️ Features

- 🏗️ **Modular Architecture**: Clean separation of concerns
- 🔧 **Extensible Tools**: Easy to add new capabilities
- 📊 **Comprehensive Evaluation**: Multiple metrics and benchmarks
- 🚀 **Unified Interface**: Single command for all operations
- 🧪 **Testing Framework**: Built-in testing and validation
- 🔄 **Parallel Execution**: Support for parallel task processing
- 💾 **Result Management**: Automatic saving and loading of results

## 📖 Usage Examples

### Command Line Interface

```bash
# Math agent
python src/run.py --mode math --data src/data/math_demo.jsonl

# Web agent with custom settings
python src/run.py --mode web --data src/data/webagent_demo.jsonl \
  --web-search-top-k 10 --web-search-type news

# Parallel execution
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --parallel --max-workers 4
```

### Programmatic Usage

```python
from run import AgentRunner, AgentConfig
from envs import MathEnvironment
from benchmark import create_benchmark

# Create configuration
config = AgentConfig(
    model_name="gpt-4",
    max_turns=10,
    evaluate_results=True
)

# Create and run agent
runner = AgentRunner(config)
runner.setup_environment("math")
runner.load_benchmark("src/data/math_demo.jsonl")
results = runner.run_benchmark()
```

### Adding Custom Tools

```python
# src/tools/my_tool.py
class MyTool:
    name = "my_tool"
    description = "A custom tool"
    parameters = [
        {
            'name': 'input',
            'type': 'string',
            'description': 'Input to process',
            'required': True
        }
    ]

    def call(self, params, **kwargs):
        input_text = params.get("input", "")
        return f"Processed: {input_text.upper()}"
```

### Creating Custom Environments

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

## 🧪 Testing

```bash
# Run all tests
python src/test_new_run.py

# Test specific components
python -m pytest tests/

# Integration tests
python src/benchmark/integration_test.py
```

## 📊 Built-in Benchmarks

- **Math Demo**: Mathematical calculation problems
- **Python Interpreter Demo**: Code execution tasks
- **Web Agent Demo**: Web search and information retrieval
- **RAG Demo**: Knowledge base question answering

## 🔧 Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_API_URL="your-openai-api-url"  # Optional
export SERPER_API_KEY="your-serper-key"      # Optional for web search
```

### Command Line Options

```bash
# Model selection
--model gpt-4

# Execution control
--max-turns 20 --max-retries 3

# Parallel processing
--parallel --max-workers 4

# Evaluation
--metric exact_match --no-eval

# Output
--output-dir results --no-save
```

## 🏗️ Project Structure

```
AgentFlow/
├── src/
│   ├── envs/              # Environment classes
│   │   ├── environment.py # Base Environment + implementations
│   │   └── example_usage.py
│   ├── tools/             # Tool implementations
│   │   ├── calculator.py
│   │   ├── web_search.py
│   │   ├── web_visit.py
│   │   └── rag_tools.py
│   ├── benchmark/         # Benchmark system
│   │   ├── benchmark.py
│   │   └── integration_test.py
│   ├── data/              # Sample datasets
│   ├── results/           # Output files
│   └── run.py            # Main execution script
├── requirements.txt
├── README.md
├── QUICKSTART.md
├── DEVELOPER_GUIDE.md
├── API_REFERENCE.md
└── RUN_USAGE.md
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the guides above
- **Issues**: Create a GitHub issue
- **Community**: Join discussions

## 🎯 Roadmap

- [ ] Additional environment types
- [ ] More evaluation metrics
- [ ] Plugin system
- [ ] Web interface
- [ ] Distributed execution

---

_Built with ❤️ for the AI community_
