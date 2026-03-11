from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)
from sqlalchemy.pool import NullPool

from swingtraderai.core.config import settings

if settings.DATABASE_URL is None:
	raise ValueError("DATABASE_URL is not set in environment variables")


def create_engine() -> AsyncEngine:
	return create_async_engine(
		settings.DATABASE_URL,
		echo=False,
		future=True,
		poolclass=NullPool,
	)


engine: AsyncEngine = create_engine()


AsyncSessionLocal = async_sessionmaker(
	bind=engine,
	expire_on_commit=False,
	class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	"""
	FastAPI dependency для получения асинхронной сессии.
	Использование: db: AsyncSession = Depends(get_db)
	"""
	session = AsyncSessionLocal()
	try:
		yield session
	except Exception:
		await session.rollback()
		raise
	finally:
		await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	async with AsyncSessionLocal() as session:
		yield session


async def dispose_engine() -> None:
	await engine.dispose()
