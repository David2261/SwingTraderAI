from datetime import datetime, timezone
from typing import Any, List
from uuid import UUID

import pandas as pd

from swingtraderai.indicators.registry import registry
from swingtraderai.schemas.indicators import IndicatorValue, TechnicalIndicatorsOut


class IndicatorService:
	def __init__(self, ticker_service: Any) -> None:
		self.ticker_service = ticker_service

	async def get_indicators(
		self,
		ticker_id: UUID,
		indicators: List[str],
		timeframe: str = "1h",
		limit: int = 500,
	) -> TechnicalIndicatorsOut:
		data = await self.ticker_service.get_historical_data(
			ticker_id=ticker_id, timeframe=timeframe, limit=limit
		)

		df = pd.DataFrame([d.model_dump() for d in data])

		result = {}
		for ind_name in indicators:
			indicator = registry.get(ind_name)
			if indicator:
				ind_result = indicator.calculate(df)
				if hasattr(ind_result, "model_dump"):
					result[ind_name] = IndicatorValue(**ind_result.model_dump())
				elif isinstance(ind_result, dict):
					result[ind_name] = IndicatorValue(**ind_result)
				else:
					result[ind_name] = IndicatorValue(value=None)

		timestamp: datetime
		current_price: float

		if not df.empty:
			last_time = df.iloc[-1].time
			if isinstance(last_time, datetime):
				timestamp = last_time
			else:
				timestamp = pd.to_datetime(last_time).to_pydatetime()

			last_close = df.iloc[-1].close
			if isinstance(last_close, (int, float)):
				current_price = float(last_close)
			else:
				current_price = 0.0
		else:
			timestamp = datetime.now(timezone.utc)
			current_price = 0.0

		symbol = "..."

		return TechnicalIndicatorsOut(
			ticker_id=ticker_id,
			symbol=symbol,
			timeframe=timeframe,
			timestamp=timestamp,
			current_price=current_price,
			indicators=result,
		)
