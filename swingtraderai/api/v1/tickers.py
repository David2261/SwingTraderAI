from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.db.models.ticker import Ticker
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.ticker import TickerCreate, TickerOut

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
