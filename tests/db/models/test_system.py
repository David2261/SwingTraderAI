import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.models.analysis import Analysis, Signal
from swingtraderai.db.models.market import Ticker
from swingtraderai.db.models.system import Notification, Watchlist, WatchlistItem


@pytest.mark.asyncio
async def test_notification_creation_and_defaults(session: AsyncSession):
	"""Проверка создания Notification + дефолтные значения"""
	ticker = Ticker(symbol="BNBUSDT", asset_type="CRYPTO")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	analysis = Analysis(ticker_id=ticker.id, timeframe="1h")
	session.add(analysis)
	await session.commit()
	await session.refresh(analysis)

	signal = Signal(
		analysis_id=analysis.id, ticker_id=ticker.id, signal_type="LONG", status="new"
	)
	session.add(signal)
	await session.commit()
	await session.refresh(signal)

	notification = Notification(
		signal_id=signal.id, channel="telegram", sent_to="@TraderIvan", status="sent"
	)

	session.add(notification)
	await session.commit()
	await session.refresh(notification)

	assert isinstance(notification.id, uuid.UUID)
	assert notification.signal_id == signal.id
	assert notification.channel == "telegram"
	assert notification.sent_to == "@TraderIvan"
	assert notification.status == "sent"

	assert isinstance(notification.created_at, datetime)
	assert notification.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_notification_minimal_creation(session: AsyncSession):
	"""Минимальное уведомление — проверка nullable полей"""
	ticker = Ticker(symbol="TEST", asset_type="CRYPTO")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	analysis = Analysis(ticker_id=ticker.id)
	session.add(analysis)
	await session.commit()
	await session.refresh(analysis)

	signal = Signal(analysis_id=analysis.id, ticker_id=ticker.id, signal_type="HOLD")
	session.add(signal)
	await session.commit()
	await session.refresh(signal)

	notif = Notification(signal_id=signal.id)
	session.add(notif)
	await session.commit()
	await session.refresh(notif)

	assert notif.channel is None
	assert notif.sent_to is None
	assert notif.status is None


@pytest.mark.asyncio
async def test_foreign_key_violation_notification(session: AsyncSession):
	"""Попытка создать Notification с несуществующим signal_id"""
	fake_signal_id = uuid.uuid4()

	notification = Notification(
		signal_id=fake_signal_id, channel="email", status="failed"
	)
	session.add(notification)

	with pytest.raises(IntegrityError):
		await session.commit()


@pytest.mark.asyncio
async def test_watchlist_and_items_cascade(session: AsyncSession):
	watchlist = Watchlist(name="My Watchlist", owner_id=uuid.uuid4(), items=[])
	session.add(watchlist)
	await session.commit()
	await session.refresh(watchlist)

	t1 = Ticker(symbol="BTCUSDT", asset_type="CRYPTO")
	t2 = Ticker(symbol="ETHUSDT", asset_type="CRYPTO")
	session.add_all([t1, t2])
	await session.commit()

	item1 = WatchlistItem(watchlist_id=watchlist.id, ticker_id=t1.id)
	item2 = WatchlistItem(watchlist_id=watchlist.id, ticker_id=t2.id)
	session.add_all([item1, item2])
	await session.commit()

	stmt = (
		select(Watchlist)
		.options(selectinload(Watchlist.items))
		.where(Watchlist.id == watchlist.id)
	)
	result = await session.execute(stmt)
	watchlist = result.scalar_one()

	assert len(watchlist.items) == 2

	await session.delete(watchlist)
	await session.commit()

	items_left = await session.execute(select(WatchlistItem))
	assert len(items_left.scalars().all()) == 0


@pytest.mark.asyncio
async def test_watchlist_item_relationship(session: AsyncSession):
	wl = Watchlist(name="Test List")
	session.add(wl)
	await session.commit()
	await session.refresh(wl)

	tk = Ticker(symbol="SOLUSDT", asset_type="CRYPTO")
	session.add(tk)
	await session.commit()
	await session.refresh(tk)

	item = WatchlistItem(watchlist_id=wl.id, ticker_id=tk.id)
	session.add(item)
	await session.commit()
	await session.refresh(item)

	assert item.watchlist_id == wl.id
	assert item.watchlist.id == wl.id
	assert item.ticker_id == tk.id
	assert item.ticker.symbol == "SOLUSDT"

	stmt = (
		select(Watchlist)
		.options(selectinload(Watchlist.items))
		.where(Watchlist.id == wl.id)
	)
	result = await session.execute(stmt)
	reloaded_wl = result.scalar_one()

	assert item in reloaded_wl.items


@pytest.mark.asyncio
async def test_watchlist_item_unique_per_watchlist_not_enforced(session: AsyncSession):
	"""
	Важно: в текущей модели НЕТ уникального ограничения
	(один тикер может быть добавлен в watchlist несколько раз)
	Если это нежелательно — нужно добавить UniqueConstraint
	"""
	watchlist = Watchlist(name="Duplicates Test")
	session.add(watchlist)
	await session.commit()
	await session.refresh(watchlist)

	ticker = Ticker(symbol="XLMUSDT", asset_type="CRYPTO")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	item1 = WatchlistItem(watchlist_id=watchlist.id, ticker_id=ticker.id)
	item2 = WatchlistItem(watchlist_id=watchlist.id, ticker_id=ticker.id)

	session.add_all([item1, item2])
	await session.commit()

	stmt = (
		select(Watchlist)
		.options(selectinload(Watchlist.items))
		.where(Watchlist.id == watchlist.id)
	)
	result = await session.execute(stmt)
	reloaded_watchlist = result.scalar_one()

	assert len(reloaded_watchlist.items) == 2

	assert reloaded_watchlist.items[0].id != reloaded_watchlist.items[1].id
