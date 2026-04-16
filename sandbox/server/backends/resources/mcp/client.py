"""
Lightweight MCP stdio client and Toolathlon YAML resolver.
"""
import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger("MCPStdioClient")

_PLACEHOLDER_PATTERN = re.compile(r"\$\{([^}]+)\}")
_SUPPORTED_PLACEHOLDERS = {"local_servers_paths", "agent_workspace", "task_dir"}
_BUNDLED_CONFIG_DIR = Path(__file__).parent / "configs"


@dataclass
class MCPProcessConfig:
    name: str
    command: str
    args: list[str]
    env: dict[str, str]
    cwd: str
    timeout_seconds: float


def resolve_mcp_value(
    value: Any,
    *,
    local_servers_path: str,
    agent_workspace: str,
    task_dir: str,
) -> Any:
    if not isinstance(value, str):
        return value

    found_placeholders = {m.group(1) for m in _PLACEHOLDER_PATTERN.finditer(value)}
    unsupported = found_placeholders - _SUPPORTED_PLACEHOLDERS
    if unsupported:
        logger.debug(
            "Skipping unsupported placeholder(s) in MCP config value: %s",
            ", ".join(sorted(unsupported)),
        )

    return (
        value.replace("${local_servers_paths}", local_servers_path)
        .replace("${agent_workspace}", agent_workspace)
        .replace("${task_dir}", task_dir)
    )


def build_server_env(
    *,
    yaml_env: Dict[str, Any] | None = None,
    process_env: Dict[str, Any] | None = None,
) -> dict[str, str]:
    yaml_env = yaml_env or {}
    process_env = process_env or {}
    merged: dict[str, Any] = {}
    merged.update(yaml_env)
    merged.update(process_env)

    pg_bridge = {
        "PG_HOST": "PGHOST",
        "PG_PORT": "PGPORT",
        "PG_DATABASE": "PGDATABASE",
        "PG_USER": "PGUSER",
        "PG_PASSWORD": "PGPASSWORD",
    }
    for target, alias in pg_bridge.items():
        value = merged.get(alias)
        if value is not None:
            merged[target] = value

    return {k: str(v) for k, v in merged.items() if v is not None}


def load_mcp_process_config(
    *,
    server_name: str,
    agent_workspace: str,
    mcp_servers_path: str | Path | None = None,
    config_dir: Path | str | None = None,
    task_dir: str = "",
    process_env: Dict[str, Any] | None = None,
    # Backward compat — deprecated, use mcp_servers_path instead.
    toolathlon_root: Path | str | None = None,
) -> MCPProcessConfig:
    # Backward compatibility: derive paths from toolathlon_root if given.
    if toolathlon_root is not None:
        toolathlon_root = Path(toolathlon_root)
        if config_dir is None:
            config_dir = toolathlon_root / "configs" / "mcp_servers"
        if mcp_servers_path is None:
            mcp_servers_path = str(toolathlon_root / "local_servers")

    config_path = Path(config_dir) if config_dir else _BUNDLED_CONFIG_DIR
    if not config_path.exists():
        raise FileNotFoundError(f"MCP config dir not found: {config_path}")

    yaml_file = config_path / f"{server_name}.yaml"
    cfg: dict[str, Any] | None = None

    if yaml_file.exists():
        with yaml_file.open(encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
    else:
        yaml_file_yml = config_path / f"{server_name}.yml"
        if yaml_file_yml.exists():
            with yaml_file_yml.open(encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
        else:
            matches: list[tuple[Path, dict[str, Any]]] = []
            for candidate in sorted(config_path.glob("*.yaml")) + sorted(config_path.glob("*.yml")):
                with candidate.open(encoding="utf-8") as fh:
                    candidate_cfg = yaml.safe_load(fh) or {}
                if not isinstance(candidate_cfg, dict):
                    continue
                candidate_name = candidate_cfg.get("name", candidate.stem)
                if candidate_name == server_name:
                    matches.append((candidate, candidate_cfg))

            if not matches:
                raise FileNotFoundError(f"MCP config not found for server: {server_name}")
            if len(matches) > 1:
                conflict_files = ", ".join(str(path.name) for path, _ in matches)
                raise ValueError(
                    f"Multiple MCP configs matched server name '{server_name}': {conflict_files}"
                )
            yaml_file, cfg = matches[0]

    assert cfg is not None

    if cfg.get("type") != "stdio":
        raise ValueError(f"Only stdio MCP servers are supported (found: {cfg.get('type')})")

    params = cfg.get("params", {}) or {}
    local_servers_path = str(mcp_servers_path) if mcp_servers_path else ""
    workspace = str(agent_workspace)
    resolve = lambda val: resolve_mcp_value(
        val,
        local_servers_path=local_servers_path,
        agent_workspace=workspace,
        task_dir=task_dir,
    )

    command = resolve(params.get("command", ""))
    args = [resolve(arg) for arg in params.get("args", []) or []]
    env_values = {k: resolve(v) for k, v in (params.get("env") or {}).items()}
    cwd_value = resolve(params.get("cwd", agent_workspace))

    runtime_env = dict(os.environ) if process_env is None else dict(process_env)
    full_env = build_server_env(yaml_env=env_values, process_env=runtime_env)

    timeout_seconds = float(cfg.get("client_session_timeout_seconds", 60.0))

    return MCPProcessConfig(
        name=cfg.get("name", server_name),
        command=command,
        args=args,
        env=full_env,
        cwd=cwd_value,
        timeout_seconds=timeout_seconds,
    )


class MCPStdioClient:
    def __init__(self, config: MCPProcessConfig):
        self._config = config
        self._process: asyncio.subprocess.Process | None = None
        self._request_id = 0
        self._request_lock = asyncio.Lock()

    async def start(self) -> None:
        if self._process is not None:
            return
        os.makedirs(self._config.cwd, exist_ok=True)
        self._process = await asyncio.create_subprocess_exec(
            self._config.command,
            *self._config.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self._config.env,
            cwd=self._config.cwd,
        )

    async def initialize(self) -> None:
        await self._ensure_process()
        await self._request(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "toolathlon-mcp-client", "version": "1.0.0"},
            },
        )
        await self._send_notifications_initialized()

    async def list_tools(self) -> list[dict]:
        await self._ensure_process()
        response = await self._request(method="tools/list", params={})
        result = response.get("result", {}) if isinstance(response, dict) else {}
        tools = result.get("tools") if isinstance(result, dict) else None
        return tools or []

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        await self._ensure_process()
        response = await self._request(
            method="tools/call", params={"name": tool_name, "arguments": arguments}
        )
        result = response.get("result", {}) if isinstance(response, dict) else {}
        return result or {}

    async def close(self) -> None:
        if not self._process:
            return
        process = self._process
        self._process = None

        try:
            process.terminate()
        except Exception:
            pass
        try:
            _, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=5.0)
            if stderr_bytes:
                stderr_text = stderr_bytes.decode("utf-8", errors="replace").strip()
                if stderr_text:
                    logger.warning(
                        "MCP server '%s' stderr on close:\n%s",
                        self._config.name,
                        stderr_text,
                    )
        except TimeoutError:
            kill = getattr(process, "kill", None)
            if callable(kill):
                kill()
            await process.wait()

    async def _send_notifications_initialized(self) -> None:
        await self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    async def _request(
        self, *, method: str, params: dict | None = None
    ) -> dict[str, Any]:
        async with self._request_lock:
            request_id = self._next_request_id()
            payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
            if params is not None:
                payload["params"] = params
            await self._send(payload)
            response = await self._read_response(expected_request_id=request_id)
            if "error" in response:
                raise RuntimeError(f"MCP request failed for '{method}': {response['error']}")
            return response

    async def _send(self, payload: dict[str, Any]) -> None:
        await self._ensure_process()
        assert self._process is not None
        data = (json.dumps(payload) + "\n").encode()
        self._process.stdin.write(data)
        await self._process.stdin.drain()

    async def _read_response(self, *, expected_request_id: int | None = None) -> dict[str, Any]:
        assert self._process is not None
        stdout = self._process.stdout
        if stdout is None:
            raise RuntimeError("MCP process stdout is unavailable")
        while True:
            try:
                line = await asyncio.wait_for(
                    stdout.readline(),
                    timeout=self._config.timeout_seconds,
                )
            except TimeoutError as exc:
                raise TimeoutError("Timed out waiting for MCP server response") from exc

            if not line:
                raise RuntimeError("MCP process stdout closed unexpectedly")
            try:
                payload = json.loads(line.decode())
            except json.JSONDecodeError:
                logger.warning(
                    "MCP server '%s': non-JSON line on stdout: %s",
                    self._config.name,
                    line.decode("utf-8", errors="replace").rstrip(),
                )
                continue
            if "id" not in payload:
                continue
            if expected_request_id is not None and payload.get("id") != expected_request_id:
                continue
            return payload

    async def _ensure_process(self) -> None:
        if self._process is None:
            raise RuntimeError("MCP stdin process has not been started")

    def _next_request_id(self) -> int:
        current = self._request_id
        self._request_id += 1
        return current
