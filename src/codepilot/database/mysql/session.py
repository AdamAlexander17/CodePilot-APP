"""Async SQLAlchemy engine and session for the MySQL target-application database."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from codepilot.config.settings import get_settings

_engine: AsyncEngine = create_async_engine(
    get_settings().mysql_dsn,
    echo=get_settings().debug,
    pool_pre_ping=True 
)

_session_factory = async_sessionmaker(
    bind = _engine,
    expire_on_commit=False,
)

async  def get_mysql_session()-> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session