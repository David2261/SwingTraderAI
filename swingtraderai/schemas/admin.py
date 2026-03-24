from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserRole(str):
	"""Доступные роли пользователей"""

	USER = "user"
	TESTER = "tester"
	SUPPORT = "support"
	ADMIN = "admin"


class UserUpdateRole(BaseModel):
	"""
	Схема для изменения роли пользователя
	"""

	role: Literal["user", "tester", "support", "admin"] = Field(
		..., description="Новая роль пользователя"
	)


class UserBanAction(BaseModel):
	"""
	Схема для бана / временного ограничения пользователя
	"""

	is_banned: bool = Field(
		..., description="Заблокировать (true) или разблокировать (false)"
	)
	reason: Optional[str] = Field(
		None,
		max_length=500,
		description="Причина блокировки (обязательно при is_banned=true)",
	)
	banned_until: Optional[datetime] = Field(
		None, description="Дата и время окончания блокировки (если временная)"
	)

	@model_validator(mode="after")
	def validate_ban_fields(self) -> "UserBanAction":
		if self.is_banned:
			if not self.reason:
				raise ValueError("reason is required when banning user")
			if self.banned_until and self.banned_until <= datetime.now(timezone.utc):
				raise ValueError("banned_until must be in the future")
		return self


class UserListFilters(BaseModel):
	"""
	Фильтры для списка пользователей (query-параметры)
	Используется в GET /admin/users
	"""

	skip: int = Field(0, ge=0, description="Смещение (pagination)")
	limit: int = Field(20, ge=1, le=200, description="Количество записей на странице")

	role: Optional[Literal["user", "tester", "support", "admin"]] = Field(
		None, description="Фильтр по роли"
	)
	is_active: Optional[bool] = Field(None, description="Только активные / неактивные")
	is_banned: Optional[bool] = Field(
		None, description="Только забаненные / не забаненные"
	)

	search: Optional[str] = Field(
		None,
		description="Поиск по email, username или telegram_id (частичное совпадение)",
	)
	created_after: Optional[datetime] = Field(
		None, description="Зарегистрированы после этой даты"
	)
	created_before: Optional[datetime] = Field(
		None, description="Зарегистрированы до этой даты"
	)
	last_login_after: Optional[datetime] = Field(
		None, description="Последний вход после этой даты"
	)

	sort_by: Literal[
		"created_at",
		"-created_at",
		"last_login",
		"-last_login",
		"username",
		"-username",
		"email",
		"-email",
	] = Field("-created_at", description="Поле и направление сортировки")


class UserAdminOut(BaseModel):
	"""
	Расширенная схема пользователя для админ-панели
	(больше полей, чем обычный UserOut)
	"""

	model_config = ConfigDict(from_attributes=True)

	id: int
	username: str
	email: EmailStr
	telegram_id: Optional[str]
	role: str
	is_active: bool
	is_banned: bool
	ban_reason: Optional[str]
	banned_until: Optional[datetime]
	created_at: datetime
	updated_at: datetime
	last_login: Optional[datetime]
	signals_received_count: int = 0


class UserBanResponse(BaseModel):
	"""Ответ после бана/разбана"""

	user_id: int
	email: EmailStr
	status: Literal["banned", "unbanned", "temporarily_banned"]
	reason: Optional[str]
	banned_until: Optional[datetime]
	message: str
