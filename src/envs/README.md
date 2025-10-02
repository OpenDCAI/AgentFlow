# AgentFlow Environment

这个模块提供了基于继承的 Environment 类体系来管理 AgentFlow 中的工具和配置。

## 功能特性

- **继承架构**: 使用抽象基类 Environment，具体环境类继承实现
- **工具管理**: 注册、获取、执行各种工具
- **环境类型**: MathEnvironment、PythonEnvironment、RAGEnvironment、WebEnvironment
- **配置管理**: 统一管理 API 密钥、模型设置等配置
- **工具模式转换**: 自动将工具转换为 OpenAI 函数调用格式
- **环境持久化**: 支持保存和加载环境配置

## 快速开始

### 基本使用

```python
from envs import create_math_environment

# 创建数学环境
env = create_math_environment()

# 执行工具
result = env.execute_tool("calculator", {"expressions": ["2+2", "sqrt(16)"]})
print(result)
```

### 不同环境类型

```python
from envs import MathEnvironment, PythonEnvironment, RAGEnvironment, WebEnvironment

# 数学环境
math_env = MathEnvironment()

# Python环境
py_env = PythonEnvironment()

# RAG环境
rag_env = RAGEnvironment()

# Web环境
web_env = WebEnvironment()
```

### 自定义配置

```python
# 创建带自定义配置的环境
env = Environment(
    mode="web",
    model_name="gpt-4",
    web_search_top_k=10,
    web_search_type="news",
    custom_param="value"
)
```

## API 参考

### Environment 基类（抽象类）

#### 构造函数

```python
Environment(
    model_name: str = "gpt-4.1-2025-04-14",
    openai_api_key: Optional[str] = None,
    openai_api_url: Optional[str] = None,
    **kwargs
)
```

### 具体环境类

- **MathEnvironment**: 数学计算环境
- **PythonEnvironment**: Python 解释器环境
- **RAGEnvironment**: RAG 检索环境
- **WebEnvironment**: 网络搜索环境

#### 主要方法

- `register_tool(tool: Tool)`: 注册工具
- `unregister_tool(tool_name: str)`: 注销工具
- `get_tool(tool_name: str)`: 获取工具
- `list_tools() -> List[str]`: 列出所有工具
- `execute_tool(tool_name: str, params: Union[str, dict], **kwargs) -> str`: 执行工具
- `get_tool_schemas() -> List[Dict[str, Any]]`: 获取工具模式（用于 OpenAI 函数调用）
- `get_tool_descriptions() -> str`: 获取工具描述
- `switch_mode(new_mode: str, **kwargs)`: 切换环境模式
- `update_config(**kwargs)`: 更新配置
- `get_config(key: str = None)`: 获取配置
- `save_environment(filepath: str)`: 保存环境配置
- `load_environment(filepath: str)`: 加载环境配置

### 便利函数

- `create_math_environment(**kwargs)`: 创建数学环境
- `create_python_environment(**kwargs)`: 创建 Python 环境
- `create_rag_environment(**kwargs)`: 创建 RAG 环境
- `create_web_environment(**kwargs)`: 创建 Web 环境

## 环境类型

### MathEnvironment

- **工具**: CalculatorTool
- **用途**: 数学计算和表达式求值
- **创建**: `MathEnvironment()` 或 `create_math_environment()`

### PythonEnvironment

- **工具**: PythonInterpreterTool
- **用途**: Python 代码执行和调试
- **创建**: `PythonEnvironment()` 或 `create_python_environment()`

### RAGEnvironment

- **工具**: QueryRAGIndexTool
- **用途**: 检索增强生成，基于知识库问答
- **创建**: `RAGEnvironment()` 或 `create_rag_environment()`

### WebEnvironment

- **工具**: WebSearchTool, WebVisitTool
- **用途**: 网络搜索和网页内容提取
- **创建**: `WebEnvironment()` 或 `create_web_environment()`

## 配置参数

### 通用配置

- `model_name`: OpenAI 模型名称
- `openai_api_key`: OpenAI API 密钥
- `openai_api_url`: OpenAI API URL

### WebEnvironment 配置

- `web_search_top_k`: 搜索结果数量（默认 5）
- `web_search_type`: 搜索类型（"search", "news", "images"）
- `web_search_max_workers`: 并发搜索数量（默认 5）
- `web_visit_summary_model`: 网页内容摘要模型

### RAGEnvironment 配置

- `index_path`: RAG 索引路径
- `kb_path`: 知识库路径

## 示例

查看 `example_usage.py` 文件获取更多使用示例。

## 注意事项

1. 确保设置了必要的环境变量（OPENAI_API_KEY 等）
2. 不同模式需要不同的工具依赖
3. RAG 模式需要先构建索引
4. Web 模式需要 Serper API 密钥
