import json

from sandbox.sandbox import Sandbox, SandboxConfig


def test_load_server_config_expands_env_default_placeholders(tmp_path, monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_ROOT", raising=False)

    config_path = tmp_path / "code_config.json"
    raw_config = {
        "resources": {
            "code": {
                "enabled": True,
                "config": {
                    "claude_code_root": "${CLAUDE_CODE_ROOT:-/home/a1/sdb/dxd/claude-code-py}"
                },
            }
        }
    }
    config_path.write_text(json.dumps(raw_config), encoding="utf-8")

    sandbox = Sandbox(config=SandboxConfig(server_config_path=str(config_path)))

    loaded = sandbox._load_server_config()

    assert (
        loaded["resources"]["code"]["config"]["claude_code_root"]
        == "/home/a1/sdb/dxd/claude-code-py"
    )
