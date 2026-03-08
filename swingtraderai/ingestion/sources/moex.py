from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from moexalgo import Ticker

from .base import BaseSource


class MoexSource(BaseSource):
	"""Официальный клиент MOEX AlgoPack
	для получения исторических данных с Московской Биржи."""

	def fetch_ohlcv(
		self,
		symbol: str,
		timeframe: str,
		since: Optional[datetime] = None,
		limit: int = 5000,
	) -> pd.DataFrame:
		ticker = Ticker(symbol)

		interval_map = {
			"1m": 1,
			"5m": 5,
			"15m": 15,
			"30m": 30,
			"1h": 60,
			"4h": 240,
			"1d": "D",
		}
		interval = interval_map.get(timeframe)
		if not interval:
			raise ValueError(f"Unsupported timeframe: {timeframe}")

		if since is None:
			since = datetime.utcnow() - timedelta(days=730)  # ~2 года

		df = ticker.candles(
			date=since.date(),
			till=None,
			interval=interval,
			limit=limit,
		)

		if df.empty:
			return pd.DataFrame()

		df = df.reset_index().rename(
			columns={
				"begin": "timestamp",
				"open": "open",
				"high": "high",
				"low": "low",
				"close": "close",
				"volume": "volume",
			}
		)
		df["timestamp"] = pd.to_datetime(df["timestamp"])
		return df[["timestamp", "open", "high", "low", "close", "volume"]]
