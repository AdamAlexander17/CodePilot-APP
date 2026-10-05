"""Database server: read-only schema and query tools over a target application's MySQL database."""
import sqlparse
from sqlalchemy import text

import os

from mcp.server.mcpserver import MCPServer
from sqlalchemy import create_engine, inspect

DB_DSN = os.environ["DATABASE_MCP_DSN"]

mcp = MCPServer("database-server")

_engine = create_engine(DB_DSN)


@mcp.tool()
def list_tables() -> list[str]:
    """List every table in the target database."""
    inspector = inspect(_engine)
    return sorted(inspector.get_table_names())


@mcp.tool()
def describe_table(table_name: str) -> list[dict[str, str]]:
    """Describe a table's columns: name, type, and whether it's nullable."""
    inspector = inspect(_engine)
    if table_name not in inspector.get_table_names():
        return [{"error": f"Table '{table_name}' does not exist."}]

    columns = []
    for col in inspector.get_columns(table_name):
        columns.append({
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": str(col["nullable"]),
        })
    return columns



MAX_ROWS = 200


@mcp.tool()
def run_query(sql: str) -> list[dict] | dict:
    """Run a read-only SELECT query. Blocks anything that isn't a single SELECT statement."""
    statements = sqlparse.parse(sql)

    if len(statements) != 1:
        return {"error": "Only a single SQL statement is allowed."}

    stmt = statements[0]
    if stmt.get_type() != "SELECT":
        return {"error": f"Only SELECT statements are allowed, got: {stmt.get_type()}"}

    with _engine.connect() as conn:
        conn.execute(text("SET SESSION TRANSACTION READ ONLY"))
        result = conn.execute(text(sql))
        rows = result.mappings().fetchmany(MAX_ROWS)
        return [dict(row) for row in rows]

if __name__ == "__main__":
    mcp.run()
