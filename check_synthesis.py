"""One-off script: verify the structured report node. Delete after use."""

import asyncio
import json
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
        print("=== Structured report ===")
        print(json.dumps(result["report"], indent=2))


asyncio.run(main())