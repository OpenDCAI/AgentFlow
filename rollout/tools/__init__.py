"""
Tool schemas for Rollout pipeline

This module provides tool schemas for agent execution.
It reuses schemas from synthesis module and adds additional tools.
"""

from typing import Optional, List, Dict, Any

# Shared tool schemas are defined in synthesis.tools
from synthesis.tools import (
    get_rag_tool_schemas,
    get_web_tool_schemas,
    get_vm_tool_schemas,
    get_doc_tool_schemas,
    get_ds_tool_schemas,
    get_sql_tool_schemas,
)


def _tool_name_aliases(name: str) -> set[str]:
    """Return equivalent tool-name variants across '-', '_' and ':' separators."""
    aliases = {name}
    if ":" in name:
        prefix, suffix = name.split(":", 1)
        aliases.add(f"{prefix}-{suffix}")
    if "_" in name:
        prefix, suffix = name.split("_", 1)
        aliases.add(f"{prefix}-{suffix}")
    if "-" in name:
        prefix, suffix = name.split("-", 1)
        aliases.add(f"{prefix}:{suffix}")
        aliases.add(f"{prefix}_{suffix}")
    return aliases


def get_tool_schemas(allowed_tools: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Get tool schemas, optionally filtered by tool names.
    
    Args:
        allowed_tools: List of tool names to include. If None, returns all tools.
            Tool names can be:
            - Full name: "vm_click", "rag_search"
            - Wildcard by prefix: "vm_*" (all vm tools), "web_*" (all web tools)
            
    Returns:
        List of tool schema dictionaries
    """
    # Collect all available schemas from synthesis tools
    all_schemas = (
        get_rag_tool_schemas()
        + get_web_tool_schemas()
        + get_vm_tool_schemas()
        + get_doc_tool_schemas()
        + get_ds_tool_schemas()
        + get_sql_tool_schemas()
    )
    
    if not allowed_tools:
        return all_schemas
    
    # Process allowed_tools to expand wildcards and naming aliases
    allowed_set = set()
    wildcard_prefixes = set()
    
    for tool in allowed_tools:
        if tool.endswith(":*") or tool.endswith("_*") or tool.endswith("-*"):
            # Wildcard pattern like "vm:*" or "vm_*"
            prefix = tool[:-1]  # Remove the "*"
            wildcard_prefixes.update(_tool_name_aliases(prefix))
        else:
            allowed_set.update(_tool_name_aliases(tool))
    
    # Filter schemas
    filtered = []
    for schema in all_schemas:
        name = schema.get("name", "")
        
        # Check exact match
        if name in allowed_set:
            filtered.append(schema)
            continue
        
        # Check wildcard match
        for prefix in wildcard_prefixes:
            if name.startswith(prefix):
                filtered.append(schema)
                break
    
    return filtered


def get_all_tool_names() -> List[str]:
    """Get all available tool names"""
    schemas = get_tool_schemas()
    return [s.get("name", "") for s in schemas]


def get_tools_by_resource(resource_type: str) -> List[Dict[str, Any]]:
    """
    Get tools for a specific resource type.
    
    Args:
        resource_type: Resource type like "vm", "rag", "web", "bash", "code"
        
    Returns:
        List of tool schemas for that resource
    """
    prefix_colon = f"{resource_type}:"
    prefix_underscore = f"{resource_type}_"
    prefix_hyphen = f"{resource_type}-"
    return [
        s for s in get_tool_schemas()
        if s.get("name", "").startswith(prefix_colon)
        or s.get("name", "").startswith(prefix_underscore)
        or s.get("name", "").startswith(prefix_hyphen)
    ]


__all__ = [
    "get_tool_schemas",
    "get_all_tool_names",
    "get_tools_by_resource",
    "get_rag_tool_schemas",
    "get_web_tool_schemas",
    "get_vm_tool_schemas",
    "get_doc_tool_schemas",
    "get_ds_tool_schemas",
    "get_sql_tool_schemas",
]
