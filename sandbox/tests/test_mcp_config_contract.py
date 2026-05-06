import json
import importlib.util
import sys
import types
from pathlib import Path

import pytest
import yaml

from sandbox.server.backends.base import BackendConfig


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "configs/sandbox-server/mcp_config.json"
CANVAS_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/canvas.yaml"
EXCEL_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/excel.yaml"
FILESYSTEM_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/filesystem.yaml"
NOTION_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/notion.yaml"
PDF_TOOLS_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/pdf-tools.yaml"
PPTX_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/pptx.yaml"
TERMINAL_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/terminal.yaml"
WORD_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/word.yaml"
WOOCOMMERCE_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/configs/woocommerce.yaml"
INTERNAL_MCP_SERVERS_PATH = (
    REPO_ROOT / "sandbox/server/backends/resources/mcp/vendor/local_servers"
)
MODULE_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/toolathlon_gym.py"


def load_mcp_backend_module():
    package_name = "sandbox.server.backends.resources"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(MODULE_PATH.parent.parent)]
        sys.modules[package_name] = package

    mcp_package_name = f"{package_name}.mcp"
    if mcp_package_name not in sys.modules:
        mcp_package = types.ModuleType(mcp_package_name)
        mcp_package.__path__ = [str(MODULE_PATH.parent)]
        sys.modules[mcp_package_name] = mcp_package

    spec = importlib.util.spec_from_file_location(
        f"{mcp_package_name}.toolathlon_gym",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mcp_config_contract():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    mcp_config = config["resources"]["mcp"]["config"]

    assert mcp_config["enabled_mcp_servers"] == [
        "excel",
        "filesystem",
        "memory",
        "pdf-tools",
        "playwright_with_chunk",
        "pptx",
        "terminal",
        "word",
        "canvas",
        "notion",
        "woocommerce",
    ]
    assert "toolathlon_root" not in mcp_config
    assert mcp_config["env_overrides"] == {
        "CANVAS_DOMAIN": "${AGENTFLOW_MCP_CANVAS_ENDPOINT:-127.0.0.1:38080}",
        "BASE_URL": "${AGENTFLOW_MCP_NOTION_ENDPOINT:-http://127.0.0.1:38081}",
        "WORDPRESS_SITE_URL": "${AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT:-http://127.0.0.1:38082}",
    }
    assert "PGHOST" not in mcp_config["env_overrides"]

    expected_env_keys = {
        CANVAS_PATH: {
            "CANVAS_API_TOKEN",
            "CANVAS_STUDENT_EMAIL",
            "CANVAS_DOMAIN",
            "NODE_TLS_REJECT_UNAUTHORIZED",
        },
        NOTION_PATH: {
            "OPENAPI_MCP_HEADERS",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "http_proxy",
            "https_proxy",
        },
        WOOCOMMERCE_PATH: {
            "WORDPRESS_SITE_URL",
            "WOOCOMMERCE_CONSUMER_KEY",
            "WOOCOMMERCE_CONSUMER_SECRET",
        },
    }

    for path, required_keys in expected_env_keys.items():
        config_yaml = yaml.safe_load(path.read_text(encoding="utf-8"))
        env = config_yaml["params"]["env"]

        assert set(env) == required_keys
        assert not any(key.startswith("PG_") for key in env)


def test_mcp_server_launch_paths_match_vendored_layout():
    expected_configs = {
        EXCEL_PATH: {
            "command": "uv",
            "args": [
                "--directory",
                "${local_servers_paths}/excel-mcp-server",
                "run",
                "excel-mcp-server",
                "stdio",
            ],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH / "excel-mcp-server",
            "kind": "directory",
        },
        PDF_TOOLS_PATH: {
            "command": "uv",
            "args": [
                "--directory",
                "${local_servers_paths}/pdf-tools-mcp",
                "run",
                "pdf-tools-mcp",
                "--workspace_path",
                "${agent_workspace}",
                "--tempfile_dir",
                "${agent_workspace}/.pdf_tools_tempfiles",
            ],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH / "pdf-tools-mcp",
            "kind": "directory",
        },
        PPTX_PATH: {
            "command": "uv",
            "args": [
                "--directory",
                "${local_servers_paths}/Office-PowerPoint-MCP-Server",
                "run",
                "ppt_mcp_server",
            ],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH
            / "Office-PowerPoint-MCP-Server",
            "kind": "directory",
        },
        TERMINAL_PATH: {
            "command": "uv",
            "args": [
                "--directory",
                "${local_servers_paths}/cli-mcp-server",
                "run",
                "cli-mcp-server",
            ],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH / "cli-mcp-server",
            "kind": "directory",
        },
        WORD_PATH: {
            "command": "uv",
            "args": [
                "--directory",
                "${local_servers_paths}/Office-Word-MCP-Server",
                "run",
                "word_mcp_server",
            ],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH / "Office-Word-MCP-Server",
            "kind": "directory",
        },
        FILESYSTEM_PATH: {
            "command": "node",
            "args": [
                "${local_servers_paths}/filesystem/dist/index.js",
                "${agent_workspace}",
            ],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH / "filesystem/dist/index.js",
            "kind": "file",
        },
        CANVAS_PATH: {
            "command": "node",
            "args": ["${local_servers_paths}/mcp-canvas-lms/build/index.js"],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH
            / "mcp-canvas-lms/build/index.js",
            "kind": "file",
        },
        NOTION_PATH: {
            "command": "node",
            "args": ["${local_servers_paths}/notion-mcp-server/bin/cli.mjs"],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH
            / "notion-mcp-server/bin/cli.mjs",
            "kind": "file",
        },
        WOOCOMMERCE_PATH: {
            "command": "node",
            "args": ["${local_servers_paths}/woocommerce-mcp/dist/index.js"],
            "vendored_path": INTERNAL_MCP_SERVERS_PATH
            / "woocommerce-mcp/dist/index.js",
            "kind": "file",
        },
    }

    for path, expected in expected_configs.items():
        config_yaml = yaml.safe_load(path.read_text(encoding="utf-8"))
        params = config_yaml["params"]

        assert params["command"] == expected["command"]
        assert params["args"] == expected["args"]

        vendored_path = expected["vendored_path"]
        if expected["kind"] == "directory":
            assert vendored_path.is_dir()
            assert (vendored_path / "pyproject.toml").is_file()
        else:
            assert vendored_path.is_file()


def test_mcp_config_requires_vendored_or_explicit_mcp_servers_path_by_default():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    module = load_mcp_backend_module()
    backend = module.ToolathlonGymBackend(
        config=BackendConfig(
            enabled=True,
            default_config=config["resources"]["mcp"]["config"],
            description="MCP backend",
        )
    )

    assert backend._get_mcp_servers_path() == str(INTERNAL_MCP_SERVERS_PATH)
