"""Connects to the Database MCP server and exposes its tools for LangChain/LangGraph."""

from contextlib import AsyncExitStack

from langchain_core.tools import BaseTool

from codepilot.config.settings import get_settings
from codepilot.mcp.clients.base import get_mcp_tools


async def get_database_tools(stack: AsyncExitStack) -> list[BaseTool]:
    settings = get_settings()
    dsn = settings.mysql_dsn.replace("+asyncmy", "+pymysql")
    return await get_mcp_tools(
        command="uv",
        args=["run", "python", "mcp_servers/database_server/server.py"],
        env={"DATABASE_MCP_DSN": dsn},
        stack=stack,
    )
