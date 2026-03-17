from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

import pandas as pd
from moexalgo import Ticker

from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA

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

		time_col = MARKET_DATA_SCHEMA.TIME_COLUMN

		df = df.reset_index().rename(
			columns={
				"begin": time_col,
				"open": "open",
				"high": "high",
				"low": "low",
				"close": "close",
				"volume": "volume",
			}
		)
		if time_col not in df.columns:
			for col in ["start", "datetime", "time"]:
				if col in df.columns:
					df = df.rename(columns={col: time_col})
					break

		df[time_col] = pd.to_datetime(df[time_col])
		if df[time_col].dt.tz is None:
			df[time_col] = df[time_col].dt.tz_localize("UTC")
		else:
			df[time_col] = df[time_col].dt.tz_convert("UTC")

		df = MARKET_DATA_SCHEMA.normalize_columns(df)
		MARKET_DATA_SCHEMA.validate_base_columns(df)

		return df[MARKET_DATA_SCHEMA.BASE_COLUMNS]
