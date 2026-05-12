from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field


class IndicatorResult(BaseModel):
	"""Стандартизированный результат расчёта индикатора"""

	name: str
	value: Any
	signal: Optional[str] = None
	regime: Optional[str] = None
	metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseIndicator(ABC):
	"""Базовый класс для всех индикаторов"""

	name: str
	category: str
	description: str = ""
	default_params: Dict[str, Any] = {}

	@abstractmethod
	def calculate(
		self, df: pd.DataFrame, **kwargs: Any
	) -> Union[IndicatorResult, pd.Series, Dict[str, Any]]:
		"""Основной метод расчёта"""
		pass

	def interpret(self, value: Any, **kwargs: Any) -> Dict[str, Any]:
		"""Интерпретация значения (bullish/bearish и т.д.)"""
		return {"signal": "neutral", "regime": None}
