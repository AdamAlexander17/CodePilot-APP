"""Investigation endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from codepilot.database.postgres.repositories import create_investigation, list_investigations
from codepilot.database.postgres.session import get_session
from codepilot.schemas.investigation import InvestigationCreate, InvestigationRead

router = APIRouter(prefix="/investigations", tags=["investigations"])

@router.post("/", status_code=201)
async def create(
    payload: InvestigationCreate,
    session: AsyncSession = Depends(get_session)
) -> InvestigationRead:
    investigation = await create_investigation(session=session, title=payload.title)
    return InvestigationRead.model_validate(investigation)


@router.get("/")
async def list_all(
    session: AsyncSession = Depends(get_session),
) -> list[InvestigationRead]:
    investigations = await list_investigations(session)
    return [InvestigationRead.model_validate(i) for i in investigations]