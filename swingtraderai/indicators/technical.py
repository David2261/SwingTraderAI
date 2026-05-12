from typing import Any

import pandas as pd
import pandas_ta as pdt

from .base import BaseIndicator, IndicatorResult
from .registry import registry


class EMAIndicator(BaseIndicator):
	def __init__(self, name: str = "ema20", length: int = 20):
		self.name = name
		self.length = length
		self.category = "trend"
		self.description = f"Exponential Moving Average {length}"

	def calculate(
		self, df: pd.DataFrame, length: int = 20, **kwargs: Any
	) -> IndicatorResult:
		length = kwargs.get("length", self.length)
		ema = pdt.ema(df["close"], length=length)
		latest = ema.iloc[-1]

		return IndicatorResult(
			name=self.name,
			value=float(latest) if not pd.isna(latest) else None,
		)


registry.register(EMAIndicator())
registry.register(EMAIndicator(name="ema50", length=50))
