import os
import sqlite3
from typing import Any, Dict, List, Optional

from . import register_api_tool
from ..error_codes import ErrorCode
from .base_tool import BaseApiTool, ToolBusinessError


class _Text2SqlBaseTool(BaseApiTool):
    def _get_databases(self) -> Dict[str, str]:
        databases = self.get_config("databases") or self.get_config("db_paths") or {}
        if not isinstance(databases, dict) or not databases:
            raise ToolBusinessError("databases config missing for text2sql tools", ErrorCode.EXECUTION_ERROR)
        return databases

    def _get_connection(self, db_id: str) -> sqlite3.Connection:
        databases = self._get_databases()
        db_path = databases.get(db_id)
        if not db_path:
            raise ToolBusinessError(f"Database not found: {db_id}", ErrorCode.EXECUTION_ERROR)
        if not os.path.exists(db_path):
            raise ToolBusinessError(f"Database file not found: {db_path}", ErrorCode.EXECUTION_ERROR)
        abs_path = os.path.abspath(db_path)
        uri = f"file:{abs_path}?mode=ro"
        return sqlite3.connect(uri, uri=True, check_same_thread=False)


class Text2SqlListDatabasesTool(_Text2SqlBaseTool):
    def __init__(self):
        super().__init__(tool_name="text2sql:list_databases", resource_type="text2sql")

    async def execute(self, **kwargs) -> Any:
        databases = self._get_databases()
        return {"databases": list(databases.keys())}


class Text2SqlGetSchemaTool(_Text2SqlBaseTool):
    def __init__(self):
        super().__init__(tool_name="text2sql:get_schema", resource_type="text2sql")

    async def execute(self, db_id: str, table_names: Optional[List[str]] = None, **kwargs) -> Any:
        conn = self._get_connection(db_id)
        cursor = conn.cursor()
        try:
            if not table_names:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
            else:
                tables = table_names

            schema: Dict[str, Any] = {}
            for table in tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
                if not cursor.fetchone():
                    continue
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                fks = cursor.fetchall()
                schema[table] = {
                    "columns": [
                        {"name": col[1], "type": col[2], "pk": bool(col[5])}
                        for col in columns
                    ],
                    "foreign_keys": [
                        {"to_table": fk[2], "from_col": fk[3], "to_col": fk[4]}
                        for fk in fks
                    ]
                }
            return {"db_id": db_id, "schema": schema}
        finally:
            cursor.close()
            conn.close()


class Text2SqlExecuteTool(_Text2SqlBaseTool):
    def __init__(self):
        super().__init__(tool_name="text2sql:execute", resource_type="text2sql")

    async def execute(self, db_id: str, query: str, **kwargs) -> Any:
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH") and not query_upper.startswith("PRAGMA"):
            raise ToolBusinessError("Only SELECT/PRAGMA queries are allowed", ErrorCode.INVALID_INPUT)
        conn = self._get_connection(db_id)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchmany(100)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": len(rows) == 100
            }
        finally:
            cursor.close()
            conn.close()


register_api_tool(
    name="text2sql:list_databases",
    config_key="text2sql",
    description="List available text2sql databases"
)(Text2SqlListDatabasesTool())

register_api_tool(
    name="text2sql:get_schema",
    config_key="text2sql",
    description="Get schema for a text2sql database"
)(Text2SqlGetSchemaTool())

register_api_tool(
    name="text2sql:execute",
    config_key="text2sql",
    description="Execute a SQL query for text2sql"
)(Text2SqlExecuteTool())
