from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .auth import UserOut


class WatchlistItem(BaseModel):
	symbol_id: int
	symbol: str
	added_at: datetime

	model_config = ConfigDict(from_attributes=True)


class UserWithWatchlist(UserOut):
	watchlist: List[WatchlistItem] = Field(default_factory=list)

	model_config = ConfigDict(from_attributes=True)


class UserOutDetailed(UserOut):
	"""Расширенный вывод пользователя (для админа или профиля)"""

	last_login_ip: Optional[str] = None
	watchlist: List[WatchlistItem] = Field(default_factory=list)
	watchlist_count: Optional[int] = None
	updated_at: Optional[datetime] = None
