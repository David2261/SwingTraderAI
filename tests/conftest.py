import asyncio
import os
import warnings
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Optional
from unittest.mock import AsyncMock

import numpy as np
import pandas as pd
import pytest
import redis
from dotenv import load_dotenv
from fastapi import Request
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request as StarletteRequest
from starlette.types import Scope

from swingtraderai.api.services.ticker_service import TickerService
from swingtraderai.db.base import Base
from swingtraderai.db.models.market import Exchange, MarketData, Ticker
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_session
from swingtraderai.main import app
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA
from swingtraderai.schemas.watchlist import WatchlistCreate

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
		await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
		await conn.execute(text("CREATE SCHEMA public;"))
		await conn.run_sync(Base.metadata.create_all)

	yield engine

	await engine.dispose()


# Фабрика сессий
@pytest.fixture
async def session(engine):
	async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

	async with engine.connect() as conn:
		async with async_session(bind=conn) as session:
			yield session


# Подмена зависимости FastAPI
@pytest.fixture
async def client(session):
	async def override_get_session():
		yield session

	app.dependency_overrides[get_session] = override_get_session

	async with AsyncClient(app=app, base_url="http://test") as ac:
		yield ac

	app.dependency_overrides.clear()


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


@pytest.fixture
async def ticker_service(session: AsyncSession) -> TickerService:
	return TickerService(session)


@pytest.fixture
async def sample_exchange(session: AsyncSession) -> Exchange:
	"""Создаёт тестовую биржу"""
	exchange = Exchange(
		name="NASDAQ",
		code="NSDQ",
		timezone="America/New_York",
		currency="USD",
	)
	session.add(exchange)
	await session.flush()
	await session.refresh(exchange)
	return exchange


@pytest.fixture
async def sample_ticker(session: AsyncSession, sample_exchange: Exchange) -> Ticker:
	"""Создаёт тестовый тикер AAPL"""
	ticker = Ticker(
		symbol="AAPL",
		asset_type="stock",
		exchange_id=sample_exchange.id,
		base_currency="USD",
		quote_currency="USD",
		is_active=True,
	)
	session.add(ticker)
	await session.flush()
	await session.refresh(ticker)
	return ticker


@pytest.fixture
async def sample_market_data(
	session: AsyncSession, sample_ticker: Ticker
) -> list[MarketData]:
	"""Создаёт исторические данные"""
	now = datetime.now(timezone.utc)
	data = []

	for i in range(50):
		md = MarketData(
			ticker_id=sample_ticker.id,
			timeframe="1d",
			timestamp=now - timedelta(days=i),
			open=Decimal("150") + Decimal(i),
			high=Decimal("155") + Decimal(i),
			low=Decimal("148") + Decimal(i),
			close=Decimal("152") + Decimal(i) * Decimal("0.5"),
			volume=Decimal(100_000 + i * 1_000),
			source="test",
		)
		data.append(md)

	session.add_all(data)
	await session.commit()
	return data


@pytest.fixture
async def watchlist(watchlist_service, user):
	watchlist_in = WatchlistCreate(name="Sample Watchlist", description="For testing")
	return await watchlist_service.create_watchlist(
		tenant_id=user.tenant_id, user_id=user.id, watchlist_in=watchlist_in
	)


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


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
	"""Реалистичный OHLCV DataFrame для тестирования индикаторов и уровней"""
	np.random.seed(42)

	dates = pd.date_range("2025-03-01 00:00", periods=100, freq="h")

	base = np.linspace(5000, 5100, 100) + np.random.normal(0, 8, 100)

	df = pd.DataFrame(
		{
			"time": dates,
			"open": base + np.random.normal(0, 5, 100),
			"high": base + np.random.normal(5, 6, 100),
			"low": base + np.random.normal(-5, 6, 100),
			"close": base + np.random.normal(0, 4, 100),
			"volume": np.random.randint(800, 12000, 100),
			"timeframe": "1h",
		}
	)

	df.loc[df.index[10], "high"] = 5080.0
	df.loc[df.index[15], "high"] = 5125.0
	df.loc[df.index[30], "low"] = 4960.0
	df.loc[df.index[50], "high"] = 5150.0
	df.loc[df.index[70], "low"] = 4925.0
	df.loc[df.index[85], "low"] = 4900.0

	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	df["time"] = pd.to_datetime(df["time"])

	return df


@pytest.fixture
def mock_request():
	"""Создает mock Request объект для тестов"""

	def _create_request(
		headers: Optional[Dict[str, str]] = None,
		method: str = "GET",
		path: str = "/",
		client_ip: str = "127.0.0.1",
	) -> Request:
		"""Создает Request с заданными параметрами"""
		scope: Scope = {
			"type": "http",
			"method": method,
			"headers": [
				[b"host", b"testserver"],
				(
					[b"x-forwarded-for", client_ip.encode()]
					if client_ip
					else [b"user-agent", b"pytest"]
				),
			],
			"path": path,
			"query_string": b"",
			"client": (client_ip, 8000),
			"server": ("testserver", 80),
			"scheme": "http",
			"asgi": {"version": "3.0", "spec_version": "2.1"},
			"http_version": "1.1",
		}

		# Добавляем дополнительные headers если есть
		if headers:
			for key, value in headers.items():
				scope["headers"].append([key.encode(), value.encode()])

		# Создаем ASGI receive/send заглушки
		async def receive():
			return {"type": "http.request", "body": b"", "more_body": False}

		async def send(message):
			pass

		# Создаем request
		request = StarletteRequest(scope, receive=receive, send=send)
		return request

	return _create_request


@pytest.fixture
def mock_request_with_user(mock_request, user):
	"""Создает request с уже авторизованным пользователем"""

	def _create_request_with_user(
		custom_user=None, headers: Optional[Dict[str, str]] = None
	) -> Request:
		request = mock_request(headers=headers)
		target_user = custom_user or user
		request.state.user = target_user
		return request

	return _create_request_with_user
