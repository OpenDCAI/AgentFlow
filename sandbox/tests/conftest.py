import os
from pathlib import Path


_REAL_MCP_TEST_FILES = {
    "test_mcp_real_domain_smokes.py",
    "test_mcp_real_server_smokes.py",
}


def pytest_ignore_collect(collection_path, config):
    if os.environ.get("AGENTFLOW_RUN_MCP_REAL") == "1":
        return False

    path = Path(str(collection_path))
    return path.name in _REAL_MCP_TEST_FILES
