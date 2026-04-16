import os
import select
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest

from sandbox.server.config_loader import ConfigLoader


_REQUIRED_PG_VARS = (
    "AGENTFLOW_MCP_PGHOST",
    "AGENTFLOW_MCP_PGPORT",
    "AGENTFLOW_MCP_PGUSER",
    "AGENTFLOW_MCP_PGPASSWORD",
    "AGENTFLOW_MCP_PGDATABASE",
)

_SERVICE_CLEANUP_ATTR = "_mcp_integration_cleanup_callbacks"


def require_mcp_integration_enabled():
    """Return a module-level pytest mark that skips unless AGENTFLOW_RUN_MCP_INTEGRATION=1."""
    return pytest.mark.skipif(
        os.environ.get("AGENTFLOW_RUN_MCP_INTEGRATION") != "1",
        reason="set AGENTFLOW_RUN_MCP_INTEGRATION=1 to run MCP integration smoke tests",
    )


def discover_toolathlon_root() -> Path:
    configured = os.environ.get("TOOLATHLON_GYM_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()

    repo_root = Path(__file__).resolve().parents[2]
    if repo_root.parent.name == ".worktrees":
        repo_root = repo_root.parent.parent

    candidates = (
        repo_root.parent / "toolathlon_gym",
        repo_root / "toolathlon_gym",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def controller_env_overrides() -> dict[str, str]:
    return {
        "PGHOST": os.environ["AGENTFLOW_MCP_PGHOST"],
        "PGPORT": os.environ["AGENTFLOW_MCP_PGPORT"],
        "PGUSER": os.environ["AGENTFLOW_MCP_PGUSER"],
        "PGPASSWORD": os.environ["AGENTFLOW_MCP_PGPASSWORD"],
        "PGDATABASE": os.environ["AGENTFLOW_MCP_PGDATABASE"],
        "CANVAS_DOMAIN": os.getenv("AGENTFLOW_MCP_CANVAS_DOMAIN", "localhost:8080"),
        "WORDPRESS_SITE_URL": os.getenv(
            "AGENTFLOW_MCP_WOOCOMMERCE_SITE_URL",
            "http://localhost:8081",
        ),
    }


def _register_cleanup(server: Any, callback) -> None:
    callbacks = list(getattr(server, _SERVICE_CLEANUP_ATTR, []))
    callbacks.append(callback)
    setattr(server, _SERVICE_CLEANUP_ATTR, callbacks)


def _drain_startup_line(process: subprocess.Popen[str], timeout_seconds: float) -> str:
    assert process.stdout is not None
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(
                "Canvas mock exited before becoming ready"
                + (f": {output.strip()}" if output.strip() else "")
            )

        ready, _, _ = select.select([process.stdout], [], [], 0.1)
        if ready:
            line = process.stdout.readline().strip()
            if line:
                return line

    raise TimeoutError("Timed out waiting for Canvas mock readiness")


def _start_canvas_mock(toolathlon_root: Path) -> tuple[str, Any]:
    mock_script = Path(__file__).with_name("canvas_pg_api_mock.mjs")
    cert_dir = toolathlon_root / "local_servers" / "playwright-mcp" / "tests" / "testserver"
    cert_path = cert_dir / "cert.pem"
    key_path = cert_dir / "key.pem"
    require_from = toolathlon_root / "local_servers" / "mcp-canvas-lms" / "package.json"

    for path in (mock_script, cert_path, key_path, require_from):
        if not path.exists():
            raise RuntimeError(f"Canvas mock prerequisite missing: {path}")

    env = dict(os.environ)
    env.update(controller_env_overrides())
    env.update(
        {
            "CANVAS_MOCK_REQUIRE_FROM": str(require_from),
            "CANVAS_MOCK_TLS_CERT": str(cert_path),
            "CANVAS_MOCK_TLS_KEY": str(key_path),
            "CANVAS_MOCK_HOST": "127.0.0.1",
            "CANVAS_MOCK_PORT": "0",
        }
    )

    process = subprocess.Popen(
        ["node", str(mock_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        cwd=str(toolathlon_root),
    )

    def cleanup() -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5.0)

    try:
        line = _drain_startup_line(process, timeout_seconds=5.0)
        if not line.startswith("READY "):
            raise RuntimeError(f"Unexpected Canvas mock startup output: {line}")
        port = line.split(" ", 1)[1].strip()
        return f"127.0.0.1:{port}", cleanup
    except Exception:
        cleanup()
        raise


def require_controller_prereqs() -> None:
    """
    Fail fast when integration tests are enabled but controller prerequisites are missing.
    """
    if os.environ.get("AGENTFLOW_RUN_MCP_INTEGRATION") != "1":
        raise RuntimeError(
            "MCP integration tests require AGENTFLOW_RUN_MCP_INTEGRATION=1 for explicit opt-in."
        )

    missing_pg = [name for name in _REQUIRED_PG_VARS if not os.environ.get(name)]
    if missing_pg:
        raise RuntimeError(
            "Missing AGENTFLOW_MCP_PG* variables: "
            + ", ".join(sorted(missing_pg))
            + ". Export all required AGENTFLOW_MCP_PG* variables before running MCP integration tests."
        )

    toolathlon_root = discover_toolathlon_root()
    if not toolathlon_root.is_dir():
        raise RuntimeError(
            "Toolathlon root not found at "
            f"{toolathlon_root}. Set TOOLATHLON_GYM_ROOT to a valid toolathlon_gym path."
        )

    mcp_servers_dir = toolathlon_root / "mcp_servers"
    if not mcp_servers_dir.is_dir():
        raise RuntimeError(
            f"Toolathlon MCP servers dir missing: {mcp_servers_dir}. "
            "Ensure toolathlon_gym is present and initialized."
        )

    missing_bins = [binary for binary in ("node", "uv") if shutil.which(binary) is None]
    if missing_bins:
        raise RuntimeError(
            "Missing required runtime binaries: "
            + ", ".join(sorted(missing_bins))
            + ". Install them and ensure they are on PATH."
        )


def build_mcp_server(*, enabled_mcp_servers: list[str], workspace_root: Path):
    require_controller_prereqs()

    workspace_root.mkdir(parents=True, exist_ok=True)
    env_overrides = controller_env_overrides()

    cleanup_callbacks = []
    if "canvas" in enabled_mcp_servers:
        canvas_domain, cleanup = _start_canvas_mock(discover_toolathlon_root())
        env_overrides["CANVAS_DOMAIN"] = canvas_domain
        cleanup_callbacks.append(cleanup)

    try:
        loader = ConfigLoader()
        loader.load_from_dict(
            {
                "server": {"title": "MCP smoke", "session_ttl": 300},
                "resources": {
                    "mcp": {
                        "enabled": True,
                        "backend_class": "sandbox.server.backends.resources.mcp.MCPBackend",
                        "config": {
                            "mcp_servers_path": str(discover_toolathlon_root() / "mcp_servers"),
                            "enabled_mcp_servers": enabled_mcp_servers,
                            "workspace_root": str(workspace_root),
                            "env_overrides": env_overrides,
                        },
                    }
                },
            }
        )
        server = loader.create_server(host="127.0.0.1", port=0)
    except Exception:
        for callback in reversed(cleanup_callbacks):
            callback()
        raise

    for callback in cleanup_callbacks:
        _register_cleanup(server, callback)
    return server


async def execute_tool(
    server: Any,
    worker_id: str,
    action: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    return await server._executor.execute(action=action, params=params, worker_id=worker_id)


async def cleanup_worker(server: Any, worker_id: str) -> None:
    try:
        await server.resource_router.destroy_worker_sessions(worker_id)
    finally:
        callbacks = list(getattr(server, _SERVICE_CLEANUP_ATTR, []))
        setattr(server, _SERVICE_CLEANUP_ATTR, [])
        for callback in callbacks:
            callback()
