import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from swingtraderai.db.base import Base


class Ticker(Base):
	__tablename__ = "tickers"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
	)
	symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
	asset_type: Mapped[str] = mapped_column(String(10), nullable=False)
	exchange: Mapped[str | None] = mapped_column(String(20))
	base_currency: Mapped[str | None] = mapped_column(String(10))
	quote_currency: Mapped[str | None] = mapped_column(String(10))
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)


class MarketData(Base):
	__tablename__ = "market_data"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
	)
	ticker_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("tickers.id")
	)
	timeframe: Mapped[str | None] = mapped_column(String(10))
	timestamp: Mapped[datetime | None] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)
	open: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	high: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	low: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	close: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	volume: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)

	ticker = relationship("Ticker")

	__table_args__ = (Index("idx_market_data", "ticker_id", "timeframe", "timestamp"),)


class Analysis(Base):
	__tablename__ = "analyses"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
	)
	ticker_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("tickers.id")
	)
	timeframe: Mapped[str | None] = mapped_column(String(10))
	model: Mapped[str | None] = mapped_column(String(50))
	trend: Mapped[str | None] = mapped_column(String(10))
	confidence: Mapped[Optional[Decimal]] = mapped_column(Float)
	summary: Mapped[str | None] = mapped_column(Text)
	raw_llm_output = mapped_column(JSONB)
	indicators = mapped_column(JSONB)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)

	__table_args__ = (Index("idx_analyses", "ticker_id", "created_at"),)


class Signal(Base):
	__tablename__ = "signals"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
	)
	analysis_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("analyses.id")
	)
	ticker_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("tickers.id")
	)
	signal_type: Mapped[str | None] = mapped_column(String(10))
	strength: Mapped[Optional[Decimal]] = mapped_column(Float)
	entry_price: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	stop_loss: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	take_profit: Mapped[Optional[Decimal]] = mapped_column(NUMERIC)
	status: Mapped[str | None] = mapped_column(String(15))
	reason: Mapped[str | None] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
	)

	__table_args__ = (
		Index("idx_signals_ticker", "ticker_id", "created_at"),
		Index("idx_signals_status", "status"),
	)


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
		"WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan"
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

	watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")
	ticker: Mapped["Ticker"] = relationship("Ticker")
