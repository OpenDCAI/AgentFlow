"""
MCP backend package.

This package provides MCP (Model Context Protocol) backend integrations.
Each sub-module implements a specific MCP provider; the generic stdio client
lives in ``client``.

Currently available providers:
- ``toolathlon_gym`` -- Toolathlon-GYM MCP server integration.
"""

from .toolathlon_gym import ToolathlonGymBackend

# Backward-compatible alias so existing configs referencing
# ``sandbox.server.backends.resources.mcp.MCPBackend`` keep working.
MCPBackend = ToolathlonGymBackend

__all__ = [
    "MCPBackend",
    "ToolathlonGymBackend",
]
