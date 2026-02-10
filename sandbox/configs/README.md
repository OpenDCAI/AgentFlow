# Sandbox 配置目录结构

> 说明：当前主干运行环境不会加载本目录中的配置文件；这些文件仅保留作为参考/历史示例。

```
configs/
├── README.md                      # 本文件
├── CONFIG_HIERARCHY.md            # 配置分级说明
│
├── server/                        # L1 - 服务器级别配置
│   ├── default.json               #   默认服务器配置
│   ├── dev.json                   #   开发环境服务器配置
│   └── production.json            #   生产环境服务器配置
│
├── resources/                     # L2 - 资源默认配置
│   ├── vm/                        #   虚拟机资源
│   │   ├── default.json           #     本地默认配置
│   │   └── cloud.json             #     云端（阿里云）配置
│   ├── rag/                       #   RAG 检索资源
│   │   ├── default.json           #     基础 Dense 检索
│   │   └── hybrid.json            #     混合检索（Dense + BM25）
│   ├── websearch/                 #   网络搜索资源
│   │   ├── default.json           #     默认配置
│   │   └── google.json            #     Google API 配置
│   ├── browser/                   #   浏览器资源
│   │   └── default.json           #     Playwright 配置
│   └── code_executor/             #   代码执行资源
│       └── default.json           #     Docker 沙箱配置
│
└── profiles/                      # 启动配置（囊括 L1 + L2）
    ├── minimal.json               #   最小配置（仅 websearch）
    ├── dev.json                   #   开发环境完整配置
    └── production.json            #   生产环境完整配置
```

---

## 📊 配置分级

| 级别 | 目录 | 说明 | 修改频率 |
|:---:|------|------|---------|
| **L1** | `server/` | 服务器配置（端口、TTL、日志） | 很少 |
| **L2** | `resources/` | 资源默认配置（各后端参数） | 偶尔 |
| **Profile** | `profiles/` | 启动配置（组合 L1 + L2） | 按需 |
| **L3** | API 参数 | 运行时配置 | 每次调用 |

---

## 🚀 使用方式

### 1. 使用启动配置（推荐）

```bash
# 开发环境
python -m sandbox.server.config_loader configs/profiles/dev.json

# 生产环境
python -m sandbox.server.config_loader configs/profiles/production.json

# 最小配置（快速测试）
python -m sandbox.server.config_loader configs/profiles/minimal.json
```

### 2. Python 代码

```python
from sandbox.server import create_server_from_config

# 使用启动配置
server = create_server_from_config("sandbox/configs/profiles/dev.json")
server.run()
```

### 3. 运行时覆盖（L3）

```python
async with Sandbox() as sandbox:
    # 预热后端
    await sandbox.warmup(["vm", "rag"])
    
    # 创建 Session 时使用自定义配置
    await sandbox.create_session({
        "vm": {"screen_size": [1024, 768], "headless": True}
    })
    
    # 重新初始化使用新配置
    await sandbox.reinitialize("rag", {"top_k": 20})
```

---

## 📝 配置文件说明

### L1: 服务器配置 (`server/`)

| 文件 | 用途 |
|------|------|
| `default.json` | 所有环境的基础默认值 |
| `dev.json` | 开发环境（DEBUG日志，长TTL） |
| `production.json` | 生产环境（INFO日志，限流） |

### L2: 资源配置 (`resources/`)

每个资源目录下：
- `default.json` - 该资源的默认配置
- 其他 `.json` - 特定场景的变体配置

### Profile: 启动配置 (`profiles/`)

| 文件 | 包含资源 | 用途 |
|------|---------|------|
| `minimal.json` | websearch | 快速测试 |
| `dev.json` | vm, rag, websearch | 本地开发 |
| `production.json` | vm, rag, websearch, browser, code | 生产部署 |

---

## 🔧 自定义配置

### 添加新资源

1. 创建目录 `resources/my_resource/`
2. 创建 `default.json`:

```json
{
  "$schema": "L2 - MyResource 默认配置",
  "$resource_type": "my_resource",
  
  "enabled": true,
  "backend_class": "backends.my_resource.MyBackend",
  "description": "MyResource 后端描述",
  
  "config": {
    "param1": "value1",
    "param2": 100
  }
}
```

3. 在 `profiles/*.json` 中引用

### 添加资源变体

在资源目录下创建新的 JSON 文件：

```json
// resources/rag/lightweight.json
{
  "$schema": "L2 - RAG 轻量配置",
  "$extends": "default.json",
  
  "config": {
    "model_name": "MiniLM-L6-v2",
    "device": "cpu",
    "default_top_k": 5,
    "batcher_trigger_batch_size": 8,
    "batcher_max_batch_size": 16,
    "batcher_max_wait_time": 0.1
  }
}
```

#### RAG 设备配置格式说明

`device` 参数支持以下格式：
- `"cuda:0"` → Encoder 用 cuda:0，Index 用 cpu（默认）
- `"cuda:0/cuda:1"` → Encoder 用 cuda:0，Index 用 cuda:1
- `"cpu"` → 全部用 cpu

#### RAG Batcher 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `batcher_trigger_batch_size` | 触发批处理的最小请求数 | 16 |
| `batcher_max_batch_size` | 单批次最大请求数 | 32 |
| `batcher_max_wait_time` | 最大等待时间（秒） | 0.05 |

---

## 🌍 环境变量

配置中支持环境变量：

```json
{
  "api_key": "${API_KEY}",                    // 必须设置
  "model": "${MODEL_NAME:-default-model}"     // 带默认值
}
```

生产环境建议：
```bash
export ALIYUN_ACCESS_KEY_ID="xxx"
export RAG_MODEL_NAME="intfloat/e5-base-v2"
export GOOGLE_API_KEY="xxx"
```
