"""Database Seeding CLI entrypoint module for AGENTPAY (Phase 078)."""

import asyncio
import logging

from app.core.config import get_settings
from app.infrastructure.database.engine import dispose_async_engine, get_async_engine
from app.infrastructure.database.seeder import DatabaseSeeder
from app.infrastructure.database.session import get_async_sessionmaker

logger = logging.getLogger("agentpay.infrastructure.database.seed")


async def run_seed() -> None:
    """Execute deterministic database seeding."""
    settings = get_settings()
    engine = get_async_engine(settings=settings)
    session_factory = get_async_sessionmaker(engine=engine)

    async with session_factory() as session:
        seeder = DatabaseSeeder(session=session)
        counts = await seeder.seed_all(env_name=settings.app_env.value)
        print("\n=======================================================")
        print("AGENTPAY DATABASE SEEDING EXECUTED SUCCESSFULLY")
        print("=======================================================")
        for entity, count in counts.items():
            print(f"  • {entity}: {count} records added")
        print("=======================================================\n")

    await dispose_async_engine()


def main() -> None:
    """CLI entry point for python -m app.infrastructure.database.seed"""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
