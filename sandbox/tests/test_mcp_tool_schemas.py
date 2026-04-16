"""
Tests for MCP tool schemas integration.
"""

from sandbox.tool_schemas import get_all_tool_names, get_tool_schemas

EXPECTED_MCP_SERVERS = {
    "arxiv-latex",
    "arxiv_local",
    "canvas",
    "emails",
    "excel",
    "fetch",
    "filesystem",
    "google_calendar",
    "google_forms",
    "google_sheet",
    "howtocook",
    "memory",
    "notion",
    "pdf-tools",
    "playwright_with_chunk",
    "pptx",
    "rail_12306",
    "scholarly",
    "snowflake",
    "terminal",
    "woocommerce",
    "word",
    "yahoo-finance",
    "youtube",
    "youtube-transcript",
}


def test_mcp_tools_visible_in_global_catalog():
    """MCP tools should appear in the global tool name catalog."""
    names = get_all_tool_names()

    assert "mcp:filesystem.list_directory" in names
    assert "mcp:terminal.run_command" in names


def test_mcp_wildcard_filtering_by_server():
    """Wildcard filtering should support mcp:server.* patterns."""
    schemas = get_tool_schemas(["mcp:filesystem.*"])
    names = {schema["name"] for schema in schemas}

    assert "mcp:filesystem.list_directory" in names
    assert "mcp:filesystem.read_text_file" in names
    assert all(name.startswith("mcp:filesystem.") for name in names)


def test_mcp_specific_tool_filtering():
    """Specific MCP tool names should filter correctly."""
    schemas = get_tool_schemas(["mcp:terminal.run_command"])

    assert len(schemas) == 1
    assert schemas[0]["name"] == "mcp:terminal.run_command"


def test_mcp_hyphenated_server_filter_does_not_match_alias_variants(monkeypatch):
    """Hyphenated MCP server filters should stay literal and not expand to alias variants."""
    import sandbox.tool_schemas as tool_schemas

    def fake_mcp_schemas():
        return [
            {
                "name": "mcp:yahoo-finance.get_stock_info",
                "description": "test tool",
                "parameters": [],
                "server": "yahoo-finance",
                "tool": "get_stock_info",
            },
            {
                "name": "mcp:yahoo_finance.fake_tool",
                "description": "alias collision",
                "parameters": [],
                "server": "yahoo_finance",
                "tool": "fake_tool",
            },
        ]

    monkeypatch.setattr(tool_schemas, "get_mcp_tool_schemas", fake_mcp_schemas)

    schemas = tool_schemas.get_tool_schemas(["mcp:yahoo-finance.*"])
    names = {schema["name"] for schema in schemas}

    assert "mcp:yahoo-finance.get_stock_info" in names
    assert "mcp:yahoo_finance.fake_tool" not in names


def test_empty_allowed_tools_keeps_global_catalog_unfiltered():
    """An empty allow-list should preserve AgentFlow's no-filtering semantics."""
    assert get_tool_schemas([]) == get_tool_schemas()


def test_mcp_manifest_covers_all_configured_servers():
    """Static MCP schemas should cover every configured Toolathlon server namespace."""
    mcp_servers = {
        name[len("mcp:"):].split(".", 1)[0]
        for name in get_all_tool_names()
        if name.startswith("mcp:")
    }

    assert EXPECTED_MCP_SERVERS.issubset(mcp_servers)
