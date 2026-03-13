import asyncio
import os

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from swingtraderai.db.base import Base
from swingtraderai.db.models.market import Ticker
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_session
from swingtraderai.main import app

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


# Отдельный event loop для async тестов
@pytest.fixture(scope="session")
def event_loop():
	loop = asyncio.new_event_loop()
	yield loop
	loop.close()


# Движок тестовой БД
@pytest.fixture
async def engine():
	engine = create_async_engine(TEST_DATABASE_URL, future=True)

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	yield engine

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)

	await engine.dispose()


# Фабрика сессий
@pytest.fixture
async def session(engine):
	async_session = sessionmaker(
		engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
	)

	async with async_session() as session:
		yield session
		await session.rollback()


# Подмена зависимости FastAPI
@pytest.fixture
async def client(db_session):
	async def override_get_session():
		yield db_session

	app.dependency_overrides[get_session] = override_get_session

	async with AsyncClient(app=app, base_url="http://test") as ac:
		yield ac

	app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def check_db_connection():
	if not TEST_DATABASE_URL:
		pytest.skip("TEST_DATABASE_URL not set")
	engine = create_async_engine(TEST_DATABASE_URL)
	try:
		async with engine.connect() as conn:
			await conn.execute("SELECT 1")
	finally:
		await engine.dispose()


@pytest.fixture
async def user(session: AsyncSession):
	"""Создает тестового пользователя и возвращает его"""
	user = User(
		username="testuser",
		email="test@example.com",
		password_hash="fakehash123",
	)

	session.add(user)
	await session.commit()
	await session.refresh(user)

	yield user

	await session.delete(user)
	await session.commit()


@pytest.fixture
async def ticker(session: AsyncSession):
	"""Создает тестовый тикер и возвращает его"""
	ticker = Ticker(
		symbol="AAPL",
		asset_type="stock",
		exchange="NASDAQ",
		base_currency="USD",
		quote_currency="USD",
		is_active=True,
	)

	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	yield ticker
	await session.delete(ticker)
	await session.commit()
