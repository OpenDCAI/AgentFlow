# Sandbox CLI 使用说明

本目录包含 Sandbox Server 的 Python 启动入口：

- `sandbox/cli/sandbox-server.py`

推荐从项目根目录使用统一 shell 入口脚本启动：

- `start_sandbox_server.sh`

## 推荐启动方式

```bash
/home/a1/sdb/lb/AgentFlow/start_sandbox_server.sh \
  --config /home/a1/sdb/lb/AgentFlow/configs/sandbox-server/web_tool_config.json
```

该脚本会调用 `sandbox/cli/sandbox-server.py`，若入口不存在会直接报错退出。

## 直接运行 Python 入口

```bash
python3 /home/a1/sdb/lb/AgentFlow/sandbox/cli/sandbox-server.py \
  --config /home/a1/sdb/lb/AgentFlow/configs/sandbox-server/web_tool_config.json
```

## 常用参数

```bash
# 指定配置文件（必填）
--config, -c <path>

# 指定主机/端口
--host <host>
--port, -p <port>

# 日志级别
--log-level DEBUG|INFO|WARNING|ERROR

# 仅展示配置，不启动服务
--show-config
```

## 示例

```bash
# 默认 host/port 启动
/home/a1/sdb/lb/AgentFlow/start_sandbox_server.sh \
  --config /home/a1/sdb/lb/AgentFlow/configs/sandbox-server/web_tool_config.json

# 指定端口
/home/a1/sdb/lb/AgentFlow/start_sandbox_server.sh \
  --config /home/a1/sdb/lb/AgentFlow/configs/sandbox-server/web_tool_config.json \
  --port 8080

# 本地调试
/home/a1/sdb/lb/AgentFlow/start_sandbox_server.sh \
  --config /home/a1/sdb/lb/AgentFlow/configs/sandbox-server/web_tool_config.json \
  --host 127.0.0.1 \
  --log-level DEBUG
```

## 停止服务

在运行终端中按 `Ctrl+C` 即可停止服务。
