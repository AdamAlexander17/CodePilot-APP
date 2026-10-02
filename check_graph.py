"""One-off script: run the bug-investigation graph end to end. Delete after use."""

import asyncio
from contextlib import AsyncExitStack

from langchain_core.messages import HumanMessage

from codepilot.agents.graphs.bug_investigation import build_graph


async def main() -> None:
    repo_path = r"C:\Dev\AI-Project\CodePilot-Enterprise\workspaces\leaderboard-board\LeaderBoard-BFX"

    async with AsyncExitStack() as stack:
        graph = await build_graph(repo_path, stack)

        result = await graph.ainvoke(
            {
                "messages": [HumanMessage("What does the leaderboard_project/main.py file do? Read it first.")],
                "repo_path": repo_path,
            }
        )

        print("\n=== Final answer ===")
        print(result["messages"][-1].content)

        print("\n=== Full message trace ===")
        for msg in result["messages"]:
            print(f"[{msg.__class__.__name__}] {str(msg.content)[:200]}")


asyncio.run(main())
