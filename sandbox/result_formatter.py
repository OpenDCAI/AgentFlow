# sandbox/result_formatter.py
"""
工具执行结果格式化器 - 独立的结果处理模块

这个模块提供统一的接口，将不同工具的执行结果转换为 Agent 可用的标准字符串格式。
设计为独立模块，不耦合到客户端内部，可被 Agent 或数据合成端直接调用。

核心设计:
1. ToolResult 基类 - 提供 to_str() 方法，将结果转换为 tool response 格式
2. 具体工具结果类 - 继承基类，实现各自的格式化逻辑，自动过滤无关信息
3. ResultFormatter - 工厂类，自动识别工具类型并返回对应的格式化器

重要原则:
- 每个工具都必须有专门的格式化器类（继承 ToolResult）
- 不支持通用格式化器，确保每个工具的输出格式都经过精心设计
- 如果工具没有对应的格式化器，会抛出 ValueError

============================================================================
统一响应格式规范 (以 rag:search 为标准模板)
============================================================================

顶层响应结构:
{
    "code": int,           # 0 = 成功，非0 = 失败（用于判断成功/失败）
    "message": str,        # "success" 或错误消息
    "data": {...},         # 业务数据（见下方 data 结构规范）
    "meta": {
        "tool": str,               # 工具名称
        "execution_time_ms": float, # 执行时间
        "resource_type": str,       # 资源类型
        "session_id": str,          # 会话 ID
        "trace_id": str             # 追踪 ID
    }
}

data 结构规范:
- 核心内容字段: 工具的主要输出（result/context/contexts/stdout 等）
- 输入回显字段: 可选的输入参数回显，用于日志/调试（query/urls/goal 等）
- 不在 data 中包含 success 字段！成功/失败应通过顶层 code 判断

各工具 data 结构:
- search:       {"result": str, "query": str}
- visit:        {"result": str, "urls": str, "goal": str, "warning"?: str}
- rag:search:   {"context": str, "query": str}
- rag:batch_search: {"contexts": List[str], "count": int, "errors"?: List[Dict]}
- bash:         {"stdout": str, "stderr": str, "return_code": int, "cwd"?: str}
- code:         {"stdout": str, "stderr": str, "return_code": int, ...}

============================================================================

已支持的工具类型:
- search: WebSearchResult - Web 搜索结果（提取 data.result）
- visit: VisitResult - 网页访问结果（提取 data.result）
- rag:search: RAGSearchResult - RAG 检索结果（提取 data.context）
- rag:batch_search: RAGBatchSearchResult - RAG 批量检索结果
- rag:stats: RAGStatsResult - RAG 统计信息
- bash: BashResult - Bash 命令执行结果（提取 stdout/stderr）
- code: CodeExecutionResult - 代码执行结果（提取 stdout/stderr）
    - browser: BrowserResult - 浏览器操作结果
    - vm: VMResult - 虚拟机操作结果（仅保留可访问性树）
- session:*: SessionResult - Session/Status 接口结果
- init:*: InitResult - Init 接口结果
- batch:execute: BatchExecuteResult - 批量执行结果

添加新工具的格式化器:
```python
from sandbox.result_formatter import ToolResult, ResultFormatter

class MyToolResult(ToolResult):
    def to_str(self, verbose: bool = False) -> str:
        # 实现格式化逻辑，过滤无关信息
        # 注意：成功/失败通过 self.success (来自顶层 code) 判断
        if not self.success:
            return f"[Error] {self.metadata.get('message', 'Unknown error')}"
        result = self.raw_data.get("result", "")
        return result.strip()

# 注册格式化器
ResultFormatter.register_formatter("my_tool", MyToolResult)
```

使用示例:
```python
from sandbox import HTTPServiceClient
from sandbox.result_formatter import ResultFormatter

async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # 执行工具
    raw_result = await client.execute("web:search", {"query": "Python tutorial"})

    # 方式1: 使用 ResultFormatter.format_to_str() 方法
    tool_response = ResultFormatter.format_to_str(raw_result)

    # 直接输入 agent
    print(tool_response)  # 只包含关键信息，已过滤无关元数据
```
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json


# ============================================================================
# 基类定义
# ============================================================================

class ToolResult(ABC):
    """
    工具执行结果基类

    所有工具结果都继承此类，实现 to_str() 方法将结果转换为
    Agent 可用的标准字符串格式。

    设计原则:
    - 过滤冗余信息，只保留关键内容
    - 格式清晰，易于 Agent 理解
    - 支持自定义过滤规则
    """

    def __init__(self, raw_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        初始化工具结果

        Args:
            raw_data: 工具执行的原始返回数据 (response["data"])
            metadata: 元数据 (如 tool, resource_type, execution_time_ms 等)
        """
        self.raw_data = raw_data
        self.metadata = metadata or {}
        self.success = self.metadata.get("success", True)
        self.tool_name = self.metadata.get("tool", "unknown")
        self.execution_time = self.metadata.get("execution_time_ms", 0)

    @abstractmethod
    def to_str(self, verbose: bool = False) -> str:
        """
        将结果转换为字符串格式

        Args:
            verbose: 是否包含详细信息 (如执行时间、元数据等)

        Returns:
            格式化后的字符串，可直接用于 tool response（已过滤无关信息）
        """
        pass


    def get_metadata(self) -> Dict[str, Any]:
        """返回元数据"""
        return self.metadata


# ============================================================================
# Bash 工具结果
# ============================================================================

class BashResult(ToolResult):
    """
    Bash 命令执行结果

    原始数据结构:
    {
        "stdout": str,
        "stderr": str,
        "return_code": int,
        "cwd": str (可选)
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        格式化 Bash 执行结果

        格式:
        - 成功: 只返回 stdout (过滤空输出)
        - 失败: 返回 stderr 和 return_code
        - verbose: 额外包含执行时间和工作目录
        """
        # 如果响应层面失败（例如工具执行异常）
        if not self.success:
            error_msg = self.metadata.get("message", "Command execution failed")
            return f"[Error] {error_msg}"

        stdout = self.raw_data.get("stdout", "")
        stderr = self.raw_data.get("stderr", "")
        return_code = self.raw_data.get("return_code", 0)
        cwd = self.raw_data.get("cwd", "")

        lines = []

        # 成功执行
        if return_code == 0:
            if stdout.strip():
                lines.append(stdout.rstrip())
            else:
                lines.append("[Command executed successfully with no output]")
        # 执行失败
        else:
            lines.append(f"[Error] Command failed with return code {return_code}")
            if stderr.strip():
                lines.append(f"Error output:\n{stderr.rstrip()}")
            if stdout.strip():
                lines.append(f"Standard output:\n{stdout.rstrip()}")

        # Verbose 模式
        if verbose:
            meta_lines = []
            if cwd:
                meta_lines.append(f"Working directory: {cwd}")
            if self.execution_time:
                meta_lines.append(f"Execution time: {self.execution_time:.2f}ms")
            if meta_lines:
                lines.append("\n" + "\n".join(meta_lines))

        return "\n".join(lines)


# ============================================================================
# 代码执行工具结果
# ============================================================================

class CodeExecutionResult(ToolResult):
    """
    代码执行结果

    原始数据结构:
    {
        "stdout": str,
        "stderr": str,
        "return_code": int,
        "execution_time_ms": float,
        "memory_used_mb": float
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        格式化代码执行结果

        格式:
        - 成功: 返回 stdout
        - 失败: 返回 stderr
        - verbose: 包含资源使用信息
        """
        # 如果响应层面失败（例如工具执行异常）
        if not self.success:
            error_msg = self.metadata.get("message", "Code execution failed")
            return f"[Error] {error_msg}"

        stdout = self.raw_data.get("stdout", "")
        stderr = self.raw_data.get("stderr", "")
        return_code = self.raw_data.get("return_code", 0)
        exec_time = self.raw_data.get("execution_time_ms", 0)
        memory = self.raw_data.get("memory_used_mb", 0)

        lines = []

        # 成功执行
        if return_code == 0:
            if stdout.strip():
                lines.append(stdout.rstrip())
            else:
                lines.append("[Code executed successfully with no output]")
        # 执行失败
        else:
            lines.append(f"[Error] Code execution failed")
            if stderr.strip():
                lines.append(stderr.rstrip())

        # Verbose 模式 - 资源使用信息
        if verbose and (exec_time or memory):
            meta_lines = []
            if exec_time:
                meta_lines.append(f"Execution time: {exec_time:.2f}ms")
            if memory:
                meta_lines.append(f"Memory used: {memory:.2f}MB")
            if meta_lines:
                lines.append("\n" + "\n".join(meta_lines))

        return "\n".join(lines)


# ============================================================================
# 虚拟机工具结果
# ============================================================================

class VMResult(ToolResult):
    """
    虚拟机操作结果

    只保留可访问性树（accessibility_tree），过滤屏幕截图等内容。
    """

    def to_str(self, verbose: bool = False) -> str:
        if not self.success:
            error_msg = self.metadata.get("message", "VM operation failed")
            return f"[Error] {error_msg}"

        tree = self.raw_data.get("accessibility_tree")
        if isinstance(tree, str) and tree.strip():
            return tree.rstrip()

        return "[No accessibility tree]"


# ============================================================================
# 浏览器工具结果
# ============================================================================

class BrowserResult(ToolResult):
    """
    浏览器操作结果

    原始数据结构 (根据不同操作而异):
    - screenshot: {"image_path": str, "size": tuple}
    - navigate: {"url": str, "title": str, "status": int}
    - extract: {"text": str, "html": str}
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        格式化浏览器操作结果

        根据操作类型返回不同格式
        """
        # Screenshot
        if "image_path" in self.raw_data:
            image_path = self.raw_data.get("image_path", "")
            size = self.raw_data.get("size", ())
            lines = [f"Screenshot saved: {image_path}"]
            if verbose and size:
                lines.append(f"Size: {size[0]}x{size[1]}")
            return "\n".join(lines)

        # Navigate
        if "url" in self.raw_data and "title" in self.raw_data:
            url = self.raw_data.get("url", "")
            title = self.raw_data.get("title", "")
            status = self.raw_data.get("status", 200)
            lines = [f"Navigated to: {url}"]
            if title:
                lines.append(f"Page title: {title}")
            if verbose:
                lines.append(f"Status: {status}")
            return "\n".join(lines)

        # Extract text
        if "text" in self.raw_data:
            text = self.raw_data.get("text", "")
            if text.strip():
                return text.rstrip()
            return "[No text content extracted]"

        # 默认: 返回 JSON
        return json.dumps(self.raw_data, indent=2, ensure_ascii=False)


# ============================================================================
# Web 搜索工具结果
# ============================================================================

class WebSearchResult(ToolResult):
    """
    Web 搜索结果 (search 工具)

    原始数据结构:
    {
        "result": str,        # 搜索结果文本（Markdown格式）
        "query": str          # 搜索查询字符串（用于日志/调试）
    }
    
    注意: 成功/失败通过顶层 code 字段判断（code=0 表示成功），
    data 内部不包含 success 字段。
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        格式化 Web 搜索结果

        格式:
        - 默认: 只返回搜索结果文本（过滤 query 等元数据）
        - verbose: 额外包含查询信息
        """
        query = self.raw_data.get("query", "")
        
        # 如果响应层面失败（code != 0），直接返回错误消息
        if not self.success:
            error_msg = self.metadata.get("message", "Search failed")
            if query:
                return f"[Search failed for query: {query}] {error_msg}"
            return f"[Search failed] {error_msg}"
        
        # 提取实际结果
        result_text = self.raw_data.get("result", "")

        # 如果结果为空
        if not result_text.strip():
            if query:
                return f"[No results found for query: {query}]"
            return "[No results found]"

        lines = []
        
        # 默认只返回搜索结果文本（这是 agent 需要的关键信息）
        lines.append(result_text.rstrip())

        # Verbose 模式：添加查询信息
        if verbose and query:
            lines.append(f"\n[Query: {query}]")

        return "\n".join(lines)


# ============================================================================
# RAG 搜索工具结果
# ============================================================================

class RAGSearchResult(ToolResult):
    """
    RAG 检索结果 (rag:search 工具) - 统一格式的标准参考
    
    这是工具返回格式的标准模板：
    - 成功/失败通过顶层 code 字段判断（code=0 表示成功）
    - data 内部只包含核心内容和必要的输入参数回显
    - 不在 data 中重复 success 字段

    原始数据结构:
    {
        "query": str,         # 检索查询字符串（输入回显，用于日志/调试）
        "context": str        # 检索到的上下文文本（核心内容）
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        格式化 RAG 检索结果

        格式:
        - 默认: 只返回检索到的上下文文本（过滤 query 等元数据）
        - verbose: 额外包含查询信息
        """
        query = self.raw_data.get("query", "")
        
        # 如果响应层面失败（code != 0），直接返回错误消息
        if not self.success:
            error_msg = self.metadata.get("message", "RAG search failed")
            if query:
                return f"[RAG search failed for query: {query}] {error_msg}"
            return f"[RAG search failed] {error_msg}"
        
        context = self.raw_data.get("context", "")

        # 如果没有结果
        if not context.strip():
            if query:
                return f"[No context found for query: {query}]"
            return "[No context found]"

        lines = []

        # 默认只返回上下文内容（这是 agent 需要的关键信息）
        lines.append(context.rstrip())

        # Verbose 模式：添加查询信息
        if verbose and query:
            lines.append(f"\n[Query: {query}]")

        return "\n".join(lines)


# ============================================================================
# 网页访问工具结果
# ============================================================================

class VisitResult(ToolResult):
    """
    网页访问结果 (visit 工具)

    原始数据结构:
    {
        "result": str,        # 网页内容摘要（Markdown格式，核心内容）
        "urls": str,          # 访问的 URL（输入回显）
        "goal": str,          # 访问目标描述（输入回显）
        "warning": str        # 可选，部分成功时的警告信息
    }
    
    注意: 成功/失败通过顶层 code 字段判断（code=0 表示成功），
    data 内部不包含 success 字段。
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        格式化网页访问结果

        格式:
        - 默认: 只返回网页内容摘要（过滤 urls、goal 等元数据）
        - verbose: 额外包含 URL 和目标信息
        """
        urls = self.raw_data.get("urls", "")
        goal = self.raw_data.get("goal", "")
        
        # 如果响应层面失败（code != 0），直接返回错误消息
        if not self.success:
            error_msg = self.metadata.get("message", "Visit failed")
            if urls:
                return f"[Failed to visit {urls}] {error_msg}"
            return f"[Visit failed] {error_msg}"
        
        result_text = self.raw_data.get("result", "")
        warning = self.raw_data.get("warning", "")

        # 如果结果为空
        if not result_text.strip():
            if urls:
                return f"[No content extracted from {urls}]"
            return "[No content extracted]"

        lines = []
        
        # 默认只返回网页内容摘要（这是 agent 需要的关键信息）
        lines.append(result_text.rstrip())
        
        # 如果有警告信息（部分成功的情况）
        if warning:
            lines.append(f"\n[Warning: {warning}]")

        # Verbose 模式：添加 URL 和目标信息
        if verbose:
            if urls:
                lines.append(f"\n[URL: {urls}]")
            if goal:
                lines.append(f"[Goal: {goal}]")

        return "\n".join(lines)


# ============================================================================
# Doc 工具结果
# ============================================================================

class DocResult(ToolResult):
    """
    Doc QA 工具结果 (doc:search / doc:read)
    数据科学工具结果 (ds:inspect_data / ds:read_csv / ds:run_python)
    
    约定原始 data 结构:
    {
        "result": str,
        "inputs": {...} (可选，仅用于调试/回显)
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        # 如果响应层面失败（code != 0），直接返回错误消息
        if not self.success:
            error_msg = self.metadata.get("message", "Doc/DS tool failed")
            return f"[Doc/DS tool failed] {error_msg}"

        result_text = self.raw_data.get("result", "")
        if isinstance(result_text, str) and result_text.strip():
            return result_text.rstrip()

        # 兜底：返回简洁 JSON（避免空输出让 agent 迷惑）
        try:
            return json.dumps(self.raw_data, ensure_ascii=False, indent=2)
        except Exception:
            return str(self.raw_data)


# ============================================================================
# 结果格式化器工厂
# ============================================================================

class ResultFormatter:
    """
    结果格式化器工厂类

    自动识别工具类型，返回对应的格式化器实例。

    使用方法:
    ```python
    # 方式1: 直接格式化
    formatted_str = ResultFormatter.format_to_str(response)

    # 方式2: 获取格式化器实例
    formatter = ResultFormatter.format(response)
    formatted_str = formatter.to_str(verbose=True)
    ```
    """

    # 工具类型到格式化器的映射
    FORMATTER_MAP = {
        "bash": BashResult,
        "code": CodeExecutionResult,
        "browser": BrowserResult,
        "vm": VMResult,
        "doc": DocResult,
        "ds": DocResult,
    }

    @classmethod
    def format(cls, response: Dict[str, Any]) -> ToolResult:
        """
        根据响应自动选择格式化器

        只支持新格式（标准格式）:
            {
                "code": int,
                "message": str,
                "data": {...},
                "meta": {
                    "tool": str,
                    "execution_time_ms": float,
                    "resource_type": str,
                    "session_id": str,
                    "trace_id": str
                }
            }

        Args:
            response: 服务器返回的完整响应

        Returns:
            对应的 ToolResult 实例

        Raises:
            ValueError: 如果响应格式不正确或找不到对应的格式化器
        """
        # 验证响应格式：必须包含 code 和 meta 字段
        if "code" not in response or "meta" not in response:
            raise ValueError(
                f"Invalid response format: expected 'code' and 'meta' fields. "
                f"Got: {list(response.keys())}"
            )

        # 从 meta 提取元数据，从 data 提取实际数据
        meta = response.get("meta", {})
        data = response.get("data", {})
        code = response.get("code", 0)

        metadata = {
            "success": code == 0,
            "code": code,
            "message": response.get("message", ""),
            "tool": meta.get("tool", ""),
            "resource_type": meta.get("resource_type", ""),
            "execution_time_ms": meta.get("execution_time_ms", 0),
            "session_id": meta.get("session_id"),
            "trace_id": meta.get("trace_id"),
        }

        # 识别工具类型
        tool_name = metadata.get("tool", "")
        resource_type = metadata.get("resource_type", "")
        
        # 根据工具名称精确匹配
        if tool_name == "web:search" and resource_type != "rag":
            formatter_class = WebSearchResult
        elif tool_name == "web:visit":
            formatter_class = VisitResult
        elif tool_name == "rag:search":
            formatter_class = RAGSearchResult
        elif tool_name.startswith("sql:"):
            formatter_class = SQLResult
        elif tool_name.startswith("doc:") or tool_name.startswith("ds:"):
            formatter_class = DocResult
        else:
            # 优先使用 resource_type，然后尝试从 tool_name 提取资源类型
            tool_type = resource_type or tool_name.split(":")[0] if ":" in tool_name else tool_name
            
            # 查找对应的格式化器
            formatter_class = cls.FORMATTER_MAP.get(tool_type)
            
            # 如果没有找到格式化器，抛出错误
            if formatter_class is None:
                raise ValueError(
                    f"No formatter found for tool '{tool_name}' "
                    f"(resource_type='{resource_type}', tool_type='{tool_type}'). "
                    f"Please implement a custom ToolResult class and register it using "
                    f"ResultFormatter.register_formatter('{tool_type}', YourFormatterClass)"
                )

        return formatter_class(data, metadata)

    @classmethod
    def format_to_str(
        cls,
        response: Dict[str, Any],
        verbose: bool = False
    ) -> str:
        """
        直接将响应格式化为字符串

        Args:
            response: 服务器返回的完整响应
            verbose: 是否包含详细信息

        Returns:
            格式化后的字符串
        """
        formatter = cls.format(response)
        return formatter.to_str(verbose=verbose)

    @classmethod
    def register_formatter(cls, tool_type: str, formatter_class: type):
        """
        注册自定义格式化器

        Args:
            tool_type: 工具类型标识
            formatter_class: 格式化器类 (必须继承 ToolResult)

        Example:
        ```python
        class MyCustomResult(ToolResult):
            def to_str(self, verbose=False):
                return "Custom format"

        ResultFormatter.register_formatter("mycustom", MyCustomResult)
        ```
        """
        if not issubclass(formatter_class, ToolResult):
            raise TypeError(f"{formatter_class} must inherit from ToolResult")

        cls.FORMATTER_MAP[tool_type] = formatter_class


# ============================================================================
# 便捷函数
# ============================================================================

def format_tool_result(response: Dict[str, Any], verbose: bool = False) -> str:
    """
    便捷函数: 格式化工具执行结果

    Args:
        response: 服务器返回的完整响应
        verbose: 是否包含详细信息

    Returns:
        格式化后的字符串，可直接用于 tool response

    Example:
    ```python
    from sandbox.result_formatter import format_tool_result

    result = await client.execute("bash:run", {"command": "ls"})
    formatted = format_tool_result(result)
    print(formatted)
    ```
    """
    return ResultFormatter.format_to_str(response, verbose=verbose)
