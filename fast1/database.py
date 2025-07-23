from sqlalchemy.ext.asyncio import AsyncSession

engine = None


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
