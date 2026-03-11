from datetime import datetime
from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from swingtraderai.api.deps import get_current_user
from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.ticker import (
	OHLCVDataOut,
	TickerCreate,
	TickerOut,
	TickerSearchOut,
)

router = APIRouter(prefix="/tickers", tags=["tickers"])


@router.post("/", response_model=TickerOut, status_code=201)
async def create_ticker(
	ticker_in: TickerCreate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> Ticker:
	existing = await db.execute(select(Ticker).where(Ticker.symbol == ticker_in.symbol))
	if existing.scalar_one_or_none():
		raise HTTPException(
			status_code=400, detail="Ticker with this symbol already exists"
		)

	ticker = Ticker(**ticker_in.model_dump())
	db.add(ticker)
	await db.commit()
	await db.refresh(ticker)
	return ticker


@router.get("/{ticker_id}", response_model=TickerOut)
async def get_ticker(ticker_id: str, db: AsyncSession = Depends(get_db)) -> Ticker:
	ticker = await db.get(Ticker, ticker_id)
	if not ticker:
		raise HTTPException(status_code=404, detail="Ticker not found")
	return ticker


@router.get("/", response_model=list[TickerOut])
async def list_tickers(
	skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> Sequence[TickerOut]:
	result = await db.execute(
		select(Ticker).offset(skip).limit(limit).order_by(Ticker.symbol)
	)
	tickers = result.scalars().all()
	return [TickerOut.from_orm(t) for t in tickers]


@router.get("/{ticker_id}/data", response_model=list[OHLCVDataOut])
async def get_ticker_historical_data(
	ticker_id: str,
	timeframe: str = Query("1d", description="Таймфрейм: 1m, 5m, 15m, 1h, 1d, 1w..."),
	limit: int = Query(500, ge=1, le=5000, description="Максимум свечей"),
	start_date: Optional[datetime] = Query(None, description="Начальная дата (ISO)"),
	end_date: Optional[datetime] = Query(None, description="Конечная дата (ISO)"),
	db: AsyncSession = Depends(get_db),
) -> List[OHLCVDataOut]:
	"""
	Возвращает исторические OHLCV данные для тикера.
	Идеально для построения графика или таблицы цен.
	"""
	ticker = await db.get(Ticker, ticker_id)
	if not ticker:
		raise HTTPException(status_code=404, detail="Ticker not found")

	stmt: Select[tuple[MarketData]] = (
		select(MarketData)
		.where(MarketData.ticker_id == ticker_id)
		.where(MarketData.timeframe == timeframe)
		.order_by(MarketData.timestamp.desc())
		.limit(limit)
	)

	if start_date:
		stmt = stmt.where(MarketData.timestamp >= start_date)
	if end_date:
		stmt = stmt.where(MarketData.timestamp <= end_date)

	result = await db.execute(stmt)
	data = result.scalars().all()

	if not data:
		return []

	return [OHLCVDataOut.model_validate(d) for d in data]


@router.get("/search", response_model=list[TickerSearchOut])
async def search_tickers(
	q: str = Query(
		..., min_length=1, description="Поиск по символу, названию или бирже"
	),
	limit: int = Query(20, ge=1, le=100),
	db: AsyncSession = Depends(get_db),
) -> List[TickerSearchOut]:
	"""
	Удобный поиск тикеров для добавления в watchlist.
	Ищет по символу, названию, бирже (LIKE %q%).
	"""
	search_term = f"%{q.lower()}%"

	stmt = (
		select(Ticker)
		.where(
			(Ticker.symbol.ilike(search_term))
			| (Ticker.asset_type.ilike(search_term))
			| (Ticker.exchange.ilike(search_term))
		)
		.order_by(Ticker.symbol)
		.limit(limit)
	)

	result = await db.execute(stmt)
	tickers = result.scalars().all()

	return [TickerSearchOut.model_validate(t) for t in tickers]


@router.post("/bulk", response_model=list[TickerOut], status_code=201)
async def bulk_create_tickers(
	tickers_in: List[TickerCreate],
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> List[TickerOut]:
	"""
	Массовое добавление или синхронизация тикеров.
	Если тикер с таким symbol уже существует — обновляет поля (кроме id).
	"""
	if len(tickers_in) > 500:
		raise HTTPException(
			status_code=400, detail="Too many tickers in bulk request (max 500)"
		)

	created_or_updated = []

	for ticker_in in tickers_in:
		stmt = select(Ticker).where(Ticker.symbol == ticker_in.symbol)
		result = await db.execute(stmt)
		existing = result.scalar_one_or_none()

		if existing:
			for key, value in ticker_in.model_dump(exclude_unset=True).items():
				setattr(existing, key, value)
			created_or_updated.append(existing)
		else:
			new_ticker = Ticker(**ticker_in.model_dump())
			db.add(new_ticker)
			created_or_updated.append(new_ticker)

	await db.commit()

	return [TickerOut.model_validate(t) for t in created_or_updated]
