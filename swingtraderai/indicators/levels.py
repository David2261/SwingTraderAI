import numpy as np
import pandas as pd

from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA


def detect_fractal_highs_lows(
	df: pd.DataFrame, window: int = 2
) -> tuple[pd.Series, pd.Series]:
	"""
	Находит fractal highs (локальные максимумы) и fractal lows (локальные минимумы).
	Классический Bill Williams fractal: бар выше/ниже соседних баров слева и справа.

	Возвращает:
	Series с High-значениями в точках fractal high (NaN иначе)
	Series с Low-значениями в точках fractal low (NaN иначе)
	"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)

	high = df[MARKET_DATA_SCHEMA.HIGH_COLUMN]
	low = df[MARKET_DATA_SCHEMA.LOW_COLUMN]

	is_fractal_high = (
		high == high.rolling(window * 2 + 1, center=True, min_periods=window + 1).max()
	)

	is_fractal_low = (
		low == low.rolling(window * 2 + 1, center=True, min_periods=window + 1).min()
	)

	return high.where(is_fractal_high), low.where(is_fractal_low)


def rolling_support_resistance_zones(
	df: pd.DataFrame,
	window: int = 50,
	min_touches: int = 3,
	price_tolerance: float = 0.003,
) -> pd.DataFrame:
	"""
	Rolling поиск горизонтальных уровней поддержки и сопротивления
	по количеству касаний (low для support, high для resistance).
	"""
	supports = []
	resistances = []
	touches_s = []
	touches_r = []

	price_col_low = MARKET_DATA_SCHEMA.LOW_COLUMN
	price_col_high = MARKET_DATA_SCHEMA.HIGH_COLUMN

	for i in range(window, len(df)):
		window_df = df.iloc[i - window : i]

		lows = window_df[price_col_low]
		if len(lows) < min_touches:
			supports.append(np.nan)
			touches_s.append(0)
		else:
			ref_price = lows.median()
			bin_size = ref_price * price_tolerance
			rounded_lows = np.round(lows / bin_size) * bin_size

			unique_lows, counts_low = np.unique(rounded_lows, return_counts=True)
			strong_mask = counts_low >= min_touches
			strong_supports = unique_lows[strong_mask]
			strong_counts = counts_low[strong_mask]

			if len(strong_supports) > 0:
				best_idx = np.argmax(strong_counts)
				supports.append(strong_supports[best_idx])
				touches_s.append(strong_counts[best_idx])
			else:
				supports.append(np.nan)
				touches_s.append(0)

		highs = window_df[price_col_high]
		if len(highs) < min_touches:
			resistances.append(np.nan)
			touches_r.append(0)
		else:
			ref_price = highs.median()
			bin_size = ref_price * price_tolerance
			rounded_highs = np.round(highs / bin_size) * bin_size

			unique_highs, counts_high = np.unique(rounded_highs, return_counts=True)
			strong_mask = counts_high >= min_touches
			strong_res = unique_highs[strong_mask]
			strong_counts = counts_high[strong_mask]

			if len(strong_res) > 0:
				best_idx = np.argmax(strong_counts)
				resistances.append(strong_res[best_idx])
				touches_r.append(strong_counts[best_idx])
			else:
				resistances.append(np.nan)
				touches_r.append(0)

	result = pd.DataFrame(
		{
			"support_level": [np.nan] * window + supports,
			"resistance_level": [np.nan] * window + resistances,
			"touches_support": [0] * window + touches_s,
			"touches_resistance": [0] * window + touches_r,
		},
		index=df.index,
	)

	return result


def calculate_classic_pivot_points(
	df: pd.DataFrame, timeframe: str = "D"
) -> pd.DataFrame:
	"""
	Классические дневные/недельные Pivot Points
	"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)

	temp_df = df.copy()

	if "time" in temp_df.columns:
		temp_df = temp_df.set_index("time")

	high = MARKET_DATA_SCHEMA.HIGH_COLUMN
	low = MARKET_DATA_SCHEMA.LOW_COLUMN
	close = MARKET_DATA_SCHEMA.CLOSE_COLUMN

	resampled = (
		temp_df.resample(timeframe)
		.agg({high: "max", low: "min", close: "last"})
		.shift(1)
	)

	pp = (resampled[high] + resampled[low] + resampled[close]) / 3

	data = pd.DataFrame(
		{
			"pp": pp,
			"r1": 2 * pp - resampled[low],
			"s1": 2 * pp - resampled[high],
			"r2": pp + (resampled[high] - resampled[low]),
			"s2": pp - (resampled[high] - resampled[low]),
		},
		index=resampled.index,
	)

	if "time" in df.columns:
		return data.reindex(df["time"], method="ffill")
	else:
		return data.reindex(df.index, method="ffill")


def add_key_levels_indicators(
	df: pd.DataFrame, fractal_window: int = 5, sr_window: int = 120, pivot_tf: str = "D"
) -> pd.DataFrame:
	"""
	Добавляет колонки, связанные с уровнями:
	- fractal_high, fractal_low
	- support_level, resistance_level (rolling)
	- PP, R1, S1, R2, S2 (pivot points)
	"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)
	df = df.copy()

	f_high, f_low = detect_fractal_highs_lows(df, window=fractal_window)
	df["fractal_high"] = f_high
	df["fractal_low"] = f_low

	zones = rolling_support_resistance_zones(
		df, window=sr_window, min_touches=3, price_tolerance=0.003
	)
	df = pd.concat([df, zones], axis=1)

	pivots = calculate_classic_pivot_points(df, timeframe=pivot_tf)
	df = pd.concat([df, pivots], axis=1)

	return df
