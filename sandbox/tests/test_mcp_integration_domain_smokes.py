import json
import sys
from pathlib import PurePosixPath
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from sandbox.server.backends.error_codes import ErrorCode
from sandbox.tests.mcp_integration_cases import DOMAIN_SMOKE_CASES
from sandbox.tests.mcp_integration_env import (
    build_mcp_server,
    cleanup_worker,
    execute_tool,
    require_mcp_integration_enabled,
)


pytestmark = require_mcp_integration_enabled()


EXPECTED_DOMAINS = (
    "canvas",
    "snowflake",
    "woocommerce",
    "yahoo_finance",
    "youtube",
    "train",
)


def assert_mcp_result_ok(result):
    assert result["code"] == ErrorCode.SUCCESS
    data = result.get("data")
    if isinstance(data, dict):
        assert data.get("isError") is not True


def extract_file_text(result):
    data = result.get("data")
    if isinstance(data, dict):
        structured = data.get("structuredContent")
        if isinstance(structured, dict):
            content = structured.get("content")
            if isinstance(content, str):
                return content

        content_blocks = data.get("content")
        if isinstance(content_blocks, list):
            for block in content_blocks:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    return block["text"]

    return str(data)


def test_domain_case_registry_is_complete():
    assert set(DOMAIN_SMOKE_CASES) == set(EXPECTED_DOMAINS)
    assert len(DOMAIN_SMOKE_CASES) == len(EXPECTED_DOMAINS)


@pytest.mark.anyio
@pytest.mark.parametrize("domain_name", EXPECTED_DOMAINS)
async def test_domain_smoke(domain_name, tmp_path):
    case = DOMAIN_SMOKE_CASES[domain_name]
    server = build_mcp_server(
        enabled_mcp_servers=case["enabled_mcp_servers"],
        workspace_root=tmp_path / domain_name,
    )
    worker_id = f"{domain_name}-domain-smoke"
    try:
        read_result = await execute_tool(
            server,
            worker_id,
            case["read_action"],
            case["read_params"],
        )
        assert_mcp_result_ok(read_result)

        payload_text = json.dumps(read_result["data"], ensure_ascii=False)
        expected_signal = case["expected_signal"].lower()
        assert expected_signal in payload_text.lower()
        artifact_parent = str(PurePosixPath(case["artifact_path"]).parent)
        if artifact_parent != ".":
            mkdir_result = await execute_tool(
                server,
                worker_id,
                "mcp:filesystem.create_directory",
                {"path": artifact_parent},
            )
            assert_mcp_result_ok(mkdir_result)

        write_result = await execute_tool(
            server,
            worker_id,
            "mcp:filesystem.write_file",
            {"path": case["artifact_path"], "content": payload_text},
        )
        assert_mcp_result_ok(write_result)

        verify_result = await execute_tool(
            server,
            worker_id,
            "mcp:filesystem.read_text_file",
            {"path": case["artifact_path"]},
        )
        assert_mcp_result_ok(verify_result)
        artifact_text = extract_file_text(verify_result)
        assert artifact_text.strip()
        assert artifact_text == payload_text
        assert expected_signal in artifact_text.lower()
    finally:
        await cleanup_worker(server, worker_id)
