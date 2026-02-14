import logging
import os
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.server.core import tool
from sandbox.server.backends.error_codes import ErrorCode
from sandbox.server.backends.response_builder import build_success_response, build_error_response

logger = logging.getLogger("DatabaseBackend")


class DatabaseBackend(Backend):
    """
    SQL backend for text2sql tasks.

    Expected config:
    {
      "databases": {
        "chinook": "/abs/path/chinook.sqlite",
        "sakila": "/abs/path/sakila.sqlite"
      }
    }
    """

    name = "sql"

    def __init__(self, config: Optional[BackendConfig] = None):
        if config is None:
            config = BackendConfig()
        super().__init__(config)
        self._shared_connections: Dict[str, sqlite3.Connection] = {}
        self._shared_db_paths: Dict[str, str] = {}

    async def warmup(self):
        cfg = self.config.default_config or {}
        databases = cfg.get("databases", {})
        connections, db_paths, _ = self._open_connections(databases)
        self._shared_connections = connections
        self._shared_db_paths = db_paths

    async def shutdown(self):
        for db_id, conn in self._shared_connections.items():
            try:
                conn.close()
            except Exception as exc:
                logger.error(f"Error closing database {db_id}: {exc}")
        self._shared_connections.clear()
        self._shared_db_paths.clear()

    async def initialize(self, worker_id: str, config: dict) -> dict:
        cfg = config or self.config.default_config or {}
        databases = cfg.get("databases", {})
        connections, db_paths, errors = self._open_connections(databases)
        return {"connections": connections, "db_paths": db_paths, "errors": errors}

    async def cleanup(self, worker_id: str, session_info: dict):
        data = session_info.get("data", {})
        connections = data.get("connections", {})
        for db_id, conn in connections.items():
            try:
                conn.close()
            except Exception as exc:
                logger.error(f"Error closing database {db_id}: {exc}")

    def _open_connections(
        self, databases: Dict[str, str]
    ) -> Tuple[Dict[str, sqlite3.Connection], Dict[str, str], List[str]]:
        connections: Dict[str, sqlite3.Connection] = {}
        db_paths: Dict[str, str] = {}
        errors: List[str] = []
        for db_id, db_path in databases.items():
            if not db_path or not os.path.exists(db_path):
                errors.append(f"Database file not found: {db_path} (id={db_id})")
                continue
            try:
                abs_path = os.path.abspath(db_path)
                uri = f"file:{abs_path}?mode=ro"
                conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
                connections[db_id] = conn
                db_paths[db_id] = abs_path
            except Exception as exc:
                errors.append(f"Failed to load database {db_id}: {exc}")
        return connections, db_paths, errors

    def _get_connections(self, session_info: Optional[Dict[str, Any]] = None) -> Dict[str, sqlite3.Connection]:
        if session_info:
            data = session_info.get("data", {})
            connections = data.get("connections")
            if connections:
                return connections
        return self._shared_connections

    @tool("sql:list_databases")
    async def list_databases(self, session_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        connections = self._get_connections(session_info)
        data = {"databases": list(connections.keys())}
        return build_success_response(data=data, tool="sql:list_databases")

    @tool("sql:get_schema")
    async def get_schema(
        self,
        db_id: str,
        table_names: Optional[List[str]] = None,
        session_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        connections = self._get_connections(session_info)
        if db_id not in connections:
            return build_error_response(ErrorCode.INVALID_INPUT, f"Database not found: {db_id}", tool="sql:get_schema")

        conn = connections[db_id]
        cursor = conn.cursor()
        try:
            if not table_names:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
            else:
                tables = table_names

            schema = {}
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
                    ],
                }

            data = {"db_id": db_id, "schema": schema}
            return build_success_response(data=data, tool="sql:get_schema")
        except Exception as exc:
            logger.error(f"Error getting schema for {db_id}: {exc}")
            return build_error_response(ErrorCode.EXECUTION_ERROR, str(exc), tool="sql:get_schema")
        finally:
            cursor.close()

    @tool("sql:execute")
    async def execute_query(
        self, db_id: str, query: str, session_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        connections = self._get_connections(session_info)
        if db_id not in connections:
            return build_error_response(ErrorCode.INVALID_INPUT, f"Database not found: {db_id}", tool="sql:execute")

        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH") and not query_upper.startswith(
            "PRAGMA"
        ):
            return build_error_response(
                ErrorCode.INVALID_INPUT, "Only SELECT/PRAGMA queries are allowed", tool="sql:execute"
            )

        conn = connections[db_id]
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchmany(100)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            data = {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": len(rows) == 100,
            }
            return build_success_response(data=data, tool="sql:execute")
        except sqlite3.Error as exc:
            return build_error_response(ErrorCode.EXECUTION_ERROR, f"SQL Error: {str(exc)}", tool="sql:execute")
        except Exception as exc:
            return build_error_response(ErrorCode.EXECUTION_ERROR, f"System Error: {str(exc)}", tool="sql:execute")
        finally:
            cursor.close()


def create_database_backend(config: Optional[BackendConfig] = None) -> DatabaseBackend:
    return DatabaseBackend(config)

