from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from swingtraderai.db.models.system import Watchlist, WatchlistItem

from .base import TenantAwareRepository


class WatchlistRepository(TenantAwareRepository[Watchlist]):
	def __init__(self, session: AsyncSession):
		super().__init__(session, Watchlist)


class WatchlistItemRepository(TenantAwareRepository[WatchlistItem]):
	def __init__(self, session: AsyncSession):
		super().__init__(session, WatchlistItem)

	async def get_user_watchlist_items(
		self, tenant_id: UUID, user_id: UUID
	) -> List[WatchlistItem]:
		"""Получить все items пользователя с тикерами"""
		query = (
			self._get_tenant_query(tenant_id)
			.join(Watchlist)
			.where(Watchlist.owner_id == user_id)
			.options(joinedload(WatchlistItem.ticker))
			.order_by(WatchlistItem.created_at.desc())
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def get_by_ticker(
		self, tenant_id: UUID, user_id: UUID, ticker_id: UUID
	) -> Optional[WatchlistItem]:
		"""Проверка, есть ли тикер уже в watchlist"""
		query = (
			self._get_tenant_query(tenant_id)
			.join(Watchlist)
			.where(
				and_(
					Watchlist.owner_id == user_id,
					WatchlistItem.ticker_id == ticker_id,
				)
			)
		)
		result = await self.session.execute(query)
		return result.scalar_one_or_none()

	async def create_watchlist_if_not_exists(
		self, tenant_id: UUID, user_id: UUID, name: str = ""
	) -> Watchlist:
		"""Создать watchlist для пользователя, если его нет"""
		result = await self.session.execute(
			select(Watchlist).where(Watchlist.owner_id == user_id)
		)
		watchlist = result.scalar_one_or_none()

		if not watchlist:
			watchlist = Watchlist(
				tenant_id=tenant_id,
				owner_id=user_id,
				name=name or f"Watchlist-{user_id}",
			)
			self.session.add(watchlist)
			await self.session.commit()
			await self.session.refresh(watchlist)

		return watchlist
