from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.watchlist_repository import (
	WatchlistItemRepository,
	WatchlistRepository,
)
from swingtraderai.db.models.system import Watchlist, WatchlistItem
from swingtraderai.schemas.watchlist import (
	WatchlistItemCreate,
	WatchlistItemUpdate,
)


class WatchlistService:
	def __init__(self, session: AsyncSession):
		self.item_repo = WatchlistItemRepository(session)
		self.watchlist_repo = WatchlistRepository(session)

	async def add_item(
		self, tenant_id: UUID, user_id: UUID, item_in: WatchlistItemCreate
	) -> WatchlistItem:
		from swingtraderai.db.models.market import Ticker

		ticker = await self.item_repo.session.get(Ticker, item_in.ticker_id)
		if not ticker:
			raise HTTPException(status_code=404, detail="Ticker not found")

		existing = await self.item_repo.get_by_ticker(
			tenant_id, user_id, item_in.ticker_id
		)
		if existing:
			raise HTTPException(status_code=400, detail="Ticker already in watchlist")

		watchlist = await self.item_repo.create_watchlist_if_not_exists(
			tenant_id, user_id
		)

		item_data = {
			"watchlist_id": watchlist.id,
			"ticker_id": item_in.ticker_id,
		}

		item = await self.item_repo.create(tenant_id, item_data)
		return item

	async def get_user_items(
		self, tenant_id: UUID, user_id: UUID
	) -> List[WatchlistItem]:
		return await self.item_repo.get_user_watchlist_items(tenant_id, user_id)

	async def update_item(
		self,
		tenant_id: UUID,
		user_id: UUID,
		item_id: UUID,
		update_data: WatchlistItemUpdate,
	) -> WatchlistItem:
		item = await self.item_repo.get_by_id(tenant_id, item_id)
		if not item:
			raise HTTPException(status_code=404, detail="Watchlist item not found")

		watchlist = await self.item_repo.session.get(Watchlist, item.watchlist_id)

		if not watchlist:
			raise HTTPException(status_code=404, detail="Watchlist not found")

		if watchlist.owner_id != user_id:
			raise HTTPException(status_code=403, detail="Not your watchlist item")

		for key, value in update_data.model_dump(exclude_unset=True).items():
			setattr(item, key, value)

		await self.item_repo.session.commit()
		await self.item_repo.session.refresh(item)
		return item

	async def remove_item(self, tenant_id: UUID, user_id: UUID, item_id: UUID) -> bool:
		item = await self.item_repo.get_by_id(tenant_id, item_id)
		if not item:
			raise HTTPException(status_code=404, detail="Item not found")

		watchlist = await self.item_repo.session.get(Watchlist, item.watchlist_id)

		if not watchlist:
			raise HTTPException(status_code=404, detail="Watchlist not found")

		if watchlist.owner_id != user_id:
			raise HTTPException(status_code=403, detail="Not your watchlist item")

		return await self.item_repo.delete(tenant_id, item_id)
