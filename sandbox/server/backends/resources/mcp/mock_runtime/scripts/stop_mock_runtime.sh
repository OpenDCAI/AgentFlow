#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

SERVICES=(canvas notion woocommerce)

load_mock_runtime_env
ensure_runtime_dirs

for service in "${SERVICES[@]}"; do
  stop_service_process "$service"
done

docker_compose down

echo "mock runtime stopped"
