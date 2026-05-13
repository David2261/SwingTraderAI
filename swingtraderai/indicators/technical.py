from typing import Any, Optional

import pandas as pd
import pandas_ta as pdt

from .base import BaseIndicator, IndicatorResult
from .registry import registry


class EMAIndicator(BaseIndicator):
	category = "trend"
	description = "Exponential Moving Average"

	def __init__(self, name: str = "ema20", length: int = 20) -> None:
		self.name = name
		self.length = length
		self.category = "trend"
		self.description = f"Exponential Moving Average {length}"

	def calculate(
		self, df: pd.DataFrame, length: Optional[int] = None, **kwargs: Any
	) -> IndicatorResult:
		if length is None:
			length = kwargs.get("length", self.length)
		else:
			length = kwargs.get("length", length)

		if df.empty or len(df) < length or "close" not in df.columns:
			return IndicatorResult(
				name=self.name,
				value=None,
				metadata={"length": length, "error": "insufficient_data"},
			)

		ema = pdt.ema(df["close"], length=length)
		latest = ema.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest) if not pd.isna(latest) else None,
			metadata={"length": length},
		)


class WMAIndicator(BaseIndicator):
	category = "trend"
	description = "Weighted Moving Average (Взвешенная скользящая средняя)"

	def __init__(self, name: str = "wma20", length: int = 20) -> None:
		self.name = name
		self.length = length
		self.description = f"Weighted Moving Average {length}"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		length = kwargs.get("length", self.length)

		if df.empty or len(df) < length or "close" not in df.columns:
			return IndicatorResult(name=self.name, value=None)

		wma_series = pdt.wma(df["close"], length=length)
		latest = wma_series.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest) if pd.notna(latest) else None,
			metadata={"length": length},
		)


class VWAPIndicator(BaseIndicator):
	name = "vwap"
	category = "volume"
	description = "Volume Weighted Average Price (Очень важен для интрадей)"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		"""
		Стандартный VWAP за весь период данных.
		Для реального intraday лучше делать reset по сессиям.
		"""
		if df.empty or "volume" not in df.columns:
			return IndicatorResult(name=self.name, value=None)

		# Typical Price = (H + L + C) / 3
		typical_price = (df.high + df.low + df.close) / 3

		# Cumulative TP * Volume
		tpv = typical_price * df.volume
		cumulative_tpv = tpv.cumsum()
		cumulative_volume = df.volume.cumsum()

		vwap_series = cumulative_tpv / cumulative_volume
		latest_vwap = vwap_series.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest_vwap) if not pd.isna(latest_vwap) else None,
			metadata={"period": "full", "note": "Standard cumulative VWAP"},
		)


class SessionVWAPIndicator(BaseIndicator):
	name = "vwap_session"
	category = "volume"
	description = "VWAP с сбросом по дням (лучше для интрадей)"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		if df.empty or "volume" not in df.columns or "time" not in df.columns:
			return IndicatorResult(name=self.name, value=None)

		df = df.copy()
		df["date"] = pd.to_datetime(df["time"]).dt.date

		typical_price = (df["high"] + df["low"] + df["close"]) / 3
		df["tpv"] = typical_price * df["volume"]

		df["cum_tpv"] = df.groupby("date")["tpv"].cumsum()
		df["cum_vol"] = df.groupby("date")["volume"].cumsum()
		df["vwap"] = df["cum_tpv"] / df["cum_vol"]

		latest = df["vwap"].iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest) if pd.notna(latest) else None,
			metadata={"type": "session_vwap"},
		)


registry.register(EMAIndicator())
registry.register(EMAIndicator("ema9", 9))
registry.register(EMAIndicator("ema20", 20))
registry.register(EMAIndicator("ema50", 50))
registry.register(EMAIndicator("ema200", 200))

registry.register(WMAIndicator())
registry.register(WMAIndicator(name="wma10", length=10))
registry.register(WMAIndicator(name="wma20", length=20))
registry.register(WMAIndicator(name="wma50", length=50))

registry.register(VWAPIndicator())
registry.register(SessionVWAPIndicator())
