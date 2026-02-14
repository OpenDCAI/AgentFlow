"""
Tool schemas for RAG synthesis pipeline
"""

from typing import Optional, List, Dict, Any

from .rag_tools import get_rag_tool_schemas
from .web_tools import get_web_tool_schemas
from .vm_tools import get_vm_tool_schemas
from .doc_tools import get_doc_tool_schemas
from .ds_tools import get_ds_tool_schemas
from .sql_tools import get_sql_tool_schemas


def get_tool_schemas(allowed_tools: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Get tool schemas, optionally filtered by tool names.
    """
    schemas = (
        get_rag_tool_schemas()
        + get_web_tool_schemas()
        + get_vm_tool_schemas()
        + get_doc_tool_schemas()
        + get_ds_tool_schemas()
        + get_sql_tool_schemas()
    )
    if not allowed_tools:
        return schemas
    allowed_set = set(allowed_tools)
    return [schema for schema in schemas if schema.get("name") in allowed_set]


__all__ = [
    "get_tool_schemas",
    "get_rag_tool_schemas",
    "get_web_tool_schemas",
    "get_vm_tool_schemas",
    "get_doc_tool_schemas",
    "get_ds_tool_schemas",
    "get_sql_tool_schemas",
]
