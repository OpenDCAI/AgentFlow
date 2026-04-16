"""
Static MCP tool schemas for Toolathlon-GYM integration.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


_MANIFEST_PATH = Path(__file__).with_name("toolathlon_gym_manifest.json")


def get_toolathlon_gym_tool_schemas() -> List[Dict[str, Any]]:
    """Load the checked-in Toolathlon-GYM MCP tool manifest."""
    with open(_MANIFEST_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)
