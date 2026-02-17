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

> **Detailed Documentation**: See [Error Codes Documentation](ERROR_CODES.md) for detailed descriptions, usage scenarios, and best practices for each error code.

### Success
| Code | Meaning |
|------|---------|
| 0 | Success |

### Client Errors (4xxx)
| Code | Meaning | Usage Scenario |
|------|---------|----------------|
| 4001 | Invalid request format | Tool name does not exist, format error, or ambiguous |
| 4002 | Missing required field | Missing required parameter (no default value) |
| 4003 | Invalid parameter type | Parameter type mismatch |
| 4004 | Invalid URL format | URL format is incorrect |
| 4005 | No results found | Search or query found no results |
| 4006 | Resource not initialized | Session or resource initialization failed |

### Server Errors (5xxx)
| Code | Meaning | Usage Scenario |
|------|---------|----------------|
| 5001 | API key not configured | API key not configured |
| 5002 | API request failed | External API call failed |
| 5003 | API response parse error | API response parsing failed |
| 5004 | Unexpected error | Unexpected exception |
| 5005 | Timeout error | Request execution timeout |
| 5006 | Crawling error | Web crawling failed |
| 5007 | Summarization error | Content summarization failed |
| 5008 | All requests failed | All batch operations failed |
| 5009 | Partial failure | Partial batch operation failure |
| 5010 | Backend not initialized | Backend resource not initialized |

### Error Code Classification

- **4xxx (Client Errors)**: Request issues, usually can be resolved by correcting request parameters
- **5xxx (Server Errors)**: System issues, may require retry or contact administrator

### Parameter Processing

- **Missing parameter (with default value)**: Use default value, no error returned
- **Missing parameter (no default value)**: Return `4002` error
- **Invalid parameter type**: Return `4003` error
- **Invalid tool name**: Return `4001` error

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
- **Error Codes Documentation**: [ERROR_CODES.md](ERROR_CODES.md) - Detailed error code descriptions and usage guide
- **Response Builder**: `sandbox/server/backends/response_builder.py`
- **Full Guide**: `sandbox/docs/zh-CN/development/BACKEND_DEVELOPMENT.md`
- **Examples**:
  - WebSearch: `sandbox/server/backends/tools/websearch.py:692-840`
  - RAG: `sandbox/server/backends/resources/rag.py:557-756`

