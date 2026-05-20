from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from swingtraderai.db.models.user import UserRole


class UserBase(BaseModel):
	username: str = Field(..., min_length=3, max_length=50)
	email: EmailStr
	telegram_id: int | None = None


class UserCreate(UserBase):
	password: str = Field(..., min_length=8, max_length=72)


class UserUpdate(BaseModel):
	username: Optional[str] = Field(None, min_length=3, max_length=50)
	email: Optional[EmailStr] = None
	telegram_id: Optional[int] = None
	telegram_username: Optional[str] = None
	avatar_url: Optional[str] = None
	timezone: Optional[str] = None

	model_config = ConfigDict(extra="forbid")


class UserPasswordUpdate(BaseModel):
	old_password: str
	new_password: str = Field(..., min_length=8, max_length=128)


class UserOut(BaseModel):
	id: UUID
	username: str
	email: EmailStr
	role: UserRole
	telegram_id: Optional[int] = None
	telegram_username: Optional[str] = None
	avatar_url: Optional[str] = None
	is_active: bool
	is_superuser: bool
	created_at: datetime
	last_login: Optional[datetime] = None
	last_login_ip: Optional[str] = None
	timezone: str = "Europe/Moscow"

	watchlist_count: int = 0
	positions_count: int = 0
	active_alerts_count: int = 0
	total_signals_received: int = 0

	model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"


class TokenRefresh(BaseModel):
	refresh_token: str


class TokenData(BaseModel):
	sub: Optional[str] = None
	type: Literal["access", "refresh"]
	exp: Optional[int] = None


class JWTPayload(BaseModel):
	sub: str
	type: str
	exp: datetime
	iat: datetime
	nbf: datetime
	jti: str
