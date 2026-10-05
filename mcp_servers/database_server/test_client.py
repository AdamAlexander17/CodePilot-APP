"""Manual test client for the Database MCP server. Not part of the real app - run by hand."""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    dsn = os.environ["DATABASE_MCP_DSN"]

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "mcp_servers/database_server/server.py"],
        env={**os.environ, "DATABASE_MCP_DSN": dsn},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            result = await session.call_tool("list_tables", arguments={})
            print("\n--- list_tables ---")
            for item in result.content:
                print(item.text)

            result = await session.call_tool("descibe_table", arguments={"table_name": "your_table_name"})
            print("\n--- descibe_table ---")
            for item in result.content:
                print(item.text)

            result = await session.call_tool("describe_table", arguments={"table_name": "orders"})
            print("\n--- describe_table(orders) ---")
            for item in result.content:
                print(item.text)
            result = await session.call_tool("run_query", arguments={"sql": "SELECT * FROM orders WHERE status = 'completed'"})
            print("\n--- run_query(SELECT completed orders) ---")
            for item in result.content:
                print(item.text)


            result = await session.call_tool("run_query", arguments={"sql": "DELETE FROM orders"})
            print("\n--- run_query(DELETE attempt - should be blocked) ---")
            for item in result.content:
                print(item.text)




asyncio.run(main())
