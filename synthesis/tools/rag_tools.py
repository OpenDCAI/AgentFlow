"""
RAG Tool Schemas

This module defines the tool schemas for RAG operations.
These schemas are used to construct prompts for the LLM agent.
"""

from typing import List, Dict, Any


def get_rag_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all RAG tool schemas.

    Returns:
        List of tool schema dictionaries
    """
    return [
        get_rag_search_schema()
    ]


def get_rag_search_schema() -> Dict[str, Any]:
    """
    Schema for local_search tool - basic RAG index query.

    This tool searches the pre-built RAG index for relevant text chunks.
    """
    return {
        "name": "rag_search",
        "description": (
            "Search the pre-built RAG index for the most relevant text chunks. "
            "Use this tool to answer questions related to the indexed knowledge."
        ),
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "Query text to look up in the index",
                "required": True
            },
            {
                "name": "top_k",
                "type": "integer",
                "description": "Number of top relevant text chunks to retrieve (default: 10)",
                "required": False
            }
        ]
    }
