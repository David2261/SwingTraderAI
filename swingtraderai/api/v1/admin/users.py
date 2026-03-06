from datetime import datetime
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_admin
from swingtraderai.db.models.user import User, UserRole
from swingtraderai.db.session import get_db
from swingtraderai.schemas.admin import (
	UserBanAction,
	UserListFilters,
	UserUpdateRole,
)
from swingtraderai.schemas.auth import UserOut

router = APIRouter(
	prefix="/users",
	tags=["admin-users"],
	dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=List[UserOut])
async def list_users(
	filters: UserListFilters = Depends(),
	db: AsyncSession = Depends(get_db),
) -> List[UserOut]:
	"""
	Получить список пользователей с фильтрами и пагинацией
	"""
	stmt = select(User).order_by(User.created_at.desc())

	if filters.role:
		stmt = stmt.where(User.role == filters.role)
	if filters.is_banned is not None:
		stmt = stmt.where(User.is_banned == filters.is_banned)
	if filters.is_active is not None:
		stmt = stmt.where(User.is_active == filters.is_active)
	if filters.search:
		search = f"%{filters.search}%"
		stmt = stmt.where((User.email.ilike(search)) | (User.username.ilike(search)))

	stmt = stmt.offset(filters.skip).limit(filters.limit)

	result = await db.execute(stmt)
	users = result.scalars().all()

	return [UserOut.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserOut)
async def get_user_detail(
	user_id: int,
	db: AsyncSession = Depends(get_db),
) -> UserOut:
	"""
	Получить подробную информацию об одном пользователе
	"""
	user = await db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=404, detail="User not found")

	return UserOut.model_validate(user)


@router.patch("/{user_id}/status", response_model=dict)
async def update_user_ban_status(
	user_id: int,
	data: UserBanAction,
	db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[int, str, Optional[datetime], Optional[str], bool]]:
	user = await db.get(User, user_id)
	if not user:
		raise HTTPException(404, "User not found")

	values = {
		"is_banned": data.is_banned,
		"is_active": not data.is_banned,
		"ban_reason": data.reason if data.is_banned else None,
		"banned_until": data.banned_until,
	}

	stmt = update(User).where(User.id == user_id).values(**values).returning(User)

	result = await db.execute(stmt)
	updated = result.scalar_one_or_none()

	if not updated:
		raise HTTPException(404, "User not found")

	await db.commit()

	status_text = "banned" if data.is_banned else "unbanned"
	if data.is_banned and data.banned_until:
		status_text = "temporarily banned"

	return {
		"user_id": updated.id,
		"email": updated.email,
		"status": status_text,
		"banned_until": updated.banned_until,
		"reason": updated.ban_reason,
	}


@router.patch("/{user_id}/role", response_model=UserOut)
async def change_user_role(
	user_id: int,
	data: UserUpdateRole,
	current_user: User = Depends(get_current_admin),
	db: AsyncSession = Depends(get_db),
) -> UserOut:
	"""
	Изменить роль пользователя (user → admin → tester и т.д.)
	"""
	try:
		UserRole(data.role)
	except ValueError as exc:
		raise HTTPException(422, "Invalid role") from exc

	if (
		user_id == current_user.id
		and UserRole(data.role).value < current_user.role.value
	):
		raise HTTPException(403, "Cannot downgrade own role")

	stmt = update(User).where(User.id == user_id).values(role=data.role).returning(User)

	result = await db.execute(stmt)
	updated_user = result.scalar_one_or_none()

	await db.commit()

	return UserOut.model_validate(updated_user)
