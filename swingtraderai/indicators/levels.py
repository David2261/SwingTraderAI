from typing import Any

import numpy as np
import pandas as pd

from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA

from .base import BaseIndicator, IndicatorResult
from .registry import registry


def detect_fractal_highs_lows(df: pd.DataFrame, window: int = 2) -> pd.DataFrame:
	"""Находит Fractal Highs и Lows (Bill Williams)"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
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
	window: int = 100,
	min_touches: int = 3,
	price_tolerance: float = 0.003,
) -> pd.DataFrame:
	"""Поиск горизонтальных уровней по количеству касаний"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)

	# Убеждаемся, что индекс - это range index
	df = df.reset_index(drop=True)

	supports = []
	resistances = []

	for i in range(window, len(df)):
		window_df = df.iloc[i - window : i]

		# Support
		lows = window_df[MARKET_DATA_SCHEMA.LOW_COLUMN]
		if len(lows) >= min_touches:
			ref = lows.median()
			bin_size = ref * price_tolerance
			rounded = np.round(lows / bin_size) * bin_size
			unique, counts = np.unique(rounded, return_counts=True)

			mask = counts >= min_touches
			strong = unique[mask]
			strong_counts = counts[mask]

			if len(strong) > 0:
				max_idx = np.argmax(strong_counts)
				supports.append(strong[max_idx])
			else:
				supports.append(np.nan)
		else:
			supports.append(np.nan)

		# Resistance
		highs = window_df[MARKET_DATA_SCHEMA.HIGH_COLUMN]
		if len(highs) >= min_touches:
			ref = highs.median()
			bin_size = ref * price_tolerance
			rounded = np.round(highs / bin_size) * bin_size
			unique, counts = np.unique(rounded, return_counts=True)

			mask = counts >= min_touches
			strong = unique[mask]
			strong_counts = counts[mask]

			if len(strong) > 0:
				max_idx = np.argmax(strong_counts)
				resistances.append(strong[max_idx])
			else:
				resistances.append(np.nan)
		else:
			resistances.append(np.nan)

	# Создаём DataFrame с точным количеством строк
	result_df = pd.DataFrame(index=df.index)

	# Первые window строк - NaN
	support_col = [np.nan] * window + supports
	resistance_col = [np.nan] * window + resistances

	# Обрезаем до нужной длины (на случай, если supports/resistances длиннее)
	result_df["support_level"] = support_col[: len(df)]
	result_df["resistance_level"] = resistance_col[: len(df)]

	return result_df


def calculate_classic_pivot_points(
	df: pd.DataFrame, timeframe: str = "D"
) -> pd.DataFrame:
	"""Классические Pivot Points с выравниванием по времени"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	temp = df.copy()

	if "time" in temp.columns:
		temp = temp.set_index("time")

	high, low, close = (
		MARKET_DATA_SCHEMA.HIGH_COLUMN,
		MARKET_DATA_SCHEMA.LOW_COLUMN,
		MARKET_DATA_SCHEMA.CLOSE_COLUMN,
	)

	daily = temp.resample(timeframe).agg({high: "max", low: "min", close: "last"})
	pp = (daily[high] + daily[low] + daily[close]) / 3

	pivot_df = pd.DataFrame(
		{
			"pp": pp,
			"r1": 2 * pp - daily[low],
			"s1": 2 * pp - daily[high],
			"r2": pp + (daily[high] - daily[low]),
			"s2": pp - (daily[high] - daily[low]),
		},
		index=daily.index,
	)

	result = pivot_df.reindex(temp.index, method="ffill")
	result = result.reset_index(drop=True)

	return result


def add_key_levels_indicators(
	df: pd.DataFrame, fractal_window: int = 2, sr_window: int = 100, pivot_tf: str = "D"
) -> pd.DataFrame:
	"""
	Главная функция — добавляет все уровневые индикаторы сразу.
	Используется в feature engineering.
	"""
	df = df.copy()

	# Fractals
	f_high, f_low = detect_fractal_highs_lows(df, window=fractal_window)
	df["fractal_high"] = f_high
	df["fractal_low"] = f_low

	# Support / Resistance
	zones = rolling_support_resistance_zones(df, window=sr_window)
	df = pd.concat([df, zones], axis=1)

	# Pivot Points
	pivots = calculate_classic_pivot_points(df, timeframe=pivot_tf)
	df = pd.concat([df, pivots], axis=1)

	return df


class FractalIndicator(BaseIndicator):
	name = "fractal"
	category = "levels"
	description = "Bill Williams Fractals (локальные экстремумы)"

	def calculate(
		self, df: pd.DataFrame, window: int = 2, **kwargs: Any
	) -> IndicatorResult:
		df = MARKET_DATA_SCHEMA.normalize_columns(df)

		high = df[MARKET_DATA_SCHEMA.HIGH_COLUMN]
		low = df[MARKET_DATA_SCHEMA.LOW_COLUMN]

		# Fractal High
		is_fractal_high = (
			high
			== high.rolling(window * 2 + 1, center=True, min_periods=window + 1).max()
		)

		# Fractal Low
		is_fractal_low = (
			low
			== low.rolling(window * 2 + 1, center=True, min_periods=window + 1).min()
		)

		latest_high = high.where(is_fractal_high).iloc[-1]
		latest_low = low.where(is_fractal_low).iloc[-1]

		return IndicatorResult(
			name=self.name,
			value={
				"fractal_high": float(latest_high) if pd.notna(latest_high) else None,
				"fractal_low": float(latest_low) if pd.notna(latest_low) else None,
			},
			metadata={"window": window},
		)


class SupportResistanceIndicator(BaseIndicator):
	name = "sr_levels"
	category = "levels"
	description = "Динамические уровни поддержки и сопротивления по касаниям"

	def calculate(
		self, df: pd.DataFrame, window: int = 120, **kwargs: Any
	) -> IndicatorResult:
		from .utils import rolling_support_resistance_zones  # вынесем позже

		zones = rolling_support_resistance_zones(
			df, window=window, min_touches=3, price_tolerance=0.003
		)

		return IndicatorResult(
			name=self.name,
			value={
				"support": (
					float(zones["support_level"].iloc[-1])
					if not pd.isna(zones["support_level"].iloc[-1])
					else None
				),
				"resistance": (
					float(zones["resistance_level"].iloc[-1])
					if not pd.isna(zones["resistance_level"].iloc[-1])
					else None
				),
				"touches_support": int(zones["touches_support"].iloc[-1]),
				"touches_resistance": int(zones["touches_resistance"].iloc[-1]),
			},
			metadata={"window": window},
		)


class PivotPointsIndicator(BaseIndicator):
	name = "pivot_points"
	category = "levels"
	description = "Classic Pivot Points (Daily/Weekly)"

	def calculate(
		self, df: pd.DataFrame, timeframe: str = "D", **kwargs: Any
	) -> IndicatorResult:
		pivots = calculate_classic_pivot_points(df, timeframe=timeframe)

		latest = pivots.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value={
				"pp": float(latest["pp"]) if pd.notna(latest["pp"]) else None,
				"r1": float(latest["r1"]) if pd.notna(latest["r1"]) else None,
				"s1": float(latest["s1"]) if pd.notna(latest["s1"]) else None,
				"r2": float(latest["r2"]) if pd.notna(latest["r2"]) else None,
				"s2": float(latest["s2"]) if pd.notna(latest["s2"]) else None,
			},
			metadata={"timeframe": timeframe},
		)


registry.register(FractalIndicator())
registry.register(SupportResistanceIndicator())
registry.register(PivotPointsIndicator())
