from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.user_repository import UserRepository
from swingtraderai.db.models.user import User
from swingtraderai.schemas.auth import UserUpdate


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
		return await self.repository.get_user_with_stats(tenant_id, user_id)

	async def update_user(
		self, tenant_id: UUID, user_id: UUID, user_update: UserUpdate
	) -> Dict[str, Any]:
		"""
		Бизнес-логика частичного обновления профиля пользователя.
		"""
		return await self.repository.update_user(tenant_id, user_id, user_update)
