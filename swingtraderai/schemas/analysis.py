from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnalysisBase(BaseModel):
	timeframe: Optional[str] = None
	model: Optional[str] = None
	trend: Optional[str] = None
	confidence: Optional[Decimal] = None
	summary: Optional[str] = None
	raw_llm_output: Optional[dict[str, Any]] = None
	indicators: Optional[dict[str, Any]] = None


class AnalysisOut(AnalysisBase):
	id: UUID
	ticker_id: UUID
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
