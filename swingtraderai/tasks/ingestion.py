import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal

import pandas as pd
from celery import Task, shared_task
from sqlalchemy import text

from swingtraderai.db.session import get_db
from swingtraderai.ingestion.saver import ensure_ticker, upsert_market_data_batch
from swingtraderai.ingestion.sources.base import BaseSource
from swingtraderai.ingestion.sources.binance import BinanceSource
from swingtraderai.ingestion.sources.bybit import BybitSource
from swingtraderai.ingestion.sources.moex import MoexSource

SupportedSource = Literal["moex", "binance", "bybit"]

SOURCES: dict[SupportedSource, type[BaseSource]] = {
	"moex": MoexSource,
	"binance": BinanceSource,
	"bybit": BybitSource,
}


async def _async_ingest_ohlcv(
	symbol: str,
	timeframe: str,
	source_name: SupportedSource,
	lookback_days: int = 30,
) -> Dict[str, Any]:
	"""
	Оптимизированная асинхронная загрузка.
	"""
	async with asynccontextmanager(get_db)() as session:
		ticker_id = await ensure_ticker(
			session=session,
			symbol=symbol,
			asset_type="stock" if source_name == "moex" else "crypto",
			exchange=source_name,
		)

		result = await session.execute(
			text(
				"""
				SELECT MAX(timestamp)
				FROM market_data
				WHERE ticker_id = :t_id
					AND timeframe = :tf
				"""
			),
			{"t_id": ticker_id, "tf": timeframe},
		)
		last_ts: datetime | None = result.scalar()

		if last_ts is not None:
			if last_ts.tzinfo is None:
				last_ts = last_ts.replace(tzinfo=timezone.utc)
			since = last_ts + timedelta(seconds=1)
		else:
			since = datetime.now(timezone.utc) - timedelta(days=lookback_days)

		source_class = SOURCES.get(source_name)
		if source_class is None:
			raise ValueError(f"Неизвестный источник: {source_name}")

		source: BaseSource = source_class()

		df: pd.DataFrame = source.fetch_ohlcv(
			symbol=symbol,
			timeframe=timeframe,
			since=since,
		)

		if df.empty:
			return {"status": "empty", "inserted": 0, "updated": 0, "total": 0}

		df["symbol"] = symbol
		df["timeframe"] = timeframe

		inserted, updated = await upsert_market_data_batch(
			session=session,
			df=df,
			source=source_name,
		)

	return {
		"status": "ok",
		"inserted": inserted,
		"updated": updated,
		"total": len(df),
	}


@shared_task(  # type: ignore
	name="ingestion.ingest_ohlcv",
	bind=True,
	max_retries=5,
	retry_backoff=True,
	retry_jitter=True,
	default_retry_delay=30,
)
def ingest_ohlcv(
	self: Task,
	symbol: str,
	timeframe: str,
	source: SupportedSource = "moex",
	lookback_days: int = 30,
) -> Dict[str, Any]:
	"""
	Синхронная обёртка над асинхронной задачей для Celery.
	"""
	try:
		return asyncio.run(
			_async_ingest_ohlcv(
				symbol=symbol,
				timeframe=timeframe,
				source_name=source,
				lookback_days=lookback_days,
			)
		)
	except Exception as exc:
		raise self.retry(exc=exc) from exc
