import uuid
import warnings
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from jose import JWTError, jwt

from swingtraderai.core.config import settings
from swingtraderai.core.security import (
	_create_token,
	create_access_token,
	create_refresh_token,
	get_password_hash,
	verify_password,
)


def test_get_password_hash_generates_different_hashes_for_same_password():
	"""Одинаковые пароли → разные хэши (соль)"""
	password = "MySuperSecret123"
	hash1 = get_password_hash(password)
	hash2 = get_password_hash(password)
	assert hash1 != hash2


def test_verify_password_correct():
	password = "testpass123"
	hashed = get_password_hash(password)
	assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
	password = "correct"
	wrong = "wrong"
	hashed = get_password_hash(password)
	assert verify_password(wrong, hashed) is False


def test_verify_password_empty_string():
	hashed = get_password_hash("")
	assert verify_password("", hashed) is True
	assert verify_password("a", hashed) is False


@pytest.fixture
def mock_settings():
	with patch.multiple(
		settings,
		SECRET_KEY="super-secret-key-for-testing-1234567890",
		ALGORITHM="HS256",
		ACCESS_TOKEN_EXPIRE_MINUTES=30,
		REFRESH_TOKEN_EXPIRE_DAYS=7,
	):
		yield


def test_create_access_token_default_expiration(mock_settings):
	subject = "user123"
	token = create_access_token(subject)

	decoded = jwt.decode(
		token,
		settings.SECRET_KEY,
		algorithms=[settings.ALGORITHM],
	)

	assert decoded["sub"] == str(subject)
	assert decoded["type"] == "access"
	assert "exp" in decoded
	assert "iat" in decoded
	assert "nbf" in decoded
	assert "jti" in decoded

	exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
	now = datetime.now(timezone.utc)
	delta = exp - now
	assert 28 * 60 < delta.total_seconds() < 32 * 60


def test_create_refresh_token_default_expiration(mock_settings):
	subject = 456
	token = create_refresh_token(subject)

	decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

	assert decoded["sub"] == "456"
	assert decoded["type"] == "refresh"

	exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
	now = datetime.now(timezone.utc)
	delta = exp - now
	assert 6.9 * 86400 < delta.total_seconds() < 7.1 * 86400


def test_create_token_custom_expiration():
	subject = "testuser"
	custom_delta = timedelta(hours=2)
	token = _create_token(subject, custom_delta, "custom")

	decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
	now = datetime.now(timezone.utc)
	delta = exp - now
	assert 7100 < delta.total_seconds() < 7300


def test_token_has_unique_jti():
	t1 = create_access_token("user1")
	t2 = create_access_token("user1")
	d1 = jwt.decode(t1, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	d2 = jwt.decode(t2, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	assert d1["jti"] != d2["jti"]


def test_token_uses_uuid4_for_jti(monkeypatch):
	fake_uuid = "123e4567-e89b-12d3-a456-426614174000"

	def fake_uuid4():
		return uuid.UUID(fake_uuid)

	monkeypatch.setattr(uuid, "uuid4", fake_uuid4)

	token = create_access_token("test")
	decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	assert decoded["jti"] == fake_uuid


def test_invalid_token_raises_jwt_error():
	invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
	with pytest.raises(JWTError):
		jwt.decode(invalid_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_token_with_wrong_secret_fails():
	token = create_access_token("user")
	with pytest.raises(JWTError):
		jwt.decode(token, "wrong-secret-key", algorithms=[settings.ALGORITHM])


def test_subject_can_be_anything_convertible_to_str():
	token = create_access_token(777)
	decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	assert decoded["sub"] == "777"

	token2 = create_access_token({"id": 42})
	decoded2 = jwt.decode(token2, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	assert decoded2["sub"] == "{'id': 42}"


def test_get_password_hash_does_not_raise_on_bcrypt_warning():
	with warnings.catch_warnings(record=True) as w:
		get_password_hash("password")
		assert len(w) == 0
