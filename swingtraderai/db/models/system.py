from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from swingtraderai.db.base import TenantBase

if TYPE_CHECKING:
	from swingtraderai.db.models.market import Ticker


class Notification(TenantBase):
	__tablename__ = "notifications"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid7
	)
	signal_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("signals.id")
	)
	channel: Mapped[str | None] = mapped_column(String(20))
	sent_to: Mapped[str | None] = mapped_column(String(100))
	status: Mapped[str | None] = mapped_column(String(15))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)


class Watchlist(TenantBase):
	__tablename__ = "watchlists"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid7
	)
	name: Mapped[str] = mapped_column(String(100), nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	owner_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
	)
	is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)
	items: Mapped[list["WatchlistItem"]] = relationship(
		"WatchlistItem",
		back_populates="watchlist",
		cascade="all, delete-orphan",
		lazy="selectin",
	)

	__table_args__ = (
		Index("ix_watchlists_owner_id", "owner_id"),
		Index("ix_watchlists_tenant_owner", "tenant_id", "owner_id"),
		Index("ix_watchlists_is_default", "is_default"),
	)


class WatchlistItem(TenantBase):
	__tablename__ = "watchlist_items"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid7
	)
	watchlist_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("watchlists.id")
	)
	ticker_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("tickers.id")
	)
	signal_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True), ForeignKey("signals.id"), nullable=True
	)
	notes: Mapped[str | None] = mapped_column(Text, nullable=True)
	reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

	target_price: Mapped[float | None] = mapped_column(Float, nullable=True)
	stop_loss: Mapped[float | None] = mapped_column(Float, nullable=True)

	last_signal_at: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)

	watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")
	ticker: Mapped["Ticker"] = relationship("Ticker")
