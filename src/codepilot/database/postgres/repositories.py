"""Data-access functions for Postgres models."""
import uuid

from codepilot.domain.enums.investigation_status import InvestigationStatus

from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession

from codepilot.database.postgres.models import Investigation


async def create_investigation(session: AsyncSession, title: str, repo_path: str) -> Investigation:
    investigation = Investigation(title=title, repo_path=repo_path)
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)
    return investigation



async def list_investigations(session: AsyncSession) -> list[Investigation]:
    result = await session.execute(
        select(Investigation).order_by(Investigation.created_at.desc())
    )
    return result.scalars().all()


async def get_investigation(session: AsyncSession, investigation_id: uuid.UUID) -> Investigation | None:
    return await session.get(Investigation, investigation_id)


async def complete_investigation(
    session: AsyncSession,
    investigation_id: uuid.UUID,
    status: InvestigationStatus,
    result: str,
    result_report: dict | None = None,
) -> None:
    investigation = await session.get(Investigation, investigation_id)
    if investigation is None:
        return
    investigation.status = status
    investigation.result = result
    investigation.result_report = result_report
    await session.commit()
