"""
MCP tool schema package.

Aggregates tool schemas from all registered MCP providers.
Currently includes:
- Toolathlon-GYM (438 tools across 25 servers)

To add a new MCP provider, create a sub-module with a
``get_<provider>_tool_schemas()`` function and add it to
``get_mcp_tool_schemas()`` below.
"""

from typing import Any, Dict, List

from .toolathlon_gym import get_toolathlon_gym_tool_schemas


def get_mcp_tool_schemas() -> List[Dict[str, Any]]:
    """Return the union of all registered MCP provider schemas."""
    return get_toolathlon_gym_tool_schemas()


__all__ = [
    "get_mcp_tool_schemas",
    "get_toolathlon_gym_tool_schemas",
]
