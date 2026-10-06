"""One-off script: verify the planning node produces a real plan before investigation. Delete after use."""

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
                "messages": [HumanMessage("Why might the leaderboard ranking be wrong for some users?")],
                "repo_path": repo_path,
            }
        )
        print("=== Plan ===")
        print(result["plan"])
        print("\n=== Final answer ===")
        print(result["messages"][-1].content)


asyncio.run(main())
