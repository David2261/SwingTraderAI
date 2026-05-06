from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from uuid6 import uuid7

from swingtraderai.api.services.watchlist_service import WatchlistService
from swingtraderai.db.models.market import MarketData
from swingtraderai.db.models.system import WatchlistItem
from swingtraderai.schemas.watchlist import WatchlistItemCreate, WatchlistItemUpdate


@pytest.fixture
async def watchlist_service(session):
	return WatchlistService(session)


def test_check_signal_target_hit(watchlist_service):
	item = WatchlistItem(target_price=Decimal("150.0"), stop_loss=None)
	signals = watchlist_service.check_signal(item, 152.5)
	assert signals == ["TARGET_HIT"]


def test_check_signal_stop_loss_hit(watchlist_service):
	item = WatchlistItem(target_price=None, stop_loss=Decimal("100.0"))
	signals = watchlist_service.check_signal(item, 98.0)
	assert signals == ["STOP_LOSS_HIT"]


def test_check_signal_both_hit(watchlist_service):
	item = WatchlistItem(target_price=Decimal("150"), stop_loss=Decimal("100"))
	signals = watchlist_service.check_signal(item, 155.0)
	assert signals == ["TARGET_HIT"]


def test_check_signal_no_signals(watchlist_service):
	item = WatchlistItem(target_price=Decimal("150"), stop_loss=Decimal("100"))
	signals = watchlist_service.check_signal(item, 120.0)
	assert signals == []


async def test_add_item_success(watchlist_service, user, ticker, watchlist):
	item_in = WatchlistItemCreate(
		ticker_id=ticker.id,
		watchlist_id=watchlist.id,
		notes="Strong buy setup",
		reason="Breakout from resistance",
		target_price=Decimal("230.0"),
		stop_loss=Decimal("195.0"),
	)

	item = await watchlist_service.add_item(user.tenant_id, user.id, item_in)

	assert item.ticker_id == ticker.id
	assert item.notes == "Strong buy setup"
	assert item.target_price == Decimal("230.0")
	assert item.stop_loss == Decimal("195.0")


async def test_add_item_ticker_not_found(watchlist_service, user):
	item_in = WatchlistItemCreate(ticker_id=uuid7(), watchlist_id=uuid7())

	with pytest.raises(HTTPException) as exc:
		await watchlist_service.add_item(user.tenant_id, user.id, item_in)
	assert exc.value.status_code == 404
	assert "Ticker not found" in exc.value.detail


async def test_add_item_already_in_watchlist(
	watchlist_service, user, ticker, watchlist
):
	item_in = WatchlistItemCreate(ticker_id=ticker.id, watchlist_id=watchlist.id)
	await watchlist_service.add_item(user.tenant_id, user.id, item_in)

	# Повторное добавление
	with pytest.raises(HTTPException) as exc:
		await watchlist_service.add_item(user.tenant_id, user.id, item_in)
	assert exc.value.status_code == 400
	assert "already in watchlist" in exc.value.detail.lower()


async def test_get_user_items(watchlist_service, user, ticker, watchlist):
	await watchlist_service.add_item(
		user.tenant_id,
		user.id,
		WatchlistItemCreate(
			ticker_id=ticker.id, watchlist_id=watchlist.id, notes="Test"
		),
	)

	items = await watchlist_service.get_user_items(user.tenant_id, user.id)
	assert len(items) == 1
	assert items[0].ticker_id == ticker.id


async def test_update_item_success(watchlist_service, user, ticker, watchlist):
	# Создаём item
	item = await watchlist_service.add_item(
		user.tenant_id,
		user.id,
		WatchlistItemCreate(ticker_id=ticker.id, watchlist_id=watchlist.id),
	)

	update_data = WatchlistItemUpdate(
		target_price=Decimal("250.0"), stop_loss=Decimal("200.0"), notes="Updated note"
	)

	updated = await watchlist_service.update_item(
		user.tenant_id, user.id, item.id, update_data
	)

	assert updated.target_price == Decimal("250.0")
	assert updated.stop_loss == Decimal("200.0")
	assert updated.notes == "Updated note"


async def test_update_item_not_found(watchlist_service, user):
	with pytest.raises(HTTPException) as exc:
		await watchlist_service.update_item(
			user.tenant_id, user.id, uuid7(), WatchlistItemUpdate()
		)
	assert exc.value.status_code == 404


async def test_update_item_forbidden(watchlist_service, user, ticker, watchlist):
	item = await watchlist_service.add_item(
		user.tenant_id,
		user.id,
		WatchlistItemCreate(ticker_id=ticker.id, watchlist_id=watchlist.id),
	)

	other_user_id = uuid7()

	with pytest.raises(HTTPException) as exc:
		await watchlist_service.update_item(
			user.tenant_id, other_user_id, item.id, WatchlistItemUpdate(notes="hack")
		)
	assert exc.value.status_code == 403


async def test_remove_item_success(watchlist_service, user, ticker, watchlist):
	item = await watchlist_service.add_item(
		user.tenant_id,
		user.id,
		WatchlistItemCreate(ticker_id=ticker.id, watchlist_id=watchlist.id),
	)

	deleted = await watchlist_service.remove_item(user.tenant_id, user.id, item.id)
	assert deleted is True

	items = await watchlist_service.get_user_items(user.tenant_id, user.id)
	assert len(items) == 0


async def test_get_watchlist_with_prices(
	watchlist_service, user, ticker, watchlist, session
):
	from datetime import datetime, timezone
	from decimal import Decimal

	market_data = MarketData(
		ticker_id=ticker.id,
		timeframe="1d",
		timestamp=datetime.now(timezone.utc),
		open=Decimal("150.0"),
		high=Decimal("160.0"),
		low=Decimal("145.0"),
		close=Decimal("155.0"),
		volume=Decimal("1000000"),
		source="test",
	)
	session.add(market_data)

	market_data_prev = MarketData(
		ticker_id=ticker.id,
		timeframe="1d",
		timestamp=datetime.now(timezone.utc) - timedelta(days=1),
		open=Decimal("145.0"),
		high=Decimal("155.0"),
		low=Decimal("140.0"),
		close=Decimal("150.0"),
		volume=Decimal("950000"),
		source="test",
	)
	session.add(market_data_prev)
	await session.flush()

	await watchlist_service.add_item(
		user.tenant_id,
		user.id,
		WatchlistItemCreate(
			ticker_id=ticker.id,
			watchlist_id=watchlist.id,
			target_price=Decimal("160"),
			stop_loss=Decimal("140"),
		),
	)

	items = await watchlist_service.get_watchlist_with_prices(
		tenant_id=user.tenant_id, user_id=user.id, limit=10, sort_by="change_percent"
	)

	assert len(items) >= 1
	item = items[0]

	assert item.symbol == ticker.symbol
	assert item.last_price is not None
	assert item.change_percent == 3.3333333333333335
	assert isinstance(item.signals, list)


async def test_get_watchlist_with_prices_empty(watchlist_service, user):
	items = await watchlist_service.get_watchlist_with_prices(user.tenant_id, user.id)
	assert items == []


async def test_get_watchlist_with_prices_sorting(
	watchlist_service, user, ticker, watchlist, session
):
	from datetime import datetime, timezone
	from decimal import Decimal

	market_data = MarketData(
		ticker_id=ticker.id,
		timeframe="1d",
		timestamp=datetime.now(timezone.utc),
		open=Decimal("150.0"),
		high=Decimal("160.0"),
		low=Decimal("145.0"),
		close=Decimal("155.0"),
		volume=Decimal("1000000"),
		source="test",
	)
	session.add(market_data)

	market_data_prev = MarketData(
		ticker_id=ticker.id,
		timeframe="1d",
		timestamp=datetime.now(timezone.utc) - timedelta(days=1),
		open=Decimal("145.0"),
		high=Decimal("155.0"),
		low=Decimal("140.0"),
		close=Decimal("150.0"),
		volume=Decimal("950000"),
		source="test",
	)
	session.add(market_data_prev)
	await session.flush()

	await watchlist_service.add_item(
		user.tenant_id,
		user.id,
		WatchlistItemCreate(ticker_id=ticker.id, watchlist_id=watchlist.id),
	)

	items_price = await watchlist_service.get_watchlist_with_prices(
		user.tenant_id, user.id, sort_by="price", order="desc"
	)

	items_change = await watchlist_service.get_watchlist_with_prices(
		user.tenant_id, user.id, sort_by="change_percent", order="asc"
	)

	assert len(items_price) == len(items_change) == 1
	assert items_price[0].symbol == ticker.symbol
	assert items_change[0].symbol == ticker.symbol
