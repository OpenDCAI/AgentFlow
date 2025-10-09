# AgentFlow API Reference

Complete API documentation for all AgentFlow components.

## Table of Contents

1. [Environment System](#environment-system)
2. [Tool System](#tool-system)
3. [Benchmark System](#benchmark-system)
4. [Agent Runner](#agent-runner)
5. [Command Line Interface](#command-line-interface)

## Environment System

### Base Environment Class

```python
class Environment(ABC):
    """Abstract base class for agent environments."""

    def __init__(self, model_name: str = "gpt-4.1-2025-04-14",
                 openai_api_key: Optional[str] = None,
                 openai_api_url: Optional[str] = None, **kwargs)

    @property
    @abstractmethod
    def mode(self) -> str:
        """Return the environment mode name."""

    @abstractmethod
    def _initialize_tools(self):
        """Initialize tools specific to this environment."""

    def register_tool(self, tool: Tool):
        """Register a tool in the environment."""

    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the environment."""

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""

    def list_tools(self) -> List[str]:
        """List all registered tool names."""

    def execute_tool(self, tool_name: str, params: Union[str, dict], **kwargs) -> str:
        """Execute a tool with given parameters."""

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas for OpenAI function calling."""

    def get_tool_descriptions(self) -> str:
        """Get tool descriptions for system prompts."""

    def update_config(self, **kwargs):
        """Update environment configuration."""

    def get_config(self, key: str = None):
        """Get configuration value(s)."""

    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information."""

    def save_environment(self, filepath: str):
        """Save environment configuration to file."""

    def load_environment(self, filepath: str):
        """Load environment configuration from file."""
```

### Concrete Environment Classes

#### MathEnvironment

```python
class MathEnvironment(Environment):
    """Math environment with calculator tools."""

    @property
    def mode(self) -> str:
        return "math"

    def _initialize_tools(self):
        """Initialize math-specific tools."""
        self.register_tool(CalculatorTool())
```

#### PythonEnvironment

```python
class PythonEnvironment(Environment):
    """Python environment with interpreter tools."""

    @property
    def mode(self) -> str:
        return "py"

    def _initialize_tools(self):
        """Initialize Python-specific tools."""
        from tools.python_interpreter import PythonInterpreterTool
        self.register_tool(PythonInterpreterTool())
```

#### WebEnvironment

```python
class WebEnvironment(Environment):
    """Web environment with search and visit tools."""

    @property
    def mode(self) -> str:
        return "web"

    def _initialize_tools(self):
        """Initialize web-specific tools."""
        web_search_config = {
            "top_k": self.config.get("web_search_top_k", 5),
            "search_type": self.config.get("web_search_type", "search"),
            "max_workers": self.config.get("web_search_max_workers", 5)
        }

        web_visit_config = {
            "summary_model": self.config.get("web_visit_summary_model", "gpt-4.1-2025-04-14")
        }

        self.register_tool(WebSearchTool(**web_search_config))
        self.register_tool(WebVisitTool(**web_visit_config))
```

#### RAGEnvironment

```python
class RAGEnvironment(Environment):
    """RAG environment with retrieval tools."""

    @property
    def mode(self) -> str:
        return "rag"

    def _initialize_tools(self):
        """Initialize RAG-specific tools."""
        from tools.rag_tools import QueryRAGIndexTool
        self.register_tool(QueryRAGIndexTool())
```

### Convenience Functions

```python
def create_math_environment(**kwargs) -> MathEnvironment:
    """Create a math environment with calculator tools."""

def create_python_environment(**kwargs) -> PythonEnvironment:
    """Create a Python environment with interpreter tools."""

def create_rag_environment(**kwargs) -> RAGEnvironment:
    """Create a RAG environment with retrieval tools."""

def create_web_environment(**kwargs) -> WebEnvironment:
    """Create a web environment with search and visit tools."""
```

## Tool System

### Base Tool Interface

```python
class Tool(ABC):
    """Abstract base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""

    @property
    @abstractmethod
    def parameters(self) -> List[Dict[str, Any]]:
        """Tool parameters schema."""

    @abstractmethod
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the tool with given parameters."""
```

### Built-in Tools

#### CalculatorTool

```python
class CalculatorTool:
    name = "calculator"
    description = "A simple calculator tool: supports basic arithmetic operations"
    parameters = [
        {
            'name': 'expressions',
            'type': 'array',
            'array_type': 'string',
            'description': 'An array of mathematical expressions to evaluate',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute calculator with given expressions."""
```

#### WebSearchTool

```python
class WebSearchTool:
    name = "web_search"
    description = "A web search tool powered by Serper API"
    parameters = [
        {
            'name': 'queries',
            'type': 'array',
            'array_type': 'string',
            'description': 'Array of search queries to execute in parallel',
            'required': True
        }
    ]

    def __init__(self, top_k=3, search_type="search", max_workers=5):
        """Initialize with configuration."""

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute web search with given queries."""
```

#### WebVisitTool

```python
class WebVisitTool:
    name = "web_visit"
    description = "A web page visiting and content extraction tool"
    parameters = [
        {
            'name': 'urls',
            'type': 'array',
            'array_type': 'string',
            'description': 'Array of URLs to visit and extract content from',
            'required': True
        },
        {
            'name': 'goal',
            'type': 'string',
            'description': 'The goal or purpose for content extraction',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Visit URLs and extract content."""
```

## Benchmark System

### Benchmark Class

```python
class Benchmark:
    """Main benchmark class for loading and evaluating datasets."""

    def __init__(self, data_path: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None)

    def load_data(self, data_path: str):
        """Load benchmark data from a file."""

    def get_item(self, item_id: str) -> Optional[BenchmarkItem]:
        """Get a specific item by ID."""

    def get_items(self) -> List[BenchmarkItem]:
        """Get all items."""

    def get_questions(self) -> List[str]:
        """Get all questions."""

    def get_answers(self) -> List[str]:
        """Get all ground truth answers."""

    def evaluate(self, predictions: Union[Dict[str, str], List[str]],
                 metric: str = "exact_match", **kwargs) -> List[EvaluationResult]:
        """Evaluate predictions against ground truth."""

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the benchmark."""

    def save_results(self, file_path: str):
        """Save evaluation results to a file."""

    def load_results(self, file_path: str):
        """Load evaluation results from a file."""
```

### Data Structures

#### BenchmarkItem

```python
@dataclass
class BenchmarkItem:
    """Represents a single benchmark item with question and answer."""
    id: str
    question: str
    answer: str
    metadata: Optional[Dict[str, Any]] = None
```

#### EvaluationResult

```python
@dataclass
class EvaluationResult:
    """Represents the result of evaluating a prediction against ground truth."""
    item_id: str
    question: str
    ground_truth: str
    prediction: str
    score: float
    metric_name: str
    details: Optional[Dict[str, Any]] = None
```

### Evaluation Metrics

#### Built-in Metrics

```python
# Exact match
benchmark.evaluate(predictions, metric="exact_match")

# F1 score
benchmark.evaluate(predictions, metric="f1_score")

# String similarity
benchmark.evaluate(predictions, metric="similarity")

# Contains answer
benchmark.evaluate(predictions, metric="contains_answer")

# Numeric match
benchmark.evaluate(predictions, metric="numeric_match")

# BLEU score
benchmark.evaluate(predictions, metric="bleu_score")

# ROUGE score
benchmark.evaluate(predictions, metric="rouge_score")
```

### Convenience Functions

```python
def create_benchmark(data_path: str, name: Optional[str] = None,
                    description: Optional[str] = None) -> Benchmark:
    """Create a benchmark from a data file."""
```

## Agent Runner

### AgentConfig

```python
@dataclass
class AgentConfig:
    """Configuration for agent execution."""
    model_name: str = "gpt-4.1-2025-04-14"
    max_turns: int = 20
    max_retries: int = 3
    max_workers: int = 1
    save_results: bool = True
    evaluate_results: bool = True
    evaluation_metric: str = "exact_match"
```

### AgentRunner

```python
class AgentRunner:
    """Main agent runner that coordinates Environment and Benchmark."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent runner."""

    def setup_environment(self, mode: str, **kwargs) -> Environment:
        """Setup environment based on mode."""

    def load_benchmark(self, data_path: str, name: Optional[str] = None, **kwargs) -> Benchmark:
        """Load benchmark from data file."""

    def run_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent on a single task."""

    def run_benchmark(self, parallel: bool = False) -> List[Dict[str, Any]]:
        """Run agent on all benchmark tasks."""

    def evaluate_results(self) -> Dict[str, Any]:
        """Evaluate results against benchmark ground truth."""

    def save_results(self, output_dir: str = "results") -> str:
        """Save results to files."""

    def run(self, mode: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """Complete run pipeline."""
```

## Command Line Interface

### Basic Usage

```bash
python src/run.py --mode <environment> --data <data_file> [options]
```

### Required Arguments

- `--mode`: Environment type (`math`, `py`, `rag`, `web`)
- `--data`: Path to benchmark data file

### Optional Arguments

#### General Options

- `--model`: OpenAI model name (default: `gpt-4.1-2025-04-14`)
- `--max-turns`: Maximum conversation turns (default: 20)
- `--max-retries`: Maximum retries per turn (default: 3)
- `--max-workers`: Maximum parallel workers (default: 1)
- `--output-dir`: Output directory for results (default: `results`)
- `--no-eval`: Skip evaluation
- `--no-save`: Skip saving results
- `--parallel`: Run tasks in parallel
- `--metric`: Evaluation metric (default: `exact_match`)

#### Environment-Specific Options

##### Web Environment

- `--web-search-top-k`: Number of search results (default: 5)
- `--web-search-type`: Search type (`search`, `news`, `images`)

##### RAG Environment

- `--kb-path`: Path to knowledge base file

### Examples

```bash
# Basic math benchmark
python src/run.py --mode math --data src/data/math_demo.jsonl

# Web search with custom settings
python src/run.py --mode web --data src/data/webagent_demo.jsonl \
  --web-search-top-k 10 --web-search-type news

# Parallel execution
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --parallel --max-workers 4

# Custom model and evaluation
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --model gpt-4 --metric f1_score

# Skip evaluation and saving
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --no-eval --no-save
```

## Error Handling

### Common Exceptions

```python
# API Key not set
ValueError: OPENAI_API_KEY is not set

# File not found
FileNotFoundError: Data file not found: path/to/file

# Tool not found
ValueError: Tool 'tool_name' not found

# Invalid metric
ValueError: Unknown metric: invalid_metric
```

### Error Recovery

```python
try:
    result = runner.run("math", "data/math_demo.jsonl")
except ValueError as e:
    print(f"Configuration error: {e}")
except FileNotFoundError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Memory Usage

- Use `--max-workers 1` for memory-constrained environments
- Consider data size when loading large benchmarks

### API Rate Limits

- Add delays between requests for high-volume usage
- Use `--max-retries` to handle temporary failures

### Parallel Execution

- Use `--parallel` for CPU-bound tasks
- Adjust `--max-workers` based on system capabilities

## Best Practices

### Tool Development

1. **Single Responsibility**: Each tool should do one thing well
2. **Error Handling**: Always handle exceptions gracefully
3. **Documentation**: Provide clear descriptions and examples
4. **Testing**: Write comprehensive tests

### Environment Design

1. **Consistency**: Follow the same patterns as built-in environments
2. **Configuration**: Make environments configurable
3. **Extensibility**: Design for future extensions

### Benchmark Creation

1. **Data Quality**: Ensure high-quality ground truth
2. **Diversity**: Include diverse test cases
3. **Documentation**: Document data format and evaluation criteria

---

_This API reference is continuously updated. Please check for the latest version._
