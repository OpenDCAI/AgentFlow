#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

SERVICES=(canvas notion woocommerce)
STARTED_SERVICES=()
POSTGRES_STARTED_BY_SCRIPT=0

cleanup_on_failure() {
  local service
  for ((idx = ${#STARTED_SERVICES[@]} - 1; idx >= 0; idx--)); do
    service="${STARTED_SERVICES[$idx]}"
    stop_service_process "$service" || true
  done

  if [[ "$POSTGRES_STARTED_BY_SCRIPT" -eq 1 ]]; then
    docker_compose stop postgres || true
  fi
}

trap cleanup_on_failure ERR

load_mock_runtime_env
require_toolathlon_root
ensure_runtime_dirs

if [[ -z "$(postgres_container_id)" ]]; then
  POSTGRES_STARTED_BY_SCRIPT=1
fi

docker_compose up -d postgres
wait_for_postgres_healthy

for service in "${SERVICES[@]}"; do
  start_service_process "$service"
  STARTED_SERVICES+=("$service")
  wait_for_service_healthz "$service"
done

trap - ERR

echo "mock runtime started"
