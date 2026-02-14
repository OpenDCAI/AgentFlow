# Bin Scripts 使用说明

本目录包含项目的可执行脚本。

## sandbox-server.sh

启动 Sandbox Server 的脚本入口（内部调用 `bin/server/sandbox-server.py`），可以在项目任何目录执行。

### 基本用法

```bash
# 直接执行（推荐）
./bin/sandbox-server.sh --config /abs/path/to/config.json
```

### 命令行参数

```bash
# 指定配置文件
./bin/sandbox-server.sh --config /abs/path/to/dev.json
./bin/sandbox-server.sh -c ./configs/production.json

# 指定主机和端口
./bin/sandbox-server.sh --config ./configs/dev.json --host 127.0.0.1 --port 9000
./bin/sandbox-server.sh --config ./configs/dev.json -p 8080

# 设置日志级别
./bin/sandbox-server.sh --config ./configs/dev.json --log-level DEBUG

# 显示配置信息（不启动服务器）
./bin/sandbox-server.sh --config ./configs/dev.json --show-config

# 查看帮助
./bin/sandbox-server.sh --help
```

### 使用示例

```bash
# 开发环境
./bin/sandbox-server.sh --config ./configs/dev.json

# 生产环境，指定端口
./bin/sandbox-server.sh --config ./configs/production.json --port 8080

# 本地测试，只监听 localhost
./bin/sandbox-server.sh --config ./configs/dev.json --host 127.0.0.1 --port 9000

# 调试模式
./bin/sandbox-server.sh --config ./configs/dev.json --log-level DEBUG
```

### 配置文件说明

脚本仅接受你显式传入的配置文件路径（绝对路径或相对当前工作目录的路径）。

### 停止服务器

按 `Ctrl+C` 停止服务器。

## kill-server.sh

清理指定端口的进程及其所有子进程。

### 基本用法

```bash
# 清理默认端口 18890
./bin/kill-server.sh

# 清理指定端口
./bin/kill-server.sh 8080

# 强制清理，不询问确认
./bin/kill-server.sh 18890 --force
./bin/kill-server.sh 18890 -f

# 查看帮助
./bin/kill-server.sh --help
```

### 功能特性

- 自动查找占用端口的主进程
- 递归查找并清理所有子进程
- 先尝试优雅关闭（SIGTERM），5秒后强制杀死（SIGKILL）
- 显示进程详细信息（PID、用户、命令）
- 支持确认提示或强制模式
- 验证端口是否成功释放

### 使用示例

```bash
# 清理 sandbox server 默认端口
./bin/kill-server.sh

# 清理其他端口
./bin/kill-server.sh 8080

# 批量清理（强制模式）
./bin/kill-server.sh 18890 -f
./bin/kill-server.sh 8080 -f
```

## start-server.sh

通过环境变量注入方式启动 Sandbox Server 的便捷脚本。

### 功能特性

- ✅ 自动从 `.env` 文件加载环境变量
- ✅ 支持命令行参数设置 API Key
- ✅ 自动注入环境变量到配置文件中的 `${VAR}` 占位符
- ✅ 环境变量状态检查和提示
- ✅ 支持传递所有 `sandbox-server.sh` 的参数

### 基本用法

```bash
# 使用环境变量启动（推荐）
export SERPER_API_KEY="your-key"
export JINA_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
./bin/start-server.sh

# 从 .env 文件加载环境变量
./bin/start-server.sh --env-file .env

# 通过命令行参数设置 API Key
./bin/start-server.sh --serper-key "key1" --jina-key "key2" --openai-key "key3"

# 启动并指定端口
./bin/start-server.sh -- --port 8080

# 启动并显示配置信息
./bin/start-server.sh -- --show-config
```

### 环境变量配置

配置文件 `web_tool_config.json` 中使用 `${VAR}` 格式的变量会从环境变量中读取：

```json
{
  "apis": {
    "websearch": {
      "serper_api_key": "${SERPER_API_KEY}",
      "jina_api_key": "${JINA_API_KEY}",
      "openai_api_key": "${OPENAI_API_KEY}",
      "openai_api_url": "https://openrouter.ai/api/v1"
    }
  }
}
```

**环境变量设置方式（按优先级）**：
1. 命令行参数（`--serper-key`, `--jina-key`, `--openai-key`）
2. 已存在的环境变量
3. `.env` 文件（在项目根目录）
4. 配置文件中的默认值

### 创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
# .env
SERPER_API_KEY=your_serper_api_key_here
JINA_API_KEY=your_jina_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_URL=https://openrouter.ai/api/v1  # 可选
```

然后直接运行：

```bash
./bin/start-server.sh
```

### 命令行选项

```bash
--serper-key KEY       设置 SERPER_API_KEY
--jina-key KEY         设置 JINA_API_KEY
--openai-key KEY       设置 OPENAI_API_KEY
--openai-url URL       设置 OPENAI_API_URL
--env-file FILE        指定 .env 文件路径（默认: .env）
--config FILE          指定配置文件（默认: web_tool_config.json）
--no-env-check         跳过环境变量检查
-h, --help             显示帮助信息
```

### 使用示例

```bash
# 方式1: 使用 .env 文件（推荐用于生产环境）
./bin/start-server.sh

# 方式2: 命令行参数设置
./bin/start-server.sh \
  --serper-key "sk-xxx" \
  --jina-key "jina-xxx" \
  --openai-key "sk-xxx" \
  -- --port 8080

# 方式3: 混合方式（部分从 .env，部分从命令行）
export SERPER_API_KEY="sk-xxx"
./bin/start-server.sh --jina-key "jina-xxx" -- --log-level DEBUG

# 方式4: 使用自定义配置文件
./bin/start-server.sh --config configs/sandbox-server/custom_config.json
```

## 快速启动流程

```bash
# 方式1: 使用启动脚本（推荐）
./bin/start-server.sh

# 方式2: 直接使用 shell 入口脚本
./bin/sandbox-server.sh --config /abs/path/to/config.json

# 停止服务器（另一个终端）
./bin/kill-server.sh

# 或者在服务器终端按 Ctrl+C
```

## 注意事项

1. **Python 环境**：确保已安装 Python 3.7+ 和所有依赖
2. **权限**：如果需要直接执行脚本，请添加可执行权限：
   ```bash
   chmod +x bin/sandbox-server.sh
   chmod +x bin/kill-server.sh
   chmod +x bin/start-server.sh
   ```
3. **端口占用**：如果端口被占用，使用 `kill-server.sh` 清理
4. **配置文件**：确保配置文件存在且格式正确
5. **环境变量**：配置文件中的 `${VAR}` 格式会被自动替换为环境变量的值
6. **.env 文件**：建议将 `.env` 文件添加到 `.gitignore`，避免泄露敏感信息
