# OSWorld 任务格式快速参考

## 标准任务结构

### 完整格式

```python
task = {
    "id": "task_id",
    "question": "任务指令",
    "config": [
        {
            "type": "execute",
            "parameters": {
                "command": ["python", "-c", "..."]
            }
        }
    ],
    "metadata": {
        "evaluator": {
            "func": "check_include_exclude",  # 或其他 metrics 函数
            "result": {
                "type": "vm_command_line",
                "command": "which spotify"
            },
            "expected": {
                "type": "rule",
                "rules": {
                    "include": ["spotify"],
                    "exclude": ["not found"]
                }
            }
        }
    }
}
```

### 最小格式（探索模式）

```python
dummy_task = {
    "id": "explore_001",
    "question": "探索方向描述",
    "config": [],
    "metadata": {
        "evaluator": {
            "func": "infeasible",  # 占位符函数
            "result": [],
            "expected": []
        }
    }
}
```

## 关键字段说明

### 1. `id` (必需)
- 类型：`str`
- 说明：任务的唯一标识符
- 示例：`"demo-spotify-001"`, `"explore_0001_a1b2c3"`

### 2. `question` (必需)
- 类型：`str`
- 说明：任务指令或探索方向
- 示例：`"I want to install Spotify on my current system."`

### 3. `config` (必需)
- 类型：`List[Dict]`
- 说明：任务初始化配置（可以为空列表）
- 用途：在任务开始前执行一些准备操作
- 示例：
  ```python
  "config": [
      {
          "type": "execute",
          "parameters": {
              "command": ["python", "-c", "import pyautogui; pyautogui.click(960, 540)"]
          }
      }
  ]
  ```

### 4. `metadata` (必需)
- 类型：`Dict`
- 说明：任务元数据，**必须包含 `evaluator` 字段**
- ⚠️ **重要**：`evaluator` 必须在 `metadata` 中，不能在顶层！

### 5. `metadata.evaluator` (必需)
- 类型：`Dict`
- 说明：任务评估器配置
- **必需子字段**：
  - `func`: 评估函数名（必须是 `metrics` 模块中存在的函数）
  - `result`: 评估结果获取方式
  - `expected`: 期望的评估结果

## Evaluator 详解

### Evaluator 结构

```python
"evaluator": {
    "func": "function_name",  # 评估函数
    "result": {...},           # 如何获取结果
    "expected": {...}          # 期望结果
}
```

### 可用的评估函数

#### 通用函数（`metrics.general`）
- `check_include_exclude` - 检查文本包含/排除规则
- `exact_match` - 精确匹配
- `fuzzy_match` - 模糊匹配
- `check_json` - JSON 验证
- `check_csv` - CSV 验证
- `file_contains` - 文件内容检查
- 等等...

#### 占位符函数
- `infeasible` - 空函数，用于不需要实际评估的场景

### Result 类型

#### 1. `vm_command_line` - 在VM中执行命令
```python
"result": {
    "type": "vm_command_line",
    "command": "which spotify"
}
```

#### 2. `vm_file_content` - 读取VM文件内容
```python
"result": {
    "type": "vm_file_content",
    "path": "/home/user/test.txt"
}
```

### Expected 类型

#### 1. `rule` - 规则验证
```python
"expected": {
    "type": "rule",
    "rules": {
        "include": ["keyword1", "keyword2"],
        "exclude": ["error", "not found"]
    }
}
```

#### 2. `exact` - 精确匹配
```python
"expected": {
    "type": "exact",
    "value": "expected_output"
}
```

## 常见评估器示例

### 1. 检查软件是否安装

```python
"evaluator": {
    "func": "check_include_exclude",
    "result": {
        "type": "vm_command_line",
        "command": "which spotify"
    },
    "expected": {
        "type": "rule",
        "rules": {
            "include": ["spotify"],
            "exclude": ["not found"]
        }
    }
}
```

### 2. 检查文件是否存在

```python
"evaluator": {
    "func": "check_include_exclude",
    "result": {
        "type": "vm_command_line",
        "command": "ls ~/test.txt"
    },
    "expected": {
        "type": "rule",
        "rules": {
            "include": ["test.txt"],
            "exclude": ["No such file"]
        }
    }
}
```

### 3. 验证文件内容

```python
"evaluator": {
    "func": "file_contains",
    "result": {
        "type": "vm_file_content",
        "path": "/home/user/test.txt"
    },
    "expected": {
        "type": "exact",
        "value": "Hello OSWorld"
    }
}
```

### 4. 探索模式占位符

```python
"evaluator": {
    "func": "infeasible",
    "result": [],
    "expected": []
}
```

## 完整任务示例

### 示例1：安装 Spotify

```python
{
    "id": "demo-spotify-001",
    "question": "I want to install Spotify on my current system. Could you please help me?",
    "config": [],
    "metadata": {
        "evaluator": {
            "func": "check_include_exclude",
            "result": {
                "type": "vm_command_line",
                "command": "which spotify"
            },
            "expected": {
                "type": "rule",
                "rules": {
                    "include": ["spotify"],
                    "exclude": ["not found"]
                }
            }
        }
    }
}
```

### 示例2：创建文件

```python
{
    "id": "demo-create-file-001",
    "question": "Create a file named 'test.txt' in the home directory with content 'Hello OSWorld'",
    "config": [],
    "metadata": {
        "evaluator": {
            "func": "file_contains",
            "result": {
                "type": "vm_file_content",
                "path": "~/test.txt"
            },
            "expected": {
                "type": "exact",
                "value": "Hello OSWorld"
            }
        }
    }
}
```

### 示例3：探索模式

```python
{
    "id": "explore_0001_abc123",
    "question": "Explore the file system and common applications.",
    "config": [],
    "metadata": {
        "evaluator": {
            "func": "infeasible",
            "result": [],
            "expected": []
        }
    }
}
```

## 常见错误

### ❌ 错误1：evaluator 在顶层

```python
# 错误！
task = {
    "id": "task_001",
    "question": "...",
    "evaluator": {...}  # ❌ 错误位置
}
```

```python
# 正确！
task = {
    "id": "task_001",
    "question": "...",
    "metadata": {
        "evaluator": {...}  # ✅ 正确位置
    }
}
```

### ❌ 错误2：使用不存在的评估函数

```python
# 错误！
"evaluator": {
    "func": "dummy",  # ❌ metrics 模块中不存在
    ...
}
```

```python
# 正确！
"evaluator": {
    "func": "infeasible",  # ✅ metrics 模块中存在
    ...
}
```

### ❌ 错误3：缺少必需字段

```python
# 错误！
task = {
    "id": "task_001",
    "question": "...",
    # ❌ 缺少 config
    # ❌ 缺少 metadata
}
```

```python
# 正确！
task = {
    "id": "task_001",
    "question": "...",
    "config": [],  # ✅ 即使为空也要提供
    "metadata": {
        "evaluator": {...}  # ✅ 必需
    }
}
```

## 调试技巧

### 1. 验证任务格式

```python
def validate_task(task):
    """验证任务格式"""
    required_fields = ["id", "question", "config", "metadata"]
    for field in required_fields:
        if field not in task:
            raise ValueError(f"Missing required field: {field}")
    
    if "evaluator" not in task["metadata"]:
        raise ValueError("Missing evaluator in metadata")
    
    evaluator = task["metadata"]["evaluator"]
    required_eval_fields = ["func", "result", "expected"]
    for field in required_eval_fields:
        if field not in evaluator:
            raise ValueError(f"Missing evaluator field: {field}")
    
    print("✓ Task format is valid")
```

### 2. 检查 evaluator 函数是否存在

```python
from utils.desktop_env.evaluators import metrics

def check_evaluator_func(func_name):
    """检查评估函数是否存在"""
    if hasattr(metrics, func_name):
        print(f"✓ Function '{func_name}' exists in metrics")
    else:
        print(f"✗ Function '{func_name}' NOT found in metrics")
        print(f"Available functions: {dir(metrics)}")
```

## 参考资源

- **评估函数列表**：`/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/evaluators/metrics/__init__.py`
- **任务结构定义**：`/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/desktop_env.py` (line 359)
- **示例任务**：`/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/configs/osworld_config.json`

---

**最后更新**: 2025-11-10  
**版本**: 1.0

