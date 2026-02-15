"""
Tests for tool schemas
"""

import pytest

from sandbox.tool_schemas import (
    get_tool_schemas,
    get_all_tool_names,
    get_tools_by_resource
)


class TestToolSchemas:
    """Test tool schema functions"""

    def test_get_all_tools(self):
        """Test getting all tools"""
        schemas = get_tool_schemas()
        
        assert len(schemas) > 0
        assert all("name" in s for s in schemas)
        assert all("description" in s for s in schemas)

    def test_get_specific_tools(self):
        """Test getting specific tools"""
        schemas = get_tool_schemas(["web-search", "rag-search"])
        
        assert len(schemas) == 2
        names = [s["name"] for s in schemas]
        assert "web-search" in names
        assert "rag-search" in names

    def test_wildcard_tools(self):
        """Test getting tools with wildcard"""
        schemas = get_tool_schemas(["vm_*"])
        
        # Should get all VM tools
        assert len(schemas) > 5
        assert all(s["name"].startswith("vm-") for s in schemas)

    def test_mixed_specific_and_wildcard(self):
        """Test mixing specific and wildcard"""
        schemas = get_tool_schemas(["web-search", "vm-*"])
        
        names = [s["name"] for s in schemas]
        assert "web-search" in names
        assert any(n.startswith("vm-") for n in names)

    def test_get_all_tool_names(self):
        """Test getting all tool names"""
        names = get_all_tool_names()
        
        assert len(names) > 0
        assert "web-search" in names
        assert "rag-search" in names

    def test_get_tools_by_resource(self):
        """Test getting tools by resource type"""
        vm_tools = get_tools_by_resource("vm")
        
        assert len(vm_tools) > 0
        assert all(t["name"].startswith("vm-") for t in vm_tools)

    def test_tool_schema_structure(self):
        """Test tool schema has correct structure"""
        schemas = get_tool_schemas(["web-search"])
        
        assert len(schemas) == 1
        schema = schemas[0]
        
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
        assert isinstance(schema["parameters"], list)

    def test_parameter_structure(self):
        """Test parameter schema structure"""
        schemas = get_tool_schemas(["web-search"])
        schema = schemas[0]
        
        for param in schema["parameters"]:
            assert "name" in param
            assert "type" in param
            assert "description" in param


class TestToolSchemaIntegration:
    """Integration tests for tool schemas"""

    def test_all_tools_valid(self):
        """Test that all tools have valid schemas"""
        schemas = get_tool_schemas()
        
        for schema in schemas:
            # Each schema should be convertible to OpenAI format
            assert "name" in schema
            assert "description" in schema
            
            # Check parameters
            for param in schema.get("parameters", []):
                assert "name" in param
                valid_types = ["string", "integer", "number", "boolean", "array", "object"]
                assert param.get("type") in valid_types, f"Invalid type for {schema['name']}.{param['name']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
