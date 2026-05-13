import numpy as np
import pandas as pd

from swingtraderai.indicators.levels import add_key_levels_indicators
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Основная функция инженерии признаков.
	Добавляет технические индикаторы + уровни + производные фичи.
	"""
	df = df.copy()
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)

	try:
		df.ta.sma(length=10, append=True)
		df.ta.sma(length=20, append=True)
		df.ta.sma(length=50, append=True)
		df.ta.ema(length=9, append=True)
		df.ta.ema(length=21, append=True)
		df.ta.rsi(length=14, append=True)
		df.ta.atr(length=14, append=True)
		df.ta.macd(append=True)
		df.ta.bbands(length=20, append=True)
	except Exception as e:
		raise RuntimeError(f"Ошибка при расчёте индикаторов pandas_ta: {e}") from e

	df = add_key_levels_indicators(df, fractal_window=2, sr_window=100, pivot_tf="D")

	close_col = MARKET_DATA_SCHEMA.CLOSE_COLUMN

	# ATR
	atr_cols = [col for col in df.columns if col.lower().startswith("atr")]
	if not atr_cols:
		raise ValueError(f"ATR колонка не найдена. Доступные: {list(df.columns)}")
	atr_col = atr_cols[0]

	# RSI
	rsi_cols = [col for col in df.columns if "rsi_14" in col.lower()]
	if not rsi_cols:
		raise ValueError(f"RSI_14 колонка не найдена. Доступные: {list(df.columns)}")
	rsi_col = rsi_cols[0]

	# EMA9 и EMA21
	ema9_col = next((col for col in df.columns if col.lower() == "ema_9"), None)
	ema21_col = next((col for col in df.columns if col.lower() == "ema_21"), None)

	# Производные признаки
	df["close_to_pp"] = (df[close_col] - df["pp"]) / df[atr_col]
	df["dist_to_r1"] = (df.get("r1", pd.Series([np.nan])) - df[close_col]) / df[atr_col]
	df["dist_to_s1"] = (df[close_col] - df.get("s1", pd.Series([np.nan]))) / df[atr_col]

	# Расстояние до фракталов
	df["dist_to_last_fractal_high"] = (df["fractal_high"].ffill() - df[close_col]) / df[
		atr_col
	]
	df["dist_to_last_fractal_low"] = (df[close_col] - df["fractal_low"].ffill()) / df[
		atr_col
	]

	# Лаги
	for lag in [1, 2, 3, 5]:
		df[f"return_{lag}"] = df[close_col].pct_change(lag)
		df[f"rsi_lag_{lag}"] = df[rsi_col].shift(lag)

	# Бинарные признаки (с защитой)
	if ema9_col:
		df["price_above_ema9"] = (df[close_col] > df[ema9_col]).astype(int)
	if ema21_col:
		df["price_above_ema21"] = (df[close_col] > df[ema21_col]).astype(int)

	df["rsi_overbought"] = (df[rsi_col] > 70).astype(int)
	df["rsi_oversold"] = (df[rsi_col] < 30).astype(int)

	# Удаляем NaN
	critical_cols = ["pp", "fractal_high", "fractal_low"]
	for col in critical_cols:
		if col in df.columns:
			df[col] = df[col].ffill()

	return df


def add_target(
	df: pd.DataFrame, horizon: int = 5, threshold: float = 0.008
) -> pd.DataFrame:
	"""Добавляет целевую переменную для обучения"""
	df = df.copy()
	close_col = MARKET_DATA_SCHEMA.CLOSE_COLUMN

	df["future_return"] = df[close_col].shift(-horizon) / df[close_col] - 1
	df["target"] = (df["future_return"] > threshold).astype(int)

	return df.dropna(subset=["target"])


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
	"""Главная точка входа"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)

	df = engineer_features(df)
	df = MARKET_DATA_SCHEMA.normalize_columns(df)

	return df
