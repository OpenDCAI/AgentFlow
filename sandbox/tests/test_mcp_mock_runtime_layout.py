from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MOCK_RUNTIME_DIR = REPO_ROOT / "sandbox/server/backends/resources/mcp/mock_runtime"
OLD_DB_PATH = REPO_ROOT / "sandbox/server/backends/resources/mcp/db/init.sql.gz"


def test_mcp_mock_runtime_layout():
    compose_path = MOCK_RUNTIME_DIR / "docker-compose.yml"
    env_example_path = MOCK_RUNTIME_DIR / ".env.example"
    readme_path = MOCK_RUNTIME_DIR / "README.md"
    scripts_dir = MOCK_RUNTIME_DIR / "scripts"

    assert compose_path.exists()
    assert env_example_path.exists()
    assert readme_path.exists()
    assert (scripts_dir / "common.sh").exists()
    assert (scripts_dir / "start_mock_runtime.sh").exists()
    assert (scripts_dir / "stop_mock_runtime.sh").exists()
    assert (scripts_dir / "status_mock_runtime.sh").exists()
    assert (MOCK_RUNTIME_DIR / "db/init.sql.gz").exists()
    assert not OLD_DB_PATH.exists()

    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = compose["services"]
    assert list(services) == ["postgres"]

    postgres = services["postgres"]
    assert postgres["volumes"] == [
        "./db/init.sql.gz:/docker-entrypoint-initdb.d/init.sql.gz:ro"
    ]
    assert postgres["ports"] == ["${POSTGRES_HOST_PORT}:5432"]
    assert "healthcheck" in postgres

    env_keys = {
        line.split("=", 1)[0]
        for line in env_example_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    assert env_keys >= {
        "POSTGRES_HOST_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "CANVAS_SHIM_HOST",
        "CANVAS_SHIM_PORT",
        "CANVAS_TLS_CERT_PATH",
        "CANVAS_TLS_KEY_PATH",
        "NOTION_SHIM_HOST",
        "NOTION_SHIM_PORT",
        "WOOCOMMERCE_SHIM_HOST",
        "WOOCOMMERCE_SHIM_PORT",
    }

    readme = readme_path.read_text(encoding="utf-8")
    assert "transparent to mock vs. real services" in readme
    assert "endpoint values wired into its own MCP config" in readme
    assert "current MCP env overrides" in readme
    assert "TOOLATHLON_GYM_ROOT" in readme
    assert "AGENTFLOW_MCP_CANVAS_ENDPOINT" in readme
    assert "AGENTFLOW_MCP_NOTION_ENDPOINT" in readme
    assert "AGENTFLOW_MCP_WOOCOMMERCE_ENDPOINT" in readme
