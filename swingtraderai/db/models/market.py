import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import NUMERIC, UUID
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
	source: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
	ingested_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	ticker = relationship("Ticker")

	__table_args__ = (
		Index("idx_market_data", "ticker_id", "timeframe", "timestamp"),
		UniqueConstraint(
			"ticker_id", "timeframe", "timestamp", name="uq_market_data_time"
		),
	)
