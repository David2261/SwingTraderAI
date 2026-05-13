from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IndicatorValue(BaseModel):
	value: Optional[float]
	signal: Optional[Literal["bullish", "bearish", "neutral"]] = None
	regime: Optional[str] = None
	metadata: Dict[str, Any] = Field(default_factory=dict)


class TechnicalIndicatorsOut(BaseModel):
	ticker_id: UUID
	symbol: str
	timeframe: str
	timestamp: datetime
	current_price: float

	indicators: Dict[str, IndicatorValue] = Field(default_factory=dict)
	summary: Dict[str, Any] = Field(default_factory=dict)
	signals: List[Dict[str, Any]] = Field(default_factory=list)

	model_config = ConfigDict(from_attributes=True)


class IndicatorRequest(BaseModel):
	indicators: List[str] = Field(
		default=["ema20", "ema50", "rsi", "macd", "bbands", "atr"],
		description="Список запрашиваемых индикаторов",
	)
	timeframe: str = "1h"
	limit: int = Field(500, ge=100, le=2000)


class SignalOut(BaseModel):
	type: Literal["STRONG_BUY", "BUY", "NEUTRAL", "SELL", "STRONG_SELL"]
	strength: int = Field(..., ge=1, le=10)
	message: str
	indicators_used: List[str]
