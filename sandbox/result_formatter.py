# sandbox/result_formatter.py
"""
Tool execution result formatter - standalone result processing module.

This module provides a unified interface that converts tool execution results
into standardized strings consumable by agents. It is intentionally decoupled
from client internals so it can be used by agents or synthesis pipelines.

Core design:
1. `ToolResult` base class - exposes `to_str()` for tool response formatting.
2. Concrete result classes - implement tool-specific filtering/formatting logic.
3. `ResultFormatter` factory - auto-detects tool type and returns formatter.

Key principles:
- Every tool should have a dedicated formatter class inheriting `ToolResult`.
- No generic fallback formatter, to keep output format intentional per tool.
- Missing formatter should raise `ValueError`.

============================================================================
Unified response format (using `rag:search` as the reference)
============================================================================

Top-level response schema:
{
    "code": int,           # 0 = success, non-zero = failure
    "message": str,        # "success" or error message
    "data": {...},         # business payload (see data schema below)
    "meta": {
        "tool": str,                # tool name
        "execution_time_ms": float, # execution time
        "resource_type": str,       # resource type
        "session_id": str,          # session ID
        "trace_id": str             # trace ID
    }
}

Data schema:
- Core content fields: primary outputs (result/context/contexts/stdout, etc.)
- Input echo fields: optional echoes for logs/debug (query/urls/goal, etc.)
- Do not include `success` inside `data`; infer from top-level `code`.

Per-tool `data` schema:
- search:       {"result": str, "query": str}
- visit:        {"result": str, "urls": str, "goal": str, "warning"?: str}
- rag:search:   {"context": str, "query": str}
- rag:batch_search: {"contexts": List[str], "count": int, "errors"?: List[Dict]}
- bash:         {"stdout": str, "stderr": str, "return_code": int, "cwd"?: str}
- code:         {"stdout": str, "stderr": str, "return_code": int, ...}

============================================================================

Supported tool types:
- search: WebSearchResult - web search result (`data.result`)
- visit: VisitResult - web visit result (`data.result`)
- rag:search: RAGSearchResult - RAG search result (`data.context`)
- rag:batch_search: RAGBatchSearchResult - batch RAG search result
- rag:stats: RAGStatsResult - RAG stats
- text2sql:*: SQLResult - SQL tool results (list_databases, get_schema, execute)
- bash: BashResult - bash execution result (`stdout/stderr`)
- code: CodeExecutionResult - code execution result (`stdout/stderr`)
    - browser: BrowserResult - browser operation result
    - vm: VMResult - VM operation result (accessibility tree only)
- session:*: SessionResult - session/status API result
- init:*: InitResult - init API result
- batch:execute: BatchExecuteResult - batch execution result

Adding a formatter for new tools:
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

# Register formatter.
ResultFormatter.register_formatter("my_tool", MyToolResult)
```

Usage example:
```python
from sandbox import HTTPServiceClient
from sandbox.result_formatter import ResultFormatter

async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # Execute tool.
    raw_result = await client.execute("web:search", {"query": "Python tutorial"})

    # Option 1: use ResultFormatter.format_to_str().
    tool_response = ResultFormatter.format_to_str(raw_result)

    # Directly feed into an agent.
    print(tool_response)  # Contains key info only; irrelevant metadata removed.
```
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json


# ============================================================================
# Base class definitions.
# ============================================================================

class ToolResult(ABC):
    """
    Base class for tool execution results.

    All tool result classes should inherit from this class and implement
    `to_str()` to produce standardized strings consumable by agents.

    Design goals:
    - Filter redundant information and keep key content.
    - Keep output clear and easy for agents to parse.
    - Support custom filtering rules when needed.
    """

    def __init__(self, raw_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a tool result object.

        Args:
            raw_data: Raw tool payload (`response["data"]`).
            metadata: Metadata (tool/resource_type/execution_time_ms, etc.).
        """
        self.raw_data = raw_data
        self.metadata = metadata or {}
        self.success = self.metadata.get("success", True)
        self.tool_name = self.metadata.get("tool", "unknown")
        self.execution_time = self.metadata.get("execution_time_ms", 0)

    @abstractmethod
    def to_str(self, verbose: bool = False) -> str:
        """
        Convert result into a string representation.

        Args:
            verbose: Whether to include detailed information.

        Returns:
            Formatted string for tool responses (irrelevant details filtered).
        """
        pass


    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata."""
        return self.metadata


# ============================================================================
# Bash tool result.
# ============================================================================

class BashResult(ToolResult):
    """
    Bash command execution result.

    Raw data schema:
    {
        "stdout": str,
        "stderr": str,
        "return_code": int,
        "cwd": str (optional)
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        Format bash execution result.

        Behavior:
        - Success: return stdout only (empty output filtered).
        - Failure: return stderr and return code.
        - Verbose: append execution time and working directory.
        """
        # Response-level failure (e.g. tool execution exception).
        if not self.success:
            error_msg = self.metadata.get("message", "Command execution failed")
            return f"[Error] {error_msg}"

        stdout = self.raw_data.get("stdout", "")
        stderr = self.raw_data.get("stderr", "")
        return_code = self.raw_data.get("return_code", 0)
        cwd = self.raw_data.get("cwd", "")

        lines = []

        # Successful execution.
        if return_code == 0:
            if stdout.strip():
                lines.append(stdout.rstrip())
            else:
                lines.append("[Command executed successfully with no output]")
        # Failed execution.
        else:
            lines.append(f"[Error] Command failed with return code {return_code}")
            if stderr.strip():
                lines.append(f"Error output:\n{stderr.rstrip()}")
            if stdout.strip():
                lines.append(f"Standard output:\n{stdout.rstrip()}")

        # Verbose mode.
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
# Code execution tool result.
# ============================================================================

class CodeExecutionResult(ToolResult):
    """
    Code execution result.

    Raw data schema:
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
        Format code execution result.

        Behavior:
        - Success: return stdout.
        - Failure: return stderr.
        - Verbose: include resource usage details.
        """
        # Response-level failure (e.g. tool execution exception).
        if not self.success:
            error_msg = self.metadata.get("message", "Code execution failed")
            return f"[Error] {error_msg}"

        stdout = self.raw_data.get("stdout", "")
        stderr = self.raw_data.get("stderr", "")
        return_code = self.raw_data.get("return_code", 0)
        exec_time = self.raw_data.get("execution_time_ms", 0)
        memory = self.raw_data.get("memory_used_mb", 0)

        lines = []

        # Successful execution.
        if return_code == 0:
            if stdout.strip():
                lines.append(stdout.rstrip())
            else:
                lines.append("[Code executed successfully with no output]")
        # Failed execution.
        else:
            lines.append(f"[Error] Code execution failed")
            if stderr.strip():
                lines.append(stderr.rstrip())

        # Verbose mode - resource usage information.
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
# VM tool result.
# ============================================================================

class VMResult(ToolResult):
    """
    VM operation result.

    Keeps only `accessibility_tree` and filters screenshots/other artifacts.
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
# Browser tool result.
# ============================================================================

class BrowserResult(ToolResult):
    """
    Browser operation result.

    Raw data schema (varies by operation):
    - screenshot: {"image_path": str, "size": tuple}
    - navigate: {"url": str, "title": str, "status": int}
    - extract: {"text": str, "html": str}
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        Format browser operation result.

        Returns different formats based on operation type.
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

        # Default: return JSON.
        return json.dumps(self.raw_data, indent=2, ensure_ascii=False)


# ============================================================================
# Web search tool result.
# ============================================================================

class WebSearchResult(ToolResult):
    """
    Web search result (`search` tool).

    Raw data schema:
    {
        "result": str,        # Search result text (markdown)
        "query": str          # Search query (for logs/debug)
    }
    
    Note: success/failure is determined by top-level `code` (`code=0` means
    success). `data` must not include a `success` field.
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        Format web search result.

        Behavior:
        - Default: return result text only (filter metadata like query).
        - Verbose: append query information.
        """
        query = self.raw_data.get("query", "")
        
        # Response-level failure (`code != 0`): return error directly.
        if not self.success:
            error_msg = self.metadata.get("message", "Search failed")
            if query:
                return f"[Search failed for query: {query}] {error_msg}"
            return f"[Search failed] {error_msg}"
        
        # Extract actual result text.
        result_text = self.raw_data.get("result", "")

        # Empty result handling.
        if not result_text.strip():
            if query:
                return f"[No results found for query: {query}]"
            return "[No results found]"

        lines = []
        
        # Default output keeps only key text needed by the agent.
        lines.append(result_text.rstrip())

        # Verbose mode: append query info.
        if verbose and query:
            lines.append(f"\n[Query: {query}]")

        return "\n".join(lines)


# ============================================================================
# RAG search tool result.
# ============================================================================

class RAGSearchResult(ToolResult):
    """
    RAG retrieval result (`rag:search`) - reference implementation.

    This is the standard template for tool return format:
    - Determine success/failure by top-level `code` (`code=0` is success).
    - Keep only core content and required input echoes in `data`.
    - Do not duplicate `success` inside `data`.

    Raw data schema:
    {
        "query": str,         # Retrieval query (echo for logs/debug)
        "context": str        # Retrieved context text (core content)
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        Format RAG retrieval result.

        Behavior:
        - Default: return context text only (filter metadata like query).
        - Verbose: append query information.
        """
        query = self.raw_data.get("query", "")
        
        # Response-level failure (`code != 0`): return error directly.
        if not self.success:
            error_msg = self.metadata.get("message", "RAG search failed")
            if query:
                return f"[RAG search failed for query: {query}] {error_msg}"
            return f"[RAG search failed] {error_msg}"
        
        context = self.raw_data.get("context", "")

        # No-result handling.
        if not context.strip():
            if query:
                return f"[No context found for query: {query}]"
            return "[No context found]"

        lines = []

        # Default output keeps only key context for the agent.
        lines.append(context.rstrip())

        # Verbose mode: append query info.
        if verbose and query:
            lines.append(f"\n[Query: {query}]")

        return "\n".join(lines)


# ============================================================================
# Web visit tool result.
# ============================================================================

class VisitResult(ToolResult):
    """
    Web visit result (`visit` tool).

    Raw data schema:
    {
        "result": str,        # Web content summary (markdown, core content)
        "urls": str,          # Requested URL(s) (input echo)
        "goal": str,          # Visit goal (input echo)
        "warning": str        # Optional warning for partial success
    }
    
    Note: success/failure is determined by top-level `code` (`code=0` means
    success). `data` must not include a `success` field.
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        Format web visit result.

        Behavior:
        - Default: return content summary only (filter urls/goal metadata).
        - Verbose: append URL and goal information.
        """
        urls = self.raw_data.get("urls", "")
        goal = self.raw_data.get("goal", "")
        
        # Response-level failure (`code != 0`): return error directly.
        if not self.success:
            error_msg = self.metadata.get("message", "Visit failed")
            if urls:
                return f"[Failed to visit {urls}] {error_msg}"
            return f"[Visit failed] {error_msg}"
        
        result_text = self.raw_data.get("result", "")
        warning = self.raw_data.get("warning", "")

        # Empty result handling.
        if not result_text.strip():
            if urls:
                return f"[No content extracted from {urls}]"
            return "[No content extracted]"

        lines = []
        
        # Default output keeps only key summary for the agent.
        lines.append(result_text.rstrip())
        
        # Append warning when partially successful.
        if warning:
            lines.append(f"\n[Warning: {warning}]")

        # Verbose mode: append URL and goal info.
        if verbose:
            if urls:
                lines.append(f"\n[URL: {urls}]")
            if goal:
                lines.append(f"[Goal: {goal}]")

        return "\n".join(lines)


# ============================================================================
# Doc tool result.
# ============================================================================

class DocResult(ToolResult):
    """
    Doc QA result (`doc:search` / `doc:read`) and
    data science tool result (`ds:inspect_data` / `ds:read_csv` / `ds:run_python`).

    Expected raw `data` schema:
    {
        "result": str,
        "inputs": {...} (optional, for debug/echo only)
    }
    """

    def to_str(self, verbose: bool = False) -> str:
        # Response-level failure (`code != 0`): return error directly.
        if not self.success:
            error_msg = self.metadata.get("message", "Doc/DS tool failed")
            return f"[Doc/DS tool failed] {error_msg}"

        result_text = self.raw_data.get("result", "")
        if isinstance(result_text, str) and result_text.strip():
            return result_text.rstrip()

        # Fallback: return compact JSON to avoid empty confusing output.
        try:
            return json.dumps(self.raw_data, ensure_ascii=False, indent=2)
        except Exception:
            return str(self.raw_data)


# ============================================================================
# SQL tool result (text2sql).
# ============================================================================

class SQLResult(ToolResult):
    """
    SQL tool result (`text2sql:list_databases`, `text2sql:get_schema`, `text2sql:execute`).

    Raw data schema varies by tool:
    - list_databases: {"result": {"databases": List[str]}}
    - get_schema: {"result": {"db_id": str, "schema": Dict[str, Any]}}
    - execute: {"result": {"columns": List[str], "rows": List[tuple], "row_count": int, "truncated": bool}}
    """

    def to_str(self, verbose: bool = False) -> str:
        """
        Format SQL tool result.

        Behavior:
        - list_databases: return comma-separated database list
        - get_schema: return formatted schema information
        - execute: return formatted table with query results
        """
        # Response-level failure (`code != 0`): return error directly.
        if not self.success:
            error_msg = self.metadata.get("message", "SQL tool failed")
            return f"[SQL tool failed] {error_msg}"

        # Extract result from data.result or data directly
        result_data = self.raw_data.get("result", {})
        if not result_data:
            result_data = self.raw_data

        tool_name = self.tool_name

        # Handle list_databases
        if "list_databases" in tool_name:
            databases = result_data.get("databases", [])
            if databases:
                db_list = ", ".join(databases)
                if verbose:
                    return f"Available databases ({len(databases)}): {db_list}"
                return db_list
            return "[No databases found]"

        # Handle get_schema
        elif "get_schema" in tool_name:
            db_id = result_data.get("db_id", "")
            schema = result_data.get("schema", {})
            
            if not schema:
                return f"[No schema found for database: {db_id}]"
            
            lines = []
            if db_id:
                lines.append(f"Database: {db_id}")
            
            for table_name, table_info in schema.items():
                lines.append(f"\nTable: {table_name}")
                columns = table_info.get("columns", [])
                if columns:
                    col_lines = []
                    for col in columns:
                        col_name = col.get("name", "")
                        col_type = col.get("type", "")
                        is_pk = col.get("pk", False)
                        pk_marker = " (PK)" if is_pk else ""
                        col_lines.append(f"  - {col_name}: {col_type}{pk_marker}")
                    lines.append("\n".join(col_lines))
                
                foreign_keys = table_info.get("foreign_keys", [])
                if foreign_keys:
                    fk_lines = []
                    for fk in foreign_keys:
                        to_table = fk.get("to_table", "")
                        from_col = fk.get("from_col", "")
                        to_col = fk.get("to_col", "")
                        fk_lines.append(f"  - {from_col} -> {to_table}.{to_col}")
                    lines.append("\nForeign Keys:")
                    lines.append("\n".join(fk_lines))
            
            return "\n".join(lines)

        # Handle execute
        elif "execute" in tool_name:
            columns = result_data.get("columns", [])
            rows = result_data.get("rows", [])
            row_count = result_data.get("row_count", 0)
            truncated = result_data.get("truncated", False)
            
            if not columns:
                return "[Query returned no columns]"
            
            lines = []
            
            # Format as table
            if rows:
                # Header
                header = " | ".join(str(col) for col in columns)
                lines.append(header)
                lines.append("-" * len(header))
                
                # Rows
                for row in rows:
                    row_str = " | ".join(str(val) if val is not None else "NULL" for val in row)
                    lines.append(row_str)
                
                # Footer info
                footer = f"\nRows returned: {row_count}"
                if truncated:
                    footer += " (truncated, showing first 100 rows)"
                lines.append(footer)
            else:
                lines.append("[Query returned no rows]")
            
            return "\n".join(lines)

        # Fallback: return JSON
        try:
            return json.dumps(result_data, ensure_ascii=False, indent=2)
        except Exception:
            return str(result_data)


# ============================================================================
# Result formatter factory.
# ============================================================================

class ResultFormatter:
    """
    Result formatter factory.

    Automatically detects tool type and returns matching formatter instance.

    Usage:
    ```python
    # Option 1: format directly.
    formatted_str = ResultFormatter.format_to_str(response)

    # Option 2: get formatter instance.
    formatter = ResultFormatter.format(response)
    formatted_str = formatter.to_str(verbose=True)
    ```
    """

    # Mapping from tool type to formatter class.
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
        Auto-select formatter based on response.

        Only supports the new standardized response format:
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
            response: Full response returned by server.

        Returns:
            Matching `ToolResult` instance.

        Raises:
            ValueError: Invalid response format or missing formatter.
        """
        # Validate response format: `code` and `meta` are required.
        if "code" not in response or "meta" not in response:
            raise ValueError(
                f"Invalid response format: expected 'code' and 'meta' fields. "
                f"Got: {list(response.keys())}"
            )

        # Extract metadata from `meta` and payload from `data`.
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

        # Detect tool type.
        tool_name = metadata.get("tool", "")
        resource_type = metadata.get("resource_type", "")
        
        # Exact matching by tool name first.
        if tool_name == "web:search" and resource_type != "rag":
            formatter_class = WebSearchResult
        elif tool_name == "web:visit":
            formatter_class = VisitResult
        elif tool_name == "rag:search":
            formatter_class = RAGSearchResult
        elif tool_name.startswith("text2sql:") or tool_name.startswith("sql:"):
            formatter_class = SQLResult
        elif (
            tool_name.startswith("doc:")
            or tool_name.startswith("ds:")
            or tool_name.startswith("doc_")
            or tool_name.startswith("ds_")
            or tool_name.startswith("doc-")
            or tool_name.startswith("ds-")
        ):
            formatter_class = DocResult
        else:
            # Prefer resource_type, then infer from tool_name prefix.
            tool_type = resource_type or tool_name.split(":")[0] if ":" in tool_name else tool_name
            
            # Lookup formatter class.
            formatter_class = cls.FORMATTER_MAP.get(tool_type)
            
            # Raise if formatter is not found.
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
        Format response directly into a string.

        Args:
            response: Full response returned by server.
            verbose: Whether to include detailed information.

        Returns:
            Formatted string.
        """
        formatter = cls.format(response)
        return formatter.to_str(verbose=verbose)

    @classmethod
    def register_formatter(cls, tool_type: str, formatter_class: type):
        """
        Register a custom formatter.

        Args:
            tool_type: Tool type identifier.
            formatter_class: Formatter class (must inherit `ToolResult`).

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
# Convenience function.
# ============================================================================

def format_tool_result(response: Dict[str, Any], verbose: bool = False) -> str:
    """
    Convenience helper: format tool execution result.

    Args:
        response: Full response returned by server.
        verbose: Whether to include detailed information.

    Returns:
        Formatted string, ready to use as tool response.

    Example:
    ```python
    from sandbox.result_formatter import format_tool_result

    result = await client.execute("bash:run", {"command": "ls"})
    formatted = format_tool_result(result)
    print(formatted)
    ```
    """
    return ResultFormatter.format_to_str(response, verbose=verbose)
