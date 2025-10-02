# AgentFlow Run Script Usage

This document describes how to use the new `run.py` script that integrates the Environment and Benchmark modules.

## Overview

The new `run.py` script provides a unified interface for running agents on different benchmarks using the Environment and Benchmark classes. It replaces the old mode-based approach with a more modular and extensible architecture.

## Key Features

- **Unified Interface**: Single script for all environment types
- **Modular Architecture**: Uses Environment and Benchmark classes
- **Flexible Configuration**: Extensive command-line options
- **Built-in Evaluation**: Automatic evaluation with multiple metrics
- **Parallel Execution**: Support for parallel task processing
- **Result Management**: Automatic saving and loading of results

## Basic Usage

### Command Line Interface

```bash
python src/run.py --mode <environment_type> --data <data_path> [options]
```

### Required Arguments

- `--mode`: Environment type (`math`, `py`, `rag`, `web`)
- `--data`: Path to benchmark data file

### Optional Arguments

- `--model`: OpenAI model name (default: `gpt-4.1-2025-04-14`)
- `--max-turns`: Maximum conversation turns (default: 20)
- `--max-retries`: Maximum retries per turn (default: 3)
- `--max-workers`: Maximum parallel workers (default: 1)
- `--output-dir`: Output directory for results (default: `results`)
- `--no-eval`: Skip evaluation
- `--no-save`: Skip saving results
- `--parallel`: Run tasks in parallel
- `--metric`: Evaluation metric (default: `exact_match`)

## Examples

### Math Environment

```bash
# Basic math benchmark
python src/run.py --mode math --data src/data/math_demo.jsonl

# With custom model and evaluation
python src/run.py --mode math --data src/data/math_demo.jsonl --model gpt-4 --metric f1_score

# Parallel execution
python src/run.py --mode math --data src/data/math_demo.jsonl --parallel --max-workers 4
```

### Python Environment

```bash
# Python interpreter benchmark
python src/run.py --mode py --data src/data/python_interpreter_demo.jsonl

# With custom configuration
python src/run.py --mode py --data src/data/python_interpreter_demo.jsonl --max-turns 10
```

### Web Environment

```bash
# Web agent benchmark
python src/run.py --mode web --data src/data/webagent_demo.jsonl

# With web-specific options
python src/run.py --mode web --data src/data/webagent_demo.jsonl \
  --web-search-top-k 10 --web-search-type news
```

### RAG Environment

```bash
# RAG benchmark with knowledge base
python src/run.py --mode rag --data src/data/rag_queries.jsonl --kb-path src/data/knowledge_base.json
```

## Configuration

### Environment-Specific Options

#### Web Environment

- `--web-search-top-k`: Number of search results (default: 5)
- `--web-search-type`: Search type (`search`, `news`, `images`)

#### RAG Environment

- `--kb-path`: Path to knowledge base file

### Evaluation Metrics

Available metrics:

- `exact_match`: Exact string matching
- `f1_score`: F1 score based on word overlap
- `similarity`: String similarity using difflib
- `contains_answer`: Check if prediction contains ground truth
- `numeric_match`: Extract and compare numeric values

## Output

### Result Files

The script generates several output files:

1. **Result File**: `results/result_<benchmark_name>.jsonl`

   - Contains conversation logs and final answers
   - One JSON object per line

2. **Evaluation File**: `results/evaluation_<benchmark_name>.json`
   - Contains evaluation results and metrics
   - Detailed analysis of performance

### Result Format

```json
{
  "task_id": "item_1",
  "question": "What is 2+2?",
  "answer": "The answer is 4.",
  "messages": [...],
  "success": true,
  "error": null
}
```

## Programmatic Usage

### Using AgentRunner Class

```python
from run import AgentRunner, AgentConfig
from envs import MathEnvironment
from benchmark import create_benchmark

# Create configuration
config = AgentConfig(
    model_name="gpt-4",
    max_turns=10,
    evaluate_results=True,
    evaluation_metric="f1_score"
)

# Create runner
runner = AgentRunner(config)

# Setup environment
runner.setup_environment("math")

# Load benchmark
runner.load_benchmark("data/math_demo.jsonl")

# Run benchmark
results = runner.run_benchmark(parallel=True)

# Evaluate results
evaluation = runner.evaluate_results()

# Save results
runner.save_results("output/")
```

### Custom Environment Integration

```python
from run import AgentRunner, AgentConfig
from envs import MathEnvironment

# Create custom environment
env = MathEnvironment(model_name="gpt-4")

# Create runner with custom environment
runner = AgentRunner(AgentConfig())
runner.environment = env

# Continue with normal workflow...
```

## Error Handling

The script includes comprehensive error handling:

- **API Errors**: Automatic retries with exponential backoff
- **Tool Errors**: Graceful handling of tool execution failures
- **Data Errors**: Validation of input data and file formats
- **Configuration Errors**: Clear error messages for invalid options

## Performance Tips

1. **Parallel Execution**: Use `--parallel` for large datasets
2. **Worker Count**: Adjust `--max-workers` based on your system
3. **Turn Limits**: Set appropriate `--max-turns` for your use case
4. **Evaluation**: Use `--no-eval` for faster execution during development

## Troubleshooting

### Common Issues

1. **API Key Not Set**

   ```
   Warning: OPENAI_API_KEY is not set
   ```

   Solution: Set the `OPENAI_API_KEY` environment variable

2. **File Not Found**

   ```
   FileNotFoundError: Data file not found
   ```

   Solution: Check the data file path

3. **Tool Execution Errors**
   ```
   Error: Tool calculator not found
   ```
   Solution: Ensure the environment is properly set up

### Debug Mode

For debugging, you can modify the script to add more verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Old Script

The new script is backward compatible with the old command-line interface:

### Old Command

```bash
python src/run.py --mode math --data math_demo
```

### New Command

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl
```

Key differences:

- Data path now includes full file path
- More configuration options available
- Better error handling and logging
- Integrated evaluation and result management
