from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from uuid6 import uuid7

from swingtraderai.schemas.admin import (
	UserAdminOut,
	UserBanAction,
	UserBanResponse,
	UserListFilters,
	UserUpdateRole,
)


class TestUserUpdateRole:
	def test_valid_role(self):
		"""Test valid role update"""
		data = {"role": "admin"}
		schema = UserUpdateRole(**data)
		assert schema.role == "admin"

	@pytest.mark.parametrize("invalid_role", ["superuser", "guest", ""])
	def test_invalid_role(self, invalid_role):
		"""Test invalid role values"""
		with pytest.raises(ValidationError):
			UserUpdateRole(role=invalid_role)


class TestUserBanAction:
	def test_ban_with_reason(self):
		"""Test banning user with reason"""
		data = {
			"is_banned": True,
			"reason": "Spam behavior",
		}
		schema = UserBanAction(**data)
		assert schema.is_banned is True
		assert schema.reason == "Spam behavior"
		assert schema.banned_until is None

	def test_ban_without_reason_raises_error(self):
		"""Test banning without reason raises validation error"""
		data = {"is_banned": True}
		with pytest.raises(ValidationError) as exc_info:
			UserBanAction(**data)
		assert "reason is required when banning user" in str(exc_info.value)

	def test_temporary_ban_with_future_date(self):
		"""Test temporary ban with future date"""
		future_date = datetime.now(timezone.utc) + timedelta(days=7)
		data = {
			"is_banned": True,
			"reason": "Violation",
			"banned_until": future_date,
		}
		schema = UserBanAction(**data)
		assert schema.banned_until == future_date

	def test_temporary_ban_with_past_date_raises_error(self):
		"""Test temporary ban with past date raises validation error"""
		past_date = datetime.now(timezone.utc) - timedelta(days=1)
		data = {
			"is_banned": True,
			"reason": "Violation",
			"banned_until": past_date,
		}
		with pytest.raises(ValidationError) as exc_info:
			UserBanAction(**data)
		assert "banned_until must be in the future" in str(exc_info.value)

	def test_unban(self):
		"""Test unbanning user"""
		data = {"is_banned": False}
		schema = UserBanAction(**data)
		assert schema.is_banned is False
		assert schema.reason is None
		assert schema.banned_until is None


class TestUserListFilters:
	def test_default_filters(self):
		"""Test default filter values"""
		filters = UserListFilters()
		assert filters.skip == 0
		assert filters.limit == 20
		assert filters.sort_by == "-created_at"

	def test_pagination_limits(self):
		"""Test pagination limits validation"""
		# Valid limits
		filters = UserListFilters(skip=10, limit=50)
		assert filters.skip == 10
		assert filters.limit == 50

		# Invalid limit (too high)
		with pytest.raises(ValidationError):
			UserListFilters(limit=300)

		# Invalid skip (negative)
		with pytest.raises(ValidationError):
			UserListFilters(skip=-1)

	@pytest.mark.parametrize("role", ["user", "tester", "support", "admin"])
	def test_role_filter(self, role):
		"""Test role filter with valid roles"""
		filters = UserListFilters(role=role)
		assert filters.role == role

	def test_date_filters(self):
		"""Test date filters"""
		created_after = datetime(2025, 1, 1)
		created_before = datetime(2025, 12, 31)
		last_login_after = datetime(2025, 6, 1)

		filters = UserListFilters(
			created_after=created_after,
			created_before=created_before,
			last_login_after=last_login_after,
		)
		assert filters.created_after == created_after
		assert filters.created_before == created_before
		assert filters.last_login_after == last_login_after

	@pytest.mark.parametrize(
		"sort_by",
		[
			"created_at",
			"-created_at",
			"last_login",
			"-last_login",
			"username",
			"-username",
			"email",
			"-email",
		],
	)
	def test_sort_by_valid(self, sort_by):
		"""Test all valid sort_by values"""
		filters = UserListFilters(sort_by=sort_by)
		assert filters.sort_by == sort_by

	def test_search_filter(self):
		"""Test search filter"""
		filters = UserListFilters(search="test@example.com")
		assert filters.search == "test@example.com"


class TestUserAdminOut:
	def test_user_admin_out_creation(self):
		"""Test creating UserAdminOut instance"""
		now = datetime.now(timezone.utc)
		user_data = {
			"id": uuid7(),
			"username": "testuser",
			"email": "test@example.com",
			"telegram_id": "123456",
			"role": "user",
			"is_active": True,
			"is_banned": False,
			"ban_reason": None,
			"banned_until": None,
			"created_at": now,
			"updated_at": now,
			"last_login": now,
			"signals_received_count": 5,
		}
		user_out = UserAdminOut(**user_data)
		assert user_out.id == user_data["id"]
		assert user_out.username == "testuser"
		assert user_out.signals_received_count == 5

	def test_user_admin_out_from_attributes(self):
		"""Test model_config from_attributes"""
		assert UserAdminOut.model_config["from_attributes"] is True


class TestUserBanResponse:
	def test_ban_response(self):
		"""Test ban response schema"""
		response = UserBanResponse(
			user_id=uuid7(),
			email="test@example.com",
			status="banned",
			reason="Spam",
			banned_until=None,
			message="User has been banned",
		)
		assert response.user_id == response.user_id
		assert response.status == "banned"
		assert response.message == "User has been banned"

	@pytest.mark.parametrize("status", ["banned", "unbanned", "temporarily_banned"])
	def test_all_status_values(self, status):
		"""Test all possible status values"""
		response = UserBanResponse(
			user_id=uuid7(),
			email="test@example.com",
			status=status,
			reason=None,
			banned_until=None,
			message="Test message",
		)
		assert response.status == status
