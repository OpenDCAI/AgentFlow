# Task 配置字段流向分析

## Task 配置文件结构

```json
{
  "id": "任务唯一标识符",
  "snapshot": "快照名称",
  "instruction": "任务指令",
  "source": "任务来源",
  "config": [环境配置列表],
  "trajectory": "轨迹存储路径",
  "related_apps": ["相关应用列表"],
  "evaluator": {评估器配置},
  "proxy": true/false,
  "fixed_ip": true/false,
  "possibility_of_env_change": "low/medium/high"
}
```

## 字段流向详细分析

### 1. `id` (任务ID)

**流向路径：**
```
JSON 文件 → task_config["id"] 
  → DesktopEnv._set_task_info() 
    → self.task_id
      → self.cache_dir (用于缓存目录)
      → lib_run_single.setup_logger() (日志记录器名称)
```

**使用位置：**
- `desktop_env/desktop_env.py:326`: `self.task_id = task_config["id"]`
- `desktop_env/desktop_env.py:327`: `self.cache_dir = os.path.join(self.cache_dir_base, self.task_id)`
- `lib_run_single.py:68`: `logging.getLogger(f"desktopenv.example.{example['id']}")`
- `mm_agents/maestro/maestro/snapshot_restorer.py:50`: 用于查找配置文件

**用途：**
- 创建任务专属的缓存目录
- 日志记录标识
- 配置文件查找

---

### 2. `snapshot` (快照名称)

**流向路径：**
```
JSON 文件 → task_config["snapshot"]
  → (当前未使用，仅在初始化时设置)
```

**使用位置：**
- **当前实现中未被使用**
- 初始化时通过 `DesktopEnv.__init__(snapshot_name=...)` 设置
- 在 `reset()` 中使用 `self.snapshot_name`（初始化时固定）

**问题：**
- 任务配置中的 `snapshot` 字段未被读取
- 所有任务使用初始化时设置的快照

---

### 3. `instruction` (任务指令)

**流向路径：**
```
JSON 文件 → task_config["instruction"] / example["instruction"]
  → DesktopEnv._set_task_info()
    → self.instruction
      → env._get_obs() 
        → observation["instruction"]
          → agent.predict(instruction, obs)
            → 传递给 LLM/Agent
```

**使用位置：**
- `desktop_env/desktop_env.py:329`: `self.instruction = task_config["instruction"]`
- `desktop_env/desktop_env.py:313`: `"instruction": self.instruction` (在 observation 中)
- `lib_run_single.py:226`: `example["instruction"]` (传递给 agent)
- `run_multienv.py:210`: 日志记录
- 所有 agent 的 `predict()` 方法接收 instruction

**用途：**
- 作为任务描述传递给 Agent
- 包含在观察中供 Agent 使用
- 日志记录

---

### 4. `source` (任务来源)

**流向路径：**
```
JSON 文件 → task_config["source"]
  → (当前未在代码中使用)
```

**使用位置：**
- **当前实现中未被使用**
- 可能用于元数据记录或分析

---

### 5. `config` (环境配置)

**流向路径：**
```
JSON 文件 → task_config["config"]
  → DesktopEnv._set_task_info()
    → self.config
      → setup_controller.setup(self.config, ...)
        → 执行各种环境设置操作
          → launch: 启动应用
          → download: 下载文件
          → execute: 执行命令
          → activate_window: 激活窗口
          → chrome_open_tabs: 打开 Chrome 标签页
          → 等等...
```

**使用位置：**
- `desktop_env/desktop_env.py:330`: `self.config = task_config["config"] if "config" in task_config else []`
- `desktop_env/desktop_env.py:285`: `self.setup_controller.setup(self.config, ...)`
- `desktop_env/desktop_env.py:288`: 检查是否有配置操作

**用途：**
- 环境初始化设置
- 启动应用
- 下载必要文件
- 执行预配置命令

**配置类型：**
- `launch`: 启动应用程序
- `download`: 下载文件
- `execute`: 执行命令
- `activate_window`: 激活窗口
- `chrome_open_tabs`: 打开 Chrome 标签页
- 等等...

---

### 6. `trajectory` (轨迹路径)

**流向路径：**
```
JSON 文件 → task_config["trajectory"]
  → (当前未在代码中使用)
```

**使用位置：**
- **当前实现中未被使用**
- 可能用于存储任务执行轨迹

---

### 7. `related_apps` (相关应用)

**流向路径：**
```
JSON 文件 → task_config["related_apps"]
  → (当前未在代码中使用)
```

**使用位置：**
- **当前实现中未被使用**
- 可能用于任务分类或元数据分析

---

### 8. `evaluator` (评估器配置)

**流向路径：**
```
JSON 文件 → task_config["evaluator"]
  → DesktopEnv._set_evaluator_info()
    → self.evaluator
      → self.metric (评估函数)
      → self.result_getter (结果获取器)
      → self.expected_getter (期望值获取器)
      → self.metric_options (评估选项)
      → env.evaluate()
        → 使用上述组件评估任务成功
```

**使用位置：**
- `desktop_env/desktop_env.py:344`: `self.evaluator = task_config["evaluator"]`
- `desktop_env/desktop_env.py:345-347`: 解析 `func` 字段，加载 metric 函数
- `desktop_env/desktop_env.py:348`: 解析 `conj` 字段（"and"/"or"）
- `desktop_env/desktop_env.py:349-353`: 解析 `result` 字段，创建 result_getter
- `desktop_env/desktop_env.py:359-363`: 解析 `expected` 字段，创建 expected_getter
- `desktop_env/desktop_env.py:368-375`: 解析 `options` 字段
- `desktop_env/desktop_env.py:425-488`: `evaluate()` 方法使用这些组件

**evaluator 子字段：**

#### 8.1 `evaluator.func`
- 评估函数名称（字符串或列表）
- 例如：`"exact_match"`, `"check_include_exclude"`, `"is_extension_installed"`
- 流向：`getattr(metrics, func)` → metric 函数

#### 8.2 `evaluator.conj`
- 多个评估函数的连接方式
- 值：`"and"` 或 `"or"`，默认 `"and"`
- 流向：`self.metric_conj`

#### 8.3 `evaluator.result`
- 结果获取器配置（对象或列表）
- 类型包括：`vm_command_line`, `vm_file`, `cloud_file`, `enable_do_not_track` 等
- 流向：`getattr(getters, "get_{type}")` → result_getter 函数

#### 8.4 `evaluator.expected`
- 期望值获取器配置（可选，对象或列表）
- 类型包括：`rule`, `cloud_file`, `vm_file` 等
- 流向：`getattr(getters, "get_{type}")` → expected_getter 函数

#### 8.5 `evaluator.options`
- 评估选项（可选）
- 流向：`self.metric_options`

#### 8.6 `evaluator.postconfig`
- 评估前的后置配置（可选）
- 流向：`evaluate()` 方法中的 `self.setup_controller.setup(postconfig, ...)`

**用途：**
- 定义如何评估任务是否成功
- 获取实际结果和期望结果
- 比较并返回评估分数（0.0-1.0）

---

### 9. `proxy` (代理配置)

**流向路径：**
```
JSON 文件 → task_config["proxy"]
  → DesktopEnv.reset()
    → task_use_proxy = task_config.get("proxy", False) and self.enable_proxy
      → self.current_use_proxy
        → setup_controller._proxy_setup() (如果需要)
        → setup_controller.setup(..., use_proxy)
```

**使用位置：**
- `desktop_env/desktop_env.py:259`: 检查任务是否需要代理
- `desktop_env/desktop_env.py:263`: 更新 `self.current_use_proxy`
- `desktop_env/desktop_env.py:279`: 检查是否需要设置代理
- `desktop_env/desktop_env.py:281`: 调用 `_proxy_setup()`
- `desktop_env/desktop_env.py:285`: 传递给 `setup()` 方法

**用途：**
- 控制任务是否使用代理网络
- 配置网络代理设置

---

### 10. `fixed_ip` (固定IP)

**流向路径：**
```
JSON 文件 → task_config["fixed_ip"]
  → (当前未在代码中使用)
```

**使用位置：**
- **当前实现中未被使用**
- 可能用于云服务 provider 的 IP 管理

---

### 11. `possibility_of_env_change` (环境变更可能性)

**流向路径：**
```
JSON 文件 → task_config["possibility_of_env_change"]
  → (当前未在代码中使用)
```

**使用位置：**
- **当前实现中未被使用**
- 可能用于优化快照恢复策略

---

## 完整数据流图

```
Task JSON 文件
    │
    ├─→ id
    │   └─→ DesktopEnv.task_id → cache_dir → 日志
    │
    ├─→ snapshot
    │   └─→ (未使用，当前使用初始化时的快照)
    │
    ├─→ instruction
    │   └─→ DesktopEnv.instruction → observation → agent.predict()
    │
    ├─→ source
    │   └─→ (未使用)
    │
    ├─→ config
    │   └─→ DesktopEnv.config → setup_controller.setup()
    │       ├─→ launch: 启动应用
    │       ├─→ download: 下载文件
    │       ├─→ execute: 执行命令
    │       └─→ 其他配置操作
    │
    ├─→ trajectory
    │   └─→ (未使用)
    │
    ├─→ related_apps
    │   └─→ (未使用)
    │
    ├─→ evaluator
    │   ├─→ func → metric 函数
    │   ├─→ conj → metric_conj
    │   ├─→ result → result_getter
    │   ├─→ expected → expected_getter
    │   ├─→ options → metric_options
    │   └─→ postconfig → evaluate() 中的后置配置
    │
    ├─→ proxy
    │   └─→ task_use_proxy → setup_controller._proxy_setup()
    │
    ├─→ fixed_ip
    │   └─→ (未使用)
    │
    └─→ possibility_of_env_change
        └─→ (未使用)
```

## 关键执行流程

### 1. 任务加载流程
```
run_multienv.py / lib_run_single.py
  → 读取 JSON 文件
    → example = json.load(f)
      → env.reset(task_config=example)
```

### 2. 环境重置流程
```
DesktopEnv.reset(task_config)
  → 检查 proxy 配置
  → 恢复快照（如需要）
  → _set_task_info(task_config)
    → 设置 id, instruction, config
    → _set_evaluator_info(task_config)
      → 设置 evaluator 相关组件
  → setup_controller.setup(config, use_proxy)
    → 执行环境配置操作
```

### 3. 任务评估流程
```
DesktopEnv.evaluate()
  → 执行 postconfig（如有）
  → 使用 result_getter 获取实际结果
  → 使用 expected_getter 获取期望结果（如有）
  → 使用 metric 函数比较
  → 根据 conj 合并多个评估结果
  → 返回 0.0-1.0 的分数
```

## 总结

### 已使用的字段：
1. ✅ `id` - 任务标识和缓存目录
2. ✅ `instruction` - 任务指令，传递给 Agent
3. ✅ `config` - 环境配置，执行初始化操作
4. ✅ `evaluator` - 评估器配置，用于任务成功判断
5. ✅ `proxy` - 代理配置，控制网络代理使用

### 未使用的字段：
1. ❌ `snapshot` - 当前未使用（使用初始化时的快照）
2. ❌ `source` - 元数据，未在代码中使用
3. ❌ `trajectory` - 轨迹路径，未在代码中使用
4. ❌ `related_apps` - 相关应用，未在代码中使用
5. ❌ `fixed_ip` - 固定IP，未在代码中使用
6. ❌ `possibility_of_env_change` - 环境变更可能性，未在代码中使用

