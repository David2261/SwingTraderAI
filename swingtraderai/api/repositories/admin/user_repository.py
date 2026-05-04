from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update

from swingtraderai.api.repositories.user_repository import UserRepository
from swingtraderai.db.models.user import User, UserRole


class AdminUserRepository(UserRepository):
	"""Расширенный репозиторий для административных операций"""

	async def list_users(
		self,
		skip: int = 0,
		limit: int = 100,
		role: Optional[str] = None,
		is_active: Optional[bool] = None,
		is_banned: Optional[bool] = None,
		search: Optional[str] = None,
	) -> List[User]:
		query = select(User).order_by(User.created_at.desc())

		if role:
			role_enum = getattr(UserRole, role.upper())
			query = query.where(User.role == role_enum)
		if is_active is not None:
			query = query.where(User.is_active == is_active)
		if is_banned is not None:
			query = query.where(User.is_banned == is_banned)
		if search:
			search_term = f"%{search}%"
			query = query.where(
				(User.email.ilike(search_term)) | (User.username.ilike(search_term))
			)

		query = query.offset(skip).limit(limit)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def update_ban_status(
		self,
		user_id: UUID,
		is_banned: bool,
		reason: Optional[str] = None,
		banned_until: Optional[datetime] = None,
	) -> Optional[User]:
		values = {
			"is_banned": is_banned,
			"is_active": not is_banned,
			"ban_reason": reason if is_banned else None,
			"banned_until": banned_until,
		}

		stmt = update(User).where(User.id == user_id).values(**values).returning(User)

		result = await self.session.execute(stmt)
		updated_user = result.scalar_one_or_none()

		if updated_user:
			await self.session.commit()
			await self.session.refresh(updated_user)

		return updated_user

	async def change_role(self, user_id: UUID, new_role: UserRole) -> Optional[User]:
		stmt = (
			update(User).where(User.id == user_id).values(role=new_role).returning(User)
		)

		result = await self.session.execute(stmt)
		updated_user = result.scalar_one_or_none()

		if updated_user:
			await self.session.commit()
			await self.session.refresh(updated_user)

		return updated_user
