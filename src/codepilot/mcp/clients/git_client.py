"""Connects to the Git MCP server and exposes its tools for LangChain/LangGraph."""

from contextlib import AsyncExitStack

from langchain_core.tools import BaseTool

from codepilot.mcp.clients.base import get_mcp_tools


async def get_git_tools(repo_path: str, stack: AsyncExitStack) -> list[BaseTool]:
    return await get_mcp_tools(
        command="uv",
        args=["run", "python", "mcp_servers/git_server/server.py"],
        env={"GIT_MCP_REPO_PATH": repo_path},
        stack=stack,
    )
