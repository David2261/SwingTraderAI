import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()

	df.ta.sma(length=10, append=True)
	df.ta.sma(length=20, append=True)
	df.ta.sma(length=50, append=True)
	df.ta.ema(length=9, append=True)
	df.ta.rsi(length=14, append=True)

	df.ta.atr(length=14, append=True)
	atr_col = "ATRr_14"

	from swingtraderai.indicators.levels import add_key_levels_indicators

	df = add_key_levels_indicators(df, sr_window=100, pivot_tf="D")

	df["close_to_PP"] = (df["close"] - df["PP"]) / df[atr_col]
	df["dist_to_R1"] = (df["R1"] - df["close"]) / df[atr_col]
	df["dist_to_S1"] = (df["close"] - df["S1"]) / df[atr_col]

	last_f_high = df["fractal_high"].ffill()
	last_f_low = df["fractal_low"].ffill()
	df["dist_to_last_f_high"] = (last_f_high - df["close"]) / df[atr_col]
	df["dist_to_last_f_low"] = (df["close"] - last_f_low) / df[atr_col]

	for lag in [1, 3, 5]:
		df[f"return_{lag}"] = df["close"].pct_change(lag)
		df[f"rsi_lag_{lag}"] = df["RSI_14"].shift(lag)

	df = df.dropna(subset=["SMA_10", "RSI_14", atr_col])

	return df


def add_target(
	df: pd.DataFrame, horizon: int = 5, threshold: float = 0.008
) -> pd.DataFrame:
	"""
	Добавляет таргет только для обучения.
	В проде эта функция вызываться не будет.
	"""
	df = df.copy()
	df["future_return"] = df["close"].shift(-horizon) / df["close"] - 1
	df["target"] = (df["future_return"] > threshold).astype(int)

	return df.dropna(subset=["target"])


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Главная точка входа для препроцессинга
	"""
	df = engineer_features(df)
	return df
