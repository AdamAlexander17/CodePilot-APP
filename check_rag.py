"""One-off script: verify semantic search retrieval works, then the full graph using it. Delete after use."""

import asyncio
from contextlib import AsyncExitStack

from langchain_core.messages import HumanMessage

from codepilot.agents.graphs.bug_investigation import build_graph
from codepilot.rag.retriever import search_similar_chunks


def check_retrieval_alone() -> None:
    repo_path = r"C:\Dev\AI-Project\CodePilot-Enterprise\workspaces\leaderboard-board\LeaderBoard-BFX"
    results = search_similar_chunks(repo_path, "how does the background sync job work")
    for r in results:
        print(f"[{r['source']}] {r['text'][:150]}")


async def check_via_graph() -> None:
    repo_path = r"C:\Dev\AI-Project\CodePilot-Enterprise\workspaces\leaderboard-board\LeaderBoard-BFX"
    async with AsyncExitStack() as stack:
        graph = await build_graph(repo_path, stack)
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage("Explain how the automatic data sync works in this project.")],
                "repo_path": repo_path,
            }
        )
        print("\n=== Final answer ===")
        print(result["messages"][-1].content)


print("=== Direct retrieval ===")
check_retrieval_alone()

asyncio.run(check_via_graph())
