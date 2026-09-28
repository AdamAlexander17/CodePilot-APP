"""Health check endpoint."""
from codepilot.database.postgres.session import get_session
from codepilot.database.mysql.session import get_mysql_session

from fastapi import APIRouter , Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from codepilot.config.settings import get_settings


from codepilot.config.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "environment": settings.environment}


@router.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    result = await session.execute(text("SELECT 1"))
    return {"status": "ok", "db": "reachable" if result.scalar() == 1 else "unreachable"}


@router.get("/health/db-mysql")
async def health_db_mysql(session: AsyncSession = Depends(get_mysql_session)) -> dict[str, str]:
    result = await session.execute(text("SELECT 1"))
    result.scalar_one()
    return {"status": "ok", "database": "mysql"}
