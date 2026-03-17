import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Tuple

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from swingtraderai.db.models.market import Exchange, MarketData, Ticker
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA


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
	df = MARKET_DATA_SCHEMA.normalize_columns(df)
	MARKET_DATA_SCHEMA.validate_base_columns(df)
	if df.empty:
		return 0, 0

	current_exchange_id = None
	if source:
		ex_stmt = select(Exchange.id).where(Exchange.code == source.upper())
		ex_result = await session.execute(ex_stmt)
		current_exchange_id = ex_result.scalar_one_or_none()

	missing = MARKET_DATA_SCHEMA.REQUIRED_INSERT_COLUMNS - set(df.columns)
	if missing:
		raise ValueError(f"Missing required columns: {missing}")

	for col in MARKET_DATA_SCHEMA.DECIMAL_COLUMNS:
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
			timestamp = row[MARKET_DATA_SCHEMA.TIME_COLUMN]
			if isinstance(timestamp, pd.Timestamp):
				timestamp = timestamp.to_pydatetime()

			if timestamp.tzinfo is None:
				timestamp = timestamp.replace(tzinfo=timezone.utc)
			else:
				timestamp = timestamp.astimezone(timezone.utc)

			records.append(
				{
					**{col: row.get(col) for col in MARKET_DATA_SCHEMA.BASE_COLUMNS},
					"timestamp": timestamp,
					"ticker_id": ticker_id,
					"timeframe": row.get("timeframe", None),
					"created_at": datetime.now(timezone.utc),
					"id": uuid7(),
				}
			)
			inserted_count += len(records)

		if not records:
			continue

		stmt: Insert = pg_insert(MarketData)

		stmt = stmt.on_conflict_do_update(
			index_elements=MARKET_DATA_SCHEMA.UNIQUE_CONSTRAINT_COLUMNS,
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

	inserted_count = inserted_count - updated_count

	await session.flush()
	await session.commit()

	return inserted_count, updated_count
