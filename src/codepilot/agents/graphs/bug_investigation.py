"""Minimal ReAct-style graph: the model calls Git tools until it has an answer."""
import json

from codepilot.schemas.report import InvestigationReport

from langchain_core.tools import tool

from codepilot.rag.retriever import search_similar_chunks


from codepilot.mcp.clients.database_client import get_database_tools

from contextlib import AsyncExitStack

from langchain_core.messages import SystemMessage , HumanMessage
from langgraph.graph import END , StateGraph
from langgraph.prebuilt import ToolNode


from codepilot.agents.state import AgentState
from codepilot.llm.factory import get_chat_model
from codepilot.mcp.clients.git_client import get_git_tools


SYSTEM_PROMPT = (
    "You are CodePilot, a software investigation assistant. You have tools to "
    "explore a git repository (list files, read file contents, view commit "
    "history, search code by exact text, or search semantically by concept), "
    "and to inspect a target application's database (list tables, describe "
    "schemas, run read-only SELECT queries). Use them to answer the user's "
    "question. Only state facts you actually observed through a tool call - "
    "never guess at file contents or data."
)

PLANNING_PROMPT = (
    "You are planning a software investigation. Given the user's question, write "
    "a short numbered plan (2-4 steps) describing what you need to find out and "
    "which kind of tool would help: git/file tools, database tools, or semantic "
    "code search. Do not call any tools yet - only output the plan as plain text."
)

REPORT_PROMPT = (
    "Review the investigation transcript above. Produce a report as a single JSON "
    "object with exactly these keys:\n"
    '  "observed_facts": a list of strings - things you directly confirmed via a tool call result\n'
    '  "hypotheses": a list of strings - plausible but unconfirmed explanations\n'
    '  "root_cause": a string naming the confirmed root cause, or null if not confirmed\n'
    '  "confidence": one of "low", "medium", "high"\n'
    "Output ONLY the JSON object, nothing else - no markdown, no explanation."
)


def _parse_report(raw_text: str) -> InvestigationReport:
    try:
        cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return InvestigationReport.model_validate(data)
    except Exception:
        return InvestigationReport(
            observed_facts=[],
            hypotheses=[raw_text.strip()],
            root_cause=None,
            confidence="low",
        )


async def build_graph(repo_path: str, stack: AsyncExitStack):

    @tool
    def search_codebase_semantically(query: str) -> list[dict[str, str]]:
        """Search the repository for code or documentation related to a concept or question,
        even if the exact words don't appear. Use this for 'where is X handled' style questions,
        and search_code (exact text match) when you already know the literal string to find."""
        return search_similar_chunks(repo_path, query)



    async def synthesis_node(state: AgentState) -> dict:
        report_model = get_chat_model("fast")
        response = await report_model.ainvoke(
            [*state["messages"], SystemMessage(REPORT_PROMPT)]
        )
        report = _parse_report(response.content)
        return {"report": report.model_dump()}





    async def planning_node(state: AgentState) -> dict:
        plan_model = get_chat_model("fast")  # no tools bound - this step only writes a plan
        question = state["messages"][-1].content
        response = await plan_model.ainvoke(
            [SystemMessage(PLANNING_PROMPT), HumanMessage(question)]
        )
        return {"plan": response.content}



    git_tools = await get_git_tools(repo_path, stack)
    db_tools = await get_database_tools(stack)
    tools = git_tools + db_tools + [search_codebase_semantically]


    model = get_chat_model("fast").bind_tools(tools)

    async def agent_node(state: AgentState) -> dict:
        messages = [
            SystemMessage(f"{SYSTEM_PROMPT}\n\nYour plan for this investigation:\n{state['plan']}"),
            *state["messages"],
        ]
        response = await model.ainvoke(messages)
        return {"messages": [response]}


    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "synthesis"

    graph = StateGraph(AgentState)
    graph.add_node("planning", planning_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("planning")
    graph.add_edge("planning", "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    graph.add_edge("synthesis", END)

    return graph.compile()


