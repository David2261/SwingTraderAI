from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from swingtraderai.ingestion.sources.moex import MoexSource


@pytest.fixture
def moex_source():
	return MoexSource()


@patch("swingtraderai.ingestion.sources.moex.Ticker")
def test_fetch_ohlcv_unsupported_timeframe(mock_ticker_class, moex_source):
	"""Неподдерживаемый timeframe → ValueError от MoexSource"""
	with pytest.raises(ValueError, match="Unsupported timeframe: 2m"):
		moex_source.fetch_ohlcv("SBER", "2m")


def test_fetch_ohlcv_renames_columns(moex_source, mocker):
	"""Переименование колонок и обработка timestamp"""
	mock_df = pd.DataFrame(
		{
			"begin": pd.date_range("2025-01-01", periods=3, freq="1h"),
			"open": [100.0, 101.0, 102.0],
			"high": [105.0, 106.0, 107.0],
			"low": [95.0, 96.0, 97.0],
			"close": [102.0, 103.0, 104.0],
			"volume": [1000.0, 1100.0, 1200.0],
		}
	)

	mock_ticker = mocker.Mock()
	mock_ticker.candles.return_value = mock_df

	with patch("swingtraderai.ingestion.sources.moex.Ticker", return_value=mock_ticker):
		df = moex_source.fetch_ohlcv("SBER", "1h")

	expected_columns = ["timestamp", "open", "high", "low", "close", "volume"]
	assert list(df.columns) == expected_columns
	assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
	assert df["timestamp"].dt.tz == timezone.utc


@pytest.mark.parametrize(
	"timeframe, expected_period",
	[
		("1m", "1min"),
		("5m", "5min"),
		("15m", "15min"),
		("30m", "30min"),
		("1h", "1h"),
		("1d", "1D"),
	],
)
@patch("swingtraderai.ingestion.sources.moex.Ticker")
def test_timeframe_mapping(mock_ticker_class, moex_source, timeframe, expected_period):
	mock_ticker = MagicMock()
	mock_ticker.candles.return_value = pd.DataFrame(columns=["begin", "open"])
	mock_ticker_class.return_value = mock_ticker

	moex_source.fetch_ohlcv("SBER", timeframe)

	mock_ticker.candles.assert_called_once()
	called_kwargs = mock_ticker.candles.call_args.kwargs
	assert called_kwargs["period"] == expected_period
	assert "start" in called_kwargs
	assert "end" in called_kwargs


@patch("swingtraderai.ingestion.sources.moex.Ticker")
def test_fetch_ohlcv_fallback_to_get_candles(mock_ticker_class, moex_source):
	"""Если candles нет — используем get_candles"""
	mock_ticker = MagicMock()
	del mock_ticker.candles
	mock_ticker.get_candles.return_value = pd.DataFrame()
	mock_ticker_class.return_value = mock_ticker

	moex_source.fetch_ohlcv("SBER", "1d")

	mock_ticker.get_candles.assert_called_once()


def test_fetch_ohlcv_since_without_tz(moex_source, mocker):
	"""since без tz → должен стать UTC"""
	mock_ticker = mocker.Mock()
	mock_ticker.candles.return_value = pd.DataFrame()

	naive_since = datetime(2025, 1, 1)

	with patch("swingtraderai.ingestion.sources.moex.Ticker", return_value=mock_ticker):
		moex_source.fetch_ohlcv("SBER", "1d", since=naive_since)

	called_kwargs = mock_ticker.candles.call_args.kwargs
	assert called_kwargs["start"].tzinfo == timezone.utc


def test_fetch_ohlcv_default_since(moex_source, mocker):
	"""since=None → последние ~2 года"""
	mock_ticker = mocker.Mock()
	mock_ticker.candles.return_value = pd.DataFrame()

	with patch("swingtraderai.ingestion.sources.moex.Ticker", return_value=mock_ticker):
		moex_source.fetch_ohlcv("SBER", "1d")

	called_kwargs = mock_ticker.candles.call_args.kwargs
	start = called_kwargs["start"]
	now = datetime.now(timezone.utc)
	assert (now - start).days >= 700  # ~2 года


def test_fetch_ohlcv_applies_limit(moex_source, mocker):
	"""Обрезка по limit"""
	mock_df = pd.DataFrame(
		{
			"begin": pd.date_range("2025-01-01", periods=1500, freq="1h", tz="UTC"),
			"open": [100.0] * 1500,
			"high": [105.0] * 1500,
			"low": [95.0] * 1500,
			"close": [102.0] * 1500,
			"volume": [1000.0] * 1500,
		}
	)

	mock_ticker = mocker.Mock()
	mock_ticker.candles.return_value = mock_df

	with patch("swingtraderai.ingestion.sources.moex.Ticker", return_value=mock_ticker):
		df = moex_source.fetch_ohlcv("SBER", "1h", limit=500)

	assert len(df) == 500
	# Проверяем последние записи
	assert df["timestamp"].iloc[-1] == mock_df["begin"].iloc[-1]


def test_fetch_ohlcv_handles_empty_result(moex_source, mocker):
	"""Пустой результат → пустой DataFrame"""
	mock_ticker = mocker.Mock()
	mock_ticker.candles.return_value = pd.DataFrame()

	with patch("swingtraderai.ingestion.sources.moex.Ticker", return_value=mock_ticker):
		df = moex_source.fetch_ohlcv("SBER", "1d")

	assert df.empty


def test_fetch_ohlcv_handles_invalid_symbol(moex_source, mocker):
	"""Неверный символ → moexalgo бросит исключение"""
	mock_ticker = mocker.Mock()
	mock_ticker.candles.side_effect = ValueError("Invalid ticker")

	with patch("swingtraderai.ingestion.sources.moex.Ticker", return_value=mock_ticker):
		with pytest.raises(ValueError):
			moex_source.fetch_ohlcv("INVALID", "1d")
