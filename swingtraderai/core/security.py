from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from uuid6 import uuid7

from swingtraderai.core.config import settings
from swingtraderai.schemas.auth import JWTPayload

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
	password_hash = pwd_context.hash(password)

	return str(password_hash)


def _create_token(
	subject: str,
	expires_delta: timedelta,
	token_type: str,
	tenant_id: UUID | None = None,
) -> str:
	now = datetime.now(timezone.utc)
	expire = now + expires_delta

	payload = {
		"sub": str(subject),
		"type": token_type,
		"exp": expire,
		"iat": now,
		"nbf": now,
		"jti": str(uuid7()),
	}

	if tenant_id:
		payload["tenant_id"] = str(tenant_id)

	encoded_token = jwt.encode(
		payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
	)

	return str(encoded_token)


def create_access_token(
	subject: str | Any,
	tenant_id: UUID | None = None,
	expires_delta: timedelta | None = None,
) -> str:
	expires = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	return _create_token(subject, expires, "access", tenant_id)


def create_refresh_token(
	subject: str | Any,
	tenant_id: UUID | None = None,
	expires_delta: timedelta | None = None,
) -> str:
	expires = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
	return _create_token(subject, expires, "refresh", tenant_id)


def decode_token(token: str) -> JWTPayload:
	payload = jwt.decode(
		token,
		settings.SECRET_KEY,
		algorithms=[settings.ALGORITHM],
	)
	return JWTPayload.model_validate(payload)
