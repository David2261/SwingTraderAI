from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from swingtraderai.schemas.signal import SignalBase, SignalOut


def test_signal_base_empty():
	"""Проверяем создание пустой модели"""
	signal = SignalBase()

	assert signal.signal_type is None
	assert signal.strength is None
	assert signal.entry_price is None
	assert signal.stop_loss is None
	assert signal.take_profit is None
	assert signal.status is None
	assert signal.reason is None


def test_signal_base_full():
	"""Проверяем заполнение всех полей"""
	signal = SignalBase(
		signal_type="buy",
		strength=Decimal("0.85"),
		entry_price=Decimal("250.50"),
		stop_loss=Decimal("240.00"),
		take_profit=Decimal("280.00"),
		status="active",
		reason="Breakout confirmed",
	)

	assert signal.signal_type == "buy"
	assert signal.strength == Decimal("0.85")
	assert signal.entry_price == Decimal("250.50")
	assert signal.stop_loss == Decimal("240.00")
	assert signal.take_profit == Decimal("280.00")
	assert signal.status == "active"
	assert signal.reason == "Breakout confirmed"


def test_signal_out_valid():
	"""Проверяем расширенную модель"""
	signal = SignalOut(
		id=uuid4(),
		analysis_id=uuid4(),
		ticker_id=uuid4(),
		created_at=datetime(2025, 3, 20, 10, 30),
		signal_type="sell",
		strength=Decimal("0.45"),
	)

	assert signal.id is not None
	assert signal.analysis_id is not None
	assert signal.ticker_id is not None
	assert signal.created_at.year == 2025
	assert signal.signal_type == "sell"
	assert signal.strength == Decimal("0.45")


def test_signal_out_inherits_base_fields():
	"""Проверяем наследование полей"""
	signal = SignalOut(
		id=uuid4(),
		analysis_id=uuid4(),
		ticker_id=uuid4(),
		created_at=datetime.now(),
		reason="Test reason",
	)

	assert signal.reason == "Test reason"
	assert signal.signal_type is None  # унаследовано


def test_signal_decimal_fields():
	"""Проверяем работу Decimal"""
	signal = SignalBase(
		strength=Decimal("0.123"),
		entry_price=Decimal("100.50"),
	)

	assert isinstance(signal.strength, Decimal)
	assert isinstance(signal.entry_price, Decimal)


def test_signal_model_dump():
	"""Проверяем сериализацию"""
	signal = SignalOut(
		id=uuid4(),
		analysis_id=uuid4(),
		ticker_id=uuid4(),
		created_at=datetime.now(),
		strength=Decimal("0.99"),
	)

	data = signal.model_dump()

	assert data["strength"] == Decimal("0.99")
	assert "id" in data
	assert "analysis_id" in data
	assert "ticker_id" in data
