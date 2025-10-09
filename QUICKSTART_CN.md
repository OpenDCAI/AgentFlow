# AgentFlow 快速入门指南

5 分钟内上手 AgentFlow！

## 🚀 快速设置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量

```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_API_URL="your-openai-api-url"  # 可选
export SERPER_API_KEY="your-serper-key"      # 网络搜索可选
```

### 3. 运行你的第一个智能体

```bash
# 数学智能体
python src/run.py --mode math --data src/data/math_demo.jsonl

# 网络智能体
python src/run.py --mode web --data src/data/webagent_demo.jsonl
```

## 📚 基本使用

### 命令行界面

```bash
# 基本语法
python src/run.py --mode <环境> --data <数据文件> [选项]

# 示例
python src/run.py --mode math --data src/data/math_demo.jsonl --model gpt-4
python src/run.py --mode web --data src/data/webagent_demo.jsonl --parallel
python src/run.py --mode py --data src/data/python_interpreter_demo.jsonl --no-eval
```

### 程序化使用

```python
from run import AgentRunner, AgentConfig
from envs import MathEnvironment
from benchmark import create_benchmark

# 创建配置
config = AgentConfig(
    model_name="gpt-4",
    max_turns=10,
    evaluate_results=True
)

# 创建并运行智能体
runner = AgentRunner(config)
runner.setup_environment("math")
runner.load_benchmark("src/data/math_demo.jsonl")
results = runner.run_benchmark()
```

## 🛠️ 添加你的第一个工具

### 1. 创建工具文件

```python
# src/tools/my_tool.py
class MyTool:
    name = "my_tool"
    description = "一个简单的示例工具"
    parameters = [
        {
            'name': 'input',
            'type': 'string',
            'description': '要处理的输入文本',
            'required': True
        }
    ]

    def call(self, params, **kwargs):
        input_text = params.get("input", "")
        return f"已处理: {input_text.upper()}"
```

### 2. 注册工具

```python
# src/tools/__init__.py
from .my_tool import MyTool
```

### 3. 创建环境

```python
# src/envs/environment.py
class MyEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "my_mode"

    def _initialize_tools(self):
        from tools.my_tool import MyTool
        self.register_tool(MyTool())
```

### 4. 测试你的工具

```python
# test_my_tool.py
from envs import MyEnvironment

env = MyEnvironment()
result = env.execute_tool("my_tool", {"input": "hello world"})
print(result)  # 输出: "已处理: HELLO WORLD"
```

## 📊 创建你的第一个基准测试

### 1. 创建数据文件

```jsonl
{"id": "q1", "question": "2+2等于多少？", "answer": "4"}
{"id": "q2", "question": "3*3等于多少？", "answer": "9"}
```

### 2. 运行基准测试

```bash
python src/run.py --mode math --data my_benchmark.jsonl
```

### 3. 查看结果

```bash
# 结果保存到 results/result_my_benchmark.jsonl
cat results/result_my_benchmark.jsonl
```

## 🔧 常见任务

### 使用不同模型

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --model gpt-3.5-turbo
```

### 并行执行

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --parallel --max-workers 4
```

### 跳过评估

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --no-eval
```

### 自定义输出目录

```bash
python src/run.py --mode math --data src/data/math_demo.jsonl --output-dir my_results
```

## 🧪 测试你的设置

### 1. 测试基本功能

```bash
python src/test_new_run.py
```

### 2. 测试特定组件

```python
# 测试环境
from envs import MathEnvironment
env = MathEnvironment()
print(env.list_tools())

# 测试基准测试
from benchmark import create_benchmark
benchmark = create_benchmark("src/data/math_demo.jsonl")
print(f"加载了 {len(benchmark.items)} 个项目")
```

### 3. 测试工具执行

```python
from envs import MathEnvironment

env = MathEnvironment()
result = env.execute_tool("calculator", {"expressions": ["2+2"]})
print(result)
```

## 🐛 故障排除

### 常见问题

1. **API 密钥未设置**

   ```
   Warning: OPENAI_API_KEY is not set
   ```

   解决方案: 设置环境变量

2. **文件未找到**

   ```
   FileNotFoundError: Data file not found
   ```

   解决方案: 检查文件路径

3. **工具未找到**

   ```
   Error: Tool calculator not found
   ```

   解决方案: 确保环境正确设置

### 调试模式

```bash
# 启用详细输出
python src/run.py --mode math --data src/data/math_demo.jsonl --max-turns 5
```

## 📖 下一步

1. **阅读完整文档**: [DEVELOPER_GUIDE_CN.md](DEVELOPER_GUIDE_CN.md)
2. **探索示例**: 查看 `src/envs/example_usage.py`
3. **运行集成测试**: `python src/benchmark/integration_test.py`
4. **创建自己的工具**: 遵循工具开发指南
5. **构建自定义环境**: 查看环境创建示例

## 🆘 需要帮助？

- **文档**: 查看上面的指南
- **示例**: 查看示例文件
- **问题**: 创建 GitHub 问题并提供详细信息
- **社区**: 加入讨论并提问

---

_使用 AgentFlow 愉快编程！🎉_
