# Result Formatter - 工具结果格式化器

## 概述

`result_formatter` 是一个独立的结果处理模块，用于将 Sandbox 工具执行的原始返回结果转换为 Agent 可用的标准字符串格式。

### 核心特性

- **统一接口**: 所有工具结果都通过 `to_str()` 方法转换为字符串
- **智能过滤**: 自动过滤冗余信息，只保留关键内容
- **类型识别**: 自动识别工具类型并应用对应的格式化逻辑
- **可扩展**: 支持注册自定义格式化器
- **独立模块**: 不耦合到客户端内部，可被 Agent 或数据合成端直接调用

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      ToolResult (基类)                       │
│  - raw_data: 原始数据                                        │
│  - metadata: 元数据                                          │
│  + to_str(verbose): 转换为字符串 (抽象方法)                  │
│  + to_dict(): 返回原始数据                                   │
│  + get_metadata(): 返回元数据                                │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │
┌───────┴────────┐  ┌────────┴────────┐
│  BashResult    │  │ CodeExecution   │
│                │  │     Result      │
│ - 格式化 Bash  │  │ - 格式化代码    │
│   命令输出     │  │   执行结果      │
└────────────────┘  └─────────────────┘

        ┌─────────────────────┐
        │  BrowserResult      │
        │                     │
        │ - 格式化浏览器      │
        │   操作结果          │
        └─────────────────────┘

        ┌─────────────────────┐
        │  GenericResult      │
        │                     │
        │ - 通用格式化器      │
        │   (默认)            │
        └─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              ResultFormatter (工厂类)                        │
│  + format(response): 自动识别并返回格式化器                  │
│  + format_to_str(response): 直接返回格式化字符串             │
│  + register_formatter(type, class): 注册自定义格式化器       │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 基本使用

```python
from sandbox import HTTPServiceClient
from sandbox.result_formatter import format_tool_result

async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # 执行工具
    response = await client.execute("bash:run", {"command": "ls -la"})

    # 格式化结果
    formatted = format_tool_result(response)

    # 直接用于 tool response
    print(formatted)
    # 输出:
    # file1.txt
    # file2.py
    # dir1/
```

### 使用 ResultFormatter 类

```python
from sandbox.result_formatter import ResultFormatter

# 获取格式化器实例
formatter = ResultFormatter.format(response)

# 简洁模式
simple_output = formatter.to_str(verbose=False)

# 详细模式 (包含执行时间、元数据等)
verbose_output = formatter.to_str(verbose=True)

# 获取原始数据
raw_data = formatter.to_dict()

# 获取元数据
metadata = formatter.get_metadata()
```

## 支持的工具类型

| 工具类型 | 格式化器 | 说明 |
|---------|---------|------|
| `bash` | BashResult | Bash 命令执行结果 |
| `code` | CodeExecutionResult | 代码执行结果 |
| `browser` / `vm` | BrowserResult | 浏览器/VM 操作结果 |
| 其他 | GenericResult | 通用格式化器（默认） |

### 1. Bash 工具

**原始数据结构:**
```python
{
    "stdout": str,
    "stderr": str,
    "return_code": int,
    "cwd": str  # 可选
}
```

**格式化输出:**
```
# 成功执行
file1.txt
file2.py

# 失败执行
[Error] Command failed with return code 127
Error output:
command not found: invalid_command

# Verbose 模式
file1.txt
file2.py

Working directory: /workspace
Execution time: 45.20ms
```

### 2. 代码执行工具

**原始数据结构:**
```python
{
    "stdout": str,
    "stderr": str,
    "return_code": int,
    "execution_time_ms": float,
    "memory_used_mb": float
}
```

**格式化输出:**
```
# 成功执行
Hello, World!
The answer is: 42

# Verbose 模式
Hello, World!
The answer is: 42

Execution time: 125.80ms
Memory used: 15.30MB
```

### 3. RAG 检索工具

**原始数据结构:**
```python
{
    "query": str,
    "results": [
        {
            "text": str,
            "score": float,
            "metadata": dict
        }
    ],
    "total": int
}
```

**格式化输出:**
```
# 简洁模式 (只显示文本)
Machine learning is a subset of AI...
ML algorithms build models...

# Verbose 模式 (包含分数和元数据)
Query: What is machine learning?
Found 3 results:

[Result 1] (score: 0.950)
Metadata: {"source": "doc1.pdf", "page": 5}
Machine learning is a subset of AI...
```

### 4. 浏览器工具

**原始数据结构:**
```python
# Navigate
{
    "url": str,
    "title": str,
    "status": int
}

# Screenshot
{
    "image_path": str,
    "size": tuple
}

# Extract
{
    "text": str
}
```

**格式化输出:**
```
# Navigate
Navigated to: https://example.com
Page title: Example Domain

# Screenshot
Screenshot saved: /tmp/screenshot.png
Size: 1920x1080

# Extract
Extracted text content...
```

### 5. 通用工具

对于未特殊处理的工具，使用通用格式化器：

- 如果数据包含 `message` 字段，优先返回该字段
- 字符串数据直接返回
- 字典/列表转换为 JSON 格式

## 高级用法

### 注册自定义格式化器

```python
from sandbox.result_formatter import ToolResult, ResultFormatter

# 1. 定义自定义格式化器
class MyCustomResult(ToolResult):
    def to_str(self, verbose=False):
        data = self.raw_data
        lines = [
            "=== Custom Tool Result ===",
            f"Status: {data.get('status', 'unknown')}",
            f"Count: {data.get('count', 0)}"
        ]

        if verbose:
            lines.append(f"Execution Time: {self.execution_time:.2f}ms")

        return "\n".join(lines)

# 2. 注册格式化器
ResultFormatter.register_formatter("mycustom", MyCustomResult)

# 3. 使用自定义格式化器
response = await client.execute("mycustom:action", {...})
formatted = format_tool_result(response)
```

### 在 Agent 中集成

```python
class MyAgent:
    def __init__(self, sandbox_client):
        self.client = sandbox_client

    async def call_tool(self, tool_name, params):
        # 1. 调用工具
        raw_response = await self.client.execute(tool_name, params)

        # 2. 格式化结果
        formatted_result = format_tool_result(raw_response)

        # 3. 构建 tool response
        tool_response = {
            "role": "tool",
            "content": formatted_result,
            "tool_call_id": "..."
        }

        return tool_response
```

### 在数据合成中使用

```python
from sandbox.result_formatter import format_tool_result

async def generate_training_data():
    """生成训练数据"""

    # 执行工具
    response = await client.execute("bash:run", {"command": "ls"})

    # 格式化为 tool response
    tool_response = format_tool_result(response)

    # 构建训练样本
    training_sample = {
        "messages": [
            {"role": "user", "content": "List files in current directory"},
            {"role": "assistant", "content": "I'll list the files", "tool_calls": [...]},
            {"role": "tool", "content": tool_response}
        ]
    }

    return training_sample
```

## API 参考

### ToolResult (基类)

所有工具结果格式化器的基类。

**方法:**

- `to_str(verbose: bool = False) -> str`: 将结果转换为字符串
  - `verbose`: 是否包含详细信息（执行时间、元数据等）

- `to_dict() -> Dict[str, Any]`: 返回原始数据字典

- `get_metadata() -> Dict[str, Any]`: 返回元数据

**属性:**

- `raw_data`: 原始数据
- `metadata`: 元数据
- `success`: 执行是否成功
- `tool_name`: 工具名称
- `execution_time`: 执行时间（毫秒）

### ResultFormatter (工厂类)

**类方法:**

- `format(response: Dict[str, Any]) -> ToolResult`
  - 根据响应自动选择格式化器
  - 返回对应的 ToolResult 实例

- `format_to_str(response: Dict[str, Any], verbose: bool = False) -> str`
  - 直接将响应格式化为字符串
  - 便捷方法，等同于 `format(response).to_str(verbose)`

- `register_formatter(tool_type: str, formatter_class: type)`
  - 注册自定义格式化器
  - `formatter_class` 必须继承 `ToolResult`

### 便捷函数

- `format_tool_result(response: Dict[str, Any], verbose: bool = False) -> str`
  - 全局便捷函数
  - 等同于 `ResultFormatter.format_to_str(response, verbose)`

## 测试

当前仓库未维护独立的 `result_formatter` 测试脚本，可通过最小调用代码进行功能验证：

```python
from sandbox.result_formatter import format_tool_result

response = {
    "code": 0,
    "message": "ok",
    "data": {"stdout": "hello\n", "stderr": "", "return_code": 0},
    "meta": {"tool": "bash:run", "execution_time_ms": 1.2, "trace_id": "demo-trace-id"}
}

print(format_tool_result(response))
```

如需做更严格验证，建议在集成流程中对典型工具响应进行快照比对。

## 设计原则

1. **独立性**: 模块完全独立，不依赖客户端实现
2. **可扩展性**: 支持注册自定义格式化器
3. **简洁性**: 过滤冗余信息，只保留关键内容
4. **一致性**: 所有工具使用统一的接口
5. **灵活性**: 支持简洁和详细两种模式

## 文件位置

- **核心模块**: `sandbox/result_formatter.py`
- **文档**: `sandbox/docs/zh-CN/development/RESULT_FORMATTER.md` (本文件)

## 使用场景

1. **Agent 工具调用**: 将工具执行结果转换为 Agent 可理解的格式
2. **数据合成**: 生成训练数据时格式化 tool response
3. **日志记录**: 以可读格式记录工具执行结果
4. **调试**: 快速查看工具返回的关键信息

## 注意事项

1. 格式化器会自动识别工具类型，无需手动指定
2. `verbose=True` 会包含更多元数据，适合调试
3. `verbose=False` 只保留核心内容，适合 Agent 使用
4. 自定义格式化器必须继承 `ToolResult` 类
5. 注册的格式化器会覆盖默认的同名格式化器

## 贡献

如需添加新的工具格式化器：

1. 继承 `ToolResult` 类
2. 实现 `to_str(verbose)` 方法
3. 在 `ResultFormatter.FORMATTER_MAP` 中注册
4. 添加对应的单元测试

## 许可证

与 Sandbox 项目保持一致。
