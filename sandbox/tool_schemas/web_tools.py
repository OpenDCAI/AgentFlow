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
        get_image_search_schema(),
        get_reverse_image_search_schema(),
    ]


def get_web_search_schema() -> Dict[str, Any]:
    """
    Schema for web_search tool - batched web search queries.
    """
    return {
        "name": "web-search",
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
        "name": "web-visit",
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


def get_image_search_schema() -> Dict[str, Any]:
    """
    Schema for image search tool - search images by text query.
    """
    return {
        "name": "web-image_search",
        "description": (
            "Search images by text query. Returns top image results "
            "with titles, image URLs, and source webpage URLs."
        ),
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "Text query to search for images.",
                "required": True
            }
        ]
    }


def get_reverse_image_search_schema() -> Dict[str, Any]:
    """
    Schema for reverse image search tool - search by image URL.
    """
    return {
        "name": "web-reverse_image_search",
        "description": (
            "Reverse image search by providing an image URL. "
            "Returns visually similar images with titles and source URLs."
        ),
        "parameters": [
            {
                "name": "image_url",
                "type": "string",
                "description": "URL of the image to search for similar images.",
                "required": True
            }
        ]
    }
