from datetime import datetime
from typing import Optional

import ccxt
import pandas as pd

from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA

from .base import BaseSource


class CcxtSource(BaseSource):
	def __init__(self, exchange_name: str):
		self.exchange = getattr(ccxt, exchange_name)(
			{
				"enableRateLimit": True,
				"options": {"defaultType": "spot"},
			}
		)

	def fetch_ohlcv(
		self,
		symbol: str,
		timeframe: str,
		since: Optional[datetime] = None,
		limit: int = 1000,
	) -> pd.DataFrame:
		since_ms = int(since.timestamp() * 1000) if since else None

		ohlcv = self.exchange.fetch_ohlcv(
			symbol, timeframe, since=since_ms, limit=limit
		)
		if not ohlcv:
			return pd.DataFrame()

		df = pd.DataFrame(
			ohlcv,
			columns=[
				MARKET_DATA_SCHEMA.TIME_COLUMN,
				*MARKET_DATA_SCHEMA.BASE_COLUMNS[1:],
			],
		)
		df[MARKET_DATA_SCHEMA.TIME_COLUMN] = pd.to_datetime(
			df[MARKET_DATA_SCHEMA.TIME_COLUMN], unit="ms"
		)

		df["timeframe"] = timeframe

		df = MARKET_DATA_SCHEMA.normalize_columns(df)
		MARKET_DATA_SCHEMA.validate_base_columns(df)
		return df
