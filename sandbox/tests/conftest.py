import os
from pathlib import Path


_INTEGRATION_MCP_TEST_FILES = {
    "test_mcp_integration_domain_smokes.py",
    "test_mcp_integration_server_smokes.py",
}


def pytest_ignore_collect(collection_path, config):
    if os.environ.get("AGENTFLOW_RUN_MCP_INTEGRATION") == "1":
        return False

    path = Path(str(collection_path))
    return path.name in _INTEGRATION_MCP_TEST_FILES
