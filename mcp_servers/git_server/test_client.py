"""Manual test client for the Git MCP server. Not part of the real app - run by hand."""

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    repo_path = sys.argv[1]

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "mcp_servers/git_server/server.py"],
        env={**os.environ, "GIT_MCP_REPO_PATH": repo_path},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            result = await session.call_tool("list_files", arguments={})
            for item in result.content:
                print(item.text)

            result = await session.call_tool("read_file", arguments={"path": "pyproject.toml"})
            print("\n--- read_file(pyproject.toml) ---")
            for item in result.content:
                print(item.text)

            result = await session.call_tool("read_file", arguments={"path": ".env"})
            print("\n--- read_file(.env) ---")
            for item in result.content:
                print(item.text)



asyncio.run(main())
