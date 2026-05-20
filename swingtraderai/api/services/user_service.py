from typing import Any, Dict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.user_repository import UserRepository
from swingtraderai.db.models.system import Watchlist, WatchlistItem
from swingtraderai.db.models.user import Position, User


class UserService:
	"""Сервис для работы с пользователями"""

	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = UserRepository(session)

	async def get_current_user_info(self, tenant_id: UUID, user_id: UUID) -> User:
		"""Получение информации о текущем пользователе"""
		user = await self.repository.get_by_id(tenant_id, user_id)
		if not user:
			raise ValueError("User not found")
		return user

	async def get_user_by_id(self, tenant_id: UUID, user_id: UUID) -> User:
		user = await self.repository.get_by_id(tenant_id, user_id)
		if not user:
			raise ValueError("User not found")
		return user

	async def get_user_with_stats(
		self, tenant_id: UUID, user_id: UUID
	) -> Dict[str, Any]:
		"""Получение пользователя + расширенная статистика для страницы профиля"""

		user = await self.get_user_by_id(tenant_id, user_id)
		if not user:
			raise ValueError("User not found")

		watchlist_count_query = (
			select(func.count(WatchlistItem.id))
			.join(Watchlist, Watchlist.id == WatchlistItem.watchlist_id)
			.where(Watchlist.tenant_id == tenant_id, Watchlist.owner_id == user_id)
		)
		watchlist_count = await self.session.scalar(watchlist_count_query) or 0

		positions_count_query = select(func.count(Position.id)).where(
			Position.tenant_id == tenant_id,
			Position.user_id == user_id,
			Position.closed_at.is_(None),
		)
		positions_count = await self.session.scalar(positions_count_query) or 0

		user_dict = {
			**{
				column.name: getattr(user, column.name)
				for column in user.__table__.columns
			},
			"watchlist_count": watchlist_count,
			"positions_count": positions_count,
			"active_alerts_count": 0,
			"total_signals_received": user.signals_received_count or 0,
			"telegram_username": getattr(user, "telegram_username", None),
			"avatar_url": getattr(user, "avatar_url", None),
			"timezone": getattr(user, "timezone", "Europe/Moscow"),
			"last_login_ip": getattr(user, "last_login_ip", None),
			"joined_at": user.created_at,
		}

		return user_dict
