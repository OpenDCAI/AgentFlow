# 探索式数据合成环境管理修复总结

## 问题描述

在运行探索式数据合成时，环境启动出现问题：

### 错误信息
```
KeyError: 'evaluator'
File "/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/desktop_env.py", line 359, in _set_evaluator_info
    self.evaluator = metadata["evaluator"]
```

### 根本原因
1. **错误的 evaluator 位置**：`evaluator` 应该在 `metadata` 字段中，而不是在任务的顶层
2. **无效的 evaluator 函数**：使用了不存在的 `"dummy"` 函数，应该使用 metrics 模块中存在的函数
3. **环境管理不完整**：环境生命周期方法调用不完整

## 修复内容

### 1. 在 `envs/__init__.py` 中添加 `OSWorldEnvironment` 导出

**文件**: `/home/a1/sdb/tzw/AgentFlow/src/envs/__init__.py`

**修改**:
- 在 `__getattr__` 函数中添加 `OSWorldEnvironment` 的延迟导入
- 在 `__all__` 列表中添加 `OSWorldEnvironment` 和 `create_osworld_environment`

这确保了其他模块可以正确导入 `OSWorldEnvironment`。

### 2. 修复 `exploration_pipeline.py` 的环境管理

**文件**: `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/exploration_pipeline.py`

**参考**: `run_osworld.py` 的环境管理逻辑

#### 修改点：

##### (1) 环境启动 (line 175-178)
```python
# 参考 run_osworld.py line 757
print("🔧 启动OSWorld环境...")
self.environment.env_start()
print("   ✓ 环境启动成功")
```

##### (2) 任务初始化 (line 207-235)
```python
# 参考 run_osworld.py line 190, 196
# 获取任务输出目录
task_output_dir = self.environment.get_task_output_dir(
    self.output_dir, 
    source_id, 
    self.config.model_name
)

# 创建完整的 dummy_task（包含必需的 evaluator）
dummy_task = {
    "id": source_id,
    "question": exploration_seed,
    "config": [],  # 无初始化配置
    "evaluator": {  # ✅ 添加占位符 evaluator
        "func": "dummy",
        "result": {"type": "dummy"},
        "expected": {"type": "dummy"}
    },
    "metadata": {}
}

# 初始化任务并获取初始观察
initial_obs = self.environment.env_task_init(dummy_task)
```

**关键修复**:
- ✅ 添加 `evaluator` 字段（探索模式使用占位符）
- ✅ 调用 `get_task_output_dir` 获取输出目录
- ✅ 接收 `env_task_init` 的返回值（初始观察）

##### (3) 任务结束 (line 285-294)
```python
# 参考 run_osworld.py line 282-289
try:
    self.environment.env_task_end(
        task_id=source_id,
        task_output_dir=task_output_dir,
        final_answer="exploration_completed"
    )
    print(f"   ✓ 任务 {source_id} 已清理")
except Exception as e:
    print(f"   ⚠️  警告: 清理任务失败: {e}")
```

**关键修复**:
- ✅ 传递正确的参数：`task_id`, `task_output_dir`, `final_answer`
- ✅ 添加异常处理

##### (4) 异常处理中的清理 (line 301-320)
```python
# 参考 run_osworld.py finally 块
try:
    # 尝试获取task_output_dir（如果失败则为None）
    try:
        cleanup_output_dir = self.environment.get_task_output_dir(
            self.output_dir, 
            source_id, 
            self.config.model_name
        )
    except:
        cleanup_output_dir = None
    
    self.environment.env_task_end(
        task_id=source_id,
        task_output_dir=cleanup_output_dir,
        final_answer=""
    )
except Exception as cleanup_error:
    print(f"   ⚠️  警告: 清理失败: {cleanup_error}")
```

##### (5) 环境关闭 (line 323-330)
```python
# 参考 run_osworld.py line 811-817
finally:
    try:
        print(f"\n🧹 关闭OSWorld环境...")
        self.environment.env_close()
        print(f"   ✓ 环境关闭成功")
    except Exception as cleanup_error:
        print(f"   ⚠️  警告: 关闭环境失败: {cleanup_error}")
```

##### (6) 其他清理
- ❌ 删除 `import pdb`
- ❌ 删除 `pdb.set_trace()` 调试断点

## 环境生命周期管理

### 完整流程（参考 run_osworld.py）

```
1. env_start()                    # 启动环境（初始化VM等）
   ↓
2. for each task:
   ├─ get_task_output_dir()       # 获取任务输出目录
   ├─ env_task_init(task)         # 初始化任务（重置VM，返回初始观察）
   ├─ [执行任务逻辑]
   ├─ env_task_end(task_id, ...)  # 结束任务（保存轨迹，清理资源）
   └─ [继续下一个任务]
   ↓
3. env_close()                     # 关闭环境（清理全局资源）
```

### 关键方法签名

```python
# 1. 启动环境
env_start() -> None

# 2. 获取任务输出目录
get_task_output_dir(
    output_dir: str,
    task_id: str,
    model_name: str
) -> Optional[str]

# 3. 初始化任务
env_task_init(task: Dict) -> Optional[Dict[str, Any]]
# task 必须包含: id, question, config, evaluator, metadata

# 4. 结束任务
env_task_end(
    task_id: str,
    task_output_dir: Optional[str],
    final_answer: str
) -> None

# 5. 关闭环境
env_close() -> None
```

## 探索模式特殊处理

### Dummy Task 结构

探索模式不需要真实的任务评估，但仍需要符合 OSWorld 的任务格式：

**重要发现**：
1. `evaluator` 必须在 `metadata` 字段中（参考 `desktop_env.py` line 359）
2. `evaluator["func"]` 必须是 metrics 模块中存在的函数
3. 可以使用 `infeasible` 函数作为占位符（`metrics/__init__.py` line 159）

```python
dummy_task = {
    "id": source_id,
    "question": exploration_seed,  # 抽象的探索方向
    "config": [],                  # 空的初始化配置
    "metadata": {
        "evaluator": {             # ⚠️ evaluator 必须在 metadata 中！
            "func": "infeasible",  # 使用 infeasible 作为占位符
            "result": [],
            "expected": []
        }
    }
}
```

### 探索流程

```
1. env_task_init(dummy_task)
   ↓ 返回 initial_obs
2. exploration_sampler.sample_exploration_tree(seed)
   ├─ 使用 environment.get_obs() 获取当前观察
   ├─ 使用 environment.execute_tool() 执行动作
   └─ 循环探索多个分支
3. 选择有价值的轨迹
4. 总结为任务/QA
5. env_task_end(source_id, task_output_dir, "exploration_completed")
```

## 验证清单

- [x] `OSWorldEnvironment` 可以被正确导入
- [x] `env_start()` 在pipeline开始时调用
- [x] 每个任务调用 `get_task_output_dir()`
- [x] 每个任务调用 `env_task_init()` 并接收返回值
- [x] Dummy task 包含所有必需字段
  - [x] `evaluator` 在 `metadata` 中（不是顶层）⚠️
  - [x] `evaluator["func"]` 使用有效的 metrics 函数（`infeasible`）⚠️
  - [x] `evaluator["result"]` 和 `evaluator["expected"]` 格式正确
- [x] 每个任务结束时调用 `env_task_end()` 并传递正确参数
- [x] 异常处理块中也调用 `env_task_end()` 清理
- [x] Pipeline结束时调用 `env_close()`
- [x] 所有环境管理调用都有异常处理
- [x] 删除调试代码（pdb）

## 测试方法

运行探索式数据合成：

```bash
cd /home/a1/sdb/tzw/AgentFlow/src/data_synthesis
./run_exploration_synthesis.sh \
  --vm /path/to/vm.vmx \
  --config configs/osworld_exploration_config.json \
  --seeds example_seed_exploration.json \
  --output exploration_results
```

预期结果：
- ✓ 环境正常启动
- ✓ 任务初始化成功（不再报 `KeyError: 'evaluator'`）
- ✓ 探索过程顺利执行
- ✓ 任务正常结束和清理
- ✓ 环境正常关闭

## 参考文件

- `run_osworld.py` - OSWorld任务运行的标准实现
- `osworld_environment.py` - OSWorld环境的具体实现
- `exploration_pipeline.py` - 探索式数据合成主流程
- `exploration_sampler.py` - 探索式轨迹采样器

---

**修复时间**: 2025-11-10  
**修复人员**: AI Assistant  
**相关Issue**: 环境启动失败 - KeyError: 'evaluator'

