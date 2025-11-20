这是一个基于 `src/envs/enviroment.py` 源码分析后重构的文档。我已将**开发指南**、**核心接口契约**以及**资源管理机制**整合到原有结构中，并修正了 API 参考部分以匹配实际代码。

-----

# AgentFlow Environment

这个模块提供了基于继承的 `Environment` 类体系，用于管理 AgentFlow 中的工具、配置、系统提示词以及底层资源。

## 功能特性

  - **继承架构**: 使用抽象基类 `Environment`，强制规范子类实现核心接口。
  - **工具管理**: 自动化管理工具注册 (`register_tool`)、Schema 生成及安全执行 (`execute_tool`)。
  - **任务闭环**: 通过 `run_task` 接口定义 Agent 的完整执行逻辑 (Prompt -\> LLM -\> Tool -\> Result)。
  - **资源管理**: 支持重型资源（如虚拟机、浏览器）的生命周期管理 (`setup_global_resources`, `env_start`, `env_close`)。
  - **Prompt 系统**: 集成 `prompts` 模块，支持自动注入工具描述和动态占位符。

## 快速开始

### 基本使用

```python
from envs import create_math_environment

# 1. 创建环境
env = create_math_environment(model_name="gpt-4")

# 2. 手动测试工具 (Debug 用)
result = env.execute_tool("calculator", {"expressions": ["2+2", "sqrt(16)"]})
print(result)

# 3. 运行完整任务 (Agent 模式)
task = {"question": "Calculate 2+2", "id": "test_01"}
result = env.run_task(task, agent_config={}, logger=None)
print(result)
```

## 开发指南 (Development Guide)

开发新环境（如 `CodingEnv`）需遵循以下核心步骤：

### 1\. 继承与接口实现

所有环境必须继承自 `Environment` 类，并实现以下三个抽象成员：

  * **`mode` (属性)**: 定义环境的唯一标识符（如 `"math"`, `"web"`）。该标识符用于查找对应的 System Prompt。
  * **`_initialize_tools(self)`**: 在此方法中实例化并注册所需工具。
      * *规范*: 使用 `self.register_tool(tool_instance)`。
  * **`run_task(self, task, ...)`**: 定义 Agent 的核心执行循环。
      * *职责*: 组装 Prompt -\> 调用 LLM -\> 解析结果 -\> 调用 `self.execute_tool` -\> 返回包含 `answer` 的结果字典。

### 2\. 提示词配置 (System Prompt)

在 `src/prompts/system_prompts.py` 中定义环境的 Prompt 模板，并在 `SYSTEM_PROMPTS` 字典中注册。

  * *要求*: 必须包含 `{tool_descriptions}` 占位符，框架会自动注入工具描述。

### 3\. 资源管理 (可选)

对于需要虚拟机或 API 连接的重资源环境：

  * 重写类方法 `@classmethod setup_global_resources(cls, config)` 初始化全局资源池。
  * 重写 `env_start()` 和 `env_close()` 管理单个任务的资源生命周期。

### 代码模板

```python
class MyCustomEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "custom_mode"

    def _initialize_tools(self):
        self.register_tool(MyTool())

    def run_task(self, task, agent_config, logger) -> Dict:
        # 实现 Agent 思考与执行循环
        prompt = self.get_system_prompt(task_question=task['question'])
        # ... LLM 调用 ...
        return {"answer": "final_result", "success": True}
```

## API 参考

### Environment 基类

#### 构造函数

```python
Environment(
    model_name: str = "gpt-4.1-2025-04-14",
    resource_manager: Optional['ResourceManager'] = None,
    **kwargs
)
```

#### 核心抽象接口 (必须实现)

  - `mode` (property): 返回环境模式名称。
  - `_initialize_tools()`: 注册环境所需的工具。
  - `run_task(task, agent_config, logger)`: 执行具体的 Agent 任务逻辑。

#### 工具与执行方法

  - `register_tool(tool: Tool)`: 注册工具并更新 Schema。
  - `list_tools() -> List[str]`: 列出可用工具名称。
  - `get_tool(name: str)`: 获取工具实例。
  - `execute_tool(tool_name: str, params: Union[str, dict], **kwargs)`: **[关键]** 执行工具的安全包装器，包含错误处理。
  - `get_tool_schemas()`: 获取 OpenAI 格式的工具定义。
  - `get_tool_descriptions()`: 获取用于 Prompt 的工具描述文本。

#### 资源与生命周期

  - `setup_global_resources(config)`: (类方法) 初始化全局资源管理器。
  - `env_start()`: Benchmark 开始时的钩子 (如分配 VM)。
  - `env_close()`: Benchmark 结束时的钩子 (如释放资源)。
  - `get_system_prompt(...)`: 获取并填充 System Prompt。

## 内置环境类型

  - **MathEnvironment**:
      - 工具: `CalculatorTool`
      - 模式: `"math"`
  - **PythonEnvironment**:
      - 工具: `PythonInterpreterTool`
      - 模式: `"python"`
  - **WebEnvironment**:
      - 工具: `WebSearchTool`
      - 模式: `"web"`

## 配置参数

### 通用配置 (`kwargs`)

所有传递给构造函数的额外参数都会存储在 `self.config` 中，可在 `run_task` 或工具初始化时使用。

  - `model_name`: 指定 LLM 模型名称。
  - `action_space`: (可选) 定义动作空间配置，影响 Prompt 生成。

### 资源配置

如果环境涉及重型资源 (如 OSWorld)，通常需要以下配置：

  - `provider_name`: 云服务商 (aliyun, aws 等)。
  - `proxy_settings`: 代理配置。

## 注意事项

1.  **严禁绕过 execute\_tool**: 在 `run_task` 中必须通过 `self.execute_tool()` 调用工具，而不是直接调用 `tool.call()`，以确保日志记录和异常捕获生效。
2.  **Prompt 占位符**: 如果使用了自定义 Prompt 变量 (如 `{PASSWORD}`)，请在子类重写 `_replace_prompt_placeholders` 方法。
3.  **Benchmark 适配**: `run_task` 返回的字典必须包含 `answer` 字段，以便 Benchmark 模块进行自动评测。