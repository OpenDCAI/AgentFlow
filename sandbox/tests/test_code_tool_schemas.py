"""
Tests for code tool schemas integration.
"""

from sandbox.tool_schemas import get_all_tool_names, get_tool_schemas, get_tools_by_resource


EXPECTED_CODE_TOOLS = {
    "code-read",
    "code-glob",
    "code-grep",
    "code-bash",
    "code-edit",
    "code-write",
}


def test_code_tools_visible_in_global_catalog():
    """Code tools should appear in the global tool name catalog."""
    names = get_all_tool_names()

    assert "code-read" in names
    assert "code-bash" in names


def test_code_wildcard_filtering():
    """Wildcard filtering should support code-* patterns."""
    schemas = get_tool_schemas(["code-*"])
    names = {schema["name"] for schema in schemas}

    assert names == EXPECTED_CODE_TOOLS


def test_get_tools_by_resource_code():
    """Resource filtering should return all code tools."""
    schemas = get_tools_by_resource("code")
    names = {schema["name"] for schema in schemas}

    assert names == EXPECTED_CODE_TOOLS
