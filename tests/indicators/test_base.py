from typing import Any

import pandas as pd
import pytest

from swingtraderai.indicators.base import BaseIndicator, IndicatorResult


def test_indicator_result_creation():
	result = IndicatorResult(
		name="rsi",
		value=67.5,
		signal="bullish",
		regime="BULLISH",
		metadata={"length": 14},
	)

	assert result.name == "rsi"
	assert result.value == 67.5
	assert result.signal == "bullish"
	assert result.regime == "BULLISH"
	assert result.metadata["length"] == 14


def test_indicator_result_default_values():
	result = IndicatorResult(name="test", value=42.0)

	assert result.signal is None
	assert result.regime is None
	assert result.metadata == {}


def test_indicator_result_from_dict():
	data = {
		"name": "macd",
		"value": {"macd": 1.23, "signal": 0.89},
		"signal": "bullish",
	}
	result = IndicatorResult(**data)

	assert result.name == "macd"
	assert isinstance(result.value, dict)
	assert result.signal == "bullish"


class DummyIndicator(BaseIndicator):
	"""Тестовый индикатор"""

	name = "dummy"
	category = "test"

	def calculate(self, df: pd.DataFrame, **kwargs: Any):
		return IndicatorResult(name=self.name, value=42.0, signal="neutral")


def test_base_indicator_abstract():
	with pytest.raises(TypeError):
		BaseIndicator()


def test_dummy_indicator_implementation():
	indicator = DummyIndicator()

	assert indicator.name == "dummy"
	assert indicator.category == "test"
	assert indicator.description == ""
	assert callable(indicator.calculate)
	assert callable(indicator.interpret)


def test_dummy_indicator_calculate(sample_ohlcv):
	indicator = DummyIndicator()
	result = indicator.calculate(sample_ohlcv)

	assert isinstance(result, IndicatorResult)
	assert result.name == "dummy"
	assert result.value == 42.0
	assert result.signal == "neutral"


def test_indicator_interpret_default():
	indicator = DummyIndicator()
	interpretation = indicator.interpret(value=75.0)

	assert isinstance(interpretation, dict)
	assert interpretation["signal"] == "neutral"
	assert interpretation["regime"] is None


class CustomInterpretIndicator(BaseIndicator):
	name = "custom"
	category = "test"

	def calculate(self, df: pd.DataFrame, **kwargs):
		return IndicatorResult(name=self.name, value=85.0)

	def interpret(self, value: Any, **kwargs):
		if value > 70:
			return {"signal": "bullish", "regime": "OVERBOUGHT"}
		return {"signal": "neutral", "regime": None}


def test_custom_interpret():
	indicator = CustomInterpretIndicator()
	result = indicator.calculate(pd.DataFrame())
	interpretation = indicator.interpret(result.value)

	assert interpretation["signal"] == "bullish"
	assert interpretation["regime"] == "OVERBOUGHT"


def test_indicator_with_custom_params():
	class ParamIndicator(BaseIndicator):
		name = "param_test"
		category = "test"
		default_params = {"length": 14, "multiplier": 2.0}

		def calculate(self, df: pd.DataFrame, **kwargs):
			length = kwargs.get("length", self.default_params["length"])
			return IndicatorResult(name=self.name, value=length)

	indicator = ParamIndicator()
	result = indicator.calculate(pd.DataFrame(), length=21)

	assert result.value == 21
