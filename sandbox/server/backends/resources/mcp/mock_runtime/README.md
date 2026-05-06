# MCP Mock Runtime

This directory contains an optional standalone mock runtime for AgentFlow's MCP backend.

AgentFlow is transparent to mock vs. real services. It only depends on the endpoint values wired into its own MCP config:

- `AGENTFLOW_MCP_CANVAS_ENDPOINT`
- `AGENTFLOW_MCP_NOTION_ENDPOINT`
- `AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT`

The current mock-runtime scope only covers these three HTTP-backed MCP integrations:

- `canvas`
- `notion`
- `woocommerce`

## What Starts Here

`scripts/start_mock_runtime.sh` brings up:

- the local `postgres` container from `docker-compose.yml`
- the three shim servers under `shims/canvas`, `shims/notion`, and `shims/woocommerce`

This runtime is extra infrastructure. AgentFlow itself still just starts the MCP servers listed in its default config and uses the endpoint overrides above for the three HTTP-backed services.

At the current defaults, that means the following self-contained MCP servers can start alongside the mock-backed HTTP trio:

- `excel`
- `filesystem`
- `howtocook`
- `memory`
- `pdf-tools`
- `playwright_with_chunk`
- `pptx`
- `terminal`
- `word`

## Bring-Up

1. Copy the example env file:

```bash
cp sandbox/server/backends/resources/mcp/mock_runtime/.env.example \
  sandbox/server/backends/resources/mcp/mock_runtime/.env
```

2. Update the copied `.env` before startup:

- `CANVAS_TLS_CERT_PATH` and `CANVAS_TLS_KEY_PATH` in `.env.example` are placeholder paths.
- Point both values at real certificate files before running the shim.
- If your team already keeps test certificates under `TOOLATHLON_GYM_ROOT`, you can repoint these paths there.

3. Export the runtime root and the AgentFlow-visible MCP endpoints:

```bash
export TOOLATHLON_GYM_ROOT=/path/to/exported_mcp_snapshot
export AGENTFLOW_MCP_CANVAS_ENDPOINT=127.0.0.1:38080
export AGENTFLOW_MCP_NOTION_ENDPOINT=http://127.0.0.1:38081
export AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT=http://127.0.0.1:38082
```

4. Start the mock runtime:

```bash
bash sandbox/server/backends/resources/mcp/mock_runtime/scripts/start_mock_runtime.sh
```

Current default shim ports from `.env.example` are:

- `canvas`: `https://127.0.0.1:38080`
- `notion`: `http://127.0.0.1:38081`
- `woocommerce`: `http://127.0.0.1:38082`

Those defaults match AgentFlow's current MCP env overrides:

- `CANVAS_DOMAIN=${AGENTFLOW_MCP_CANVAS_ENDPOINT:-127.0.0.1:38080}`
- `BASE_URL=${AGENTFLOW_MCP_NOTION_ENDPOINT:-http://127.0.0.1:38081}`
- `WORDPRESS_SITE_URL=${AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT:-http://127.0.0.1:38082}`

## Status And Shutdown

Check runtime status:

```bash
bash sandbox/server/backends/resources/mcp/mock_runtime/scripts/status_mock_runtime.sh
```

Stop the runtime:

```bash
bash sandbox/server/backends/resources/mcp/mock_runtime/scripts/stop_mock_runtime.sh
```

`status_mock_runtime.sh` reports postgres health plus each shim's PID/process state and `/healthz` result. `stop_mock_runtime.sh` stops the three shim processes and runs `docker compose down` for the local postgres stack.

## Validation

This phase does not include a dedicated smoke-test suite for the mock runtime. Validation is manual:

- bring the runtime up with `start_mock_runtime.sh`
- confirm healthy output from `status_mock_runtime.sh`
- point AgentFlow at the three exported `AGENTFLOW_MCP_*_ENDPOINT` values
- verify requests against `canvas`, `notion`, and `woocommerce` end-to-end by hand
