import pandas as pd

from swingtraderai.indicators.base import IndicatorResult
from swingtraderai.indicators.registry import registry
from swingtraderai.indicators.technical import (
	EMAIndicator,
	SessionVWAPIndicator,
	VWAPIndicator,
	WMAIndicator,
)


def test_ema_indicator_basic(sample_ohlcv):
	indicator = EMAIndicator("ema20", length=20)
	result = indicator.calculate(sample_ohlcv)

	assert isinstance(result, IndicatorResult)
	assert result.name == "ema20"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["length"] == 20


def test_ema_indicator_different_lengths(sample_ohlcv):
	for length in [9, 20, 50, 200]:
		indicator = EMAIndicator(f"ema{length}", length=length)
		result = indicator.calculate(sample_ohlcv)

		assert result.name == f"ema{length}"
		assert result.metadata["length"] == length


def test_ema_on_small_dataframe():
	small_df = pd.DataFrame({"close": [100, 101, 102, 103]})
	indicator = EMAIndicator("ema20", length=20)
	result = indicator.calculate(small_df)

	assert result.value is None


def test_wma_indicator_basic(sample_ohlcv):
	indicator = WMAIndicator("wma20", length=20)
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "wma20"
	assert isinstance(result.value, (float, type(None)))


def test_wma_different_lengths(sample_ohlcv):
	indicator = WMAIndicator("wma10", length=10)
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "wma10"


def test_vwap_indicator_basic(sample_ohlcv):
	indicator = VWAPIndicator()
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "vwap"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["period"] == "full"


def test_vwap_without_volume():
	df = pd.DataFrame(
		{
			"open": [100, 101],
			"high": [102, 103],
			"low": [99, 100],
			"close": [101, 102],
			# volume отсутствует
		}
	)
	indicator = VWAPIndicator()
	result = indicator.calculate(df)

	assert result.value is None


def test_session_vwap_basic(sample_ohlcv):
	indicator = SessionVWAPIndicator()
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "vwap_session"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["type"] == "session_vwap"


def test_all_indicators_registered():
	"""Проверяем, что все индикаторы из technical.py зарегистрированы"""
	registered = registry.list_all()

	expected = [
		"ema20",
		"ema50",
		"ema200",
		"wma10",
		"wma20",
		"wma50",
		"vwap",
		"vwap_session",
	]

	for name in expected:
		assert name in registered, f"Индикатор {name} не зарегистрирован"


def test_ema_indicator_in_registry():
	ema = registry.get("ema20")
	assert ema is not None
	assert ema.category == "trend"


def test_vwap_indicator_in_registry():
	vwap = registry.get("vwap")
	assert vwap is not None
	assert vwap.category == "volume"


def test_indicators_on_empty_dataframe():
	empty_df = pd.DataFrame(columns=["open", "high", "low", "close", "volume", "time"])

	indicators = [
		EMAIndicator("ema20"),
		WMAIndicator("wma20"),
		VWAPIndicator(),
		SessionVWAPIndicator(),
	]

	for ind in indicators:
		result = ind.calculate(empty_df)
		assert (
			result.value is None or result.value == 0 or isinstance(result.value, dict)
		)


def test_ema_with_custom_length_via_kwargs(sample_ohlcv):
	indicator = EMAIndicator("ema_custom", length=30)
	result = indicator.calculate(sample_ohlcv, length=15)

	assert result.metadata["length"] == 15
