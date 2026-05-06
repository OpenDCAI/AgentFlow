#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

SERVICES=(canvas notion woocommerce)
overall_status=0

load_mock_runtime_env
ensure_runtime_dirs

postgres_status="$(postgres_health_status 2>/dev/null || true)"
if [[ -z "$postgres_status" ]]; then
  postgres_status="not_running"
  overall_status=1
elif [[ "$postgres_status" != "healthy" ]]; then
  overall_status=1
fi
echo "postgres: $postgres_status"

for service in "${SERVICES[@]}"; do
  pid="$(service_pid "$service")"
  if [[ -n "$pid" ]] && is_pid_running "$pid"; then
    process_status="running"
  elif [[ -n "$pid" ]]; then
    process_status="stale_pid"
    overall_status=1
  else
    process_status="not_running"
    overall_status=1
  fi

  if probe_service_healthz "$service"; then
    health_status="healthy"
  else
    health_status="unhealthy"
    overall_status=1
  fi

  echo "$service: pid=${pid:-none} process=$process_status healthz=$health_status"
done

exit "$overall_status"
