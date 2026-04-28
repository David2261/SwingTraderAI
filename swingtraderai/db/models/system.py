import uuid
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from swingtraderai.db.base import TenantBase
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
	name: Mapped[str | None] = mapped_column(String(50))
	owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)
	items: Mapped[list["WatchlistItem"]] = relationship(
		"WatchlistItem",
		back_populates="watchlist",
		cascade="all, delete-orphan",
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
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)

	watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")
	ticker: Mapped["Ticker"] = relationship("Ticker")
