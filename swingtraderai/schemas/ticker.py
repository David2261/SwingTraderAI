from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TickerBase(BaseModel):
	symbol: str = Field(..., max_length=20)
	asset_type: str = Field(..., max_length=10)
	exchange: Optional[str] = Field(None, max_length=20)
	base_currency: Optional[str] = Field(None, max_length=10)
	quote_currency: Optional[str] = Field(None, max_length=10)
	is_active: bool = True


class TickerCreate(TickerBase):
	pass


class TickerOut(TickerBase):
	id: UUID
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
