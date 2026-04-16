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
            "description": "Read a text file from the current code workspace and return contents with line numbers.",
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
                    "description": "Optional start line number for partial reads (1-indexed).",
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
            "description": "Search file contents in the coding workspace with a regex pattern.",
            "parameters": [
                {
                    "name": "pattern",
                    "type": "string",
                    "description": "Regex pattern to search for.",
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
            "description": "Run a shell command in the current coding workspace.",
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
            "description": "Edit a file in the coding workspace by exact string replacement, expecting a unique match unless replace_all=true.",
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
                    "description": "Exact text to find in the file.",
                    "required": True,
                },
                {
                    "name": "new_string",
                    "type": "string",
                    "description": "Text used to replace the matched string.",
                    "required": True,
                },
                {
                    "name": "replace_all",
                    "type": "boolean",
                    "description": "When true, replace all exact matches; otherwise exactly one unique match is expected.",
                    "required": False,
                },
            ],
        },
        {
            "name": "code-write",
            "description": "Write full file content to a file in the coding workspace and create parent directories if needed.",
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
