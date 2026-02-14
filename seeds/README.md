# RAG Synthesis - 多工具调用与结果格式化

## 概述

本目录包含在 `rag_synthesis` 模块中使用 Sandbox 客户端进行多工具调用，并使用 `format_tool_result` 格式化结果的完整示例。

## 文件说明

### 1. `multi_tool_demo_mock.py` - 模拟数据版本 ⭐

使用模拟数据演示格式化效果，无需运行服务器。

**功能:**
- 使用预定义的模拟响应数据
- 演示 5 种工具的格式化效果 (WebSearch, WebVisit, RAG Search, Bash, Code Execution)
- 详细展示每一步的输出结果
- 对比原始数据和格式化后的数据
- 展示 Agent 集成场景

**运行方式:**
```bash
python rag_synthesis/examples/multi_tool_demo_mock.py
```

**优势:**
- ✅ 无需运行服务器
- ✅ 快速查看格式化效果
- ✅ 适合学习和演示

## 演示内容

### 工具类型

示例涵盖以下工具类型：

1. **WebSearch** - 网络搜索
2. **WebVisit** - 网页访问
3. **RAG Search** - RAG 检索
4. **Bash** - Bash 命令执行
5. **Code Execution** - 代码执行

### 展示步骤

每个工具的演示包含以下步骤：

1. **原始响应** - 显示服务器返回的完整 JSON 数据
2. **格式化结果（简洁模式）** - 过滤冗余信息，只保留核心内容
3. **格式化结果（详细模式）** - 包含额外的元数据和执行信息
4. **过滤效果对比** - 对比原始数据和格式化后的数据长度
5. **ResultFormatter 详细信息** - 展示格式化器的高级功能

## 格式化效果

根据模拟数据的测试结果：

| 工具 | 原始长度 | 简洁模式 | 详细模式 | 压缩比例 |
|------|---------|---------|---------|---------|
| WebSearch | 1070 字符 | 751 字符 | 751 字符 | 29.8% |
| WebVisit | 711 字符 | 529 字符 | 529 字符 | 25.6% |
| RAG Search | 996 字符 | 372 字符 | 934 字符 | **62.7%** |
| Bash | 134 字符 | 53 字符 | 116 字符 | **60.4%** |
| Code Execution | 203 字符 | 100 字符 | 147 字符 | 50.7% |

**关键发现:**
- RAG Search 和 Bash 工具的压缩效果最显著（60%+）
- 格式化后的结果更适合 Agent 理解和处理
- 简洁模式适合 Agent 使用，详细模式适合调试

## 使用示例

### 基本使用

```python
from sandbox import HTTPServiceClient
from sandbox.result_formatter import format_tool_result

async with HTTPServiceClient(base_url="http://localhost:8080") as client:
    # 调用工具
    response = await client.execute("rag:search", {
        "query": "什么是机器学习？",
        "top_k": 5
    })

    # 格式化结果
    formatted = format_tool_result(response, verbose=False)

    # 使用格式化后的结果
    print(formatted)
```

### Agent 集成

```python
class MyAgent:
    async def call_tool(self, tool_name, params):
        # 1. 调用工具
        response = await self.client.execute(tool_name, params)

        # 2. 格式化结果
        formatted = format_tool_result(response)

        # 3. 构建 tool response
        return {
            "role": "tool",
            "content": formatted,
            "tool_call_id": "call_123",
            "name": tool_name
        }
```

### 数据合成

```python
# 执行工具
response = await client.execute("bash:run", {"command": "ls"})

# 格式化为 tool response
tool_response = format_tool_result(response)

# 构建训练样本
training_sample = {
    "messages": [
        {"role": "user", "content": "List files"},
        {"role": "assistant", "content": "...", "tool_calls": [...]},
        {"role": "tool", "content": tool_response}
    ]
}
```

## 核心优势

1. **自动识别** - 自动识别工具类型并应用对应格式化器
2. **智能过滤** - 过滤冗余信息，只保留关键内容
3. **双模式** - 支持简洁和详细两种模式
4. **显著压缩** - 压缩比例通常在 30%-70%
5. **即插即用** - 可直接用于 Agent 的 tool response

## 运行结果示例

### RAG Search 工具

**原始数据（1310 字符）:**
```json
{
  "query": "什么是机器学习？",
  "results": [
    {
      "text": "机器学习是人工智能的一个分支...",
      "score": 0.95,
      "metadata": {"source": "ml_basics.pdf", "page": 5}
    },
    ...
  ],
  "total": 5
}
```

**格式化后（372 字符，压缩 71.6%）:**
```
机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进，而无需明确编程。
机器学习的主要类型包括监督学习、无监督学习和强化学习。
常见的机器学习算法包括线性回归、逻辑回归、决策树、随机森林、支持向量机、神经网络等。
...
```

### Bash 工具

**原始数据（144 字符）:**
```json
{
  "stdout": "main.py\nutils.py\nconfig.py\nREADME.md\nrequirements.txt\n",
  "stderr": "",
  "return_code": 0,
  "cwd": "/home/user/project"
}
```

**格式化后（53 字符，压缩 63.2%）:**
```
main.py
utils.py
config.py
README.md
requirements.txt
```

## 相关文档

- **完整文档**: [sandbox/docs/RESULT_FORMATTER.md](../../sandbox/docs/RESULT_FORMATTER.md)
- **快速入门**: [sandbox/docs/RESULT_FORMATTER_QUICKSTART.md](../../sandbox/docs/RESULT_FORMATTER_QUICKSTART.md)
- **实现总结**: [sandbox/docs/RESULT_FORMATTER_SUMMARY.md](../../sandbox/docs/RESULT_FORMATTER_SUMMARY.md)

## 下一步

1. 运行模拟数据版本查看效果
2. 启动 Sandbox 服务器并按需自行编写工具调用脚本做联调
3. 集成到你的 Agent 或数据合成流程中
4. 根据需要注册自定义格式化器

## 技术支持

如有问题，请参考：
- Sandbox 文档: `sandbox/README.md`
- Result Formatter 文档: `sandbox/docs/RESULT_FORMATTER.md`
- 测试用例: `sandbox/tests/test_result_formatter.py`
