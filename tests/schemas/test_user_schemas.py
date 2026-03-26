from datetime import datetime
from uuid import UUID

import pytest
from uuid6 import uuid7

from swingtraderai.schemas.user import (
	PortfolioAsset,
	PortfolioSummary,
	PositionCreate,
	PositionOut,
	PositionUpdate,
	UserOutDetailed,
	UserWithWatchlist,
	WatchlistItem,
)


def test_watchlist_item_valid():
	item = WatchlistItem(
		ticker_id=uuid7(),
		symbol_id=123,
		symbol="AAPL",
		added_at=datetime(2025, 3, 20, 10, 30),
	)

	assert item.symbol == "AAPL"
	assert isinstance(item.ticker_id, uuid7().__class__)
	assert isinstance(item.added_at, datetime)


def test_user_with_watchlist():
	user = UserWithWatchlist(
		id=uuid7(),
		username="trader1",
		email="trader@example.com",
		role="user",
		is_active=True,
		is_superuser=False,
		created_at=datetime(2025, 3, 20, 10, 30),
		watchlist=[
			WatchlistItem(
				ticker_id=uuid7(),
				symbol_id=101,
				symbol="BTCUSDT",
				added_at=datetime.now(),
			)
		],
	)

	assert len(user.watchlist) == 1
	assert user.watchlist[0].symbol == "BTCUSDT"
	assert isinstance(user.id, UUID)
	assert user.username == "trader1"
	assert user.role == "user"


def test_user_out_detailed():
	user = UserOutDetailed(
		id=uuid7(),
		username="admin",
		email="admin@swingtrader.ai",
		last_login_ip="192.168.1.100",
		role="user",
		is_active=True,
		is_superuser=False,
		watchlist_count=15,
		created_at=datetime(2025, 2, 20, 10, 30),
		updated_at=datetime(2025, 3, 25, 14, 20),
		watchlist=[],
	)

	assert user.last_login_ip == "192.168.1.100"
	assert user.watchlist_count == 15
	assert user.watchlist == []


def test_portfolio_asset_valid():
	asset = PortfolioAsset(
		asset_type="stock",
		value=15420.75,
		percent=45.3,
		change_percent=2.15,
		change_abs=325.40,
	)

	assert asset.asset_type == "stock"
	assert asset.value == 15420.75
	assert asset.percent == 45.3


def test_portfolio_summary_valid():
	summary = PortfolioSummary(
		total_value=125000.0,
		total_change_percent=3.45,
		total_change_abs=4150.0,
		assets=[
			PortfolioAsset(
				asset_type="crypto", value=45000, percent=36.0, change_percent=5.2
			),
			PortfolioAsset(
				asset_type="stock", value=80000, percent=64.0, change_percent=2.1
			),
		],
	)

	assert summary.total_value == 125000.0
	assert len(summary.assets) == 2
	assert summary.assets[0].asset_type == "crypto"


def test_position_create_valid():
	pos = PositionCreate(
		ticker_id=uuid7(),
		position_type="short",
		quantity=10.5,
		average_entry_price=245.67,
		notes="Short на коррекции",
	)

	assert pos.position_type == "short"
	assert pos.quantity == 10.5
	assert pos.average_entry_price == 245.67


def test_position_create_default_long():
	pos = PositionCreate(ticker_id=uuid7(), quantity=5.0, average_entry_price=100.0)
	assert pos.position_type == "long"


def test_position_create_quantity_must_be_positive():
	with pytest.raises(ValueError):
		PositionCreate(ticker_id=uuid7(), quantity=-1.0, average_entry_price=100.0)


def test_position_update_optional_fields():
	update = PositionUpdate(quantity=15.0, notes="Увеличил позицию")
	assert update.quantity == 15.0
	assert update.average_entry_price is None
	assert update.notes == "Увеличил позицию"


def test_position_out_long_position():
	pos = PositionOut(
		id=1,
		ticker_id=uuid7(),
		symbol="AAPL",
		position_type="long",
		quantity=10,
		average_entry_price=150.0,
		total_cost=1500.0,
		current_price=165.0,
		opened_at=datetime(2025, 3, 1),
	)

	assert pos.current_value == 1650.0
	assert pos.unrealized_pnl == 150.0
	assert pos.unrealized_pnl_percent == 10.0


def test_position_out_short_position():
	pos = PositionOut(
		id=2,
		ticker_id=uuid7(),
		symbol="TSLA",
		position_type="short",
		quantity=5,
		average_entry_price=300.0,
		total_cost=1500.0,
		current_price=280.0,
		opened_at=datetime.now(),
	)

	assert pos.current_value == -1400.0
	assert pos.unrealized_pnl == 100.0
	assert pos.unrealized_pnl_percent == pytest.approx(6.6667, abs=0.001)


def test_position_out_no_current_price():
	"""Если current_price = None, то computed поля должны возвращать None"""
	pos = PositionOut(
		id=3,
		ticker_id=uuid7(),
		symbol="GOOGL",
		position_type="long",
		quantity=2,
		average_entry_price=1000.0,
		total_cost=2000.0,
		current_price=None,
		opened_at=datetime.now(),
	)

	assert pos.current_value is None
	assert pos.unrealized_pnl is None
	assert pos.unrealized_pnl_percent is None


def test_position_out_zero_total_cost():
	pos = PositionOut(
		id=4,
		ticker_id=uuid7(),
		symbol="TEST",
		position_type="long",
		quantity=1,
		average_entry_price=0.0,
		total_cost=0.0,
		current_price=100.0,
		opened_at=datetime.now(),
	)

	assert pos.unrealized_pnl_percent is None


def test_position_out_computed_fields_are_in_model_dump():
	"""Проверяем, что computed fields попадают в model_dump()"""
	pos = PositionOut(
		id=1,
		ticker_id=uuid7(),
		symbol="NVDA",
		position_type="long",
		quantity=10,
		average_entry_price=120.0,
		total_cost=1200.0,
		current_price=135.0,
		opened_at=datetime.now(),
	)

	data = pos.model_dump()

	assert "current_value" in data
	assert "unrealized_pnl" in data
	assert "unrealized_pnl_percent" in data
	assert data["current_value"] == 1350.0
	assert data["unrealized_pnl"] == 150.0
