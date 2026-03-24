import asyncio
import os
import warnings
from unittest.mock import AsyncMock

import numpy as np
import pandas as pd
import pytest
import redis
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from swingtraderai.db.base import Base
from swingtraderai.db.models.market import Exchange, Ticker
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_session
from swingtraderai.main import app

load_dotenv()

warnings.filterwarnings(
	"ignore", message=".*rite' option is deprecated.*", category=FutureWarning
)

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
async def client(session):
	async def override_get_session():
		yield session

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
	"""Создает тестовую биржу и тикер, связывая их через ID"""
	nasdaq = Exchange(name="NASDAQ", code="NSDQ", timezone="UTC", currency="USD")
	session.add(nasdaq)
	await session.flush()

	test_ticker = Ticker(
		symbol="AAPL",
		asset_type="stock",
		exchange_id=nasdaq.id,
		base_currency="USD",
		quote_currency="USD",
		is_active=True,
	)

	session.add(test_ticker)
	await session.flush()
	await session.refresh(test_ticker)

	yield test_ticker

	await session.delete(test_ticker)
	await session.delete(nasdaq)
	await session.commit()


@pytest.fixture
def registrations() -> pd.Series:
	"""Серия с датами регистрации пользователей"""
	n_users = 1000
	dates = pd.date_range("2025-01-01", periods=90, freq="D")
	reg_dates = np.random.choice(dates, size=n_users, replace=True)
	return pd.Series(
		reg_dates,
		index=range(n_users),
		name="registration_date",
		dtype="datetime64[ns]",
	)


@pytest.fixture
def activity_df() -> pd.DataFrame:
	"""Активность пользователей"""
	dates = pd.date_range("2025-02-01", "2025-03-20", freq="D")

	data = {
		"user_id": [i % 800 for i in range(5000)],
		"activity_date": [dates[i % len(dates)] for i in range(5000)],
	}
	df = pd.DataFrame(data)
	df["activity_date"] = pd.to_datetime(df["activity_date"])
	return df


@pytest.fixture
def registration_dict(activity_df, registrations) -> dict:
	"""Словарь user_id -> дата регистрации (для cohort retention)"""
	return registrations.to_dict()


@pytest.fixture
def mock_redis(mocker):
	redis_mock = mocker.Mock(spec=redis.Redis)
	redis_mock.ping.return_value = True
	redis_mock.llen.return_value = 42
	redis_mock.get.return_value = None
	redis_mock.keys = AsyncMock(return_value=[])
	redis_mock.pipeline.return_value = mocker.Mock()
	return redis_mock


@pytest.fixture
def mock_async_redis(mocker):
	redis_mock = mocker.Mock(spec=redis.asyncio.Redis)
	redis_mock.llen = AsyncMock(return_value=7)
	return redis_mock


@pytest.fixture
def mock_celery(mocker):
	celery_app = mocker.Mock()
	inspector = mocker.Mock()
	inspector.ping.return_value = {"worker1": "pong"}
	celery_app.control.inspect.return_value = inspector
	return celery_app
