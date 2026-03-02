from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SignalBase(BaseModel):
	signal_type: Optional[str] = None
	strength: Optional[Decimal] = None
	entry_price: Optional[Decimal] = None
	stop_loss: Optional[Decimal] = None
	take_profit: Optional[Decimal] = None
	status: Optional[str] = None
	reason: Optional[str] = None


class SignalOut(SignalBase):
	id: UUID
	analysis_id: UUID
	ticker_id: UUID
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
