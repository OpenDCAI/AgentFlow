#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/sandbox/cli/sandbox-server.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
  echo "错误: 未找到启动脚本: $PYTHON_SCRIPT" >&2
  exit 1
fi

CONFIG_PATH=""
PASSTHROUGH_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config|-c)
      if [[ $# -lt 2 ]]; then
        echo "错误: --config 需要传入配置文件路径" >&2
        exit 1
      fi
      CONFIG_PATH="$2"
      PASSTHROUGH_ARGS+=("$1" "$2")
      shift 2
      ;;
    --host|--port|-p)
      # host/port 统一由配置文件提供，忽略外部传入避免多来源
      if [[ "$1" == "--port" || "$1" == "-p" || "$1" == "--host" ]]; then
        if [[ $# -lt 2 ]]; then
          echo "错误: $1 需要传入参数" >&2
          exit 1
        fi
        echo "提示: 检测到 $1 参数，已忽略（统一使用配置文件中的 server.url/server.port）"
        shift 2
      fi
      ;;
    *)
      PASSTHROUGH_ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ -z "$CONFIG_PATH" ]]; then
  echo "错误: 必须提供 --config <path>" >&2
  exit 1
fi

readarray -t ENDPOINT < <(
python3 - "$CONFIG_PATH" <<'PY'
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

config_path = Path(sys.argv[1]).expanduser()
if not config_path.is_absolute():
    config_path = Path.cwd() / config_path

if not config_path.exists():
    raise FileNotFoundError(f"配置文件未找到: {config_path}")

with open(config_path, "r", encoding="utf-8") as f:
    data = json.load(f)

server = data.get("server", {})
url = str(server.get("url", "")).strip()
port = int(server.get("port", 18890))
host = str(server.get("host", "")).strip()

if url:
    parsed = urlparse(url)
    host = parsed.hostname or host
    if parsed.port:
        port = parsed.port

host = host or "127.0.0.1"
print(host)
print(str(port))
PY
)

HOST="${ENDPOINT[0]}"
PORT="${ENDPOINT[1]}"

exec python3 "$PYTHON_SCRIPT" "${PASSTHROUGH_ARGS[@]}" --host "$HOST" --port "$PORT"

