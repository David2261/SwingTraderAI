import os
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from swingtraderai.core.config import Settings


def test_settings_types_are_correct():
	"""Проверяем, что типы полей соответствуют объявленным (статически)"""

	s = Settings(
		SECRET_KEY="dummy-key",
		ALGORITHM="HS256",
		DATABASE_URL="postgresql://user:pass@localhost/db",
		REDIS_URL="redis://localhost:6379/0",
	)

	assert isinstance(s.SECRET_KEY, str)
	assert isinstance(s.ALGORITHM, str)
	assert isinstance(s.DATABASE_URL, str)
	assert isinstance(s.REDIS_URL, str)
	assert isinstance(s.ACCESS_TOKEN_EXPIRE_MINUTES, int)
	assert isinstance(s.REFRESH_TOKEN_EXPIRE_DAYS, int)


def test_defaults_have_correct_types():
	s = Settings(
		SECRET_KEY="key",
		ALGORITHM="HS256",
		DATABASE_URL="sqlite:///:memory:",
		REDIS_URL="redis://localhost:0",
	)

	assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
	assert isinstance(s.ACCESS_TOKEN_EXPIRE_MINUTES, int)

	assert s.REFRESH_TOKEN_EXPIRE_DAYS == 7
	assert isinstance(s.REFRESH_TOKEN_EXPIRE_DAYS, int)


@pytest.mark.parametrize(
	"field_name, invalid_value, expected_error_msg",
	[
		("ACCESS_TOKEN_EXPIRE_MINUTES", "thirty", "Input should be a valid integer"),
		("ACCESS_TOKEN_EXPIRE_MINUTES", 3.14, "Input should be a valid integer"),
		("REFRESH_TOKEN_EXPIRE_DAYS", "seven", "Input should be a valid integer"),
		("SECRET_KEY", 12345, "Input should be a valid string"),
		("ALGORITHM", ["HS256"], "Input should be a valid string"),
	],
)
def test_invalid_types_raise_validation_error(
	field_name: str, invalid_value: Any, expected_error_msg: str
):
	kwargs = {
		"SECRET_KEY": "key",
		"ALGORITHM": "HS256",
		"DATABASE_URL": "postgresql://localhost",
		"REDIS_URL": "redis://localhost",
		field_name: invalid_value,
	}

	with pytest.raises(ValidationError) as exc_info:
		Settings(**kwargs)

	errors = exc_info.value.errors()
	assert len(errors) >= 1
	assert expected_error_msg in errors[0]["msg"]
	assert errors[0]["loc"] == (field_name,)


def test_env_string_coerced_to_int():
	"""Pydantic должен приводить строку → int автоматически"""
	with patch.dict(
		os.environ,
		{
			"SECRET_KEY": "test-secret",
			"ALGORITHM": "HS256",
			"DATABASE_URL": "sqlite:///:memory:",
			"REDIS_URL": "redis://localhost:6379",
			"ACCESS_TOKEN_EXPIRE_MINUTES": "45",
			"REFRESH_TOKEN_EXPIRE_DAYS": "14",
		},
	):
		s = Settings()

		assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 45
		assert isinstance(s.ACCESS_TOKEN_EXPIRE_MINUTES, int)

		assert s.REFRESH_TOKEN_EXPIRE_DAYS == 14
		assert isinstance(s.REFRESH_TOKEN_EXPIRE_DAYS, int)


def test_extra_fields_are_ignored():
	"""extra='ignore' → лишние поля не вызывают ошибку"""
	s = Settings(
		SECRET_KEY="key",
		ALGORITHM="HS256",
		DATABASE_URL="sqlite://",
		REDIS_URL="redis://",
		UNKNOWN_FIELD="should-be-ignored",
	)
	assert not hasattr(s, "UNKNOWN_FIELD")


def test_empty_env_values_are_ignored():
	"""env_ignore_empty=True → пустые строки не перезаписывают значения"""
	with patch.dict(
		os.environ,
		{
			"SECRET_KEY": "",
			"ACCESS_TOKEN_EXPIRE_MINUTES": "",
		},
	):
		s = Settings(
			SECRET_KEY="real-key",
			ALGORITHM="HS256",
			DATABASE_URL="sqlite://",
			REDIS_URL="redis://",
		)

		assert s.SECRET_KEY == "real-key"
		assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
