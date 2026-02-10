# 错误代码详细说明

本文档详细说明 Sandbox 系统中所有错误代码的含义、使用场景和最佳实践。

> **相关文档**:
> - [快速参考](QUICK_REFERENCE.md): API 响应格式和错误代码快速查询
> - [错误代码定义](../server/backends/error_codes.py): 源代码定义

## 📋 目录

1. [错误代码分类](#错误代码分类)
2. [客户端错误 (4xxx)](#客户端错误-4xxx)
3. [服务器错误 (5xxx)](#服务器错误-5xxx)
4. [使用指南](#使用指南)
5. [最佳实践](#最佳实践)

---

## 错误代码分类

Sandbox 使用标准的 HTTP 风格错误代码分类：

| 代码范围 | 类型 | 说明 | 处理建议 |
|---------|------|------|---------|
| `0` | 成功 | 操作成功完成 | 正常处理响应数据 |
| `4xxx` | 客户端错误 | 请求格式错误、参数错误、资源未找到等 | 检查请求参数，修正后重试 |
| `5xxx` | 服务器错误 | 服务器内部错误、API 调用失败等 | 可能需要重试或联系管理员 |

---

## 客户端错误 (4xxx)

### 4001 - INVALID_REQUEST_FORMAT

**含义**: 无效的请求格式

**使用场景**:
- 工具名称不存在或格式错误
- 请求体格式不正确
- 工具名称存在歧义（多个匹配）

**示例**:

```python
# 工具名称不存在
await sandbox.execute("nonexistent_tool", {})
# 返回: {"code": 4001, "message": "Tool not found: nonexistent_tool"}

# 工具名称歧义（多个匹配）
await sandbox.execute("screenshot", {})  # 如果存在 "vm:screenshot" 和 "browser:screenshot"
# 返回: {"code": 4001, "message": "Ambiguous tool name 'screenshot'. Multiple matches: [...]"}
```

**在代码中的使用**:
```python
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import build_error_response

# 工具未找到
return build_error_response(
    code=ErrorCode.INVALID_REQUEST_FORMAT,
    message=f"Tool not found: {action}",
    tool=action,
    data={"action": action}
)
```

**处理建议**: 检查工具名称是否正确，或使用完整的工具名称（如 `vm:screenshot`）

---

### 4002 - MISSING_REQUIRED_FIELD

**含义**: 缺少必填字段

**使用场景**:
- 工具函数需要必填参数但未提供
- 请求中缺少必需的配置项

**示例**:

```python
# 缺少必填参数
await sandbox.execute("web:search", {})  # search 工具需要 query 参数
# 返回: {"code": 4002, "message": "Missing required field: query"}
```

**在代码中的使用**:
```python
if "query" not in params:
    return build_error_response(
        code=ErrorCode.MISSING_REQUIRED_FIELD,
        message="Missing required field: query",
        tool="search",
        data={"required_fields": ["query"]}
    )
```

**处理建议**: 检查请求参数，确保所有必填字段都已提供

**注意**: 如果参数有默认值，则不应返回此错误，而应使用默认值继续执行。

---

### 4003 - INVALID_PARAMETER_TYPE

**含义**: 无效的参数类型

**使用场景**:
- 参数类型不匹配（如期望 `int` 但收到 `str`）
- 参数值格式错误（如期望 URL 但格式不正确）

**示例**:

```python
# 参数类型错误
await sandbox.execute("click", {"x": "100", "y": 200})  # x 应该是 int 但传了 str
# 返回: {"code": 4003, "message": "Invalid parameter type: x must be int, got str"}
```

**在代码中的使用**:
```python
if not isinstance(params.get("x"), int):
    return build_error_response(
        code=ErrorCode.INVALID_PARAMETER_TYPE,
        message=f"Invalid parameter type: x must be int, got {type(params.get('x')).__name__}",
        tool="click",
        data={"parameter": "x", "expected_type": "int", "actual_type": type(params.get("x")).__name__}
    )
```

**处理建议**: 检查参数类型，确保与工具函数签名匹配

**与参数缺失的区别**:
- **参数缺失**: 参数未提供，但有默认值 → 使用默认值，不返回错误
- **参数错误**: 参数提供了，但类型或值不正确 → 返回 `4003` 错误

---

### 4004 - INVALID_URL_FORMAT

**含义**: 无效的 URL 格式

**使用场景**:
- URL 格式不正确
- URL 协议不支持

**示例**:

```python
# URL 格式错误
await sandbox.execute("web:visit", {"url": "not-a-url"})
# 返回: {"code": 4004, "message": "Invalid URL format: not-a-url"}
```

**在代码中的使用**:
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

**处理建议**: 检查 URL 格式，确保包含协议（如 `http://` 或 `https://`）

---

### 4005 - NO_RESULTS_FOUND

**含义**: 未找到结果

**使用场景**:
- 搜索操作未找到匹配结果
- 查询操作返回空结果集

**示例**:

```python
# 搜索无结果
await sandbox.execute("web:search", {"query": "nonexistent_unique_term_xyz"})
# 返回: {"code": 4005, "message": "No results found", "data": {"query": "..."}}
```

**在代码中的使用**:
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

**处理建议**: 这是业务层面的正常情况，可以尝试调整查询条件或向用户说明未找到结果

---

### 4006 - RESOURCE_NOT_INITIALIZED

**含义**: 资源未初始化

**使用场景**:
- Session 创建失败
- 后端资源初始化失败
- 尝试使用未初始化的资源

**示例**:

```python
# Session 创建失败
await sandbox.create_session("vm", {"invalid_config": True})
# 返回: {"code": 4006, "message": "Resource initialization failed: ..."}
```

**在代码中的使用**:
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

**处理建议**: 检查配置是否正确，或尝试重新创建 Session

---

## 服务器错误 (5xxx)

### 5001 - API_KEY_NOT_CONFIGURED

**含义**: API 密钥未配置

**使用场景**:
- 外部 API 需要密钥但未配置
- 环境变量缺失

**示例**:

```python
# API 密钥未配置
await sandbox.execute("web:search", {"query": "test"})  # 如果 SERPER_API_KEY 未设置
# 返回: {"code": 5001, "message": "API key not configured: SERPER_API_KEY"}
```

**在代码中的使用**:
```python
api_key = os.getenv("SERPER_API_KEY")
if not api_key:
    return build_error_response(
        code=ErrorCode.API_KEY_NOT_CONFIGURED,
        message="API key not configured: SERPER_API_KEY",
        tool="search"
    )
```

**处理建议**: 检查环境变量或配置文件，确保 API 密钥已正确配置

---

### 5002 - API_REQUEST_FAILED

**含义**: API 请求失败

**使用场景**:
- 外部 API 调用失败
- 网络连接问题
- API 返回错误状态码

**示例**:

```python
# API 请求失败
await sandbox.execute("web:search", {"query": "test"})
# 返回: {"code": 5002, "message": "API request failed: Connection timeout"}
```

**在代码中的使用**:
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

**处理建议**: 检查网络连接，或稍后重试。如果是临时性错误，可以实现重试机制

---

### 5003 - API_RESPONSE_PARSE_ERROR

**含义**: API 响应解析错误

**使用场景**:
- API 返回的 JSON 格式不正确
- 响应结构不符合预期

**示例**:

```python
# API 响应解析失败
await sandbox.execute("web:search", {"query": "test"})
# 返回: {"code": 5003, "message": "Failed to parse API response: Expecting value: line 1 column 1 (char 0)"}
```

**在代码中的使用**:
```python
try:
    data = response.json()
except json.JSONDecodeError as e:
    return build_error_response(
        code=ErrorCode.API_RESPONSE_PARSE_ERROR,
        message=f"Failed to parse API response: {str(e)}",
        tool="search",
        data={"raw_response": response.text[:200]}  # 只记录前200字符
    )
```

**处理建议**: 检查 API 响应格式，可能需要联系 API 提供方或检查 API 版本

---

### 5004 - UNEXPECTED_ERROR

**含义**: 意外错误

**使用场景**:
- 未预期的异常
- 代码逻辑错误
- 未知的系统错误

**示例**:

```python
# 未预期的异常
await sandbox.execute("some_tool", {})
# 返回: {"code": 5004, "message": "Unexpected error occurred: ...", "data": {"traceback": "..."}}
```

**在代码中的使用**:
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

**处理建议**: 查看日志和 traceback，报告给开发团队

---

### 5005 - TIMEOUT_ERROR

**含义**: 请求超时

**使用场景**:
- 工具执行超时
- 长时间运行的操作被中断

**示例**:

```python
# 执行超时
await sandbox.execute("long_running_tool", {}, timeout=5)
# 返回: {"code": 5005, "message": "Tool execution timed out after 5s"}
```

**在代码中的使用**:
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

**处理建议**: 增加超时时间，或优化工具执行效率

---

### 5006 - CRAWLING_ERROR

**含义**: 爬取错误

**使用场景**:
- 网页爬取失败
- 内容提取失败

**示例**:

```python
# 爬取失败
await sandbox.execute("web:visit", {"url": "https://example.com"})
# 返回: {"code": 5006, "message": "Crawling error: Failed to load page"}
```

**在代码中的使用**:
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

**处理建议**: 检查目标网站是否可访问，或稍后重试

---

### 5007 - SUMMARIZATION_ERROR

**含义**: 摘要错误

**使用场景**:
- 内容摘要生成失败
- LLM 调用失败

**示例**:

```python
# 摘要生成失败
await sandbox.execute("summarize", {"content": "..."})
# 返回: {"code": 5007, "message": "Summarization error: LLM API call failed"}
```

**在代码中的使用**:
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

**处理建议**: 检查 LLM 服务状态，或调整内容长度

---

### 5008 - ALL_REQUESTS_FAILED

**含义**: 所有请求失败

**使用场景**:
- 批量操作中所有请求都失败
- 所有重试都失败

**示例**:

```python
# 批量操作全部失败
await sandbox.execute_batch([
    {"action": "search", "params": {"query": "q1"}},
    {"action": "search", "params": {"query": "q2"}},
])
# 返回: {"code": 5008, "message": "All requests failed", "data": {"results": [...]}}
```

**在代码中的使用**:
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

**处理建议**: 检查所有请求失败的原因，可能需要调整请求参数或重试策略

---

### 5009 - PARTIAL_FAILURE

**含义**: 部分失败

**使用场景**:
- 批量操作中部分请求成功，部分失败
- 部分结果可用但存在错误

**示例**:

```python
# 批量操作部分失败
await sandbox.execute_batch([
    {"action": "search", "params": {"query": "q1"}},  # 成功
    {"action": "search", "params": {"query": "q2"}},  # 失败
])
# 返回: {"code": 5009, "message": "1 out of 2 actions failed", "data": {"results": [...]}}
```

**在代码中的使用**:
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

**处理建议**: 检查失败项的具体错误，部分结果可能仍然可用

---

### 5010 - BACKEND_NOT_INITIALIZED

**含义**: 后端未初始化

**使用场景**:
- 后端资源未预热
- 后端实例未正确加载

**示例**:

```python
# 后端未初始化
await sandbox.execute("rag:search", {"query": "test"})  # 如果 RAG 后端未预热
# 返回: {"code": 5010, "message": "Backend not initialized: RAG backend not warmed up"}
```

**在代码中的使用**:
```python
if not self._model_loaded:
    return build_error_response(
        code=ErrorCode.BACKEND_NOT_INITIALIZED,
        message="Backend not initialized: Model not loaded",
        tool="rag:search"
    )
```

**处理建议**: 确保后端已正确初始化，或调用 `warmup()` 方法预热后端

---

## 使用指南

### 工具执行错误处理

#### 工具名称错误

当工具名称不存在或格式错误时，系统返回 `4001` 错误：

```python
# 错误示例
result = await sandbox.execute("wrong_tool_name", {})
if result["code"] == 4001:
    print(f"工具不存在: {result['message']}")
```

#### 参数错误处理

**参数缺失 vs 参数错误**:

1. **参数缺失**（有默认值）:
   ```python
   # 工具函数定义
   @tool("my_tool")
   async def my_tool(x: int, y: int = 10):  # y 有默认值
       return {"result": x + y}
   
   # 调用时只提供 x，y 使用默认值
   result = await sandbox.execute("my_tool", {"x": 5})  # y 使用默认值 10，不返回错误
   ```

2. **参数缺失**（无默认值，必填）:
   ```python
   # 工具函数定义
   @tool("my_tool")
   async def my_tool(x: int, y: int):  # y 无默认值，必填
       return {"result": x + y}
   
   # 调用时缺少 y
   result = await sandbox.execute("my_tool", {"x": 5})  # 返回 4002 错误
   ```

3. **参数类型错误**:
   ```python
   # 参数类型不匹配
   result = await sandbox.execute("my_tool", {"x": "5", "y": 10})  # x 应该是 int 但传了 str
   # 返回 4003 错误
   ```

### 错误响应结构

所有错误响应都遵循统一的结构：

```python
{
    "code": int,           # 错误代码
    "message": str,        # 错误描述
    "data": dict | None,   # 错误详情（可选）
    "meta": {              # 元数据
        "tool": str,
        "execution_time_ms": float,
        "resource_type": str | None,
        "session_id": str | None,
        "trace_id": str
    }
}
```

### 错误处理最佳实践

1. **检查错误代码**:
   ```python
   result = await sandbox.execute("tool", params)
   
   if result["code"] == 0:
       # 成功
       data = result["data"]
   elif 4000 <= result["code"] < 5000:
       # 客户端错误，修正请求后重试
       print(f"请求错误: {result['message']}")
   else:
       # 服务器错误，可能需要重试
       print(f"服务器错误: {result['message']}")
   ```

2. **处理特定错误**:
   ```python
   result = await sandbox.execute("tool", params)
   
   if result["code"] == ErrorCode.TIMEOUT_ERROR:
       # 超时，可以增加超时时间重试
       result = await sandbox.execute("tool", params, timeout=60)
   elif result["code"] == ErrorCode.API_REQUEST_FAILED:
       # API 失败，可以实现重试逻辑
       for attempt in range(3):
           result = await sandbox.execute("tool", params)
           if result["code"] == 0:
               break
   ```

3. **记录错误详情**:
   ```python
   result = await sandbox.execute("tool", params)
   
   if result["code"] != 0:
       logger.error(f"工具执行失败: {result['message']}")
       logger.error(f"错误代码: {result['code']}")
       logger.error(f"错误详情: {result.get('data', {})}")
       if "traceback" in result.get("data", {}):
           logger.error(f"堆栈跟踪: {result['data']['traceback']}")
   ```

---

## 最佳实践

### 1. 选择合适的错误代码

- **客户端错误 (4xxx)**: 请求问题，用户或调用方可以修正
- **服务器错误 (5xxx)**: 系统问题，可能需要重试或联系管理员

### 2. 提供有意义的错误消息

```python
# ❌ 不好的做法
return build_error_response(
    code=ErrorCode.API_REQUEST_FAILED,
    message="Error",
    tool="search"
)

# ✅ 好的做法
return build_error_response(
    code=ErrorCode.API_REQUEST_FAILED,
    message=f"API request failed: Connection timeout after 30s",
    tool="search",
    data={"url": url, "timeout": 30}
)
```

### 3. 在 data 中提供有用的上下文

```python
return build_error_response(
    code=ErrorCode.INVALID_PARAMETER_TYPE,
    message="Invalid parameter type: x must be int",
    tool="click",
    data={
        "parameter": "x",
        "expected_type": "int",
        "actual_type": type(value).__name__,
        "actual_value": str(value)  # 避免敏感信息
    }
)
```

### 4. 区分参数缺失和参数错误

- **参数缺失 + 有默认值**: 使用默认值，不返回错误
- **参数缺失 + 无默认值**: 返回 `4002` 错误
- **参数错误（类型/值）**: 返回 `4003` 错误

### 5. 实现重试机制

对于临时性错误（如 `5002`, `5005`），可以实现重试：

```python
async def execute_with_retry(action, params, max_retries=3):
    for attempt in range(max_retries):
        result = await sandbox.execute(action, params)
        
        if result["code"] == 0:
            return result
        
        # 只对特定错误重试
        if result["code"] in [ErrorCode.API_REQUEST_FAILED, ErrorCode.TIMEOUT_ERROR]:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
                continue
        
        # 其他错误直接返回
        return result
    
    return result
```

---

## 相关文件

- **错误代码定义**: `sandbox/server/backends/error_codes.py`
- **响应构建器**: `sandbox/server/backends/response_builder.py`
- **工具执行器**: `sandbox/server/core/tool_executor.py`
- **快速参考**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

