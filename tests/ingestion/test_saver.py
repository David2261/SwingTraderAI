from datetime import timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from swingtraderai.db.models.market import Exchange, Ticker
from swingtraderai.ingestion import saver
from swingtraderai.ingestion.saver import ensure_ticker, upsert_market_data_batch
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA


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


@pytest.mark.asyncio
async def test_ensure_ticker_assigns_exchange_and_currencies(async_session):
	"""Создаём тикер с exchange_id, base_currency и quote_currency"""
	mock_result = MagicMock()
	mock_result.scalar_one_or_none.return_value = None
	async_session.execute.return_value = mock_result

	new_id = uuid7()
	async_session.add.side_effect = lambda obj: setattr(obj, "id", new_id)

	result = await ensure_ticker(
		session=async_session,
		symbol="NEWCOIN",
		asset_type="crypto",
		exchange_id=uuid7(),
		base_currency="USD",
		quote_currency="USDT",
	)

	assert result == new_id
	added_obj = async_session.add.call_args[0][0]
	assert added_obj.symbol == "NEWCOIN"
	assert added_obj.asset_type == "crypto"
	assert added_obj.base_currency == "USD"
	assert added_obj.quote_currency == "USDT"


@pytest.mark.asyncio
async def test_upsert_market_data_batch_missing_columns(async_session, sample_df):
	"""Если в df нет обязательных колонок → ValueError"""
	df = sample_df.drop(columns=["open"])

	with pytest.raises(ValueError) as exc_info:
		await upsert_market_data_batch(async_session, df)
	assert "Отсутствуют колонки: {'open'}" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upsert_market_data_batch_no_records(async_session, mocker):
	df = pd.DataFrame(
		{
			"symbol": [],
			"timeframe": [],
			"timestamp": [],
			"open": [],
			"high": [],
			"low": [],
			"close": [],
			"volume": [],
		}
	)

	with (
		patch.object(
			saver.MARKET_DATA_SCHEMA.__class__,
			"normalize_columns",
			side_effect=lambda self, df: df,
			autospec=True,
		),
		patch.object(
			saver.MARKET_DATA_SCHEMA.__class__,
			"validate_base_columns",
			side_effect=lambda self, df: None,
			autospec=True,
		),
	):
		inserted, updated = await saver.upsert_market_data_batch(async_session, df)

	assert inserted == 0
	assert updated == 0


@pytest.mark.asyncio
async def test_upsert_market_data_batch_updates_only(async_session, sample_df, mocker):
	"""Проверяем обновление записей через on_conflict_do_update"""
	mock_ticker_id = uuid7()
	mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker", return_value=mock_ticker_id
	)

	mock_result = MagicMock()

	def side_effect(stmt, params=None):
		mock_result.rowcount = len(params) if params is not None else 0
		return mock_result

	async_session.execute.side_effect = side_effect

	sample_df = sample_df.copy()
	sample_df["time"] = sample_df["timestamp"]
	sample_df["ticker_id"] = mock_ticker_id

	mocker.patch.object(
		MARKET_DATA_SCHEMA.__class__, "normalize_columns", side_effect=lambda x: x
	)
	mocker.patch.object(
		MARKET_DATA_SCHEMA.__class__,
		"validate_base_columns",
		side_effect=lambda x: None,
	)

	inserted, updated = await upsert_market_data_batch(async_session, sample_df)

	assert inserted == 0
	assert updated == len(sample_df)


@pytest.mark.asyncio
async def test_upsert_market_data_batch_timestamp_normalization(
	async_session, sample_df, mocker
):
	"""timestamp без tzinfo → должен быть преобразован в UTC"""
	mock_ticker_id = uuid7()
	mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker", return_value=mock_ticker_id
	)

	df = sample_df.copy()

	df["time"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)  # убираем tz
	df["ticker_id"] = mock_ticker_id

	mock_result = MagicMock()
	mock_result.rowcount = 0
	async_session.execute.return_value = mock_result

	# Мокаем методы схемы
	mocker.patch.object(
		saver.MARKET_DATA_SCHEMA.__class__,
		"normalize_columns",
		side_effect=lambda df: df,
		autospec=False,
	)
	mocker.patch.object(
		saver.MARKET_DATA_SCHEMA.__class__,
		"validate_base_columns",
		side_effect=lambda df: None,
		autospec=False,
	)

	inserted, updated = await saver.upsert_market_data_batch(async_session, df)

	args, kwargs = async_session.execute.call_args
	records = args[1]

	for rec in records:
		assert rec["timestamp"].tzinfo == timezone.utc, (
			f"Timestamp {rec['timestamp']} is not UTC"
		)


@pytest.mark.asyncio
async def test_upsert_market_data_batch_multiple_symbols_same_ticker_cache(
	async_session, sample_df, mocker
):
	"""ticker_cache должен использовать один id для повторяющихся символов"""
	mock_ticker_id = uuid7()
	mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker", return_value=mock_ticker_id
	)
	mock_ensure = mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker", return_value=uuid7()
	)
	mock_result = MagicMock()
	mock_result.rowcount = 1
	async_session.execute.return_value = mock_result
	sample_df["time"] = sample_df["timestamp"]
	sample_df["ticker_id"] = mock_ticker_id

	mocker.patch.object(
		MARKET_DATA_SCHEMA.__class__, "normalize_columns", side_effect=lambda x: x
	)
	mocker.patch.object(
		MARKET_DATA_SCHEMA.__class__,
		"validate_base_columns",
		side_effect=lambda x: None,
	)

	inserted, updated = await upsert_market_data_batch(async_session, sample_df)
	symbols = sample_df["symbol"].unique()
	assert mock_ensure.call_count == len(symbols)


@pytest.mark.asyncio
async def test_upsert_market_data_batch_missing_required_columns(
	async_session, sample_df, mocker
):
	"""Проверка ошибки при отсутствии обязательных колонок"""
	df = sample_df.copy()

	# Удаляем обязательные колонки
	df = df.drop(columns=["timestamp"], errors="ignore")
	df = df.drop(columns=["time"], errors="ignore")
	df = df.drop(columns=["ticker_id"], errors="ignore")

	with pytest.raises(ValueError) as exc_info:
		await upsert_market_data_batch(async_session, df)

	error_text = str(exc_info.value).lower()

	assert any(
		phrase in error_text
		for phrase in ["отсутствуют колонки", "missing required columns"]
	)
	assert any(col in error_text for col in ["time", "ticker_id"])


async def test_upsert_market_data_batch_decimal_conversion(
	async_session, sample_df, mocker
):
	"""Проверяем корректную конвертацию числовых колонок в Decimal"""
	mock_ticker_id = uuid7()
	mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker", return_value=mock_ticker_id
	)

	df = sample_df.copy()
	df["time"] = df["timestamp"]
	df["ticker_id"] = mock_ticker_id

	mocker.patch.object(
		MARKET_DATA_SCHEMA.__class__, "normalize_columns", side_effect=lambda x: x
	)
	mocker.patch.object(
		MARKET_DATA_SCHEMA.__class__,
		"validate_base_columns",
		side_effect=lambda x: None,
	)

	mock_result = MagicMock()
	mock_result.rowcount = 0
	async_session.execute.return_value = mock_result

	await upsert_market_data_batch(async_session, df)

	call_args = async_session.execute.call_args
	records = call_args[0][1]

	for rec in records[:3]:
		assert isinstance(rec["open"], Decimal)
		assert isinstance(rec["high"], Decimal)
		assert isinstance(rec["low"], Decimal)
		assert isinstance(rec["close"], Decimal)
		assert isinstance(rec["volume"], Decimal) or rec["volume"] is None


async def test_upsert_market_data_batch_empty_records_after_groupby(
	async_session, mocker
):
	"""Если после groupby по symbol записей не осталось — должен вернуть (0, 0)"""
	mock_ticker_id = uuid7()
	mocker.patch(
		"swingtraderai.ingestion.saver.ensure_ticker", return_value=mock_ticker_id
	)

	empty_df = pd.DataFrame(
		columns=[
			"symbol",
			"time",
			"open",
			"high",
			"low",
			"close",
			"volume",
			"timeframe",
		]
	)

	inserted, updated = await upsert_market_data_batch(async_session, empty_df)

	assert inserted == 0
	assert updated == 0
