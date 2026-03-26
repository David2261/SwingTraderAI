from datetime import datetime
from typing import TYPE_CHECKING, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .auth import UserOut


class WatchlistItem(BaseModel):
	ticker_id: UUID
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


class PortfolioAsset(BaseModel):
	asset_type: str
	value: float
	percent: float
	change_percent: float = 0.0
	change_abs: float = 0.0

	model_config = ConfigDict(from_attributes=True)


class PortfolioSummary(BaseModel):
	total_value: float
	total_change_percent: float
	total_change_abs: float
	assets: List[PortfolioAsset]

	model_config = ConfigDict(from_attributes=True)


class PositionCreate(BaseModel):
	ticker_id: UUID
	position_type: Literal["long", "short"] = "long"
	quantity: float = Field(..., gt=0)
	average_entry_price: float = Field(..., gt=0)
	notes: Optional[str] = None


class PositionUpdate(BaseModel):
	quantity: Optional[float] = Field(None, gt=0)
	average_entry_price: Optional[float] = Field(None, gt=0)
	notes: Optional[str] = None


class PositionOut(BaseModel):
	id: int
	ticker_id: UUID
	symbol: str
	position_type: Literal["long", "short"]
	quantity: float
	average_entry_price: float
	total_cost: float
	current_price: Optional[float] = None
	opened_at: datetime
	notes: Optional[str] = None

	@computed_field
	def current_value(self) -> Optional[float]:
		if self.current_price is None:
			return None
		if self.position_type == "long":
			return self.quantity * self.current_price
		else:
			return -self.quantity * self.current_price

	@computed_field
	def unrealized_pnl(self) -> Optional[float]:
		if self.current_price is None:
			return None

		current_val = self.current_value
		if current_val is None:
			return None

		if self.position_type == "long":
			return (self.current_price - self.average_entry_price) * self.quantity
		else:
			return (self.average_entry_price - self.current_price) * self.quantity

	@computed_field
	def unrealized_pnl_percent(self) -> Optional[float]:
		if self.current_price is None or self.total_cost == 0:
			return None

		if TYPE_CHECKING:
			pnl = self.unrealized_pnl()
		else:
			pnl = self.unrealized_pnl
		if pnl is None:
			return None

		return pnl / abs(self.total_cost) * 100

	model_config = ConfigDict(from_attributes=True)
