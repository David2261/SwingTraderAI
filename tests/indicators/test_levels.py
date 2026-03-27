from datetime import datetime

import numpy as np
import pandas as pd

from swingtraderai.indicators.levels import (
	add_key_levels_indicators,
	calculate_classic_pivot_points,
	detect_fractal_highs_lows,
	rolling_support_resistance_zones,
)


def test_detect_fractal_highs_lows(sample_ohlcv):
	highs, lows = detect_fractal_highs_lows(sample_ohlcv, window=2)

	assert isinstance(highs, pd.Series)
	assert isinstance(lows, pd.Series)
	assert len(highs) == len(sample_ohlcv)
	assert len(lows) == len(sample_ohlcv)

	assert highs.notna().sum() > 0
	assert lows.notna().sum() > 0

	fractal_high_idx = highs.first_valid_index()
	if fractal_high_idx is not None:
		window_slice = sample_ohlcv["high"].iloc[
			max(0, fractal_high_idx - 2) : fractal_high_idx + 3
		]
		assert sample_ohlcv.loc[fractal_high_idx, "high"] == window_slice.max()


def test_detect_fractal_with_small_window(sample_ohlcv):
	highs, lows = detect_fractal_highs_lows(sample_ohlcv, window=1)
	assert highs.notna().sum() >= 5


def test_rolling_support_resistance_zones(sample_ohlcv):
	result = rolling_support_resistance_zones(
		sample_ohlcv, window=30, min_touches=2, price_tolerance=0.005
	)

	assert isinstance(result, pd.DataFrame)
	assert list(result.columns) == [
		"support_level",
		"resistance_level",
		"touches_support",
		"touches_resistance",
	]

	assert len(result) == len(sample_ohlcv)
	assert result.index.equals(sample_ohlcv.index)

	assert result["support_level"].iloc[30:].notna().sum() > 0
	assert result["resistance_level"].iloc[30:].notna().sum() > 0


def test_calculate_classic_pivot_points(sample_ohlcv):
	pivots = calculate_classic_pivot_points(sample_ohlcv, timeframe="D")

	assert isinstance(pivots, pd.DataFrame)
	assert "pp" in pivots.columns
	assert "r1" in pivots.columns
	assert "s1" in pivots.columns
	assert "r2" in pivots.columns
	assert "s2" in pivots.columns

	assert pivots["pp"].notna().sum() > 0


def test_add_key_levels_indicators(sample_ohlcv):
	result = add_key_levels_indicators(
		sample_ohlcv, fractal_window=2, sr_window=40, pivot_tf="D"
	)

	expected_columns = {
		"open",
		"high",
		"low",
		"close",
		"volume",
		"fractal_high",
		"fractal_low",
		"support_level",
		"resistance_level",
		"touches_support",
		"touches_resistance",
		"pp",
		"r1",
		"s1",
		"r2",
		"s2",
	}

	assert isinstance(result, pd.DataFrame)
	assert expected_columns.issubset(result.columns)

	assert result["fractal_high"].notna().sum() > 0
	assert result["fractal_low"].notna().sum() > 0
	assert result["pp"].notna().sum() > 10


def test_detect_fractal_on_empty_dataframe():
	empty_df = pd.DataFrame(
		columns=["open", "high", "low", "close", "volume", "time", "timeframe"]
	)
	highs, lows = detect_fractal_highs_lows(empty_df, window=2)

	assert len(highs) == 0
	assert len(lows) == 0


def test_rolling_support_resistance_small_window():
	small_df = pd.DataFrame(
		{
			"high": np.random.rand(20) * 100 + 5000,
			"low": np.random.rand(20) * 100 + 4900,
		}
	)

	result = rolling_support_resistance_zones(small_df, window=10, min_touches=5)

	assert result["support_level"].iloc[:15].isna().all()
	assert result["resistance_level"].iloc[:15].isna().all()


def test_pivot_points_on_single_day_data():
	df = pd.DataFrame(
		{
			"open": [5000],
			"high": [5050],
			"low": [4980],
			"close": [5020],
			"volume": [1000],
			"time": [pd.Timestamp("2025-03-01")],
			"timeframe": ["1D"],
		},
		index=[datetime(2025, 3, 1)],
	)

	pivots = calculate_classic_pivot_points(df, timeframe="1D")
	assert not pivots.empty


def test_add_key_levels_preserves_original_data(sample_ohlcv):
	result = add_key_levels_indicators(sample_ohlcv, fractal_window=2, sr_window=30)

	for col in ["open", "high", "low", "close", "volume"]:
		assert col in result.columns
		assert (
			result[col].values[: len(sample_ohlcv)] == sample_ohlcv[col].values
		).all(), f"Column '{col}' values do not match"
