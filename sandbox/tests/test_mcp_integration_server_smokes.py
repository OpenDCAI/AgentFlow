import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from sandbox.server.backends.error_codes import ErrorCode
from sandbox.tests.mcp_integration_cases import (
    ALL_MCP_SERVERS,
    FILESYSTEM_TERMINAL_BOOTSTRAP_CASE,
    PARALLEL_SAFE_MCP_SERVERS,
    SERVER_SMOKE_CASES,
    SERIAL_ONLY_MCP_SERVERS,
)
from sandbox.tests.mcp_integration_env import (
    build_mcp_server,
    cleanup_worker,
    execute_tool,
    require_mcp_integration_enabled,
)


pytestmark = require_mcp_integration_enabled()


def render_payload_text(result) -> str:
    return json.dumps(result.get("data"), ensure_ascii=False)


def resolve_case_params(value, workspace_root: Path):
    if isinstance(value, dict):
        return {
            key: resolve_case_params(inner_value, workspace_root)
            for key, inner_value in value.items()
        }
    if isinstance(value, list):
        return [resolve_case_params(item, workspace_root) for item in value]
    if isinstance(value, str):
        return (
            value.replace("{workspace_root}", str(workspace_root))
            .replace(
                "{woocommerce_site_url}",
                os.getenv("AGENTFLOW_MCP_WOOCOMMERCE_SITE_URL", "http://localhost:8081"),
            )
        )
    return value


def smoke_context(*, server_name: str, workspace_root: Path) -> str:
    execution_class = "A" if server_name in PARALLEL_SAFE_MCP_SERVERS else "B"
    return (
        "server smoke failed"
        f" [server={server_name}]"
        f" [class={execution_class}]"
        " [phase=tool execution]"
        f" [workspace={workspace_root}]"
    )


async def assert_single_server_smoke(server_name: str, tmp_path: Path) -> None:
    case = SERVER_SMOKE_CASES[server_name]
    workspace_root = tmp_path / server_name
    server = build_mcp_server(
        enabled_mcp_servers=[server_name],
        workspace_root=workspace_root,
    )
    worker_id = f"single-{server_name}"
    try:
        result = await execute_tool(
            server,
            worker_id,
            case["action"],
            resolve_case_params(case.get("params", {}), workspace_root),
        )
        assert result["code"] == ErrorCode.SUCCESS, (
            f"{smoke_context(server_name=server_name, workspace_root=workspace_root)} "
            f"returned code={result['code']} payload={render_payload_text(result)}"
        )

        payload_text = render_payload_text(result)
        expected_signal = case["expected_signal"].lower()
        assert expected_signal in payload_text.lower(), (
            f"{smoke_context(server_name=server_name, workspace_root=workspace_root)} "
            f"missing expected signal={case['expected_signal']!r} payload={payload_text}"
        )

        if not case.get("allow_error_payload", False):
            data = result.get("data")
            if isinstance(data, dict):
                assert data.get("isError") is not True, (
                    f"{smoke_context(server_name=server_name, workspace_root=workspace_root)} "
                    f"returned isError payload={payload_text}"
                )
    finally:
        await cleanup_worker(server, worker_id)


def test_server_partition_is_complete():
    assert set(ALL_MCP_SERVERS) == set(PARALLEL_SAFE_MCP_SERVERS) | set(SERIAL_ONLY_MCP_SERVERS)
    assert set(PARALLEL_SAFE_MCP_SERVERS).isdisjoint(SERIAL_ONLY_MCP_SERVERS)
    assert set(SERVER_SMOKE_CASES) == set(ALL_MCP_SERVERS)


@pytest.mark.anyio
@pytest.mark.parametrize("server_name", PARALLEL_SAFE_MCP_SERVERS)
async def test_single_server_parallel_safe_smoke(server_name, tmp_path):
    await assert_single_server_smoke(server_name, tmp_path)


@pytest.mark.anyio
@pytest.mark.parametrize("server_name", SERIAL_ONLY_MCP_SERVERS)
async def test_single_server_serial_smoke(server_name, tmp_path):
    await assert_single_server_smoke(server_name, tmp_path)


@pytest.mark.anyio
async def test_all_enabled_mcp_servers_startup_serial(tmp_path):
    server = build_mcp_server(
        enabled_mcp_servers=list(ALL_MCP_SERVERS),
        workspace_root=tmp_path / "all-enabled",
    )
    worker_id = "all-enabled-startup"
    try:
        session = await server.resource_router.get_or_create_session(worker_id, "mcp")
        clients = session["data"]["clients"]
        assert set(clients) == set(ALL_MCP_SERVERS)
    finally:
        await cleanup_worker(server, worker_id)


@pytest.mark.anyio
async def test_filesystem_terminal_shared_session_smoke(tmp_path):
    server = build_mcp_server(
        enabled_mcp_servers=FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["enabled_mcp_servers"],
        workspace_root=tmp_path / "workspaces",
    )
    worker_id = "filesystem-terminal-bootstrap"
    try:
        write_result = await execute_tool(
            server,
            worker_id,
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["write_action"],
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["write_params"],
        )
        assert write_result["code"] == ErrorCode.SUCCESS

        run_result = await execute_tool(
            server,
            worker_id,
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["verify_action"],
            FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["verify_params"],
        )
        assert run_result["code"] == ErrorCode.SUCCESS
        assert FILESYSTEM_TERMINAL_BOOTSTRAP_CASE["expected_signal"] in str(run_result["data"])
    finally:
        await cleanup_worker(server, worker_id)
