"""
Document QA Tool Schemas

This module defines the tool schemas for document QA operations.
These schemas are used to construct prompts for the LLM agent.
"""

from typing import List, Dict, Any


def get_doc_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all document QA tool schemas.

    Returns:
        List of tool schema dictionaries
    """
    return [
        get_doc_search_schema(),
        get_doc_read_schema(),
    ]


def get_doc_search_schema() -> Dict[str, Any]:
    """
    Schema for doc_search tool - search keywords in document.
    """
    return {
        "name": "doc-search",
        "description": (
            "Search for keywords in the document. This tool searches through "
            "headings, paragraphs, tables, and image captions/alt text. "
            "Use this tool to find relevant sections before reading them. "
            "Note: seed_path is automatically provided from seed.jsonl kwargs, you don't need to specify it."
        ),
        "parameters": [
            {
                "name": "key_words",
                "type": "array",
                "array_type": "string",
                "description": (
                    "List of keywords to search for. Can be a single keyword or multiple keywords. "
                    "The tool will search for all occurrences of these keywords in the document."
                ),
                "required": True,
            },
            {
                "name": "max_search_results",
                "type": "integer",
                "description": "Maximum number of search results to return per keyword (default: 10)",
                "required": False,
            },
        ],
    }


def get_doc_read_schema() -> Dict[str, Any]:
    """
    Schema for doc_read tool - read document sections with visual and textual content.
    """
    return {
        "name": "doc-read",
        "description": (
            "Read specific document sections and extract useful information using visual language model. "
            "This tool processes both text and images (figures, tables, page layouts) from the specified sections. "
            "Use this tool after searching to read the relevant sections and extract detailed information. "
            "Note: seed_path is automatically provided from seed.jsonl kwargs, you don't need to specify it."
        ),
        "parameters": [
            {
                "name": "section_ids",
                "type": "array",
                "array_type": "string",
                "description": (
                    "List of section IDs to read (e.g., ['1.2.1', '1.2.2']). "
                    "Section IDs can be found from search results or document outline."
                ),
                "required": True,
            },
            {
                "name": "goal",
                "type": "string",
                "description": (
                    "The goal or question describing what information to extract from the sections. "
                    "This guides the visual language model to focus on relevant content."
                ),
                "required": True,
            },
            {
                "name": "max_image_num",
                "type": "integer",
                "description": "Maximum number of visual inputs (pages/images/tables) to include (default: 10)",
                "required": False,
            },
            {
                "name": "max_text_token",
                "type": "integer",
                "description": "Maximum text length in characters (default: 20000)",
                "required": False,
            },
        ],
    }

