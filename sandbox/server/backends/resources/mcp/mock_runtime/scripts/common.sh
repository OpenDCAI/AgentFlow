#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOCK_RUNTIME_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$MOCK_RUNTIME_DIR/.env"
COMPOSE_FILE="$MOCK_RUNTIME_DIR/docker-compose.yml"
LOG_DIR="$MOCK_RUNTIME_DIR/logs"
RUN_DIR="$MOCK_RUNTIME_DIR/run"
NODE_BIN="${NODE_BIN:-node}"

load_mock_runtime_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "mock runtime env file not found: $ENV_FILE" >&2
    return 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
}

require_toolathlon_root() {
  if [[ -z "${TOOLATHLON_GYM_ROOT:-}" ]]; then
    echo "TOOLATHLON_GYM_ROOT is required" >&2
    return 1
  fi

  if [[ ! -d "$TOOLATHLON_GYM_ROOT" ]]; then
    echo "TOOLATHLON_GYM_ROOT does not exist: $TOOLATHLON_GYM_ROOT" >&2
    return 1
  fi
}

ensure_runtime_dirs() {
  mkdir -p "$LOG_DIR" "$RUN_DIR"
}

service_script_path() {
  local service="$1"
  printf '%s/shims/%s/server.mjs\n' "$MOCK_RUNTIME_DIR" "$service"
}

service_pid_path() {
  local service="$1"
  background_pid_path "$service"
}

service_log_path() {
  local service="$1"
  background_log_path "$service"
}

background_pid_path() {
  local name="$1"
  printf '%s/%s.pid\n' "$RUN_DIR" "$name"
}

background_log_path() {
  local name="$1"
  printf '%s/%s.log\n' "$LOG_DIR" "$name"
}

service_host() {
  local service="$1"
  case "$service" in
    canvas) printf '%s\n' "${CANVAS_SHIM_HOST:-127.0.0.1}" ;;
    notion) printf '%s\n' "${NOTION_SHIM_HOST:-127.0.0.1}" ;;
    woocommerce) printf '%s\n' "${WOOCOMMERCE_SHIM_HOST:-127.0.0.1}" ;;
    *)
      echo "unknown service: $service" >&2
      return 1
      ;;
  esac
}

service_port() {
  local service="$1"
  case "$service" in
    canvas) printf '%s\n' "${CANVAS_SHIM_PORT:-38080}" ;;
    notion) printf '%s\n' "${NOTION_SHIM_PORT:-38081}" ;;
    woocommerce) printf '%s\n' "${WOOCOMMERCE_SHIM_PORT:-38082}" ;;
    *)
      echo "unknown service: $service" >&2
      return 1
      ;;
  esac
}

service_healthz_url() {
  local service="$1"
  local host
  local port
  host="$(service_host "$service")" || return 1
  port="$(service_port "$service")" || return 1

  if [[ "$service" == "canvas" ]]; then
    printf 'https://%s:%s/healthz\n' "$host" "$port"
    return 0
  fi

  printf 'http://%s:%s/healthz\n' "$host" "$port"
}

docker_compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

postgres_container_id() {
  docker_compose ps -q postgres
}

postgres_health_status() {
  local container_id
  container_id="$(postgres_container_id)"
  if [[ -z "$container_id" ]]; then
    printf 'not_running\n'
    return 1
  fi

  docker inspect \
    --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
    "$container_id"
}

wait_for_postgres_healthy() {
  local attempts="${1:-30}"
  local sleep_seconds="${2:-2}"
  local status=""
  local attempt

  for ((attempt = 1; attempt <= attempts; attempt++)); do
    status="$(postgres_health_status 2>/dev/null || true)"
    if [[ "$status" == "healthy" ]]; then
      return 0
    fi
    sleep "$sleep_seconds"
  done

  echo "postgres did not become healthy; last status: ${status:-unknown}" >&2
  return 1
}

is_pid_running() {
  local pid="$1"
  kill -0 "$pid" 2>/dev/null
}

service_pid() {
  local service="$1"
  local pid_file
  pid_file="$(service_pid_path "$service")"
  if [[ -f "$pid_file" ]]; then
    cat "$pid_file"
  fi
}

service_is_running() {
  local service="$1"
  local pid
  pid="$(service_pid "$service")"
  [[ -n "$pid" ]] && is_pid_running "$pid"
}

start_service_process() {
  local service="$1"
  local script_path

  script_path="$(service_script_path "$service")"

  if [[ ! -f "$script_path" ]]; then
    echo "service script not found: $script_path" >&2
    return 1
  fi

  if service_is_running "$service"; then
    echo "$service is already running" >&2
    return 1
  fi

  start_node_background "$service" env TOOLATHLON_GYM_ROOT="$TOOLATHLON_GYM_ROOT" \
    "$NODE_BIN" "$script_path"
}

start_node_background() {
  local name="$1"
  shift

  local pid_file
  local log_file
  local pid

  pid_file="$(background_pid_path "$name")"
  log_file="$(background_log_path "$name")"

  rm -f "$pid_file"
  (
    cd "$MOCK_RUNTIME_DIR"
    nohup "$@" >>"$log_file" 2>&1 &
    echo $! >"$pid_file"
  )

  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]] || ! is_pid_running "$pid"; then
    echo "failed to start $name" >&2
    return 1
  fi
}

stop_service_process() {
  local service="$1"
  local pid_file
  local pid

  pid_file="$(service_pid_path "$service")"
  if [[ ! -f "$pid_file" ]]; then
    return 0
  fi

  pid="$(cat "$pid_file")"
  if [[ -n "$pid" ]] && is_pid_running "$pid"; then
    kill "$pid"
    for _ in {1..10}; do
      if ! is_pid_running "$pid"; then
        break
      fi
      sleep 1
    done
    if is_pid_running "$pid"; then
      kill -9 "$pid"
    fi
  fi

  rm -f "$pid_file"
}

probe_service_healthz() {
  local service="$1"
  local url
  local curl_args=(-fsS --max-time 5)

  url="$(service_healthz_url "$service")" || return 1
  if [[ "$service" == "canvas" ]]; then
    curl_args+=(-k)
  fi

  curl "${curl_args[@]}" "$url" >/dev/null
}

wait_for_service_healthz() {
  local service="$1"
  local attempts="${2:-20}"
  local sleep_seconds="${3:-1}"
  local attempt

  for ((attempt = 1; attempt <= attempts; attempt++)); do
    if probe_service_healthz "$service"; then
      return 0
    fi
    sleep "$sleep_seconds"
  done

  echo "$service health check failed" >&2
  return 1
}
