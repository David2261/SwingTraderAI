import uuid
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from swingtraderai.db.base import Base
from swingtraderai.db.models.market import Ticker


class Notification(Base):
	__tablename__ = "notifications"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
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


class Watchlist(Base):
	__tablename__ = "watchlists"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
	)
	name: Mapped[str | None] = mapped_column(String(50))
	owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)
	items: Mapped[list["WatchlistItem"]] = relationship(
		"WatchlistItem",
		back_populates="watchlist",
		cascade="all, delete-orphan",
	)


class WatchlistItem(Base):
	__tablename__ = "watchlist_items"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
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
