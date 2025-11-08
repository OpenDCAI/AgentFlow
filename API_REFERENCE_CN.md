# AgentFlow API 参考

AgentFlow 所有组件的完整 API 文档。

## 目录

1. [环境系统](#环境系统)
2. [工具系统](#工具系统)
3. [基准测试系统](#基准测试系统)
4. [智能体运行器](#智能体运行器)
5. [命令行界面](#命令行界面)

## 环境系统

### 基础环境类

```python
class Environment(ABC):
    """智能体环境的抽象基类。"""

    def __init__(self, model_name: str = "gpt-4.1-2025-04-14",
                 openai_api_key: Optional[str] = None,
                 openai_api_url: Optional[str] = None, **kwargs)

    @property
    @abstractmethod
    def mode(self) -> str:
        """返回环境模式名称。"""

    @abstractmethod
    def _initialize_tools(self):
        """初始化此环境特定的工具。"""

    def register_tool(self, tool: Tool):
        """在环境中注册工具。"""

    def unregister_tool(self, tool_name: str):
        """从环境中注销工具。"""

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """按名称获取工具。"""

    def list_tools(self) -> List[str]:
        """列出所有注册的工具名称。"""

    def execute_tool(self, tool_name: str, params: Union[str, dict], **kwargs) -> str:
        """使用给定参数执行工具。"""

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """获取OpenAI函数调用的工具模式。"""

    def get_tool_descriptions(self) -> str:
        """获取系统提示的工具描述。"""

    def update_config(self, **kwargs):
        """更新环境配置。"""

    def get_config(self, key: str = None):
        """获取配置值。"""

    def get_environment_info(self) -> Dict[str, Any]:
        """获取全面的环境信息。"""

    def save_environment(self, filepath: str):
        """保存环境配置到文件。"""

    def load_environment(self, filepath: str):
        """从文件加载环境配置。"""
```

### 具体环境类

#### MathEnvironment

```python
class MathEnvironment(Environment):
    """带有计算器工具的数学环境。"""

    @property
    def mode(self) -> str:
        return "math"

    def _initialize_tools(self):
        """初始化数学特定工具。"""
        self.register_tool(CalculatorTool())
```

#### PythonEnvironment

```python
class PythonEnvironment(Environment):
    """带有解释器工具的Python环境。"""

    @property
    def mode(self) -> str:
        return "py"

    def _initialize_tools(self):
        """初始化Python特定工具。"""
        from tools.python_interpreter import PythonInterpreterTool
        self.register_tool(PythonInterpreterTool())
```

#### WebEnvironment

```python
class WebEnvironment(Environment):
    """带有搜索和访问工具的Web环境。"""

    @property
    def mode(self) -> str:
        return "web"

    def _initialize_tools(self):
        """初始化Web特定工具。"""
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
    """带有检索工具的RAG环境。"""

    @property
    def mode(self) -> str:
        return "rag"

    def _initialize_tools(self):
        """初始化RAG特定工具。"""
        from tools.rag_tools import QueryRAGIndexTool
        self.register_tool(QueryRAGIndexTool())
```

#### DocEnvironment

```python
class DocEnvironment(Environment):
    """带有解析检查、文档解析、关键词检索、多模态分析等的Doc环境。"""
    @property
    def mode(self) -> str:
        return "doc"
    
    def _initialize_tools(self):
        """初始化Doc特定工具。""""
        
        self.register_tool(DocCheckTool())
        ocr_tool = DocOCRTool(
            model_path=self.config.get("ocr_model_path"), 
            backend_type=self.config.get("ocr_backend_type", "transformers")
        )
        self.register_tool(ocr_tool)
        self.register_tool(SearchKeywordTool())
        self.register_tool(GetPageOCRTool())
        self.register_tool(GetPageImageTool())
        self.register_tool(CropImageTool())
        api_key = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY") or None
        if api_key and api_key.strip():
            api_key = api_key.strip()
        else:
            api_key = None
        api_base = (self.config.get("openai_api_url") or 
                   os.environ.get("OPENAI_API_BASE") or 
                   os.environ.get("OPENAI_API_URL") or None)
        if api_base and api_base.strip():
            api_base = api_base.strip()
        else:
            api_base = None
        image_desc_tool = ImageDescriptionTool(
            model_name="gpt-4o",
            api_key=api_key,
            api_base=api_base
        )
        self.register_tool(image_desc_tool)

```


### 便利函数

```python
def create_math_environment(**kwargs) -> MathEnvironment:
    """创建带有计算器工具的数学环境。"""

def create_python_environment(**kwargs) -> PythonEnvironment:
    """创建带有解释器工具的Python环境。"""

def create_rag_environment(**kwargs) -> RAGEnvironment:
    """创建带有检索工具的RAG环境。"""

def create_web_environment(**kwargs) -> WebEnvironment:
    """创建带有搜索和访问工具的Web环境。"""

def create_doc_environment(**kwargs) -> DocEnvironment:
    """创建带有解析检查、文档解析、关键词检索、多模态分析等的Doc环境。"""
```

## 工具系统

### 基础工具接口

```python
class Tool(ABC):
    """所有工具的抽象基类。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称。"""

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述。"""

    @property
    @abstractmethod
    def parameters(self) -> List[Dict[str, Any]]:
        """工具参数模式。"""

    @abstractmethod
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """使用给定参数执行工具。"""
```

### 内置工具

#### CalculatorTool

```python
class CalculatorTool:
    name = "calculator"
    description = "一个简单的计算器工具：支持基本算术运算"
    parameters = [
        {
            'name': 'expressions',
            'type': 'array',
            'array_type': 'string',
            'description': '要评估的数学表达式数组',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """使用给定表达式执行计算器。"""
```

#### WebSearchTool

```python
class WebSearchTool:
    name = "web_search"
    description = "由Serper API驱动的网络搜索工具"
    parameters = [
        {
            'name': 'queries',
            'type': 'array',
            'array_type': 'string',
            'description': '并行执行的搜索查询数组',
            'required': True
        }
    ]

    def __init__(self, top_k=3, search_type="search", max_workers=5):
        """使用配置初始化。"""

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """使用给定查询执行网络搜索。"""
```

#### WebVisitTool

```python
class WebVisitTool:
    name = "web_visit"
    description = "网页访问和内容提取工具"
    parameters = [
        {
            'name': 'urls',
            'type': 'array',
            'array_type': 'string',
            'description': '要访问和提取内容的URL数组',
            'required': True
        },
        {
            'name': 'goal',
            'type': 'string',
            'description': '内容提取的目标或目的',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """访问URL并提取内容。"""
```

## 基准测试系统

### Benchmark 类

```python
class Benchmark:
    """用于加载和评估数据集的主基准测试类。"""

    def __init__(self, data_path: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None)

    def load_data(self, data_path: str):
        """从文件加载基准测试数据。"""

    def get_item(self, item_id: str) -> Optional[BenchmarkItem]:
        """按ID获取特定项目。"""

    def get_items(self) -> List[BenchmarkItem]:
        """获取所有项目。"""

    def get_questions(self) -> List[str]:
        """获取所有问题。"""

    def get_answers(self) -> List[str]:
        """获取所有基准答案。"""

    def evaluate(self, predictions: Union[Dict[str, str], List[str]],
                 metric: str = "exact_match", **kwargs) -> List[EvaluationResult]:
        """根据基准答案评估预测。"""

    def get_summary(self) -> Dict[str, Any]:
        """获取基准测试摘要。"""

    def save_results(self, file_path: str):
        """保存评估结果到文件。"""

    def load_results(self, file_path: str):
        """从文件加载评估结果。"""
```

### 数据结构

#### BenchmarkItem

```python
@dataclass
class BenchmarkItem:
    """表示带有问题和答案的单个基准测试项目。"""
    id: str
    question: str
    answer: str
    metadata: Optional[Dict[str, Any]] = None
```

#### EvaluationResult

```python
@dataclass
class EvaluationResult:
    """表示预测与基准答案的评估结果。"""
    item_id: str
    question: str
    ground_truth: str
    prediction: str
    score: float
    metric_name: str
    details: Optional[Dict[str, Any]] = None
```

### 评估指标

#### 内置指标

```python
# 完全匹配
benchmark.evaluate(predictions, metric="exact_match")

# F1分数
benchmark.evaluate(predictions, metric="f1_score")

# 字符串相似度
benchmark.evaluate(predictions, metric="similarity")

# 包含答案
benchmark.evaluate(predictions, metric="contains_answer")

# 数值匹配
benchmark.evaluate(predictions, metric="numeric_match")

# BLEU分数
benchmark.evaluate(predictions, metric="bleu_score")

# ROUGE分数
benchmark.evaluate(predictions, metric="rouge_score")
```

### 便利函数

```python
def create_benchmark(data_path: str, name: Optional[str] = None,
                    description: Optional[str] = None) -> Benchmark:
    """从数据文件创建基准测试。"""
```

## 智能体运行器

### AgentConfig

```python
@dataclass
class AgentConfig:
    """智能体执行的配置。"""
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
    """协调环境和基准测试的主智能体运行器。"""

    def __init__(self, config: AgentConfig):
        """初始化智能体运行器。"""

    def setup_environment(self, mode: str, **kwargs) -> Environment:
        """根据模式设置环境。"""

    def load_benchmark(self, data_path: str, name: Optional[str] = None, **kwargs) -> Benchmark:
        """从数据文件加载基准测试。"""

    def run_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """在单个任务上运行智能体。"""

    def run_benchmark(self, parallel: bool = False) -> List[Dict[str, Any]]:
        """在所有基准测试任务上运行智能体。"""

    def evaluate_results(self) -> Dict[str, Any]:
        """根据基准测试基准答案评估结果。"""

    def save_results(self, output_dir: str = "results") -> str:
        """保存结果到文件。"""

    def run(self, mode: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """完整的运行管道。"""
```

## 命令行界面

### 基本使用

```bash
python src/run.py --mode <环境> --data <数据文件> [选项]
```

### 必需参数

- `--mode`: 环境类型（`math`, `py`, `rag`, `web`）
- `--data`: 基准测试数据文件路径

### 可选参数

#### 常规选项

- `--model`: OpenAI 模型名称（默认：`gpt-4.1-2025-04-14`）
- `--max-turns`: 最大对话轮数（默认：20）
- `--max-retries`: 每轮最大重试次数（默认：3）
- `--max-workers`: 最大并行工作进程（默认：1）
- `--output-dir`: 结果输出目录（默认：`results`）
- `--no-eval`: 跳过评估
- `--no-save`: 跳过保存结果
- `--parallel`: 并行运行任务
- `--metric`: 评估指标（默认：`exact_match`）

#### 环境特定选项

##### Web 环境

- `--web-search-top-k`: 搜索结果数量（默认：5）
- `--web-search-type`: 搜索类型（`search`, `news`, `images`）

##### RAG 环境

- `--kb-path`: 知识库文件路径

##### Doc 环境

- `--ocr-model-path`: MinerU2.5权重路径
- `--ocr-backend-type`: 文档解析推理模式`transformers`, `vllm`, 默认:`transformers`）
- `--pdf-root`: PDF文档路径（默认：`src/data/doc_demo/PDF`）
- `--ocr-output-root`: 文档解析存储路径（默认：`src/data/doc_demo/output`）
- `--temp-output-root`: 中间文件存储路径（默认：`src/data/doc_demo/temp`）

### 示例

```bash
# 基本数学基准测试
python src/run.py --mode math --data src/data/math_demo.jsonl

# 自定义设置的网络搜索
python src/run.py --mode web --data src/data/webagent_demo.jsonl \
  --web-search-top-k 10 --web-search-type news

# 并行执行
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --parallel --max-workers 4

# 自定义模型和评估
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --model gpt-4 --metric f1_score

# 跳过评估和保存
python src/run.py --mode math --data src/data/math_demo.jsonl \
  --no-eval --no-save
```

## 错误处理

### 常见异常

```python
# API密钥未设置
ValueError: OPENAI_API_KEY is not set

# 文件未找到
FileNotFoundError: Data file not found: path/to/file

# 工具未找到
ValueError: Tool 'tool_name' not found

# 无效指标
ValueError: Unknown metric: invalid_metric
```

### 错误恢复

```python
try:
    result = runner.run("math", "data/math_demo.jsonl")
except ValueError as e:
    print(f"配置错误: {e}")
except FileNotFoundError as e:
    print(f"文件错误: {e}")
except Exception as e:
    print(f"意外错误: {e}")
```

## 性能考虑

### 内存使用

- 在内存受限环境中使用`--max-workers 1`
- 加载大型基准测试时考虑数据大小

### API 速率限制

- 在高容量使用中在请求之间添加延迟
- 使用`--max-retries`处理临时故障

### 并行执行

- 对 CPU 密集型任务使用`--parallel`
- 根据系统能力调整`--max-workers`

## 最佳实践

### 工具开发

1. **单一职责**: 每个工具应该做好一件事
2. **错误处理**: 始终优雅地处理异常
3. **文档**: 提供清晰的描述和示例
4. **测试**: 编写全面的测试

### 环境设计

1. **一致性**: 遵循与内置环境相同的模式
2. **配置**: 使环境可配置
3. **可扩展性**: 为未来扩展而设计

### 基准测试创建

1. **数据质量**: 确保高质量的基准答案
2. **多样性**: 包含多样化的测试用例
3. **文档**: 记录数据格式和评估标准

---

_此 API 参考持续更新。请查看最新版本。_
