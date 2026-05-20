from typing import Any, Dict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.core.exceptions import UserAlreadyExistsException
from swingtraderai.db.models.system import Watchlist, WatchlistItem
from swingtraderai.db.models.user import Position, User
from swingtraderai.schemas.auth import UserUpdate

from .base import TenantAwareRepository


class UserRepository(TenantAwareRepository[User]):
	"""Репозиторий для управления пользователями (без tenant_id)"""

	def __init__(self, session: AsyncSession):
		super().__init__(session, User)

	async def get_by_email(self, email: str) -> User | None:
		"""Метод без фильтра по tenant (используется при регистрации)"""
		result = await self.session.execute(select(User).where(User.email == email))
		return result.scalar_one_or_none()

	async def get_by_username(self, username: str) -> User | None:
		result = await self.session.execute(
			select(User).where(User.username == username)
		)
		return result.scalar_one_or_none()

	async def get_by_id_with_tenant(
		self, tenant_id: UUID, user_id: UUID
	) -> User | None:
		"""Получение пользователя по ID с проверкой tenant"""
		result = await self.session.execute(
			select(User).where(User.tenant_id == tenant_id, User.id == user_id)
		)
		return result.scalar_one_or_none()

	async def get_user_with_stats(
		self, tenant_id: UUID, user_id: UUID
	) -> Dict[str, Any]:
		"""Получение пользователя + расширенная статистика для страницы профиля"""

		user = await self.get_by_id_with_tenant(tenant_id, user_id)
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

		user_dict: Dict[str, Any] = {
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

	async def update_user(
		self, tenant_id: UUID, user_id: UUID, user_update: UserUpdate
	) -> Dict[str, Any]:
		"""Частичное обновление профиля пользователя с проверкой уникальности"""

		user = await self.get_by_id_with_tenant(tenant_id, user_id)
		if not user:
			raise ValueError("User not found")

		update_data = user_update.model_dump(exclude_unset=True)

		if not update_data:
			return await self.get_user_with_stats(tenant_id, user_id)

		new_username = update_data.get("username")
		if new_username and new_username != user.username:
			existing_user = await self.get_by_username(new_username)
			if existing_user:
				raise UserAlreadyExistsException(
					detail="Пользователь с таким логином уже существует."
				)
		for key, value in update_data.items():
			setattr(user, key, value)

		await self.session.commit()

		return await self.get_user_with_stats(tenant_id, user_id)
