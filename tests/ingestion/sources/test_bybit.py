from datetime import datetime, timezone

import pandas as pd
import pytest

from swingtraderai.ingestion.sources.bybit import BybitSource


@pytest.fixture
def mock_ccxt_bybit(mocker):
	"""Мок биржи ccxt.bybit"""
	exchange = mocker.Mock()
	exchange.options = {}
	exchange.fetch_ohlcv = mocker.Mock()
	return exchange


@pytest.fixture
def bybit_source(mocker, mock_ccxt_bybit):
	"""BybitSource с замоканной биржей"""
	mocker.patch("ccxt.bybit", return_value=mock_ccxt_bybit)
	return BybitSource()


def test_init_calls_super_correctly(mocker):
	"""Проверяем, что __init__ вызывает super и устанавливает defaultType=spot"""

	def mock_init(self, exchange_id):
		self.exchange = mocker.Mock()
		self.exchange.options = {}

	mocker.patch(
		"swingtraderai.ingestion.sources.ccxt_base.CcxtSource.__init__",
		autospec=True,
		side_effect=mock_init,
	)

	source = BybitSource()

	assert source.exchange.options["defaultType"] == "spot"


def test_fetch_ohlcv_calls_parent_method(bybit_source, mock_ccxt_bybit):
	"""Проверяем, что fetch_ohlcv вызывает родительский метод ccxt"""
	mock_data = [
		[1735689600000, 100.0, 105.0, 95.0, 102.0, 1000.0],
		[1735693200000, 102.0, 107.0, 99.0, 104.0, 1200.0],
	]
	mock_ccxt_bybit.fetch_ohlcv.return_value = mock_data

	df = bybit_source.fetch_ohlcv("BTCUSDT", "1h", limit=500)

	mock_ccxt_bybit.fetch_ohlcv.assert_called_once_with(
		"BTCUSDT", "1h", since=None, limit=500
	)

	assert isinstance(df, pd.DataFrame)
	assert len(df) == 2
	assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]


@pytest.mark.parametrize(
	"symbol, timeframe, since, limit, expected_since_ms",
	[
		("BTCUSDT", "1h", None, 1000, None),
		(
			"ETHUSDT",
			"15m",
			datetime(2025, 1, 1, tzinfo=timezone.utc),
			500,
			1735689600000,
		),
	],
)
def test_fetch_ohlcv_parameters(
	bybit_source,
	mock_ccxt_bybit,
	symbol,
	timeframe,
	since,
	limit,
	expected_since_ms,
):
	"""Проверяем передачу всех параметров в ccxt.fetch_ohlcv"""
	mock_ccxt_bybit.fetch_ohlcv.return_value = []

	bybit_source.fetch_ohlcv(symbol, timeframe, since, limit)

	mock_ccxt_bybit.fetch_ohlcv.assert_called_once_with(
		symbol, timeframe, since=expected_since_ms, limit=limit
	)


def test_fetch_ohlcv_handles_empty_response(bybit_source, mock_ccxt_bybit):
	"""Пустой ответ от Bybit → пустой DataFrame"""
	mock_ccxt_bybit.fetch_ohlcv.return_value = []

	df = bybit_source.fetch_ohlcv("BTCUSDT", "1h")

	assert isinstance(df, pd.DataFrame)
	assert df.empty


def test_fetch_ohlcv_converts_timestamp_correctly(bybit_source, mock_ccxt_bybit):
	"""Конвертация миллисекунд в datetime"""
	mock_data = [[1735689600000, 100.0, 105.0, 95.0, 102.0, 1000.0]]
	mock_ccxt_bybit.fetch_ohlcv.return_value = mock_data

	df = bybit_source.fetch_ohlcv("BTCUSDT", "1h")

	expected = pd.Timestamp("2025-01-01 00:00:00")
	assert df["timestamp"].iloc[0] == expected


def test_fetch_ohlcv_preserves_numeric_precision(bybit_source, mock_ccxt_bybit):
	"""Точность чисел не теряется после конвертации"""
	mock_data = [
		[1735689600000, 12345.6789, 12350.1234, 12340.5678, 12348.9012, 9876.54321],
	]
	mock_ccxt_bybit.fetch_ohlcv.return_value = mock_data

	df = bybit_source.fetch_ohlcv("TEST/USDT", "1h")

	assert df["open"].iloc[0] == 12345.6789
	assert df["volume"].iloc[0] == 9876.54321
