from typing import Optional

from fastapi import HTTPException, status


class BaseAppException(Exception):
	"""Базовый класс для всех исключений приложения"""

	status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
	detail: str = "Internal Server Error"
	headers: Optional[dict[str, str]] = None


class AuthException(BaseAppException):
	"""Базовое исключение для аутентификации"""

	status_code = status.HTTP_401_UNAUTHORIZED
	detail = "Could not validate credentials"


class InvalidCredentialsException(AuthException):
	detail = "Incorrect email or password"


class InactiveUserException(AuthException):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "Inactive user"


class InsufficientPermissionsException(BaseAppException):
	status_code = status.HTTP_403_FORBIDDEN
	detail = "Not enough permissions"


class UserAlreadyExistsException(BaseAppException):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "User with this email or username already exists"


class TokenExpiredException(AuthException):
	detail = "Token has expired"


class InvalidTokenException(AuthException):
	detail = "Invalid token"


class ResourceNotFoundException(BaseAppException):
	status_code = status.HTTP_404_NOT_FOUND
	detail = "Resource not found"


class InvalidDataException(BaseAppException):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "Invalid data"


def raise_http_exception(exc: BaseAppException) -> None:
	"""Преобразует BaseAppException в HTTPException и вызывает его"""
	raise HTTPException(
		status_code=exc.status_code, detail=exc.detail, headers=exc.headers
	)
