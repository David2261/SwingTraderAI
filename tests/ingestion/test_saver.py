from datetime import timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pandas as pd
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from swingtraderai.db.models.market import Exchange, Ticker
from swingtraderai.ingestion.saver import ensure_ticker, upsert_market_data_batch


@pytest.fixture
def async_session(mocker):
	"""Мок асинхронной сессии SQLAlchemy"""
	session = mocker.AsyncMock(spec=AsyncSession)
	session.execute = mocker.AsyncMock()
	session.add = mocker.Mock()
	session.flush = mocker.AsyncMock()
	session.commit = mocker.AsyncMock()
	session.rollback = mocker.AsyncMock()
	return session


@pytest.fixture
def sample_df():
	"""Фикстура с тестовым DataFrame"""
	data = {
		"symbol": ["SBER", "SBER", "BTCUSDT"],
		"timeframe": ["1d", "1d", "1h"],
		"timestamp": [
			pd.Timestamp("2025-01-01 00:00:00"),
			pd.Timestamp("2025-01-02 00:00:00"),
			pd.Timestamp("2025-01-01 12:00:00"),
		],
		"open": [300.5, 301.2, 42000.0],
		"high": [305.0, 306.1, 42500.0],
		"low": [298.0, 299.5, 41500.0],
		"close": [302.0, 303.8, 42200.0],
		"volume": [1500000.0, 1800000.0, 1200.0],
	}
	return pd.DataFrame(data)


@pytest.mark.asyncio
async def test_ensure_ticker_finds_existing(async_session):
	"""Тикер уже существует → возвращает существующий id"""
	ticker_id = uuid7()
	mock_result = MagicMock()
	mock_result.scalar_one_or_none.return_value = ticker_id

	async_session.execute.return_value = mock_result

	result = await ensure_ticker(
		session=async_session,
		symbol="SBER",
		asset_type="stock",
	)

	assert result == ticker_id
	async_session.execute.assert_called_once()
	async_session.add.assert_not_called()
	async_session.flush.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_ticker_creates_new(async_session):
	mock_result = MagicMock()
	mock_result.scalar_one_or_none.return_value = None
	async_session.execute.return_value = mock_result

	new_id = uuid7()
	async_session.add = MagicMock()

	def mock_add_side_effect(obj):
		obj.id = new_id

	async_session.add.side_effect = mock_add_side_effect

	result = await ensure_ticker(
		session=async_session,
		symbol="NEWTOKEN",
		asset_type="crypto",
	)

	assert result == new_id
	async_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_upsert_market_data_batch_empty_df(async_session):
	"""Пустой DataFrame → ничего не делает, возвращает 0,0"""
	df = pd.DataFrame()

	with pytest.raises(ValueError) as exc_info:
		inserted, updated = await upsert_market_data_batch(
			session=async_session, df=df, source="bybit"
		)

	assert "Отсутствуют колонки" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upsert_market_data_batch_converts_decimal(async_session, mocker):
	"""Проверка преобразования float → Decimal"""
	moex = Exchange(name="Moex", code="MOEX")
	async_session.add(moex)
	await async_session.commit()
	ticker = Ticker(
		symbol="SBER",
		asset_type="QUOTE",
		exchange_id=moex.id,
		base_currency="RUB",
		quote_currency="USDT",
	)
	async_session.add(ticker)
	await async_session.commit()
	await async_session.refresh(ticker)

	df = pd.DataFrame(
		{
			"symbol": ["SBER"],
			"timeframe": ["1d"],
			"timestamp": [pd.Timestamp("2025-01-01")],
			"open": [300.123456789],
			"high": [305.9],
			"low": [298.1],
			"close": [302.5],
			"volume": [1234567.89],
		}
	)
	df["ticker_id"] = ticker.id

	mocker.patch("swingtraderai.ingestion.saver.ensure_ticker", return_value=uuid7())
	async_session.execute.return_value = MagicMock(rowcount=1)

	await upsert_market_data_batch(session=async_session, df=df)

	args, _ = async_session.execute.call_args
	inserted_records = args[1]

	first_record = inserted_records[0]

	assert isinstance(first_record["open"], Decimal)
	assert first_record["open"] == Decimal("300.123456789")
	assert isinstance(first_record["volume"], Decimal)


@pytest.mark.asyncio
async def test_upsert_market_data_batch_timestamp_tz(async_session, mocker):
	"""timestamp с tz и без → должен быть UTC"""
	df = pd.DataFrame(
		{
			"symbol": ["SBER", "SBER"],
			"timeframe": ["1d", "1d"],
			"time": [
				pd.Timestamp("2025-01-01 12:00:00", tz="UTC"),
				pd.Timestamp("2025-01-02 12:00:00"),
			],
			"open": [100.0, 101.0],
			"high": [105.0, 106.0],
			"low": [95.0, 96.0],
			"close": [102.0, 103.0],
			"volume": [1000.0, 1100.0],
		}
	)
	moex = Exchange(name="Moex", code="MOEX")
	async_session.add(moex)
	await async_session.commit()
	ticker = Ticker(
		symbol="SBER",
		asset_type="QUOTE",
		exchange_id=moex.id,
		base_currency="RUB",
		quote_currency="RUB",
	)
	async_session.add(ticker)
	await async_session.commit()
	await async_session.refresh(ticker)
	df["ticker_id"] = ticker.id

	mocker.patch("swingtraderai.ingestion.saver.ensure_ticker", return_value=uuid7())
	async_session.execute.return_value = MagicMock(rowcount=2)

	await upsert_market_data_batch(session=async_session, df=df)

	args, _ = async_session.execute.call_args
	records = args[1]

	assert records[0]["time"].tzinfo == timezone.utc
	assert records[0]["time"] == pd.Timestamp("2025-01-01 12:00:00", tz="UTC")
	assert records[1]["time"] == pd.Timestamp("2025-01-02 12:00:00", tz="UTC")


@pytest.mark.asyncio
async def test_upsert_market_data_batch_groups_by_symbol(async_session, mocker):
	"""Группировка по symbol → отдельный ensure_ticker на каждый"""
	df = pd.DataFrame(
		{
			"symbol": ["SBER", "SBER", "GAZP", "BTCUSDT"],
			"timeframe": ["1d"] * 4,
			"time": pd.date_range("2025-01-01", periods=4, freq="D"),
			"open": [100.0] * 4,
			"high": [105.0] * 4,
			"low": [95.0] * 4,
			"close": [102.0] * 4,
			"volume": [1000.0] * 4,
		}
	)
	moex = Exchange(name="Moex", code="MOEX")
	async_session.add(moex)
	await async_session.commit()
	ticker = Ticker(
		symbol="SBER",
		asset_type="QUOTE",
		exchange_id=moex.id,
		base_currency="RUB",
		quote_currency="RUB",
	)
	async_session.add(ticker)
	await async_session.commit()
	await async_session.refresh(ticker)
	df["ticker_id"] = ticker.id

	mock_ensure = mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker",
		return_value=uuid7(),
	)

	mock_result = MagicMock()
	mock_result.rowcount = 0
	async_session.execute.return_value = mock_result

	await upsert_market_data_batch(session=async_session, df=df)

	assert mock_ensure.call_count == 3
