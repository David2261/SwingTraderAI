from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MarketDataBase(BaseModel):
	timeframe: Optional[str] = None
	open: Optional[Decimal] = None
	high: Optional[Decimal] = None
	low: Optional[Decimal] = None
	close: Optional[Decimal] = None
	volume: Optional[Decimal] = None


class MarketDataOut(MarketDataBase):
	id: UUID
	ticker_id: UUID
	timestamp: datetime
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
