"""
SQL Tool Schemas

This module defines tool schemas for text2sql-style database operations.
"""

from typing import List, Dict, Any


def get_sql_tool_schemas() -> List[Dict[str, Any]]:
    """Return all SQL tool schemas."""
    return [
        get_list_databases_schema(),
        get_get_schema_schema(),
        get_execute_query_schema(),
    ]


def get_list_databases_schema() -> Dict[str, Any]:
    return {
        "name": "sql:list_databases",
        "description": "List all available databases that can be queried.",
        "parameters": [],
    }


def get_get_schema_schema() -> Dict[str, Any]:
    return {
        "name": "sql:get_schema",
        "description": "Get table structures (tables, columns, foreign keys) of a database.",
        "parameters": [
            {
                "name": "db_id",
                "type": "string",
                "description": "Database ID returned by sql:list_databases.",
                "required": True,
            },
            {
                "name": "table_names",
                "type": "array",
                "array_type": "string",
                "description": "Optional table-name filter; omit to return all tables.",
                "required": False,
            },
        ],
    }


def get_execute_query_schema() -> Dict[str, Any]:
    return {
        "name": "sql:execute",
        "description": "Execute a SQL query on a specific database. Only SELECT/WITH/PRAGMA are allowed.",
        "parameters": [
            {
                "name": "db_id",
                "type": "string",
                "description": "Database ID to query.",
                "required": True,
            },
            {
                "name": "query",
                "type": "string",
                "description": "SQL query string.",
                "required": True,
            },
        ],
    }

