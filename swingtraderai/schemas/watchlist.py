from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WatchlistBase(BaseModel):
	name: Optional[str] = None
	owner_id: Optional[UUID] = None


class WatchlistOut(WatchlistBase):
	id: UUID
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class WatchlistItemBase(BaseModel):
	watchlist_id: UUID = Field(..., description="ID списка наблюдения")
	ticker_id: UUID = Field(..., description="ID тикера для добавления в список")


class WatchlistItemOut(WatchlistItemBase):
	id: UUID
	watchlist_id: UUID
	ticker_id: UUID

	model_config = ConfigDict(from_attributes=True)


class WatchlistItemCreate(WatchlistItemBase):
	"""
	Схема для создания нового элемента в watchlist.
	Можно расширить дополнительными полями при необходимости.
	"""

	pass
