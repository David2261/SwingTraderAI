from datetime import datetime, timezone

import pandas as pd
import pytest

from swingtraderai.ingestion.sources.ccxt_base import CcxtSource


@pytest.fixture
def mock_exchange(mocker):
	"""Мок биржи ccxt"""
	exchange = mocker.Mock()
	exchange.fetch_ohlcv = mocker.Mock()
	return exchange


@pytest.fixture
def ccxt_source(mocker, mock_exchange):
	"""CcxtSource с замоканной биржей"""
	# Патчим класс биржи, чтобы он возвращал наш мок
	mocker.patch("ccxt.binance", return_value=mock_exchange)

	source = CcxtSource("binance")
	return source


def test_init_sets_exchange_correctly(mocker):
	"""Проверяем создание exchange с правильными параметрами"""
	mock_binance = mocker.patch("ccxt.binance")

	CcxtSource("binance")

	mock_binance.assert_called_once_with(
		{
			"enableRateLimit": True,
			"options": {"defaultType": "spot"},
		}
	)


@pytest.mark.parametrize(
	"symbol, timeframe, since, limit, expected_since_ms",
	[
		("BTC/USDT", "1h", None, 1000, None),
		(
			"ETH/BTC",
			"15m",
			datetime(2025, 1, 1, tzinfo=timezone.utc),
			500,
			1735689600000,
		),
	],
)
def test_fetch_ohlcv_calls_exchange_correctly(
	ccxt_source,
	mock_exchange,
	symbol,
	timeframe,
	since,
	limit,
	expected_since_ms,
):
	"""Проверяем вызов fetch_ohlcv с правильными параметрами"""
	mock_data = [
		[1735689600000, 100.0, 105.0, 95.0, 102.0, 1000.0, "1h"],
		[1735693200000, 102.0, 107.0, 99.0, 104.0, 1200.0, "1h"],
	]
	mock_exchange.fetch_ohlcv.return_value = mock_data

	df = ccxt_source.fetch_ohlcv(symbol, timeframe, since, limit)

	mock_exchange.fetch_ohlcv.assert_called_once_with(
		symbol, timeframe, since=expected_since_ms, limit=limit
	)

	assert isinstance(df, pd.DataFrame)
	assert len(df) == 2
	assert list(df.columns) == [
		"time",
		"open",
		"high",
		"low",
		"close",
		"volume",
		"timeframe",
	]


def test_fetch_ohlcv_handles_empty_response(ccxt_source, mock_exchange):
	"""Пустой ответ от биржи → пустой DataFrame"""
	mock_exchange.fetch_ohlcv.return_value = []

	df = ccxt_source.fetch_ohlcv("BTC/USDT", "1h")

	assert isinstance(df, pd.DataFrame)
	assert df.empty


def test_fetch_ohlcv_converts_time_correctly(ccxt_source, mock_exchange):
	"""Конвертация ms → datetime"""
	mock_data = [
		[1735689600000, 100.0, 105.0, 95.0, 102.0, 1000.0, "1h"],
	]
	mock_exchange.fetch_ohlcv.return_value = mock_data

	df = ccxt_source.fetch_ohlcv("BTC/USDT", "1h")

	assert df["time"].iloc[0] == pd.Timestamp("2025-01-01 00:00:00", tz=None)


def test_fetch_ohlcv_preserves_numeric_precision(ccxt_source, mock_exchange):
	"""Точность чисел после конвертации"""
	mock_data = [
		[
			1735689600000,
			12345.6789,
			12350.1234,
			12340.5678,
			12348.9012,
			9876.54321,
			"1h",
		],
	]
	mock_exchange.fetch_ohlcv.return_value = mock_data

	df = ccxt_source.fetch_ohlcv("TEST/USDT", "1h")

	assert df["open"].iloc[0] == 12345.6789
	assert df["volume"].iloc[0] == 9876.54321
