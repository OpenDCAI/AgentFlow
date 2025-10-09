# AgentFlow Quick Start Guide

Get up and running with AgentFlow in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_API_URL="your-openai-api-url"  # Optional
export SERPER_API_KEY="your-serper-key"      # Optional for web search
```

### 3. Run Your First Agent

```bash
# Math agent
python src/run.py --mode math --data src/data/math_demo.jsonl

# Web agent
python src/run.py --mode web --data src/data/webagent_demo.jsonl
```

## 📚 Basic Usage

### Command Line Interface

```bash
# Basic syntax
python src/run.py --mode <environment> --data <data_file> [options]

# Examples
python src/run.py --mode math --data src/data/math_demo.jsonl --model gpt-4
python src/run.py --mode web --data src/data/webagent_demo.jsonl --parallel
python src/run.py --mode py --data src/data/python_interpreter_demo.jsonl --no-eval
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

## 🛠️ Adding Your First Tool

### 1. Create Tool File

```python
# src/tools/my_tool.py
class MyTool:
    name = "my_tool"
    description = "A simple example tool"
    parameters = [
        {
            'name': 'input',
            'type': 'string',
            'description': 'Input text to process',
            'required': True
        }
    ]

    def call(self, params, **kwargs):
        input_text = params.get("input", "")
        return f"Processed: {input_text.upper()}"
```

### 2. Register Tool

```python
# src/tools/__init__.py
from .my_tool import MyTool
```

### 3. Create Environment

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

### 4. Test Your Tool

```python
# test_my_tool.py
from envs import MyEnvironment

env = MyEnvironment()
result = env.execute_tool("my_tool", {"input": "hello world"})
print(result)  # Output: "Processed: HELLO WORLD"
```

## 📊 Creating Your First Benchmark

### 1. Create Data File

```jsonl
{"id": "q1", "question": "What is 2+2?", "answer": "4"}
{"id": "q2", "question": "What is 3*3?", "answer": "9"}
```

### 2. Run Benchmark

```bash
python src/run.py --mode math --data my_benchmark.jsonl
```

### 3. View Results

```bash
# Results are saved to results/result_my_benchmark.jsonl
cat results/result_my_benchmark.jsonl
```

## 🔧 Common Tasks

### Run with Different Models

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --model gpt-3.5-turbo
```

### Parallel Execution

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --parallel --max-workers 4
```

### Skip Evaluation

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --no-eval
```

### Custom Output Directory

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --output-dir my_results
```

## 🧪 Testing Your Setup

### 1. Test Basic Functionality

```bash
python src/test_new_run.py
```

### 2. Test Specific Components

```python
# Test environment
from envs import MathEnvironment
env = MathEnvironment()
print(env.list_tools())

# Test benchmark
from benchmark import create_benchmark
benchmark = create_benchmark("src/data/math_demo.jsonl")
print(f"Loaded {len(benchmark.items)} items")
```

### 3. Test Tool Execution

```python
from envs import MathEnvironment

env = MathEnvironment()
result = env.execute_tool("calculator", {"expressions": ["2+2"]})
print(result)
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Set**

   ```
   Warning: OPENAI_API_KEY is not set
   ```

   Solution: Set the environment variable

2. **File Not Found**

   ```
   FileNotFoundError: Data file not found
   ```

   Solution: Check the file path

3. **Tool Not Found**
   ```
   Error: Tool calculator not found
   ```
   Solution: Ensure environment is properly set up

### Debug Mode

```bash
# Enable verbose output
python src/run.py --mode math --data src/data/math_demo.jsonl --max-turns 5
```

## 📖 Next Steps

1. **Read the full documentation**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
2. **Explore examples**: Check `src/envs/example_usage.py`
3. **Run integration tests**: `python src/benchmark/integration_test.py`
4. **Create your own tools**: Follow the tool development guide
5. **Build custom environments**: See environment creation examples

## 🆘 Need Help?

- **Documentation**: Check the full developer guide
- **Examples**: Look at the example files
- **Issues**: Create a GitHub issue with details
- **Community**: Join discussions and ask questions

---

_Happy coding with AgentFlow! 🎉_
