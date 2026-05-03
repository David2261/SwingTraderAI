from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.ticker_repository import TickerRepository
from swingtraderai.db.models.market import Ticker
from swingtraderai.schemas.ticker import TickerCreate


class TickerService:
	def __init__(self, session: AsyncSession):
		self.repo = TickerRepository(session)

	async def create(self, ticker_in: TickerCreate) -> Ticker:
		existing = await self.repo.get_by_symbol(ticker_in.symbol)
		if existing:
			raise HTTPException(
				status_code=400, detail="Ticker with this symbol already exists"
			)

		ticker = await self.repo.create(ticker_in.model_dump())
		return ticker

	async def get_all(self, skip: int = 0, limit: int = 100) -> List[Ticker]:
		return await self.repo.get_all(skip, limit)

	async def get_by_id(self, ticker_id: UUID) -> Ticker:
		ticker = await self.repo.get_by_id(ticker_id)
		if not ticker:
			raise HTTPException(status_code=404, detail="Ticker not found")
		return ticker

	async def search(self, q: str, limit: int = 20) -> List[Ticker]:
		if len(q) < 1:
			raise HTTPException(status_code=400, detail="Search query too short")
		return await self.repo.search(q, limit)

	async def bulk_create(self, tickers_in: List[TickerCreate]) -> List[Ticker]:
		if len(tickers_in) > 500:
			raise HTTPException(status_code=400, detail="Too many tickers (max 500)")
		return await self.repo.bulk_create_or_update(
			[t.model_dump() for t in tickers_in]
		)
