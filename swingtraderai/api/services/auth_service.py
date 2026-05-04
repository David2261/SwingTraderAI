from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from swingtraderai.api.repositories.user_repository import UserRepository
from swingtraderai.core.exceptions import UserAlreadyExistsException
from swingtraderai.core.security import (
	create_access_token,
	create_refresh_token,
	get_password_hash,
	verify_password,
)
from swingtraderai.db.models.user import User
from swingtraderai.schemas.auth import UserCreate


class AuthService:
	def __init__(self, session: AsyncSession):
		self.user_repo = UserRepository(session)

	async def register(self, user_in: UserCreate) -> Dict[str, str]:
		"""Регистрация нового пользователя"""
		# Проверка на существование
		existing = await self.user_repo.get_by_email(user_in.email)
		if existing:
			raise UserAlreadyExistsException()

		# Создаём пользователя
		hashed_password = get_password_hash(user_in.password)
		new_tenant_id = uuid7()

		user_data = {
			"username": user_in.username,
			"email": user_in.email,
			"password_hash": hashed_password,
			"telegram_id": user_in.telegram_id,
			"tenant_id": new_tenant_id,
		}

		user = await self.user_repo.create(new_tenant_id, user_data)

		# Создаём токены
		access_token = create_access_token(
			subject=str(user.id), tenant_id=user.tenant_id
		)
		refresh_token = create_refresh_token(
			subject=str(user.id), tenant_id=user.tenant_id
		)

		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"token_type": "bearer",
		}

	async def login(self, email: str, password: str) -> Dict[str, str]:
		"""Аутентификация пользователя"""
		user = await self.user_repo.get_by_email(email)
		if not user or not verify_password(password, user.password_hash):
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect email or password",
				headers={"WWW-Authenticate": "Bearer"},
			)

		access_token = create_access_token(
			subject=str(user.id), tenant_id=user.tenant_id
		)
		refresh_token = create_refresh_token(
			subject=str(user.id), tenant_id=user.tenant_id
		)

		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"token_type": "bearer",
		}

	async def change_password(
		self, user: User, old_password: str, new_password: str
	) -> Dict[str, str]:
		"""Смена пароля"""
		if not verify_password(old_password, user.password_hash):
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
			)

		user.password_hash = get_password_hash(new_password)
		return {"msg": "Password changed successfully"}
