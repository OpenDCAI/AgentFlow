# Bin Scripts 使用说明

本目录包含项目的可执行脚本。

## sandbox-server.py

启动 Sandbox Server 的脚本，可以在项目任何目录执行。

### 基本用法

```bash
# 使用默认配置启动（dev.json，端口 18890）
python3 bin/sandbox-server.py

# 或者直接执行（需要可执行权限）
./bin/sandbox-server.py
```

### 命令行参数

```bash
# 指定配置文件
python3 bin/sandbox-server.py --config dev.json
python3 bin/sandbox-server.py -c production.json

# 指定主机和端口
python3 bin/sandbox-server.py --host 127.0.0.1 --port 9000
python3 bin/sandbox-server.py -p 8080

# 设置日志级别
python3 bin/sandbox-server.py --log-level DEBUG

# 显示配置信息（不启动服务器）
python3 bin/sandbox-server.py --show-config

# 查看帮助
python3 bin/sandbox-server.py --help
```

### 使用示例

```bash
# 开发环境
python3 bin/sandbox-server.py --config dev.json

# 生产环境，指定端口
python3 bin/sandbox-server.py --config production.json --port 8080

# 本地测试，只监听 localhost
python3 bin/sandbox-server.py --host 127.0.0.1 --port 9000

# 调试模式
python3 bin/sandbox-server.py --log-level DEBUG
```

### 配置文件查找顺序

脚本会按以下顺序查找配置文件：
1. 绝对路径（如果提供）
2. 当前目录
3. 当前工作目录
4. 项目根目录
5. `sandbox/configs/profiles/` 目录

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

## 快速启动流程

```bash
# 1. 启动服务器
python3 bin/sandbox-server.py

# 2. 停止服务器（另一个终端）
./bin/kill-server.sh

# 或者在服务器终端按 Ctrl+C
```

## 注意事项

1. **Python 环境**：确保已安装 Python 3.7+ 和所有依赖
2. **权限**：如果需要直接执行脚本，请添加可执行权限：
   ```bash
   chmod +x bin/sandbox-server.py
   chmod +x bin/kill-server.sh
   ```
3. **端口占用**：如果端口被占用，使用 `kill-server.sh` 清理
4. **配置文件**：确保配置文件存在且格式正确
