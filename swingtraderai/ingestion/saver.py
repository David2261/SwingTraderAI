import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Tuple

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.models.market import Exchange, MarketData, Ticker


async def ensure_ticker(
	session: AsyncSession,
	symbol: str,
	asset_type: str = "stock",
	exchange_id: uuid.UUID | None = None,
	base_currency: str | None = None,
	quote_currency: str | None = None,
) -> uuid.UUID:
	"""
	Находит или создаёт запись тикера в базе и возвращает его UUID.
	"""
	stmt = select(Ticker.id).where(Ticker.symbol == symbol)
	result = await session.execute(stmt)
	ticker_id: uuid.UUID | None = result.scalar_one_or_none()

	if ticker_id is not None:
		return ticker_id

	new_ticker = Ticker(
		symbol=symbol,
		asset_type=asset_type,
		exchange_id=exchange_id,
		base_currency=base_currency,
		quote_currency=quote_currency,
	)

	session.add(new_ticker)
	await session.flush()

	return new_ticker.id


async def upsert_market_data_batch(
	session: AsyncSession,
	df: pd.DataFrame,
	source: str | None = None,
) -> Tuple[int, int]:
	"""
	Массовый upsert рыночных данных через PostgreSQL ON CONFLICT.
	"""
	if df.empty:
		return 0, 0

	current_exchange_id = None
	if source:
		ex_stmt = select(Exchange.id).where(Exchange.code == source.upper())
		ex_result = await session.execute(ex_stmt)
		current_exchange_id = ex_result.scalar_one_or_none()

	numeric_cols = ["open", "high", "low", "close", "volume"]
	for col in numeric_cols:
		if col in df.columns:
			df[col] = df[col].apply(lambda x: Decimal(str(x)) if pd.notna(x) else None)

	inserted_count = 0
	updated_count = 0

	for symbol, group_df in df.groupby("symbol", sort=False):
		ticker_id = await ensure_ticker(
			session=session,
			symbol=symbol,
			asset_type="stock" if source == "moex" else "crypto",
			exchange_id=current_exchange_id,
		)

		records: List[Dict[str, Any]] = []

		for _, row in group_df.iterrows():
			timestamp = row["timestamp"]
			if pd.api.types.is_datetime64_any_dtype(timestamp):
				timestamp = timestamp.to_pydatetime().replace(tzinfo=timezone.utc)
			elif isinstance(timestamp, pd.Timestamp):
				timestamp = timestamp.to_pydatetime().replace(tzinfo=timezone.utc)

			records.append(
				{
					"id": uuid.uuid4(),
					"ticker_id": ticker_id,
					"timeframe": str(row["timeframe"]),
					"timestamp": timestamp,
					"open": row.get("open"),
					"high": row.get("high"),
					"low": row.get("low"),
					"close": row.get("close"),
					"volume": row.get("volume"),
					"created_at": datetime.now(timezone.utc),
				}
			)

		if not records:
			continue

		stmt: Insert = pg_insert(MarketData)

		stmt = stmt.on_conflict_do_update(
			index_elements=["ticker_id", "timeframe", "timestamp"],
			set_={
				"open": stmt.excluded.open,
				"high": stmt.excluded.high,
				"low": stmt.excluded.low,
				"close": stmt.excluded.close,
				"volume": stmt.excluded.volume,
				"created_at": stmt.excluded.created_at,
			},
		)

		result = await session.execute(stmt, records)
		affected = getattr(result, "rowcount", 0) or 0
		updated_count += affected

	await session.flush()
	await session.commit()

	return inserted_count, updated_count
