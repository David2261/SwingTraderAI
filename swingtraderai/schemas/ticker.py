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


class OHLCVDataOut(BaseModel):
	timestamp: datetime
	open: Optional[float]
	high: Optional[float]
	low: Optional[float]
	close: Optional[float]
	volume: Optional[float]

	model_config = ConfigDict(from_attributes=True)


class TickerSearchOut(BaseModel):
	id: str
	symbol: str
	asset_type: str
	exchange: Optional[str]
	base_currency: Optional[str]
	quote_currency: Optional[str]

	model_config = ConfigDict(from_attributes=True)
