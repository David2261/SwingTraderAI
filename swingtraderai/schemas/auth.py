from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
	username: str = Field(..., min_length=3, max_length=50)
	email: EmailStr
	telegram_id: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
	password: str = Field(..., min_length=8, max_length=72)


class UserUpdate(BaseModel):
	username: Optional[str] = Field(None, min_length=3, max_length=50)
	email: Optional[EmailStr] = None
	telegram_id: Optional[str] = Field(None, max_length=50)
	password: Optional[str] = Field(None, min_length=8, max_length=128)

	model_config = ConfigDict(extra="forbid")


class UserPasswordUpdate(BaseModel):
	old_password: str
	new_password: str = Field(..., min_length=8, max_length=128)


class UserOut(UserBase):
	id: int
	is_active: bool
	is_superuser: bool
	created_at: datetime
	last_login: Optional[datetime] = None

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
