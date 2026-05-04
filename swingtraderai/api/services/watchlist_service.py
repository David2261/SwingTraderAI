from typing import Any, List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.watchlist_repository import (
	WatchlistItemRepository,
	WatchlistRepository,
)
from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.system import Watchlist, WatchlistItem
from swingtraderai.schemas.watchlist import (
	WatchlistDataItem,
	WatchlistItemCreate,
	WatchlistItemUpdate,
)


class WatchlistService:
	"""Сервис для управления списком наблюдения пользователя"""

	def __init__(self, session: AsyncSession):
		self.session = session
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

	async def get_watchlist_with_prices(
		self,
		tenant_id: UUID,
		user_id: UUID,
		limit: int = 50,
		sort_by: str = "change_percent",
		order: str = "desc",
	) -> List[WatchlistDataItem]:
		"""
		Возвращает watchlist с актуальными ценами и изменениями.
		"""
		# Subquery для последних двух цен
		subq = (
			select(
				MarketData.ticker_id,
				MarketData.close.label("last_price"),
				MarketData.volume.label("last_volume"),
				MarketData.timestamp,
				func.lag(MarketData.close)
				.over(partition_by=MarketData.ticker_id, order_by=MarketData.timestamp)
				.label("prev_price"),
			).order_by(MarketData.ticker_id, MarketData.timestamp.desc())
		).subquery()

		last_prices = (
			select(subq)
			.distinct(subq.c.ticker_id)
			.order_by(subq.c.ticker_id, subq.c.timestamp.desc())
		).subquery()

		# Основной запрос
		stmt = (
			select(
				WatchlistItem,
				Ticker.symbol,
				Ticker.asset_type,
				last_prices.c.last_price,
				last_prices.c.last_volume,
				last_prices.c.prev_price,
			)
			.join(Watchlist, WatchlistItem.watchlist_id == Watchlist.id)
			.join(Ticker, WatchlistItem.ticker_id == Ticker.id)
			.join(last_prices, last_prices.c.ticker_id == Ticker.id)
			.where(Watchlist.owner_id == user_id)
		)

		sort_field: Any

		# Сортировка
		if sort_by == "price":
			sort_field = last_prices.c.last_price
		elif sort_by == "volume":
			sort_field = last_prices.c.last_volume
		elif sort_by == "change_percent":
			sort_field = (
				last_prices.c.last_price - last_prices.c.prev_price
			) / func.nullif(last_prices.c.prev_price, 0)
		else:
			sort_field = Ticker.symbol

		if order.lower() == "asc":
			stmt = stmt.order_by(sort_field.asc())
		else:
			stmt = stmt.order_by(sort_field.desc())

		result = await self.session.execute(stmt.limit(limit))
		rows = result.all()

		items = []
		for row in rows:
			wi, symbol, a_type, lp, lv, pp = row

			change_abs = float(lp - pp) if lp and pp else 0.0
			change_pct = float((lp - pp) / pp * 100) if lp and pp and pp != 0 else 0.0

			items.append(
				WatchlistDataItem(
					item_id=wi.id,
					ticker_id=wi.ticker_id,
					symbol=symbol,
					asset_type=a_type,
					last_price=float(lp) if lp else None,
					change_percent=change_pct,
					change_abs=change_abs,
					volume=float(lv) if lv else None,
					added_at=wi.created_at,
				)
			)

		return items
