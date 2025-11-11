from __future__ import annotations

import asyncio

from app.db.session import AsyncSessionFactory
from app.seeds.reference import seed_reference_data


async def main() -> None:
    async with AsyncSessionFactory() as session:
        await seed_reference_data(session)


if __name__ == "__main__":
    asyncio.run(main())
