import numpy as np
import pandas as pd
import pytest

from swingtraderai.indicators.matrix import (
	add_all_indicators,
	add_target,
	engineer_features,
)
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA


@pytest.fixture
def sample_ohlcv_features() -> pd.DataFrame:
	"""DataFrame подходящий для тестирования feature engineering"""
	np.random.seed(42)
	dates = pd.date_range("2025-03-01", periods=200, freq="h")

	base = np.linspace(5000, 5150, 200) + np.random.normal(0, 15, 200)

	df = pd.DataFrame(
		{
			"time": dates,
			"open": base + np.random.normal(5000, 30, 200).cumsum(),
			"high": base + np.random.normal(5010, 35, 200).cumsum(),
			"low": base + np.random.normal(4990, 35, 200).cumsum(),
			"close": base + np.random.normal(5000, 30, 200).cumsum(),
			"volume": np.random.randint(500, 15000, 200),
			"timeframe": "1h",
		}
	)
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	df["time"] = pd.to_datetime(df["time"])
	return df


def test_engineer_features(sample_ohlcv_features):
	result = engineer_features(sample_ohlcv_features)

	assert isinstance(result, pd.DataFrame)
	assert len(result) > 0
	indicators_lower = [col.lower() for col in result.columns]

	assert any("sma_10" in c for c in indicators_lower)
	assert any("sma_20" in c for c in indicators_lower)
	assert any("sma_50" in c for c in indicators_lower)
	assert any("ema_9" in c for c in indicators_lower)
	assert any("rsi_14" in c for c in indicators_lower)
	assert any("atr" in c for c in indicators_lower)

	assert "fractal_high" in result.columns
	assert "fractal_low" in result.columns
	assert "pp" in result.columns
	assert "close_to_pp" in result.columns
	assert "dist_to_r1" in result.columns
	assert "dist_to_last_f_high" in result.columns
	assert "return_1" in result.columns
	assert "rsi_lag_1" in result.columns


def test_add_target(sample_ohlcv_features):
	df = engineer_features(sample_ohlcv_features)
	result = add_target(df, horizon=5, threshold=0.008)

	assert isinstance(result, pd.DataFrame)
	assert "future_return" in result.columns
	assert "target" in result.columns
	assert result["target"].isin([0, 1]).all()
	assert len(result) == len(df)


def test_add_all_indicators(sample_ohlcv_features):
	result = add_all_indicators(sample_ohlcv_features)

	assert isinstance(result, pd.DataFrame)
	assert "pp" in result.columns
	assert "target" not in result.columns


def test_engineer_features_raises_if_no_atr_rsi():
	"""Проверяем, что функция корректно падает при невозможности создать ATR/RSI"""

	bad_df = pd.DataFrame(
		{
			"time": pd.date_range("2025-03-01", periods=5, freq="h"),
			"open": np.random.rand(5) * 100,
			"high": np.random.rand(5) * 100,
			"low": np.random.rand(5) * 100,
			"close": np.random.rand(5) * 100,
			"volume": np.random.randint(100, 1000, 5),
			"timeframe": "1h",
		}
	)

	with pytest.raises(ValueError, match="ATR колонка не найдена"):
		engineer_features(bad_df)


def test_add_target_with_different_params(sample_ohlcv_features):
	df = engineer_features(sample_ohlcv_features)

	result1 = add_target(df, horizon=3, threshold=0.005)
	result2 = add_target(df, horizon=10, threshold=0.01)

	assert "target" in result1.columns
	assert "target" in result2.columns
	assert len(result1) > 0
	assert len(result2) > 0


def test_add_all_indicators_preserves_time_column(sample_ohlcv_features):
	result = add_all_indicators(sample_ohlcv_features)

	assert "time" in result.columns
	assert pd.api.types.is_datetime64_any_dtype(result["time"])


def test_empty_dataframe_handling():
	empty_df = pd.DataFrame(
		columns=["time", "open", "high", "low", "close", "volume", "timeframe"]
	)

	with pytest.raises(ValueError):
		add_all_indicators(empty_df)


def test_required_indicators_are_present(sample_ohlcv_features):
	result = add_all_indicators(sample_ohlcv_features)

	columns_lower = [c.lower() for c in result.columns]

	assert any("sma_10" in c for c in columns_lower)
	assert any("rsi_14" in c for c in columns_lower)
	assert any("atr" in c for c in columns_lower)
	assert "pp" in result.columns
	assert "fractal_high" in result.columns
