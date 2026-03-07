import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.models.market import MarketData, Ticker


@pytest.mark.asyncio
async def test_ticker_creation_and_defaults(session: AsyncSession):
	"""Проверка создания Ticker + значения по умолчанию"""
	ticker = Ticker(
		symbol="BTCUSDT",
		asset_type="CRYPTO",
		exchange="BINANCE",
		base_currency="BTC",
		quote_currency="USDT",
	)

	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	assert isinstance(ticker.id, uuid.UUID)
	assert ticker.symbol == "BTCUSDT"
	assert ticker.asset_type == "CRYPTO"
	assert ticker.exchange == "BINANCE"
	assert ticker.base_currency == "BTC"
	assert ticker.quote_currency == "USDT"
	assert ticker.is_active is True

	assert isinstance(ticker.created_at, datetime)
	assert ticker.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_ticker_minimal_creation(session: AsyncSession):
	"""Минимальный тикер — проверка обязательных полей и дефолтов"""
	ticker = Ticker(symbol="ETHBTC", asset_type="CRYPTO")

	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	assert ticker.exchange is None
	assert ticker.base_currency is None
	assert ticker.quote_currency is None
	assert ticker.is_active is True
	assert isinstance(ticker.id, uuid.UUID)


@pytest.mark.asyncio
async def test_ticker_symbol_unique_constraint(session: AsyncSession):
	"""Проверка уникальности symbol"""
	t1 = Ticker(symbol="XRPUSDT", asset_type="CRYPTO")
	t2 = Ticker(symbol="XRPUSDT", asset_type="CRYPTO")

	session.add(t1)
	await session.commit()

	session.add(t2)
	with pytest.raises(IntegrityError):
		await session.commit()


@pytest.mark.asyncio
async def test_market_data_creation_and_relationship(session: AsyncSession):
	"""Создание MarketData + связь с Ticker + проверка Decimal"""
	ticker = Ticker(symbol="ADAUSDT", asset_type="CRYPTO", exchange="BINANCE")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	now = datetime.now(timezone.utc)

	md = MarketData(
		ticker_id=ticker.id,
		timeframe="1h",
		timestamp=now,
		open=Decimal("1.2345"),
		high=Decimal("1.2567"),
		low=Decimal("1.2100"),
		close=Decimal("1.2456"),
		volume=Decimal("1234567.89"),
	)

	session.add(md)
	await session.commit()
	await session.refresh(md)

	assert isinstance(md.id, uuid.UUID)
	assert md.ticker_id == ticker.id
	assert md.timeframe == "1h"
	assert md.timestamp == now
	assert md.open == Decimal("1.2345")
	assert md.high == Decimal("1.2567")
	assert md.low == Decimal("1.2100")
	assert md.close == Decimal("1.2456")
	assert md.volume == Decimal("1234567.89")

	assert isinstance(md.created_at, datetime)
	assert md.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_market_data_default_timestamp(session: AsyncSession):
	"""Проверка автоматического заполнения timestamp, если не указан"""
	ticker = Ticker(symbol="SOLUSDT", asset_type="CRYPTO")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	md = MarketData(
		ticker_id=ticker.id,
		timeframe="15m",
		close=Decimal("142.75"),
		volume=Decimal("987654.32"),
	)

	session.add(md)
	await session.commit()
	await session.refresh(md)

	assert md.timestamp is not None
	assert isinstance(md.timestamp, datetime)
	assert md.timestamp.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_market_data_unique_constraint_violation(session: AsyncSession):
	"""Проверка уникального ограничения (ticker_id, timeframe, timestamp)"""
	ticker = Ticker(symbol="LINKUSDT", asset_type="CRYPTO")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	ts = datetime(2025, 6, 15, 14, 30, tzinfo=timezone.utc)

	md1 = MarketData(
		ticker_id=ticker.id, timeframe="30m", timestamp=ts, close=Decimal("18.45")
	)

	md2 = MarketData(
		ticker_id=ticker.id, timeframe="30m", timestamp=ts, close=Decimal("18.60")
	)

	session.add(md1)
	await session.commit()

	session.add(md2)
	with pytest.raises(IntegrityError):
		await session.commit()


@pytest.mark.asyncio
async def test_market_data_nullable_ohlcv_fields(session: AsyncSession):
	"""Проверка, что OHLCV могут быть NULL"""
	ticker = Ticker(symbol="TESTUSDT", asset_type="CRYPTO")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	md = MarketData(ticker_id=ticker.id, timeframe="1d")

	session.add(md)
	await session.commit()
	await session.refresh(md)

	assert md.open is None
	assert md.high is None
	assert md.low is None
	assert md.close is None
	assert md.volume is None
