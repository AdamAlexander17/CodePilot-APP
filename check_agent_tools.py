"""One-off script: verify the LLM can call a real Git MCP tool. Delete after use."""

import asyncio
from contextlib import AsyncExitStack

from codepilot.llm.factory import get_chat_model
from codepilot.mcp.clients.git_client import get_git_tools


async def main() -> None:
    repo_path = r"C:\Dev\AI-Project\CodePilot-Enterprise\workspaces\leaderboard-board\LeaderBoard-BFX"

    async with AsyncExitStack() as stack:
        tools = await get_git_tools(repo_path, stack)
        print("Tools available to the model:", [t.name for t in tools])

        model = get_chat_model("fast").bind_tools(tools)
        response = model.invoke("List the files in this repository.")

        print("Model's tool calls:", response.tool_calls)
        print("Model's text response:", response.content)


asyncio.run(main())
