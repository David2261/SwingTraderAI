from typing import Dict, List, Optional

from .base import BaseIndicator


class IndicatorRegistry:
	_indicators: Dict[str, BaseIndicator] = {}
	_categories: Dict[str, List[str]] = {}

	@classmethod
	def register(cls, indicator: BaseIndicator) -> None:
		cls._indicators[indicator.name.lower()] = indicator

		if indicator.category not in cls._categories:
			cls._categories[indicator.category] = []
		cls._categories[indicator.category].append(indicator.name)

	@classmethod
	def get(cls, name: str) -> Optional[BaseIndicator]:
		return cls._indicators.get(name.lower())

	@classmethod
	def get_by_category(cls, category: str) -> List[BaseIndicator]:
		names = cls._categories.get(category, [])
		return [cls._indicators[name.lower()] for name in names]

	@classmethod
	def list_all(cls) -> List[str]:
		return list(cls._indicators.keys())

	@classmethod
	def list_categories(cls) -> List[str]:
		return list(cls._categories.keys())


registry = IndicatorRegistry()
