"""Connects to the Git MCP server and exposes its tools as LangChain tools.

We don't use langchain-mcp-adapters here: as of this writing it still requires
mcp<2.0.0, and this project is on mcp 2.x. This is a small, direct bridge instead.
"""

from contextlib import AsyncExitStack
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import create_model

_JSON_TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}


def _schema_to_pydantic_model(tool_name: str, schema: dict[str, Any]) -> type:
    """Build a Pydantic model from an MCP tool's JSON input schema."""
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    fields = {}
    for field_name, field_schema in properties.items():
        py_type = _JSON_TYPE_MAP.get(field_schema.get("type"), str)
        default = ... if field_name in required else field_schema.get("default", None)
        fields[field_name] = (py_type, default)

    return create_model(f"{tool_name}Args", **fields)


async def get_git_tools(repo_path: str, stack: AsyncExitStack) -> list[BaseTool]:
    """Start the Git MCP server and return its tools as LangChain tools.

    `stack` must stay open for as long as the tools will be used - it owns the
    subprocess and the session. The caller is responsible for the AsyncExitStack.
    """
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "mcp_servers/git_server/server.py"],
        env={"GIT_MCP_REPO_PATH": repo_path},
    )

    read, write = await stack.enter_async_context(stdio_client(server_params))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()

    mcp_tools = await session.list_tools()

    def make_tool(mcp_tool) -> BaseTool:
        args_model = _schema_to_pydantic_model(mcp_tool.name, mcp_tool.input_schema)


        async def call(**kwargs: Any) -> str:
            result = await session.call_tool(mcp_tool.name, arguments=kwargs)
            return "\n".join(item.text for item in result.content)

        return StructuredTool.from_function(
            coroutine=call,
            name=mcp_tool.name,
            description=mcp_tool.description or "",
            args_schema=args_model,
        )

    return [make_tool(t) for t in mcp_tools.tools]
