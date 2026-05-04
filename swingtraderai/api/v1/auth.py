from typing import Any, Dict, cast

from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.api.services.auth_service import AuthService
from swingtraderai.core.config import settings
from swingtraderai.core.exceptions import (
	InvalidCredentialsException,
	raise_http_exception,
)
from swingtraderai.core.rate_limit import limiter
from swingtraderai.core.security import (
	create_access_token,
	get_password_hash,
	verify_password,
)
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.auth import Token, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
	return AuthService(db)


@router.post("/register", response_model=Token)
@limiter.limit("5/minute")
async def register(
	user_in: UserCreate,
	auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
	"""
	Регистрация нового пользователя.
	Проверяет, не существует ли пользователь с таким email,
	создает нового пользователя
	и возвращает токены доступа и обновления.
	"""
	return await auth_service.register(user_in)


@router.post("/login", response_model=Token)
@limiter.limit("12/minute")
async def login(
	form_data: OAuth2PasswordRequestForm = Depends(),
	auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
	"""
	Аутентификация пользователя.
	Проверяет учетные данные и возвращает токены доступа,
	а также токен и обновления.
	"""
	return await auth_service.login(form_data.username, form_data.password)


@router.post("/forgot-password")
@limiter.limit("6/minute")
async def forgot_password(
	email: str = Body(...), db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
	"""
	Отправка ссылки для сброса пароля.
	В реальной системе нужно отправлять email с токеном.
	"""
	result = await db.execute(select(User).where(User.email == email))
	user = result.scalar_one_or_none()
	if not user:
		return {"msg": "If the email exists, a reset link has been sent"}

	reset_token = create_access_token(user.id, expires_delta=None)
	return {"msg": "Reset password token generated", "reset_token": reset_token}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
	token: str = Body(...),
	new_password: str = Body(...),
	db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
	"""
	Смена пароля по токену.
	"""
	try:
		payload = jwt.decode(
			token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
		)
		user_id_value: Any = payload.get("sub")
		if not isinstance(user_id_value, str):
			raise_http_exception(InvalidCredentialsException())

		user_id: str = user_id_value

		if user_id is None:
			raise_http_exception(InvalidCredentialsException())
	except JWTError:
		raise_http_exception(InvalidCredentialsException())

	try:
		user_id_int = int(user_id)
	except ValueError:
		raise_http_exception(InvalidCredentialsException())

	user = await db.get(User, user_id_int)
	if not user:
		raise_http_exception(InvalidCredentialsException())

	user = cast(User, user)
	user.password_hash = get_password_hash(new_password)
	db.add(user)
	await db.commit()
	await db.refresh(user)

	return {"msg": "Password has been reset successfully"}


@router.post("/change-password")
@limiter.limit("8/10minutes")
async def change_password(
	current_user: User = Depends(get_current_user),
	old_password: str = Body(...),
	new_password: str = Body(...),
	db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
	"""
	Смена пароля для авторизованного пользователя.
	"""
	if not verify_password(old_password, current_user.password_hash):
		raise_http_exception(InvalidCredentialsException())

	current_user.password_hash = get_password_hash(new_password)
	db.add(current_user)
	await db.commit()
	await db.refresh(current_user)

	return {"msg": "Password changed successfully"}


@router.post("/logout")
@limiter.limit("5/minute")
async def logout(current_user: User = Depends(get_current_user)) -> Dict[str, str]:
	"""
	Логика выхода: если используешь refresh tokens, можно их инвалидировать.
	В простом варианте можно просто возвращать сообщение.
	"""
	return {"msg": "Successfully logged out"}
