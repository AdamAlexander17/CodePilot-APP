"""Investigation endpoints."""

import uuid
from contextlib import AsyncExitStack

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from codepilot.agents.graphs.bug_investigation import build_graph
from codepilot.database.postgres.repositories import (
    complete_investigation,
    create_investigation,
    get_investigation,
    list_investigations,
)
from codepilot.database.postgres.session import get_session, new_session
from codepilot.domain.enums.investigation_status import InvestigationStatus
from codepilot.schemas.investigation import InvestigationCreate, InvestigationRead

router = APIRouter(prefix="/investigations", tags=["investigations"])


async def _run_investigation(investigation_id: uuid.UUID, title: str, repo_path: str) -> None:
    """Runs in the background, after the HTTP response has already been sent."""
    try:
        async with AsyncExitStack() as stack:
            graph = await build_graph(repo_path, stack)
            result = await graph.ainvoke(
                {"messages": [HumanMessage(title)], "repo_path": repo_path}
            )
        answer = result["messages"][-1].content
        status = InvestigationStatus.COMPLETED
    except Exception as exc:
        answer = f"Investigation failed: {exc}"
        status = InvestigationStatus.FAILED

    async with new_session() as session:
        await complete_investigation(session, investigation_id, status, answer)


@router.post("/", status_code=201)
async def create(
                        payload: InvestigationCreate,
                        background_tasks: BackgroundTasks,
                        session: AsyncSession = Depends(get_session),
                    ) -> InvestigationRead:
    investigation = await create_investigation(session, title=payload.title, repo_path=payload.repo_path)
    investigation.repo_path = payload.repo_path
    await session.commit()
    await session.refresh(investigation)

    background_tasks.add_task(_run_investigation, investigation.id, payload.title, payload.repo_path)

    return InvestigationRead.model_validate(investigation)


@router.get("/")
async def list_all(session: AsyncSession = Depends(get_session)) -> list[InvestigationRead]:
    investigations = await list_investigations(session)
    return [InvestigationRead.model_validate(i) for i in investigations]


@router.get("/{investigation_id}")
async def get_one(
    investigation_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> InvestigationRead:
    investigation = await get_investigation(session, investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return InvestigationRead.model_validate(investigation)
