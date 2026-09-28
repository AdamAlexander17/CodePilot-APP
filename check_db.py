"""One-off script to verify both databases are reachable. Delete after use."""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from codepilot.config.settings import get_settings


async def main() -> None:
    settings = get_settings()

    pg_engine = create_async_engine(settings.postgres_dsn)
    async with pg_engine.connect() as conn:
        result = await conn.exec_driver_sql("SELECT version()")
        print("Postgres OK:", result.scalar())
    await pg_engine.dispose()

    mysql_engine = create_async_engine(settings.mysql_dsn)
    async with mysql_engine.connect() as conn:
        result = await conn.exec_driver_sql("SELECT VERSION()")
        print("MySQL OK:", result.scalar())
    await mysql_engine.dispose()


asyncio.run(main())
