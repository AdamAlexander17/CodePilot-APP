"""Data-access functions for Postgres models."""

from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession

from codepilot.database.postgres.models import Investigation


async def create_investigation(session: AsyncSession, title: str) -> Investigation:
    investigation = Investigation(title=title)
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)
    return investigation


async def list_investigations(session: AsyncSession) -> list[Investigation]:
    result = await session.execute(
        select(Investigation).order_by(Investigation.created_at.desc())
    )
    return result.scalars().all()

