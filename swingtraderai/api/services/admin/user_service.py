from typing import Any, Dict, List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.admin.user_repository import AdminUserRepository
from swingtraderai.db.models.user import User, UserRole
from swingtraderai.schemas.admin import UserBanAction, UserListFilters, UserUpdateRole


class AdminUserService:
	def __init__(self, session: AsyncSession):
		self.repo = AdminUserRepository(session)

	async def list_users(self, filters: UserListFilters) -> List[User]:
		result = await self.repo.list_users(
			skip=filters.skip,
			limit=filters.limit,
			role=filters.role,
			is_active=filters.is_active,
			is_banned=filters.is_banned,
			search=filters.search,
		)
		return result

	async def get_user_detail(self, user_id: UUID) -> User:
		"""Детальная информация о пользователе"""
		user = await self.repo.get_by_id(
			UUID(int=0), user_id
		)  # tenant_id=None для админа
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		return user

	async def update_ban_status(
		self, user_id: UUID, data: UserBanAction
	) -> Dict[str, Any]:
		updated = await self.repo.update_ban_status(
			user_id=user_id,
			is_banned=data.is_banned,
			reason=data.reason,
			banned_until=data.banned_until,
		)

		if not updated:
			raise HTTPException(status_code=404, detail="User not found")

		status_text = "banned" if data.is_banned else "unbanned"
		if data.is_banned and data.banned_until:
			status_text = "temporarily banned"

		return {
			"user_id": updated.id,
			"email": updated.email,
			"status": status_text,
			"banned_until": updated.banned_until,
			"reason": updated.ban_reason,
			"message": f"User {status_text} successfully",
		}

	async def change_role(
		self, user_id: UUID, data: UserUpdateRole, current_admin: User
	) -> User:
		try:
			new_role = UserRole[data.role.upper()]
		except KeyError:
			raise HTTPException(422, "Invalid role") from KeyError

		# Важные проверки безопасности
		if new_role == UserRole.ADMIN:
			raise HTTPException(403, "Cannot assign admin role directly")

		target_user = await self.repo.get_by_id(UUID(int=0), user_id)
		if not target_user:
			raise HTTPException(404, "User not found")

		if target_user.role == UserRole.ADMIN and current_admin.id != user_id:
			raise HTTPException(403, "Cannot change another admin's role")

		updated = await self.repo.change_role(user_id, new_role)
		if not updated:
			raise HTTPException(404, "User not found")

		return updated
