from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from swingtraderai.api.deps import (
	ROLE_HIERARCHY,
	get_current_admin,
	get_current_tester_or_higher,
	get_current_user,
	require_role,
	require_role_or_higher,
)
from swingtraderai.core.config import settings
from swingtraderai.db.models.user import User, UserRole


@pytest.fixture
def mock_db():
	db = AsyncMock(spec=AsyncSession)
	return db


@pytest.fixture
def valid_token():
	"""Создаёт валидный access token"""
	return jwt.encode(
		{"sub": str(uuid7()), "type": "access"}, "test-secret-key", algorithm="HS256"
	)


@pytest.fixture
def inactive_user(mock_db):
	user = User(
		id=uuid7(),
		username="inactive",
		email="inactive@test.com",
		role=UserRole.USER,
		is_active=False,
	)
	mock_db.get.return_value = user
	return user


@pytest.fixture
def active_user(mock_db):
	user = User(
		id=uuid7(),
		username="activeuser",
		email="active@test.com",
		role=UserRole.USER,
		is_active=True,
	)
	mock_db.get.return_value = user
	return user


@pytest.fixture
def admin_user(mock_db):
	user = User(
		id=uuid7(),
		username="admin",
		email="admin@test.com",
		role=UserRole.ADMIN,
		is_active=True,
	)
	mock_db.get.return_value = user
	return user


@pytest.mark.asyncio
async def test_get_current_user_success(mock_db, active_user):
	test_secret = settings.SECRET_KEY
	token = jwt.encode(
		{"sub": str(active_user.id), "type": "access"}, test_secret, algorithm="HS256"
	)

	with pytest.MonkeyPatch.context() as mp:
		mp.setattr("swingtraderai.api.deps.get_db", lambda: mock_db)

		user = await get_current_user(token=token, db=mock_db)

	assert user.id == active_user.id
	assert user.is_active is True


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
	with pytest.raises(HTTPException) as exc_info:
		await get_current_user(token="invalid.token.here", db=mock_db)

	assert exc_info.value.status_code == 401
	assert "Could not validate credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_wrong_token_type(mock_db):
	token = jwt.encode(
		{"sub": str(uuid7()), "type": "refresh"}, "test-secret-key", algorithm="HS256"
	)

	with pytest.raises(HTTPException) as exc_info:
		await get_current_user(token=token, db=mock_db)

	assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_inactive(mock_db, inactive_user):
	token = jwt.encode(
		{"sub": str(inactive_user.id), "type": "access"},
		settings.SECRET_KEY,
		algorithm="HS256",
	)

	with pytest.raises(HTTPException) as exc_info:
		await get_current_user(token=token, db=mock_db)

	assert exc_info.value.status_code == 403
	assert "Inactive user" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_role_admin_success(admin_user):
	dependency = require_role(UserRole.ADMIN)

	result = await dependency(current_user=admin_user)
	assert result == admin_user


@pytest.mark.asyncio
async def test_require_role_admin_forbidden(active_user):
	dependency = require_role(UserRole.ADMIN)

	with pytest.raises(HTTPException) as exc_info:
		await dependency(current_user=active_user)

	assert exc_info.value.status_code == 403
	assert "Required role: admin" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_role_or_higher_admin_allows_admin(admin_user):
	dep = require_role_or_higher(UserRole.ADMIN)
	result = await dep(current_user=admin_user)
	assert result == admin_user


@pytest.mark.asyncio
async def test_require_role_or_higher_admin_allows_support():
	support_user = User(
		id=uuid7(),
		username="support",
		email="s@test.com",
		role=UserRole.SUPPORT,
		is_active=True,
	)

	dep = require_role_or_higher(UserRole.ADMIN)
	with pytest.raises(HTTPException) as exc:
		await dep(current_user=support_user)

	assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_or_higher_tester_allows_user():
	"""Пользователь не проходит требование tester или выше"""
	user = User(
		id=uuid7(),
		username="regular",
		email="u@test.com",
		role=UserRole.USER,
		is_active=True,
	)

	dep = require_role_or_higher(UserRole.TESTER)

	with pytest.raises(HTTPException) as exc:
		await dep(current_user=user)

	assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_current_admin(admin_user):
	result = await get_current_admin(current_user=admin_user)
	assert result.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_get_current_tester_or_higher():
	tester = User(
		id=uuid7(),
		username="tester",
		email="t@test.com",
		role=UserRole.TESTER,
		is_active=True,
	)

	result = await get_current_tester_or_higher(current_user=tester)
	assert result.role == UserRole.TESTER


def test_role_hierarchy_values():
	assert ROLE_HIERARCHY[UserRole.ADMIN] == 4
	assert ROLE_HIERARCHY[UserRole.SUPPORT] == 3
	assert ROLE_HIERARCHY[UserRole.TESTER] == 2
	assert ROLE_HIERARCHY[UserRole.USER] == 1


def test_role_hierarchy_unknown_role_returns_0():
	unknown_user = User(
		id=uuid7(), username="hacker", email="h@test.com", role="hacker", is_active=True
	)

	dep = require_role_or_higher(UserRole.USER)
	with pytest.raises(HTTPException):
		import asyncio

		asyncio.run(dep(current_user=unknown_user))
