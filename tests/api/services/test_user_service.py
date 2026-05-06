import pytest
from uuid6 import uuid7

from swingtraderai.api.services.user_service import UserService
from swingtraderai.db.models.user import User


@pytest.fixture
async def user_service(session):
	return UserService(session)


async def test_get_current_user_info_success(user_service, user):
	"""Успешное получение информации о текущем пользователе"""
	result = await user_service.get_current_user_info(
		tenant_id=user.tenant_id, user_id=user.id
	)

	assert isinstance(result, User)
	assert result.id == user.id
	assert result.tenant_id == user.tenant_id
	assert result.email == user.email
	assert result.username == user.username


async def test_get_current_user_info_not_found(user_service, user):
	"""Пользователь не найден — должно бросать ValueError"""
	non_existent_id = uuid7()

	with pytest.raises(ValueError) as exc_info:
		await user_service.get_current_user_info(
			tenant_id=user.tenant_id, user_id=non_existent_id
		)

	assert str(exc_info.value) == "User not found"


async def test_get_current_user_info_wrong_tenant(user_service, user):
	"""Пользователь существует, но в другом tenant'е"""
	wrong_tenant_id = uuid7()

	with pytest.raises(ValueError) as exc_info:
		await user_service.get_current_user_info(
			tenant_id=wrong_tenant_id, user_id=user.id
		)

	assert str(exc_info.value) == "User not found"


async def test_get_user_by_id_success(user_service, user):
	"""Успешное получение пользователя по ID"""
	result = await user_service.get_user_by_id(
		tenant_id=user.tenant_id, user_id=user.id
	)

	assert isinstance(result, User)
	assert result.id == user.id
	assert result.email == user.email


async def test_get_user_by_id_not_found(user_service):
	"""Пользователь не найден"""
	with pytest.raises(ValueError) as exc_info:
		await user_service.get_user_by_id(tenant_id=uuid7(), user_id=uuid7())

	assert str(exc_info.value) == "User not found"


async def test_both_methods_return_same_user(user_service, user):
	"""Оба метода должны возвращать одинакового пользователя"""
	user1 = await user_service.get_current_user_info(user.tenant_id, user.id)
	user2 = await user_service.get_user_by_id(user.tenant_id, user.id)

	assert user1.id == user2.id
	assert user1.email == user2.email
	assert user1.tenant_id == user2.tenant_id


async def test_service_uses_repository_correctly(user_service, user, mocker):
	"""Проверка, что сервис правильно вызывает репозиторий"""
	mock_repo = mocker.patch.object(
		user_service.repository, "get_by_id", autospec=True, return_value=user
	)

	await user_service.get_current_user_info(user.tenant_id, user.id)

	mock_repo.assert_called_once_with(user.tenant_id, user.id)


async def test_get_user_by_id_with_different_user(user_service, user, session):
	"""Создаём второго пользователя и проверяем получение"""
	another_user = User(
		username="another",
		email="another@example.com",
		password_hash="hash123",
		tenant_id=user.tenant_id,
	)
	session.add(another_user)
	await session.commit()
	await session.refresh(another_user)

	result = await user_service.get_user_by_id(
		tenant_id=user.tenant_id, user_id=another_user.id
	)

	assert result.id == another_user.id
	assert result.email == "another@example.com"
