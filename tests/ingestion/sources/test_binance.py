from datetime import datetime, timezone

import pandas as pd
import pytest

from swingtraderai.ingestion.sources.binance import BinanceSource


@pytest.fixture
def mock_ccxt_binance(mocker):
	exchange = mocker.Mock()
	exchange.options = {}
	exchange.fetch_ohlcv = mocker.Mock()
	return exchange


@pytest.fixture
def binance_source(mocker, mock_ccxt_binance):
	"""BinanceSource с замоканной библиотекой ccxt"""
	mocker.patch("ccxt.binance", return_value=mock_ccxt_binance)
	return BinanceSource()


def test_binance_init_config(binance_source, mock_ccxt_binance):
	"""Проверяем корректность инициализации Binance"""
	assert mock_ccxt_binance.options["defaultType"] == "spot"
	import ccxt

	ccxt.binance.assert_called_once()


def test_binance_fetch_ohlcv_calls_ccxt(binance_source, mock_ccxt_binance):
	"""Проверяем передачу параметров в метод fetch_ohlcv биржи"""
	mock_ccxt_binance.fetch_ohlcv.return_value = []

	symbol = "BTC/USDT"
	tf = "1d"
	since = datetime(2025, 1, 1, tzinfo=timezone.utc)
	limit = 50

	binance_source.fetch_ohlcv(symbol, tf, since=since, limit=limit)

	mock_ccxt_binance.fetch_ohlcv.assert_called_once_with(
		symbol, tf, since=1735689600000, limit=limit
	)


def test_binance_fetch_ohlcv_returns_dataframe(binance_source, mock_ccxt_binance):
	"""Проверяем, что на выходе корректный DataFrame"""
	mock_ccxt_binance.fetch_ohlcv.return_value = [
		[1735689600000, 60000.0, 61000.0, 59000.0, 60500.0, 10.5]
	]

	df = binance_source.fetch_ohlcv("BTC/USDT", "1h")

	assert isinstance(df, pd.DataFrame)
	assert not df.empty
	assert df["close"].iloc[0] == 60500.0
	assert df["timestamp"].iloc[0] == pd.Timestamp("2025-01-01 00:00:00")
