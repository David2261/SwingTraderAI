import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.models.market import Ticker
from swingtraderai.db.models.user import Position, User, UserRole


@pytest.mark.asyncio
async def test_user_model_default_values(session: AsyncSession):
	"""Проверяем значения по умолчанию при создании пользователя"""
	user = User(
		username="testuser",
		email="test@example.com",
		password_hash="fakehash123",
	)

	session.add(user)
	await session.commit()
	await session.refresh(user)

	assert user.id is not None
	assert user.username == "testuser"
	assert user.email == "test@example.com"
	assert user.password_hash == "fakehash123"

	assert user.role == UserRole.USER
	assert user.is_active is True
	assert user.is_banned is False
	assert user.is_superuser is False
	assert user.telegram_verified is False
	assert user.failed_login_attempts == 0
	assert user.signals_received_count == 0
	assert user.api_request_count_last_hour == 0

	assert isinstance(user.created_at, datetime)
	assert user.created_at.tzinfo == timezone.utc

	assert isinstance(user.updated_at, datetime)
	assert user.updated_at.tzinfo == timezone.utc
	assert abs(user.updated_at - user.created_at) < timedelta(seconds=1)

	assert user.telegram_id is None
	assert user.ban_reason is None
	assert user.banned_until is None
	assert user.last_login is None
	assert user.password_changed_at is None
	assert user.locked_until is None
	assert user.last_api_request_at is None


@pytest.mark.asyncio
async def test_user_role_enum(session: AsyncSession):
	"""Проверяем работу Enum и допустимые значения"""
	user = User(
		username="enumtest",
		email="enum@test.com",
		password_hash="hash",
		role=UserRole.ADMIN,
	)

	session.add(user)
	await session.commit()
	await session.refresh(user)

	assert user.role == UserRole.ADMIN
	assert user.role.value == "admin"

	for role in UserRole:
		user.role = role
		assert user.role == role


@pytest.mark.asyncio
async def test_user_timestamps_onupdate(session: AsyncSession):
	"""Проверяем, что updated_at обновляется при изменении"""
	user = User(
		username="updatetest",
		email="update@example.com",
		password_hash="hash123",
	)
	session.add(user)
	await session.commit()
	await session.refresh(user)

	original_updated = user.updated_at

	await asyncio.sleep(0.01)
	user.username = "updatedname"
	await session.commit()
	await session.refresh(user)

	assert user.updated_at > original_updated


@pytest.mark.asyncio
async def test_user_ban_fields(session: AsyncSession):
	"""Пример заполнения полей бана"""
	until = datetime.now(timezone.utc) + timedelta(days=7)

	user = User(
		username="banneduser",
		email="ban@example.com",
		password_hash="hash",
		is_banned=True,
		ban_reason="Spamming signals",
		banned_until=until,
	)

	session.add(user)
	await session.commit()
	await session.refresh(user)

	assert user.is_banned is True
	assert user.ban_reason == "Spamming signals"
	assert user.banned_until == until


@pytest.mark.asyncio
async def test_create_minimal_user_and_query(session: AsyncSession):
	"""Просто создание + выборка по email (проверка индекса и unique)"""
	email = "minimal@exam.pl"

	user = User(
		username="minimal",
		email=email,
		password_hash="minimalhash",
	)
	session.add(user)
	await session.commit()

	stmt = select(User).where(User.email == email)
	result = await session.execute(stmt)
	found = result.scalar_one()

	assert found.id == user.id
	assert found.username == "minimal"


@pytest.mark.asyncio
async def test_telegram_id_nullable_and_unique_violation(session: AsyncSession):
	"""Проверяем nullable + попытку duplicate telegram_id"""
	user1 = User(
		username="tg1",
		email="tg1@example.com",
		password_hash="h1",
		telegram_id=123456789,
	)
	session.add(user1)
	await session.commit()

	user2 = User(
		username="tg2",
		email="tg2@example.com",
		password_hash="h2",
		telegram_id=123456789,
	)
	session.add(user2)

	with pytest.raises(IntegrityError):
		await session.commit()


@pytest.mark.asyncio
async def test_position_creation_long(
	session: AsyncSession, user: User, ticker: Ticker
):
	"""Простое создание long-позиции"""
	position = Position(
		user_id=user.id,
		ticker_id=ticker.id,
		position_type="long",
		quantity=Decimal("10.5"),
		average_buy_price=Decimal("300.75"),
		total_cost=Decimal("3157.875"),
		notes="Купил на просадке",
	)

	session.add(position)
	await session.commit()
	await session.refresh(position)

	assert position.id is not None
	assert position.user_id == user.id
	assert position.ticker_id == ticker.id
	assert position.position_type == "long"
	assert position.quantity == Decimal("10.5")
	assert position.average_buy_price == Decimal("300.75")
	assert position.total_cost == Decimal("3157.875")
	assert position.notes == "Купил на просадке"
	assert position.closed_at is None

	assert isinstance(position.opened_at, datetime)
	assert position.opened_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_position_creation_short(
	session: AsyncSession, user: User, ticker: Ticker
):
	"""Создание short-позиции"""
	position = Position(
		user_id=user.id,
		ticker_id=ticker.id,
		position_type="short",
		quantity=Decimal("5.0"),
		average_buy_price=Decimal("42000.0"),
		total_cost=Decimal("-210000.0"),
		notes="Шорт на хаях",
	)

	session.add(position)
	await session.commit()
	await session.refresh(position)

	assert position.position_type == "short"
	assert position.total_cost == Decimal("-210000.0")


@pytest.mark.asyncio
async def test_position_type_constraint_violation(
	session: AsyncSession, user: User, ticker: Ticker
):
	"""Попытка создать позицию с неверным position_type → IntegrityError"""
	position = Position(
		user_id=user.id,
		ticker_id=ticker.id,
		position_type="invalid",
		quantity=Decimal("1"),
		average_buy_price=Decimal("100"),
		total_cost=Decimal("100"),
	)

	session.add(position)

	with pytest.raises(IntegrityError) as exc_info:
		await session.commit()

	await session.rollback()

	assert (
		"valid_position_type" in str(exc_info.value)
		or "check constraint" in str(exc_info.value).lower()
	)


@pytest.mark.asyncio
async def test_position_different_types_allowed(
	session: AsyncSession, user: User, ticker: Ticker
):
	"""Long и short по одному тикеру — разрешено одновременно"""
	long_pos = Position(
		user_id=user.id,
		ticker_id=ticker.id,
		position_type="long",
		quantity=Decimal("10"),
		average_buy_price=Decimal("300"),
		total_cost=Decimal("3000"),
	)

	short_pos = Position(
		user_id=user.id,
		ticker_id=ticker.id,
		position_type="short",
		quantity=Decimal("5"),
		average_buy_price=Decimal("320"),
		total_cost=Decimal("-1600"),
	)

	session.add_all([long_pos, short_pos])
	await session.commit()

	result = await session.execute(
		select(Position).where(
			Position.user_id == user.id, Position.ticker_id == ticker.id
		)
	)
	positions = result.scalars().all()

	assert len(positions) == 2
	types = {p.position_type for p in positions}
	assert types == {"long", "short"}


@pytest.mark.asyncio
async def test_position_closed_at_optional(
	session: AsyncSession, user: User, ticker: Ticker
):
	"""closed_at может быть None (активная позиция)"""
	position = Position(
		user_id=user.id,
		ticker_id=ticker.id,
		position_type="long",
		quantity=Decimal("10"),
		average_buy_price=Decimal("300"),
		total_cost=Decimal("3000"),
	)

	session.add(position)
	await session.commit()
	await session.refresh(position)

	assert position.closed_at is None

	position.closed_at = datetime.now(timezone.utc)
	await session.commit()
	await session.refresh(position)

	assert position.closed_at is not None
