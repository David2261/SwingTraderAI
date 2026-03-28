import pandas as pd

from swingtraderai.indicators.levels import add_key_levels_indicators
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA

close = MARKET_DATA_SCHEMA.CLOSE_COLUMN


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()

	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)

	df.ta.sma(length=10, append=True)
	df.ta.sma(length=20, append=True)
	df.ta.sma(length=50, append=True)
	df.ta.ema(length=9, append=True)
	df.ta.rsi(length=14, append=True)
	df.ta.atr(length=14, append=True)

	atr_candidates = [c for c in df.columns if "atr" in c.lower()]
	rsi_candidates = [c for c in df.columns if "rsi_14" in c.lower()]

	if not atr_candidates:
		raise ValueError(
			f"ATR колонка не найдена. Доступные колонки: {list(df.columns)}"
		)
	if not rsi_candidates:
		raise ValueError(
			f"RSI_14 колонка не найдена. Доступные колонки: {list(df.columns)}"
		)

	atr_col = atr_candidates[0]
	rsi_col = rsi_candidates[0]

	df = add_key_levels_indicators(df, sr_window=100, pivot_tf="D")
	atr_candidates = [c for c in df.columns if "atr" in c.lower()]
	rsi_candidates = [c for c in df.columns if "rsi_14" in c.lower()]
	if not atr_candidates:
		raise ValueError(
			f"ATR колонка потерялась после add_key_levels_indicators.\
			Доступные: {list(df.columns)}"
		)
	if not rsi_candidates:
		raise ValueError(
			f"RSI_14 колонка не найдена. Доступные колонки: {list(df.columns)}"
		)

	atr_col = atr_candidates[0]
	rsi_col = rsi_candidates[0]

	df["close_to_pp"] = (df[close] - df["pp"]) / df[atr_col]
	df["dist_to_r1"] = (df["r1"] - df[close]) / df[atr_col]
	df["dist_to_s1"] = (df[close] - df["s1"]) / df[atr_col]

	last_f_high = df["fractal_high"].ffill()
	last_f_low = df["fractal_low"].ffill()

	df["dist_to_last_f_high"] = (last_f_high - df[close]) / df[atr_col]
	df["dist_to_last_f_low"] = (df[close] - last_f_low) / df[atr_col]

	for lag in [1, 3, 5]:
		df[f"return_{lag}"] = df[close].pct_change(lag)
		df[f"rsi_lag_{lag}"] = df[rsi_col].shift(lag)

	subset = list(MARKET_DATA_SCHEMA.REQUIRED_INDICATORS & set(df.columns))
	if subset:
		df = df.dropna(subset=subset)

	return df


def add_target(
	df: pd.DataFrame, horizon: int = 5, threshold: float = 0.008
) -> pd.DataFrame:
	"""
	Добавляет таргет только для обучения.
	В проде эта функция вызываться не будет.
	"""
	df = df.copy()
	df["future_return"] = df[close].shift(-horizon) / df[close] - 1
	df["target"] = (df["future_return"] > threshold).astype(int)

	return df.dropna(subset=["target"])


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Главная точка входа для препроцессинга
	"""
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)

	df = engineer_features(df)

	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	return df
