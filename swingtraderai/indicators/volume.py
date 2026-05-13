from typing import Any

import pandas as pd
import pandas_ta as pdt

from .base import BaseIndicator, IndicatorResult
from .registry import registry

MIN_ROWS = 20


class BollingerBandsIndicator(BaseIndicator):
	name = "bbands"
	category = "volatility"
	description = "Bollinger Bands (20, 2)"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		if df.empty or "close" not in df.columns:
			return IndicatorResult(name=self.name, value=None)

		if len(df) < MIN_ROWS:
			return IndicatorResult(
				name=self.name,
				value=None,
				metadata={
					"error": "insufficient_data",
					"required_rows": MIN_ROWS,
					"available_rows": len(df),
				},
			)

		bb = pdt.bbands(close=df["close"], length=20, std=2)

		if bb is None or bb.empty:
			return IndicatorResult(
				name=self.name, value=None, metadata={"error": "calculation_failed"}
			)

		latest = bb.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value={
				"upper": (
					float(latest["BBU_20_2.0"])
					if pd.notna(latest.get("BBU_20_2.0"))
					else None
				),
				"middle": (
					float(latest["BBM_20_2.0"])
					if pd.notna(latest.get("BBM_20_2.0"))
					else None
				),
				"lower": (
					float(latest["BBL_20_2.0"])
					if pd.notna(latest.get("BBL_20_2.0"))
					else None
				),
				"bandwidth": (
					float(latest["BBB_20_2.0"])
					if pd.notna(latest.get("BBB_20_2.0"))
					else None
				),
			},
			metadata={"length": 20, "std": 2},
		)


class ATRIndicator(BaseIndicator):
	name = "atr"
	category = "volatility"
	description = "Average True Range"

	def __init__(self, name: str = "atr", length: int = 14):
		self.name = name
		self.length = length
		self.category = "volatility"
		self.description = f"Average True Range ({length})"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		length = kwargs.get("length", self.length)

		if (
			df.empty
			or len(df) < length
			or not all(col in df.columns for col in ["high", "low", "close"])
		):
			return IndicatorResult(name=self.name, value=None)

		atr = pdt.atr(df["high"], df["low"], df["close"], length=length)
		latest = atr.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest) if pd.notna(latest) else None,
			metadata={"length": length},
		)


class DonchianChannelsIndicator(BaseIndicator):
	name = "donchian"
	category = "volatility"
	description = "Donchian Channels"

	def calculate(
		self, df: pd.DataFrame, length: int = 20, **kwargs: Any
	) -> IndicatorResult:
		if (
			df.empty
			or len(df) < length
			or not all(col in df.columns for col in ["high", "low"])
		):
			return IndicatorResult(name=self.name, value=None)

		dc = pdt.donchian(
			df["high"], df["low"], lower_length=length, upper_length=length
		)
		latest = dc.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value={
				"upper": (
					float(latest.get("DCU_20_20"))
					if pd.notna(latest.get("DCU_20_20"))
					else None
				),
				"lower": (
					float(latest.get("DCL_20_20"))
					if pd.notna(latest.get("DCL_20_20"))
					else None
				),
				"middle": (
					float(latest.get("DCM_20_20"))
					if pd.notna(latest.get("DCM_20_20"))
					else None
				),
			},
			metadata={"length": length},
		)


class VolumeSMAIndicator(BaseIndicator):
	category = "volume"
	description = "Volume Simple Moving Average"

	def __init__(self, name: str = "volume_sma", length: int = 14):
		self.name = name
		self.length = length
		self.category = "volume"
		self.description = f"Volume Simple Moving Average ({length})"

	def calculate(
		self, df: pd.DataFrame, length: int = 20, **kwargs: Any
	) -> IndicatorResult:
		if df.empty or "volume" not in df.columns:
			return IndicatorResult(name=self.name, value=None)

		sma = pdt.sma(df["volume"], length=length)
		latest = sma.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest) if pd.notna(latest) else None,
			metadata={"length": length},
		)


class OBVIndicator(BaseIndicator):
	name = "obv"
	category = "volume"
	description = "On-Balance Volume"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		if df.empty or not all(col in df.columns for col in ["close", "volume"]):
			return IndicatorResult(name=self.name, value=None)

		obv = pdt.obv(df["close"], df["volume"])
		latest = obv.iloc[-1]

		return IndicatorResult(
			name=self.name, value=float(latest) if pd.notna(latest) else None
		)


class ADIndicator(BaseIndicator):
	name = "ad"
	category = "volume"
	description = "Accumulation / Distribution Line"

	def calculate(self, df: pd.DataFrame, **kwargs: Any) -> IndicatorResult:
		if df.empty or not all(
			col in df.columns for col in ["high", "low", "close", "volume"]
		):
			return IndicatorResult(name=self.name, value=None)

		ad = pdt.ad(df["high"], df["low"], df["close"], df["volume"])
		latest = ad.iloc[-1]

		return IndicatorResult(
			name=self.name, value=float(latest) if pd.notna(latest) else None
		)


registry.register(BollingerBandsIndicator())
registry.register(ATRIndicator())
registry.register(ATRIndicator(name="atr10", length=10))
registry.register(ATRIndicator(name="atr20", length=20))

registry.register(DonchianChannelsIndicator())

registry.register(VolumeSMAIndicator())
registry.register(VolumeSMAIndicator(name="volume_sma10", length=10))
registry.register(VolumeSMAIndicator(name="volume_sma20", length=20))

registry.register(OBVIndicator())
registry.register(ADIndicator())
