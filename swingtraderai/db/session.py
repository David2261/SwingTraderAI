from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)

from swingtraderai.core.config import DATABASE_URL

if DATABASE_URL is None:
	raise ValueError("DATABASE_URL is not set in environment variables")

engine: AsyncEngine = create_async_engine(
	DATABASE_URL,
	echo=False,
	future=True,
)

AsyncSessionLocal = async_sessionmaker(
	bind=engine,
	expire_on_commit=False,
	class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	async with AsyncSessionLocal() as session:
		yield session
