from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from swingtraderai.schemas.analysis import AnalysisBase, AnalysisOut


def test_analysis_base_empty():
	"""Проверяем, что модель создаётся без обязательных полей"""
	analysis = AnalysisBase()

	assert analysis.timeframe is None
	assert analysis.model is None
	assert analysis.trend is None
	assert analysis.confidence is None
	assert analysis.summary is None
	assert analysis.raw_llm_output is None
	assert analysis.indicators is None


def test_analysis_base_full():
	"""Проверяем корректную инициализацию всех полей"""
	data = {
		"timeframe": "1h",
		"model": "gpt-4",
		"trend": "bullish",
		"confidence": Decimal("0.87"),
		"summary": "Strong uptrend",
		"raw_llm_output": {"text": "buy signal"},
		"indicators": {"rsi": 65, "macd": "positive"},
	}

	analysis = AnalysisBase(**data)

	assert analysis.timeframe == "1h"
	assert analysis.model == "gpt-4"
	assert analysis.trend == "bullish"
	assert analysis.confidence == Decimal("0.87")
	assert analysis.summary == "Strong uptrend"
	assert analysis.raw_llm_output["text"] == "buy signal"
	assert analysis.indicators["rsi"] == 65


def test_analysis_out_valid():
	"""Проверяем расширенную модель с обязательными полями"""
	analysis = AnalysisOut(
		id=uuid4(),
		ticker_id=uuid4(),
		created_at=datetime(2025, 3, 20, 10, 30),
		timeframe="4h",
		model="gpt-4",
		trend="bearish",
		confidence=Decimal("0.42"),
	)

	assert analysis.id is not None
	assert analysis.ticker_id is not None
	assert analysis.created_at.year == 2025
	assert analysis.trend == "bearish"
	assert analysis.confidence == Decimal("0.42")


def test_analysis_out_inherits_base_fields():
	"""Проверяем, что AnalysisOut наследует поля AnalysisBase"""
	analysis = AnalysisOut(
		id=uuid4(),
		ticker_id=uuid4(),
		created_at=datetime.now(),
		summary="Test summary",
	)

	assert analysis.summary == "Test summary"
	assert analysis.timeframe is None  # унаследовано


def test_analysis_decimal_serialization():
	"""Проверяем, что Decimal корректно сериализуется"""
	analysis = AnalysisOut(
		id=uuid4(),
		ticker_id=uuid4(),
		created_at=datetime.now(),
		confidence=Decimal("0.1234"),
	)

	data = analysis.model_dump()

	assert data["confidence"] == Decimal("0.1234")


def test_analysis_dict_fields_mutable():
	"""Проверяем работу со словарями (частая точка багов)"""
	analysis = AnalysisBase(
		raw_llm_output={"a": 1},
		indicators={"rsi": 50},
	)

	analysis.raw_llm_output["b"] = 2

	assert analysis.raw_llm_output["b"] == 2
