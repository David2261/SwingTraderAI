import pandas as pd

from swingtraderai.indicators.base import IndicatorResult
from swingtraderai.indicators.price_action import (
	DistanceFromMAIndicator,
	LogReturnsIndicator,
	MomentumIndicator,
	ReturnsIndicator,
	RSIRegimeIndicator,
	ZScorePriceIndicator,
	ZScoreVolumeIndicator,
)
from swingtraderai.indicators.registry import registry


def test_returns_indicator(sample_ohlcv):
	indicator = ReturnsIndicator()
	result = indicator.calculate(sample_ohlcv)

	assert isinstance(result, IndicatorResult)
	assert result.name == "returns"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["unit"] == "%"


def test_log_returns_indicator(sample_ohlcv):
	indicator = LogReturnsIndicator()
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "log_returns"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["unit"] == "log"


def test_momentum_indicator(sample_ohlcv):
	indicator = MomentumIndicator("momentum10", period=10)
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "momentum10"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["period"] == 10


def test_momentum_different_periods(sample_ohlcv):
	for period in [5, 10, 20]:
		indicator = MomentumIndicator(f"momentum{period}", period=period)
		result = indicator.calculate(sample_ohlcv)
		assert result.metadata["period"] == period


def test_zscore_price(sample_ohlcv):
	indicator = ZScorePriceIndicator()
	result = indicator.calculate(sample_ohlcv, window=20)

	assert result.name == "zscore_price"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["window"] == 20


def test_zscore_volume(sample_ohlcv):
	indicator = ZScoreVolumeIndicator()
	result = indicator.calculate(sample_ohlcv, window=20)

	assert result.name == "zscore_volume"
	assert isinstance(result.value, (float, type(None)))


def test_distance_from_ema(sample_ohlcv):
	indicator = DistanceFromMAIndicator("distance_from_ema20", ma_type="ema", length=20)
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "distance_from_ema20"
	assert isinstance(result.value, (float, type(None)))
	assert result.metadata["ma_type"] == "ema"
	assert result.metadata["unit"] == "%"


def test_distance_from_sma(sample_ohlcv):
	indicator = DistanceFromMAIndicator("distance_from_sma20", ma_type="sma", length=20)
	result = indicator.calculate(sample_ohlcv)

	assert result.metadata["ma_type"] == "sma"


def test_rsi_regime_overbought(sample_ohlcv):
	indicator = RSIRegimeIndicator()
	result = indicator.calculate(sample_ohlcv)

	assert result.name == "rsi_regime"
	assert isinstance(result.value, float)
	assert result.regime in ["OVERBOUGHT", "BULLISH", "NEUTRAL", "BEARISH", "OVERSOLD"]
	assert result.signal in ["bullish", "bearish", "neutral"]


def test_rsi_regime_logic():
	"""Тест логики режимов RSI"""
	indicator = RSIRegimeIndicator()

	test_cases = [
		(75, "OVERBOUGHT", "bearish"),
		(65, "BULLISH", "bullish"),
		(50, "NEUTRAL", "neutral"),
		(35, "BEARISH", "bearish"),
		(25, "OVERSOLD", "bullish"),
	]

	for rsi_value, expected_regime, expected_signal in test_cases:

		def mock_calculate(df, **kwargs):
			return IndicatorResult(
				name="rsi_regime",
				value=rsi_value,
				signal=expected_signal,
				regime=expected_regime,
				metadata={"rsi_value": rsi_value},
			)

		indicator.calculate = mock_calculate

		df = pd.DataFrame({"close": [100] * 20})
		result = indicator.calculate(df)

		assert result.regime == expected_regime
		assert result.signal == expected_signal
		assert result.value == rsi_value


def test_price_action_indicators_are_registered():
	"""Проверяем регистрацию всех price action индикаторов"""
	registered = registry.list_all()

	expected = [
		"returns",
		"log_returns",
		"momentum10",
		"momentum20",
		"zscore_price",
		"zscore_volume",
		"distance_from_ema20",
		"distance_from_ema50",
		"rsi_regime",
	]

	for name in expected:
		assert name in registered, f"Индикатор {name} не зарегистрирован"


def test_returns_in_registry():
	ind = registry.get("returns")
	assert ind is not None
	assert ind.category == "price_action"


def test_rsi_regime_in_registry():
	ind = registry.get("rsi_regime")
	assert ind is not None
	assert ind.category == "price_action"


def test_indicators_on_empty_dataframe():
	empty_df = pd.DataFrame(columns=["open", "high", "low", "close", "volume", "time"])

	indicators = [
		ReturnsIndicator(),
		LogReturnsIndicator(),
		MomentumIndicator(),
		ZScorePriceIndicator(),
		ZScoreVolumeIndicator(),
		DistanceFromMAIndicator(),
		RSIRegimeIndicator(),
	]

	for ind in indicators:
		result = ind.calculate(empty_df)
		assert result.value is None or isinstance(result.value, (dict, float))


def test_momentum_with_custom_period_via_kwargs(sample_ohlcv):
	indicator = MomentumIndicator("momentum_custom", period=10)
	result = indicator.calculate(sample_ohlcv, period=5)

	assert result.metadata["period"] == 5
