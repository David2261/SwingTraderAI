from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

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
			"1m": "1min",
			"5m": "5min",
			"15m": "15min",
			"30m": "30min",
			"1h": "1h",
			"4h": "4h",
			"1d": "1D",
		}
		interval = interval_map.get(timeframe)
		if not interval:
			raise ValueError(f"Unsupported timeframe: {timeframe}")

		now = datetime.now(timezone.utc)

		if since is None:
			since = now - timedelta(days=730)  # ~2 года
		elif since.tzinfo is None:
			since = since.replace(tzinfo=timezone.utc)

		if hasattr(ticker, "candles"):
			result = ticker.candles(start=since, end=now, period=interval)
		elif hasattr(ticker, "get_candles"):
			result = ticker.get_candles(from_date=since, to_date=now, interval=interval)
		else:
			raise AttributeError(f"Ticker object for {symbol} has no candle methods")

		if not isinstance(result, pd.DataFrame):
			if isinstance(result, Iterable) and not isinstance(result, (str, bytes)):
				df = pd.DataFrame(list(result))
			else:
				df = pd.DataFrame(result)
		else:
			df = result

		if df.empty:
			return pd.DataFrame()

		if limit and len(df) > limit:
			df = df.iloc[-limit:]

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
		if "timestamp" not in df.columns:
			for time_col in ["start", "datetime", "time"]:
				if time_col in df.columns:
					df = df.rename(columns={time_col: "timestamp"})
					break

		# Преобразуем timestamp и УБЕДИМСЯ что он timezone-aware
		if "timestamp" in df.columns:
			df["timestamp"] = pd.to_datetime(df["timestamp"])
			if df["timestamp"].dt.tz is None:
				df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
			elif df["timestamp"].dt.tz != timezone.utc:
				df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

		result_columns = ["timestamp", "open", "high", "low", "close", "volume"]
		existing_columns = [col for col in result_columns if col in df.columns]

		return df[existing_columns]
