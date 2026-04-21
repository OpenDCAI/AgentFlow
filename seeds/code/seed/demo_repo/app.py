import json
from pathlib import Path

from lib.helpers import render_greeting


CONFIG_PATH = Path(__file__).parent / "config" / "app_config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def build_message() -> str:
    config = load_config()
    return render_greeting(config["default_name"], "?")


if __name__ == "__main__":
    print(build_message())
