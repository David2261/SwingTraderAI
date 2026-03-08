from datetime import datetime
from typing import Optional

import ccxt
import pandas as pd

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
			ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
		)
		df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
		return df
