import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.services.auth_service import AuthService
from swingtraderai.core.exceptions import UserAlreadyExistsException
from swingtraderai.core.security import get_password_hash, verify_password
from swingtraderai.schemas.auth import UserCreate


@pytest.fixture
async def auth_service(session: AsyncSession) -> AuthService:
	return AuthService(session)


async def test_register_success(auth_service: AuthService):
	user_data = UserCreate(
		username="newuser",
		email="newuser@example.com",
		password="StrongPass123!",
		telegram_id=None,
	)

	result = await auth_service.register(user_data)

	assert "access_token" in result
	assert "refresh_token" in result
	assert result["token_type"] == "bearer"

	# Проверяем, что пользователь действительно создался
	user = await auth_service.user_repo.get_by_email(user_data.email)
	assert user is not None
	assert user.username == user_data.username
	assert user.email == user_data.email
	assert user.tenant_id is not None


async def test_register_email_already_exists(auth_service: AuthService, user):
	user_data = UserCreate(
		username="duplicate",
		email=user.email,
		password="StrongPass123!",
		telegram_id=None,
	)

	with pytest.raises(UserAlreadyExistsException):
		await auth_service.register(user_data)


async def test_login_success(auth_service: AuthService, user):
	# Сначала обновляем пароль пользователя на известный
	user.password_hash = get_password_hash("correctpassword123")
	await auth_service.user_repo.session.commit()

	result = await auth_service.login(email=user.email, password="correctpassword123")

	assert "access_token" in result
	assert "refresh_token" in result
	assert result["token_type"] == "bearer"


async def test_login_wrong_password(auth_service: AuthService, user):
	user.password_hash = get_password_hash("correctpassword123")
	await auth_service.user_repo.session.commit()

	with pytest.raises(HTTPException) as exc_info:
		await auth_service.login(user.email, "wrongpassword")

	assert exc_info.value.status_code == 401
	assert exc_info.value.detail == "Incorrect email or password"


async def test_login_user_not_found(auth_service: AuthService):
	with pytest.raises(HTTPException) as exc_info:
		await auth_service.login("nonexistent@example.com", "anypassword")

	assert exc_info.value.status_code == 401


async def test_change_password_success(auth_service: AuthService, user):
	old_password = "oldpass123"
	new_password = "newStrongPass456!"

	user.password_hash = get_password_hash(old_password)
	await auth_service.user_repo.session.commit()

	result = await auth_service.change_password(
		user=user, old_password=old_password, new_password=new_password
	)

	assert result["msg"] == "Password changed successfully"

	await auth_service.user_repo.session.refresh(user)
	assert not verify_password(old_password, user.password_hash)


async def test_change_password_wrong_old_password(auth_service: AuthService, user):
	user.password_hash = get_password_hash("realpassword")
	await auth_service.user_repo.session.commit()

	with pytest.raises(HTTPException) as exc_info:
		await auth_service.change_password(
			user=user, old_password="wrongoldpass", new_password="newpass123"
		)

	assert exc_info.value.status_code == 400
	assert exc_info.value.detail == "Incorrect old password"


async def test_register_creates_unique_tenant_id(auth_service: AuthService):
	users = []

	for i in range(3):
		user_data = UserCreate(
			username=f"tenantuser{i}",
			email=f"tenant{i}@example.com",
			password="Pass123!",
			telegram_id=None,
		)
		await auth_service.register(user_data)
		user = await auth_service.user_repo.get_by_email(user_data.email)
		users.append(user)

	tenant_ids = {u.tenant_id for u in users}
	assert len(tenant_ids) == 3  # все tenant_id уникальные


async def test_register_with_telegram_id(auth_service: AuthService):
	telegram_id = 123456789

	user_data = UserCreate(
		username="tguser",
		email="tg@example.com",
		password="Pass123!",
		telegram_id=telegram_id,
	)

	await auth_service.register(user_data)

	user = await auth_service.user_repo.get_by_email(user_data.email)
	assert user.telegram_id == telegram_id
