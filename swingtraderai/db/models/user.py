from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from swingtraderai.db.base import Base


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
	is_active: Mapped[bool] = mapped_column(
		Boolean, default=True, server_default=text("true"), nullable=False
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
