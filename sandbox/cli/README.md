# Sandbox CLI Usage

This directory contains the Python startup entry for Sandbox Server:

- `sandbox/cli/sandbox-server.py`

Recommended: start from the project root via the unified shell entry script:

- `start_sandbox_server.sh`

## Recommended Startup

```bash
./start_sandbox_server.sh \
  --config ./configs/sandbox-server/web_config.json
```

This script calls `sandbox/cli/sandbox-server.py` and exits with an error if
the entry file is missing.

## Run Python Entry Directly

```bash
python3 ./sandbox/cli/sandbox-server.py \
  --config ./configs/sandbox-server/web_config.json
```

## Common Arguments

```bash
# Specify config file (required)
--config, -c <path>

# Specify host/port (when using wrapper script, these are ignored and read from config)
# To override, use Python script directly
--host <host>
--port, -p <port>

# Log level
--log-level DEBUG|INFO|WARNING|ERROR

# Show parsed config only (do not start the server)
--show-config
```

**Note**: The `start_sandbox_server.sh` wrapper script ignores `--host` and `--port` arguments and reads these values from the config file (`server.url`, `server.host`, `server.port`). To override host/port, either:
- Modify the config file, or
- Use the Python script directly: `python3 ./sandbox/cli/sandbox-server.py`

## Examples

```bash
# Start with host/port from config
./start_sandbox_server.sh \
  --config ./configs/sandbox-server/web_config.json

# Override port (the wrapper ignores --host/--port and uses config values)
# Note: To override host/port, modify the config file or use Python script directly
./start_sandbox_server.sh \
  --config ./configs/sandbox-server/web_config.json \
  --port 8080

# Local debug (use Python script directly to override host/port)
python3 ./sandbox/cli/sandbox-server.py \
  --config ./configs/sandbox-server/web_config.json \
  --host 127.0.0.1 \
  --log-level DEBUG
```

## Stop the Server

Press `Ctrl+C` in the running terminal to stop the server.
