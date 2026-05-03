from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.user_repository import UserRepository
from swingtraderai.db.models.user import User


class UserService:
	def __init__(self, session: AsyncSession):
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
