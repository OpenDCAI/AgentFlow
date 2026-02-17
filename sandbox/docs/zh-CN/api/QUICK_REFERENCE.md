# Quick Reference: New Response Format

## Response Structure

```python
{
    "code": int,           # 0 = success, 4xxx = client error, 5xxx = server error
    "message": str,        # "success" or error description
    "data": dict | None,   # Business data (tool-specific)
    "meta": {              # Metadata (tracking info)
        "tool": str,
        "execution_time_ms": float,
        "resource_type": str | None,
        "session_id": str | None,
        "trace_id": str
    }
}
```

## Error Codes

> **详细说明**: 查看 [错误代码详细文档](ERROR_CODES.md) 了解每个错误代码的详细说明、使用场景和最佳实践。

### 成功
| Code | Meaning |
|------|---------|
| 0 | Success |

### 客户端错误 (4xxx)
| Code | Meaning | 使用场景 |
|------|---------|---------|
| 4001 | Invalid request format | 工具名称不存在、格式错误或存在歧义 |
| 4002 | Missing required field | 缺少必填参数（无默认值） |
| 4003 | Invalid parameter type | 参数类型不匹配 |
| 4004 | Invalid URL format | URL 格式不正确 |
| 4005 | No results found | 搜索或查询未找到结果 |
| 4006 | Resource not initialized | Session 或资源初始化失败 |

### 服务器错误 (5xxx)
| Code | Meaning | 使用场景 |
|------|---------|---------|
| 5001 | API key not configured | API 密钥未配置 |
| 5002 | API request failed | 外部 API 调用失败 |
| 5003 | API response parse error | API 响应解析失败 |
| 5004 | Unexpected error | 未预期的异常 |
| 5005 | Timeout error | 请求执行超时 |
| 5006 | Crawling error | 网页爬取失败 |
| 5007 | Summarization error | 内容摘要生成失败 |
| 5008 | All requests failed | 批量操作全部失败 |
| 5009 | Partial failure | 批量操作部分失败 |
| 5010 | Backend not initialized | 后端资源未初始化 |

### 错误代码分类说明

- **4xxx (客户端错误)**: 请求问题，通常可以通过修正请求参数解决
- **5xxx (服务器错误)**: 系统问题，可能需要重试或联系管理员

### 参数处理说明

- **参数缺失（有默认值）**: 使用默认值，不返回错误
- **参数缺失（无默认值）**: 返回 `4002` 错误
- **参数类型错误**: 返回 `4003` 错误
- **工具名称错误**: 返回 `4001` 错误

## Usage Examples

### Building Success Response

```python
from sandbox.server.backends.response_builder import build_success_response, ResponseTimer

async def my_tool(query: str, session_id=None, trace_id=None):
    with ResponseTimer() as timer:
        result = do_work(query)
        return build_success_response(
            data={"result": result, "query": query},
            tool="my_tool",
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
```

### Building Error Response

```python
from sandbox.server.backends.response_builder import build_error_response
from sandbox.server.backends.error_codes import ErrorCode

return build_error_response(
    code=ErrorCode.API_REQUEST_FAILED,
    message="Connection timeout",
    tool="my_tool",
    data={"query": query},  # Optional partial data
    execution_time_ms=timer.get_elapsed_ms(),
    resource_type="my_resource",
    session_id=session_id,
    trace_id=trace_id
)
```

### Consuming Responses

```python
# Check success
if response["code"] == 0:
    # Access business data
    result = response["data"]["result"]
    query = response["data"]["query"]

    # Access metadata
    exec_time = response["meta"]["execution_time_ms"]
    trace_id = response["meta"]["trace_id"]
else:
    # Handle error
    error_code = response["code"]
    error_msg = response["message"]
    partial_data = response["data"]  # May contain partial results
```

## Tool-Specific Data Fields

### search
```python
data = {
    "result": str,  # Search results
    "query": str    # Original query
}
```

### visit
```python
data = {
    "result": str,        # Extracted content
    "urls": list[str],    # URLs visited
    "goal": str,          # Extraction goal
    "warning": str        # Optional, for partial success
}
```

### rag:search
```python
data = {
    "query": str,    # Original query
    "context": str   # Retrieved documents
}
```

### rag:batch_search
```python
data = {
    "count": int,           # Number of queries
    "contexts": list[str],  # Retrieved documents
    "errors": list[dict]    # Optional, for failures
}
```

## Migration Checklist

- [ ] Import error codes and response builder
- [ ] Add `session_id` and `trace_id` parameters
- [ ] Wrap function with `ResponseTimer`
- [ ] Replace `return {"success": ...}` with `build_success_response()`
- [ ] Replace error returns with `build_error_response()`
- [ ] Update tests to check `code` instead of `success`
- [ ] Update documentation

## Common Patterns

### Pattern 1: Simple Success/Error

```python
with ResponseTimer() as timer:
    try:
        result = do_work()
        return build_success_response(
            data={"result": result},
            tool="my_tool",
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
    except Exception as e:
        return build_error_response(
            code=ErrorCode.UNEXPECTED_ERROR,
            message=str(e),
            tool="my_tool",
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
```

### Pattern 2: Conditional Success/Error

```python
with ResponseTimer() as timer:
    result_dict = external_api_call()

    if result_dict.get("success"):
        return build_success_response(
            data={"result": result_dict["result"]},
            tool="my_tool",
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
    else:
        return build_error_response(
            code=ErrorCode.API_REQUEST_FAILED,
            message=result_dict.get("error", "Unknown error"),
            tool="my_tool",
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
```

### Pattern 3: Partial Success

```python
with ResponseTimer() as timer:
    results = process_batch(items)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    if not successful:
        # All failed
        return build_error_response(
            code=ErrorCode.ALL_REQUESTS_FAILED,
            message="All items failed",
            tool="my_tool",
            data={"results": results},
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
    elif failed:
        # Partial failure
        return build_error_response(
            code=ErrorCode.PARTIAL_FAILURE,
            message=f"{len(failed)} out of {len(results)} items failed",
            tool="my_tool",
            data={"results": results, "failed_count": len(failed)},
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
    else:
        # All successful
        return build_success_response(
            data={"results": results},
            tool="my_tool",
            execution_time_ms=timer.get_elapsed_ms(),
            resource_type="my_resource",
            session_id=session_id,
            trace_id=trace_id
        )
```

## Testing

```python
async def test_my_tool_success():
    result = await my_tool(query="test")

    # Check structure
    assert "code" in result
    assert "message" in result
    assert "data" in result
    assert "meta" in result

    # Check success
    assert result["code"] == 0
    assert result["message"] == "success"

    # Check data
    assert "result" in result["data"]

    # Check meta
    assert result["meta"]["tool"] == "my_tool"
    assert result["meta"]["execution_time_ms"] > 0
    assert result["meta"]["trace_id"] is not None

async def test_my_tool_error():
    result = await my_tool(query="")

    # Check error
    assert result["code"] != 0
    assert result["message"] != "success"

    # Meta should still be present
    assert result["meta"]["tool"] == "my_tool"
```

## Files Reference

- **Error Codes**: `sandbox/server/backends/error_codes.py`
- **Error Codes Documentation**: [ERROR_CODES.md](ERROR_CODES.md) - 详细的错误代码说明和使用指南
- **Response Builder**: `sandbox/server/backends/response_builder.py`
- **Full Guide**: `sandbox/docs/zh-CN/development/BACKEND_DEVELOPMENT.md`
- **Examples**:
  - WebSearch: `sandbox/server/backends/tools/websearch.py:692-840`
  - RAG: `sandbox/server/backends/resources/rag.py:557-756`
