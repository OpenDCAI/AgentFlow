
"""
SQL Tool Schemas

This module defines the tool schemas for database operations.
These schemas are used to construct prompts for the LLM agent.
"""

from typing import List, Dict, Any


_REGISTERED_SQL_TOOLS: List[Dict[str, Any]] = []


def register_sql_tool(schema: Dict[str, Any]) -> Dict[str, Any]:
    _REGISTERED_SQL_TOOLS.append(schema)
    return schema


def get_sql_tool_schemas() -> List[Dict[str, Any]]:
    return list(_REGISTERED_SQL_TOOLS)


def get_list_databases_schema() -> Dict[str, Any]:
    return register_sql_tool({
        "name": "text2sql-list_databases",
        "description": "List all available databases that can be queried.",
        "parameters": []
    })


def get_get_schema_schema() -> Dict[str, Any]:
    return register_sql_tool({
        "name": "text2sql-get_schema",
        "description": "Get the table structure (tables, columns, foreign keys) of a specific database.",
        "parameters": [
            {
                "name": "db_id",
                "type": "string",
                "description": "The ID of the database to inspect (returned by text2sql-list_databases)",
                "required": True
            },
            {
                "name": "table_names",
                "type": "array",
                "array_type": "string",
                "description": "Optional list of table names to filter. If omitted, returns all tables.",
                "required": False
            }
        ]
    })


def get_execute_query_schema() -> Dict[str, Any]:
    return register_sql_tool({
        "name": "text2sql-execute",
        "description": "Execute a SQL query on a specific database. Only SELECT statements are allowed.",
        "parameters": [
            {
                "name": "db_id",
                "type": "string",
                "description": "The ID of the database to query",
                "required": True
            },
            {
                "name": "query",
                "type": "string",
                "description": "The SQL query string (e.g., 'SELECT * FROM users LIMIT 5')",
                "required": True
            }
        ]
    })


get_list_databases_schema()
get_get_schema_schema()
get_execute_query_schema()
