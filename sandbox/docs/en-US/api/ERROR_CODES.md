# Error Codes Detailed Documentation

This document provides detailed descriptions of all error codes in the Sandbox system, including usage scenarios and best practices.

> **Related Documentation**:
> - [Quick Reference](QUICK_REFERENCE.md): API response formats and error codes quick reference
> - [Error Code Definitions](../../server/backends/error_codes.py): Source code definitions

## 📋 Table of Contents

1. [Error Code Classification](#error-code-classification)
2. [Client Errors (4xxx)](#client-errors-4xxx)
3. [Server Errors (5xxx)](#server-errors-5xxx)
4. [Usage Guide](#usage-guide)
5. [Best Practices](#best-practices)

---

## Error Code Classification

Sandbox uses standard HTTP-style error code classification:

| Code Range | Type | Description | Handling Suggestion |
|------------|------|-------------|-------------------|
| `0` | Success | Operation completed successfully | Process response data normally |
| `4xxx` | Client Error | Request format error, parameter error, resource not found, etc. | Check request parameters, correct and retry |
| `5xxx` | Server Error | Server internal error, API call failure, etc. | May require retry or contact administrator |

---

## Client Errors (4xxx)

### 4001 - INVALID_REQUEST_FORMAT

**Meaning**: Invalid request format

**Usage Scenarios**:
- Tool name does not exist or format error
- Request body format is incorrect
- Tool name is ambiguous (multiple matches)

**Examples**:

```python
# Tool name does not exist
await sandbox.execute("nonexistent_tool", {})
# Returns: {"code": 4001, "message": "Tool not found: nonexistent_tool"}

# Tool name ambiguous (multiple matches)
await sandbox.execute("screenshot", {})  # If both "vm:screenshot" and "browser:screenshot" exist
# Returns: {"code": 4001, "message": "Ambiguous tool name 'screenshot'. Multiple matches: [...]"}
```

**Usage in Code**:
```python
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import build_error_response

# Tool not found
return build_error_response(
    code=ErrorCode.INVALID_REQUEST_FORMAT,
    message=f"Tool not found: {action}",
    tool=action,
    data={"action": action}
)
```

**Handling Suggestion**: Check if the tool name is correct, or use the full tool name (e.g., `vm:screenshot`)

---

### 4002 - MISSING_REQUIRED_FIELD

**Meaning**: Missing required field

**Usage Scenarios**:
- Tool function requires required parameters but not provided
- Missing required configuration items in request

**Examples**:

```python
# Missing required parameter
await sandbox.execute("web:search", {})  # search tool requires query parameter
# Returns: {"code": 4002, "message": "Missing required field: query"}
```

**Usage in Code**:
```python
if "query" not in params:
    return build_error_response(
        code=ErrorCode.MISSING_REQUIRED_FIELD,
        message="Missing required field: query",
        tool="search",
        data={"required_fields": ["query"]}
    )
```

**Handling Suggestion**: Check request parameters to ensure all required fields are provided

**Note**: If a parameter has a default value, this error should not be returned; instead, use the default value and continue execution.

---

### 4003 - INVALID_PARAMETER_TYPE

**Meaning**: Invalid parameter type

**Usage Scenarios**:
- Parameter type mismatch (e.g., expecting `int` but received `str`)
- Parameter value format error (e.g., expecting URL but format is incorrect)

**Examples**:

```python
# Parameter type error
await sandbox.execute("click", {"x": "100", "y": 200})  # x should be int but passed str
# Returns: {"code": 4003, "message": "Invalid parameter type: x must be int, got str"}
```

**Usage in Code**:
```python
if not isinstance(params.get("x"), int):
    return build_error_response(
        code=ErrorCode.INVALID_PARAMETER_TYPE,
        message=f"Invalid parameter type: x must be int, got {type(params.get('x')).__name__}",
        tool="click",
        data={"parameter": "x", "expected_type": "int", "actual_type": type(params.get("x")).__name__}
    )
```

**Handling Suggestion**: Check parameter types to ensure they match the tool function signature

**Difference from Missing Parameter**:
- **Missing Parameter**: Parameter not provided, but has default value → Use default value, no error returned
- **Parameter Error**: Parameter provided, but type or value is incorrect → Return `4003` error

---

### 4004 - INVALID_URL_FORMAT

**Meaning**: Invalid URL format

**Usage Scenarios**:
- URL format is incorrect
- URL protocol not supported

**Examples**:

```python
# URL format error
await sandbox.execute("web:visit", {"url": "not-a-url"})
# Returns: {"code": 4004, "message": "Invalid URL format: not-a-url"}
```

**Usage in Code**:
```python
from urllib.parse import urlparse

parsed = urlparse(params.get("url"))
if not parsed.scheme or not parsed.netloc:
    return build_error_response(
        code=ErrorCode.INVALID_URL_FORMAT,
        message=f"Invalid URL format: {params.get('url')}",
        tool="visit",
        data={"url": params.get("url")}
    )
```

**Handling Suggestion**: Check URL format to ensure it includes protocol (e.g., `http://` or `https://`)

---

### 4005 - NO_RESULTS_FOUND

**Meaning**: No results found

**Usage Scenarios**:
- Search operation found no matching results
- Query operation returned empty result set

**Examples**:

```python
# Search found no results
await sandbox.execute("web:search", {"query": "nonexistent_unique_term_xyz"})
# Returns: {"code": 4005, "message": "No results found", "data": {"query": "..."}}
```

**Usage in Code**:
```python
results = await search_api(query)
if not results:
    return build_error_response(
        code=ErrorCode.NO_RESULTS_FOUND,
        message="No results found",
        tool="search",
        data={"query": query}
    )
```

**Handling Suggestion**: This is a normal business-level situation. You can try adjusting query conditions or inform the user that no results were found.

---

### 4006 - RESOURCE_NOT_INITIALIZED

**Meaning**: Resource not initialized

**Usage Scenarios**:
- Session creation failed
- Backend resource initialization failed
- Attempting to use uninitialized resource

**Examples**:

```python
# Session creation failed
await sandbox.create_session("vm", {"invalid_config": True})
# Returns: {"code": 4006, "message": "Resource initialization failed: ..."}
```

**Usage in Code**:
```python
try:
    session_info = await backend.initialize(worker_id, config)
    if session_info.get("status") == "error":
        return build_error_response(
            code=ErrorCode.RESOURCE_NOT_INITIALIZED,
            message=f"Resource initialization failed: {session_info.get('error')}",
            tool=full_name,
            data={"resource_type": resource_type, "details": session_info.get("error")}
        )
except Exception as e:
    return build_error_response(
        code=ErrorCode.RESOURCE_NOT_INITIALIZED,
        message=f"Resource initialization failed: {str(e)}",
        tool=full_name,
        data={"resource_type": resource_type}
    )
```

**Handling Suggestion**: Check if configuration is correct, or try recreating the Session

---

## Server Errors (5xxx)

### 5001 - API_KEY_NOT_CONFIGURED

**Meaning**: API key not configured

**Usage Scenarios**:
- External API requires key but not configured
- Environment variable missing

**Examples**:

```python
# API key not configured
await sandbox.execute("web:search", {"query": "test"})  # If SERPER_API_KEY is not set
# Returns: {"code": 5001, "message": "API key not configured: SERPER_API_KEY"}
```

**Usage in Code**:
```python
api_key = os.getenv("SERPER_API_KEY")
if not api_key:
    return build_error_response(
        code=ErrorCode.API_KEY_NOT_CONFIGURED,
        message="API key not configured: SERPER_API_KEY",
        tool="search"
    )
```

**Handling Suggestion**: Check environment variables or configuration files to ensure API key is correctly configured

---

### 5002 - API_REQUEST_FAILED

**Meaning**: API request failed

**Usage Scenarios**:
- External API call failed
- Network connection issue
- API returned error status code

**Examples**:

```python
# API request failed
await sandbox.execute("web:search", {"query": "test"})
# Returns: {"code": 5002, "message": "API request failed: Connection timeout"}
```

**Usage in Code**:
```python
try:
    response = await http_client.get(url, params=params)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    return build_error_response(
        code=ErrorCode.API_REQUEST_FAILED,
        message=f"API request failed: {str(e)}",
        tool="search",
        data={"url": url, "params": params}
    )
```

**Handling Suggestion**: Check network connection, or retry later. If it's a temporary error, you can implement a retry mechanism

---

### 5003 - API_RESPONSE_PARSE_ERROR

**Meaning**: API response parse error

**Usage Scenarios**:
- API returned JSON format is incorrect
- Response structure does not match expectations

**Examples**:

```python
# API response parsing failed
await sandbox.execute("web:search", {"query": "test"})
# Returns: {"code": 5003, "message": "Failed to parse API response: Expecting value: line 1 column 1 (char 0)"}
```

**Usage in Code**:
```python
try:
    data = response.json()
except json.JSONDecodeError as e:
    return build_error_response(
        code=ErrorCode.API_RESPONSE_PARSE_ERROR,
        message=f"Failed to parse API response: {str(e)}",
        tool="search",
        data={"raw_response": response.text[:200]}  # Only record first 200 characters
    )
```

**Handling Suggestion**: Check API response format, may need to contact API provider or check API version

---

### 5004 - UNEXPECTED_ERROR

**Meaning**: Unexpected error

**Usage Scenarios**:
- Unexpected exception
- Code logic error
- Unknown system error

**Examples**:

```python
# Unexpected exception
await sandbox.execute("some_tool", {})
# Returns: {"code": 5004, "message": "Unexpected error occurred: ...", "data": {"traceback": "..."}}
```

**Usage in Code**:
```python
try:
    result = await do_work()
    return build_success_response(data=result, tool="my_tool")
except Exception as e:
    logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
    return build_error_response(
        code=ErrorCode.UNEXPECTED_ERROR,
        message=str(e),
        tool="my_tool",
        data={"traceback": traceback.format_exc()}
    )
```

**Handling Suggestion**: Check logs and traceback, report to development team

---

### 5005 - TIMEOUT_ERROR

**Meaning**: Request timeout

**Usage Scenarios**:
- Tool execution timeout
- Long-running operation interrupted

**Examples**:

```python
# Execution timeout
await sandbox.execute("long_running_tool", {}, timeout=5)
# Returns: {"code": 5005, "message": "Tool execution timed out after 5s"}
```

**Usage in Code**:
```python
try:
    result = await asyncio.wait_for(func(**params), timeout=timeout)
except asyncio.TimeoutError:
    return build_error_response(
        code=ErrorCode.TIMEOUT_ERROR,
        message=f"Tool execution timed out after {timeout}s",
        tool=full_name,
        data={"timeout": timeout}
    )
```

**Handling Suggestion**: Increase timeout time, or optimize tool execution efficiency

---

### 5006 - CRAWLING_ERROR

**Meaning**: Crawling error

**Usage Scenarios**:
- Web page crawling failed
- Content extraction failed

**Examples**:

```python
# Crawling failed
await sandbox.execute("web:visit", {"url": "https://example.com"})
# Returns: {"code": 5006, "message": "Crawling error: Failed to load page"}
```

**Usage in Code**:
```python
try:
    content = await crawl_page(url)
except Exception as e:
    return build_error_response(
        code=ErrorCode.CRAWLING_ERROR,
        message=f"Crawling error: {str(e)}",
        tool="visit",
        data={"url": url}
    )
```

**Handling Suggestion**: Check if target website is accessible, or retry later

---

### 5007 - SUMMARIZATION_ERROR

**Meaning**: Summarization error

**Usage Scenarios**:
- Content summarization generation failed
- LLM call failed

**Examples**:

```python
# Summarization generation failed
await sandbox.execute("summarize", {"content": "..."})
# Returns: {"code": 5007, "message": "Summarization error: LLM API call failed"}
```

**Usage in Code**:
```python
try:
    summary = await llm.summarize(content)
except Exception as e:
    return build_error_response(
        code=ErrorCode.SUMMARIZATION_ERROR,
        message=f"Summarization error: {str(e)}",
        tool="summarize",
        data={"content_length": len(content)}
    )
```

**Handling Suggestion**: Check LLM service status, or adjust content length

---

### 5008 - ALL_REQUESTS_FAILED

**Meaning**: All requests failed

**Usage Scenarios**:
- All requests in batch operation failed
- All retries failed

**Examples**:

```python
# All batch operations failed
await sandbox.execute_batch([
    {"action": "search", "params": {"query": "q1"}},
    {"action": "search", "params": {"query": "q2"}},
])
# Returns: {"code": 5008, "message": "All requests failed", "data": {"results": [...]}}
```

**Usage in Code**:
```python
results = await batch_process(items)
success_count = sum(1 for r in results if r.get("code") == 0)

if success_count == 0:
    return build_error_response(
        code=ErrorCode.ALL_REQUESTS_FAILED,
        message="All requests failed",
        tool="batch:execute",
        data={"results": results, "total": len(items)}
    )
```

**Handling Suggestion**: Check reasons for all request failures, may need to adjust request parameters or retry strategy

---

### 5009 - PARTIAL_FAILURE

**Meaning**: Partial failure

**Usage Scenarios**:
- Some requests succeeded, some failed in batch operation
- Some results available but errors exist

**Examples**:

```python
# Partial batch operation failure
await sandbox.execute_batch([
    {"action": "search", "params": {"query": "q1"}},  # Success
    {"action": "search", "params": {"query": "q2"}},  # Failed
])
# Returns: {"code": 5009, "message": "1 out of 2 actions failed", "data": {"results": [...]}}
```

**Usage in Code**:
```python
results = await batch_process(items)
success_count = sum(1 for r in results if r.get("code") == 0)
failed_count = len(items) - success_count

if failed_count > 0 and success_count > 0:
    return build_error_response(
        code=ErrorCode.PARTIAL_FAILURE,
        message=f"{failed_count} out of {len(items)} actions failed",
        tool="batch:execute",
        data={"results": results, "success_count": success_count, "failed_count": failed_count}
    )
```

**Handling Suggestion**: Check specific errors of failed items, partial results may still be usable

---

### 5010 - BACKEND_NOT_INITIALIZED

**Meaning**: Backend not initialized

**Usage Scenarios**:
- Backend resource not warmed up
- Backend instance not correctly loaded

**Examples**:

```python
# Backend not initialized
await sandbox.execute("rag:search", {"query": "test"})  # If RAG backend not warmed up
# Returns: {"code": 5010, "message": "Backend not initialized: RAG backend not warmed up"}
```

**Usage in Code**:
```python
if not self._model_loaded:
    return build_error_response(
        code=ErrorCode.BACKEND_NOT_INITIALIZED,
        message="Backend not initialized: Model not loaded",
        tool="rag:search"
    )
```

**Handling Suggestion**: Ensure backend is correctly initialized, or call `warmup()` method to warm up backend

---

## Usage Guide

### Tool Execution Error Handling

#### Tool Name Error

When tool name does not exist or format is incorrect, system returns `4001` error:

```python
# Error example
result = await sandbox.execute("wrong_tool_name", {})
if result["code"] == 4001:
    print(f"Tool does not exist: {result['message']}")
```

#### Parameter Error Handling

**Missing Parameter vs Parameter Error**:

1. **Missing Parameter** (with default value):
   ```python
   # Tool function definition
   @tool("my_tool")
   async def my_tool(x: int, y: int = 10):  # y has default value
       return {"result": x + y}
   
   # Only provide x when calling, y uses default value
   result = await sandbox.execute("my_tool", {"x": 5})  # y uses default value 10, no error returned
   ```

2. **Missing Parameter** (no default value, required):
   ```python
   # Tool function definition
   @tool("my_tool")
   async def my_tool(x: int, y: int):  # y has no default value, required
       return {"result": x + y}
   
   # Missing y when calling
   result = await sandbox.execute("my_tool", {"x": 5})  # Returns 4002 error
   ```

3. **Parameter Type Error**:
   ```python
   # Parameter type mismatch
   result = await sandbox.execute("my_tool", {"x": "5", "y": 10})  # x should be int but passed str
   # Returns 4003 error
   ```

### Error Response Structure

All error responses follow a unified structure:

```python
{
    "code": int,           # Error code
    "message": str,        # Error description
    "data": dict | None,   # Error details (optional)
    "meta": {              # Metadata
        "tool": str,
        "execution_time_ms": float,
        "resource_type": str | None,
        "session_id": str | None,
        "trace_id": str
    }
}
```

### Error Handling Best Practices

1. **Check Error Code**:
   ```python
   result = await sandbox.execute("tool", params)
   
   if result["code"] == 0:
       # Success
       data = result["data"]
   elif 4000 <= result["code"] < 5000:
       # Client error, correct request and retry
       print(f"Request error: {result['message']}")
   else:
       # Server error, may need retry
       print(f"Server error: {result['message']}")
   ```

2. **Handle Specific Errors**:
   ```python
   result = await sandbox.execute("tool", params)
   
   if result["code"] == ErrorCode.TIMEOUT_ERROR:
       # Timeout, can increase timeout and retry
       result = await sandbox.execute("tool", params, timeout=60)
   elif result["code"] == ErrorCode.API_REQUEST_FAILED:
       # API failed, can implement retry logic
       for attempt in range(3):
           result = await sandbox.execute("tool", params)
           if result["code"] == 0:
               break
   ```

3. **Log Error Details**:
   ```python
   result = await sandbox.execute("tool", params)
   
   if result["code"] != 0:
       logger.error(f"Tool execution failed: {result['message']}")
       logger.error(f"Error code: {result['code']}")
       logger.error(f"Error details: {result.get('data', {})}")
       if "traceback" in result.get("data", {}):
           logger.error(f"Stack trace: {result['data']['traceback']}")
   ```

---

## Best Practices

### 1. Choose Appropriate Error Code

- **Client Errors (4xxx)**: Request issues, user or caller can correct
- **Server Errors (5xxx)**: System issues, may require retry or contact administrator

### 2. Provide Meaningful Error Messages

```python
# ❌ Bad practice
return build_error_response(
    code=ErrorCode.API_REQUEST_FAILED,
    message="Error",
    tool="search"
)

# ✅ Good practice
return build_error_response(
    code=ErrorCode.API_REQUEST_FAILED,
    message=f"API request failed: Connection timeout after 30s",
    tool="search",
    data={"url": url, "timeout": 30}
)
```

### 3. Provide Useful Context in data

```python
return build_error_response(
    code=ErrorCode.INVALID_PARAMETER_TYPE,
    message="Invalid parameter type: x must be int",
    tool="click",
    data={
        "parameter": "x",
        "expected_type": "int",
        "actual_type": type(value).__name__,
        "actual_value": str(value)  # Avoid sensitive information
    }
)
```

### 4. Distinguish Missing Parameter and Parameter Error

- **Missing Parameter + Has Default Value**: Use default value, no error returned
- **Missing Parameter + No Default Value**: Return `4002` error
- **Parameter Error (type/value)**: Return `4003` error

### 5. Implement Retry Mechanism

For temporary errors (such as `5002`, `5005`), you can implement retry:

```python
async def execute_with_retry(action, params, max_retries=3):
    for attempt in range(max_retries):
        result = await sandbox.execute(action, params)
        
        if result["code"] == 0:
            return result
        
        # Only retry for specific errors
        if result["code"] in [ErrorCode.API_REQUEST_FAILED, ErrorCode.TIMEOUT_ERROR]:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        # Other errors return directly
        return result
    
    return result
```

---

## Related Files

- **Error Code Definitions**: `sandbox/server/backends/error_codes.py`
- **Response Builder**: `sandbox/server/backends/response_builder.py`
- **Tool Executor**: `sandbox/server/core/tool_executor.py`
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

