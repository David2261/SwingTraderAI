from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.models.user import User

from .base import TenantAwareRepository


class UserRepository(TenantAwareRepository[User]):
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
