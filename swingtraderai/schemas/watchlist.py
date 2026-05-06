from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WatchlistBase(BaseModel):
	name: Optional[str] = None
	owner_id: Optional[UUID] = None


class WatchlistCreate(BaseModel):
	"""Схема для создания нового watchlist"""

	name: str = Field(
		..., min_length=1, max_length=100, description="Название списка наблюдения"
	)
	description: Optional[str] = Field(
		None, max_length=500, description="Описание списка"
	)

	model_config = ConfigDict(from_attributes=True)


class WatchlistUpdate(BaseModel):
	"""Схема для обновления watchlist"""

	name: Optional[str] = Field(None, min_length=1, max_length=100)
	description: Optional[str] = Field(None, max_length=500)

	model_config = ConfigDict(from_attributes=True)


class WatchlistInDB(WatchlistBase):
	"""Полная схема watchlist из БД"""

	id: UUID
	owner_id: UUID
	created_at: datetime
	updated_at: Optional[datetime] = None

	model_config = ConfigDict(from_attributes=True)


class WatchlistOut(WatchlistBase):
	id: UUID
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class WatchlistItemBase(BaseModel):
	watchlist_id: UUID = Field(..., description="ID списка наблюдения")
	ticker_id: UUID = Field(..., description="ID тикера для добавления в список")


class WatchlistItemOut(WatchlistItemBase):
	id: UUID
	notes: Optional[str] = None
	reason: Optional[str] = None
	target_price: Optional[float] = None
	stop_loss: Optional[float] = None
	watchlist_id: UUID
	ticker_id: UUID

	model_config = ConfigDict(from_attributes=True)


class WatchlistItemCreate(WatchlistItemBase):
	"""
	Схема для создания нового элемента в watchlist.
	Можно расширить дополнительными полями при необходимости.
	"""

	notes: Optional[str] = None
	reason: Optional[str] = None
	target_price: Optional[float] = None
	stop_loss: Optional[float] = None


class WatchlistItemUpdate(BaseModel):
	"""Схема для частичного обновления элемента в watchlist"""

	notes: Optional[str] = None
	reason: Optional[str] = None
	target_price: Optional[float] = None
	stop_loss: Optional[float] = None

	model_config = ConfigDict(from_attributes=True)


class WatchlistDataItem(BaseModel):
	item_id: UUID
	ticker_id: UUID
	symbol: str
	asset_type: str
	last_price: Optional[float]
	change_percent: Optional[float]
	change_abs: Optional[float]
	volume: Optional[float]
	added_at: datetime
	notes: Optional[str] = None
	reason: Optional[str] = None
	target_price: Optional[float] = None
	stop_loss: Optional[float] = None
	signals: list[str] = []

	model_config = ConfigDict(from_attributes=True)
