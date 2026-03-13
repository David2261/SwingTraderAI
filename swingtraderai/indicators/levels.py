import numpy as np
import pandas as pd


def detect_fractal_highs_lows(df: pd.DataFrame, window: int = 2) -> pd.DataFrame:
	"""
	Находит fractal highs (локальные максимумы) и fractal lows (локальные минимумы).
	Классический Bill Williams fractal: бар выше/ниже соседних баров слева и справа.

	Возвращает:
	Series с High-значениями в точках fractal high (NaN иначе)
	Series с Low-значениями в точках fractal low (NaN иначе)
	"""
	high = df["High"]
	low = df["Low"]

	is_high = pd.Series(True, index=df.index)
	is_low = pd.Series(True, index=df.index)

	for i in range(1, window + 1):
		is_high &= (high.shift(window) > high.shift(window + i)) & (
			high.shift(window) > high.shift(window - i)
		)
		is_low &= (low.shift(window) < low.shift(window + i)) & (
			low.shift(window) < low.shift(window - i)
		)

	return high.where(is_high), low.where(is_low)


def rolling_support_resistance_zones(
	df: pd.DataFrame,
	window: int = 50,
	min_touches: int = 3,
	price_tolerance: float = 0.003,
) -> pd.DataFrame:
	"""
	Простой rolling-алгоритм поиска уровней по количеству касаний.
	"""
	supports = []
	resistances = []
	touches_s = []
	touches_r = []

	for i in range(window, len(df)):
		window_df = df.iloc[i - window : i]

		lows = window_df["Low"]
		unique_lows, counts_low = np.unique(
			np.round(lows / (lows.mean() * price_tolerance))
			* (lows.mean() * price_tolerance),
			return_counts=True,
		)

		strong_supports = unique_lows[counts_low >= min_touches]
		if len(strong_supports) > 0:
			supports.append(strong_supports[-1])
		else:
			supports.append(np.nan)

		highs = window_df["High"]
		unique_highs, counts_high = np.unique(
			np.round(highs / (highs.mean() * price_tolerance))
			* (highs.mean() * price_tolerance),
			return_counts=True,
		)

		strong_res = unique_highs[counts_high >= min_touches]
		if len(strong_res) > 0:
			resistances.append(strong_res[-1])
		else:
			resistances.append(np.nan)

		touches_s.append(max(counts_low) if len(counts_low) > 0 else 0)
		touches_r.append(max(counts_high) if len(counts_high) > 0 else 0)

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
	resampled = (
		df.resample(timeframe)
		.agg({"High": "max", "Low": "min", "Close": "last"})
		.shift(1)
	)

	pp = (resampled["High"] + resampled["Low"] + resampled["Close"]) / 3

	data = pd.DataFrame(index=resampled.index)
	data["PP"] = pp
	data["R1"] = 2 * pp - resampled["Low"]
	data["S1"] = 2 * pp - resampled["High"]
	data["R2"] = pp + (resampled["High"] - resampled["Low"])
	data["S2"] = pp - (resampled["High"] - resampled["Low"])

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
