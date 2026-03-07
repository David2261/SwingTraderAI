import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import TIMESTAMP, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC, UUID
from sqlalchemy.orm import Mapped, mapped_column

from swingtraderai.db.base import Base


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
