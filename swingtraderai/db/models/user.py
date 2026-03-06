from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import TIMESTAMP, Boolean, Enum, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from swingtraderai.db.base import Base


class UserRole(str, PyEnum):
	USER = "user"
	TESTER = "tester"
	SUPPORT = "support"
	ADMIN = "admin"


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	username: Mapped[str] = mapped_column(
		String(50), unique=True, nullable=False, index=True
	)
	email: Mapped[str] = mapped_column(
		String(255), unique=True, nullable=False, index=True
	)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	telegram_id: Mapped[str | None] = mapped_column(
		String(50), unique=True, nullable=True, index=True
	)
	telegram_verified: Mapped[bool] = mapped_column(
		Boolean, default=False, nullable=False
	)
	is_active: Mapped[bool] = mapped_column(
		Boolean, default=True, server_default=text("true"), nullable=False
	)
	is_banned: Mapped[bool] = mapped_column(
		Boolean, server_default=text("false"), nullable=False
	)
	ban_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
	banned_until: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)
	role: Mapped[UserRole] = mapped_column(
		Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
		default=UserRole.USER,
		nullable=False,
		index=True,
	)
	is_superuser: Mapped[bool] = mapped_column(
		Boolean, default=False, server_default=text("false"), nullable=False
	)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		server_default=func.now(),
		nullable=False,
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		server_default=func.now(),
		nullable=False,
	)
	last_login: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)
	password_changed_at: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)
	failed_login_attempts: Mapped[int] = mapped_column(
		Integer, server_default=text("0"), nullable=False
	)
	locked_until: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)
	signals_received_count: Mapped[int] = mapped_column(
		Integer, server_default=text("0"), nullable=False
	)
	api_request_count_last_hour: Mapped[int] = mapped_column(
		Integer, server_default=text("0"), nullable=False
	)
	last_api_request_at: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)

	# Индексы для частых запросов
	__table_args__ = (
		Index("ix_users_role", "role"),
		Index("ix_users_is_banned", "is_banned"),
	)
