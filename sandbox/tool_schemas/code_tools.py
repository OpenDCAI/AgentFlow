"""
Code Tool Schemas

This module defines tool schemas for code workspace operations.
"""

from typing import List, Dict, Any


def get_code_tool_schemas() -> List[Dict[str, Any]]:
    """Get all code tool schemas."""
    return [
        {
            "name": "code-read",
            "description": "Read file content from the coding workspace by file path.",
            "parameters": [
                {
                    "name": "file_path",
                    "type": "string",
                    "description": "Path to the file to read.",
                    "required": True,
                },
                {
                    "name": "offset",
                    "type": "integer",
                    "description": "Optional starting line offset for partial reads.",
                    "required": False,
                },
                {
                    "name": "limit",
                    "type": "integer",
                    "description": "Optional maximum number of lines to return.",
                    "required": False,
                },
            ],
        },
        {
            "name": "code-glob",
            "description": "Find files in the coding workspace using a glob pattern.",
            "parameters": [
                {
                    "name": "pattern",
                    "type": "string",
                    "description": "Glob pattern to match files, such as '**/*.py'.",
                    "required": True,
                },
                {
                    "name": "path",
                    "type": "string",
                    "description": "Optional base directory to search from.",
                    "required": False,
                },
            ],
        },
        {
            "name": "code-grep",
            "description": "Search file contents in the coding workspace with a text pattern.",
            "parameters": [
                {
                    "name": "pattern",
                    "type": "string",
                    "description": "Text or regex pattern to search for.",
                    "required": True,
                },
                {
                    "name": "path",
                    "type": "string",
                    "description": "Optional directory path to scope the search.",
                    "required": False,
                },
                {
                    "name": "glob",
                    "type": "string",
                    "description": "Optional glob filter for file selection, such as '*.ts'.",
                    "required": False,
                },
            ],
        },
        {
            "name": "code-bash",
            "description": "Run a shell command in the coding workspace.",
            "parameters": [
                {
                    "name": "command",
                    "type": "string",
                    "description": "Shell command to execute.",
                    "required": True,
                },
            ],
        },
        {
            "name": "code-edit",
            "description": "Edit a file by replacing text content in the coding workspace.",
            "parameters": [
                {
                    "name": "file_path",
                    "type": "string",
                    "description": "Path to the file to edit.",
                    "required": True,
                },
                {
                    "name": "old_string",
                    "type": "string",
                    "description": "The text to find in the file.",
                    "required": True,
                },
                {
                    "name": "new_string",
                    "type": "string",
                    "description": "Replacement text.",
                    "required": True,
                },
                {
                    "name": "replace_all",
                    "type": "boolean",
                    "description": "Whether to replace all matches instead of just one.",
                    "required": False,
                },
            ],
        },
        {
            "name": "code-write",
            "description": "Write full file content to a path in the coding workspace.",
            "parameters": [
                {
                    "name": "file_path",
                    "type": "string",
                    "description": "Path to the file to write.",
                    "required": True,
                },
                {
                    "name": "content",
                    "type": "string",
                    "description": "Complete file content to write.",
                    "required": True,
                },
            ],
        },
    ]
