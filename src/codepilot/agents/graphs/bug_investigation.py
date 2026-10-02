"""Minimal ReAct-style graph: the model calls Git tools until it has an answer."""

from contextlib import AsyncExitStack

from langchain_core.messages import SystemMessage
from langgraph.graph import END , StateGraph
from langgraph.prebuilt import ToolNode


from codepilot.agents.state import AgentState
from codepilot.llm.factory import get_chat_model
from codepilot.mcp.clients.git_client import get_git_tools


SYSTEM_PROMPT = (
    "You are CodePilot, a software investigation assistant. You have tools to "
    "explore a git repository: list files, read file contents, and view commit "
    "history. Use them to answer the user's question. Only state facts you "
    "actually observed through a tool call - never guess at file contents."
)


async def build_graph(repo_path: str, stack: AsyncExitStack) -> dict:
    tools = await get_git_tools(repo_path, stack)
    model = get_chat_model("fast").bind_tools(tools)


    async def agent_node(state: AgentState) -> dict:
        print(f"DEBUG agent_node: called with {len(state['messages'])} messages")
        messages = [SystemMessage(SYSTEM_PROMPT), *state["messages"]]
        response = await model.ainvoke(messages)
        print(f"DEBUG agent_node: got response type={type(response).__name__}, tool_calls={getattr(response, 'tool_calls', 'N/A')}")
        return {"messages": [response]}


    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        print(f"DEBUG should_continue: {len(state['messages'])} messages, last is {type(last_message).__name__}")
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END


    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()

  