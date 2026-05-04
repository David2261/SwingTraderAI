from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_admin
from swingtraderai.api.services.admin.user_service import AdminUserService
from swingtraderai.db.models.user import User
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


def get_admin_user_service(db: AsyncSession = Depends(get_db)) -> AdminUserService:
	return AdminUserService(db)


@router.get("", response_model=List[UserOut])
async def list_users(
	filters: UserListFilters = Depends(),
	admin_service: AdminUserService = Depends(get_admin_user_service),
	current_admin: User = Depends(get_current_admin),
) -> List[User]:
	"""
	Получить список пользователей с фильтрами и пагинацией
	"""
	return await admin_service.list_users(filters)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_detail(
	user_id: UUID,
	admin_service: AdminUserService = Depends(get_admin_user_service),
	current_admin: User = Depends(get_current_admin),
) -> User:
	"""
	Получить подробную информацию об одном пользователе
	"""
	return await admin_service.get_user_detail(user_id)


@router.patch("/{user_id}/status", response_model=dict)
async def update_user_ban_status(
	user_id: UUID,
	data: UserBanAction,
	admin_service: AdminUserService = Depends(get_admin_user_service),
	current_admin: User = Depends(get_current_admin),
) -> Dict[str, Union[UUID, str, Optional[datetime], Optional[str], bool]]:
	return await admin_service.update_ban_status(user_id, data)


@router.patch("/{user_id}/role", response_model=UserOut)
async def change_user_role(
	user_id: UUID,
	data: UserUpdateRole,
	admin_service: AdminUserService = Depends(get_admin_user_service),
	current_admin: User = Depends(get_current_admin),
) -> User:
	"""
	Изменить роль пользователя с дополнительными проверками
	"""
	return await admin_service.change_role(user_id, data, current_admin)
