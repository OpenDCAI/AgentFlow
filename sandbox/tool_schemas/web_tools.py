"""
Web Tool Schemas

This module defines the tool schemas for web operations.
These schemas are used to construct prompts for the LLM agent.
"""

from typing import List, Dict, Any


def get_web_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all web tool schemas.

    Returns:
        List of tool schema dictionaries
    """
    return [
        get_web_search_schema(),
        get_web_visit_schema(),
    ]


def get_web_search_schema() -> Dict[str, Any]:
    """
    Schema for web_search tool - batched web search queries.
    """
    return {
        "name": "web_search",
        "description": (
            "Perform batched web searches and return top results for each query."
        ),
        "parameters": [
            {
                "name": "query",
                "type": "array",
                "array_type": "string",
                "description": (
                    "Array of query strings. Include multiple complementary "
                    "search queries in a single call."
                ),
                "required": True
            }
        ]
    }


def get_web_visit_schema() -> Dict[str, Any]:
    """
    Schema for web_visit tool - visit URLs and extract content by goal.
    """
    return {
        "name": "web_visit",
        "description": (
            "Visit web pages and extract relevant content based on the goal."
        ),
        "parameters": [
            {
                "name": "urls",
                "type": "array",
                "array_type": "string",
                "description": (
                    "Array of URLs to visit and extract content from."
                ),
                "required": True
            },
            {
                "name": "goal",
                "type": "string",
                "description": "The goal or purpose for content extraction.",
                "required": True
            }
        ]
    }
