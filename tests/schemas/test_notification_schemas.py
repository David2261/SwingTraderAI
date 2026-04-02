from datetime import datetime
from uuid import uuid4

from swingtraderai.schemas.notification import NotificationBase, NotificationOut


def test_notification_base_empty():
	"""Проверяем создание пустой модели"""
	notification = NotificationBase()

	assert notification.channel is None
	assert notification.sent_to is None
	assert notification.status is None


def test_notification_base_full():
	"""Проверяем заполнение всех полей"""
	notification = NotificationBase(
		channel="email",
		sent_to="user@example.com",
		status="sent",
	)

	assert notification.channel == "email"
	assert notification.sent_to == "user@example.com"
	assert notification.status == "sent"


def test_notification_out_valid():
	"""Проверяем расширенную модель"""
	notification = NotificationOut(
		id=uuid4(),
		signal_id=uuid4(),
		created_at=datetime(2025, 3, 20, 10, 30),
		channel="telegram",
		sent_to="@trader",
		status="delivered",
	)

	assert notification.id is not None
	assert notification.signal_id is not None
	assert notification.created_at.year == 2025
	assert notification.channel == "telegram"
	assert notification.status == "delivered"


def test_notification_out_inherits_base_fields():
	"""Проверяем наследование полей"""
	notification = NotificationOut(
		id=uuid4(),
		signal_id=uuid4(),
		created_at=datetime.now(),
		channel="sms",
	)

	assert notification.channel == "sms"
	assert notification.sent_to is None  # унаследовано


def test_notification_model_dump():
	"""Проверяем сериализацию"""
	notification = NotificationOut(
		id=uuid4(),
		signal_id=uuid4(),
		created_at=datetime.now(),
		status="queued",
	)

	data = notification.model_dump()

	assert "id" in data
	assert "signal_id" in data
	assert "created_at" in data
	assert data["status"] == "queued"
