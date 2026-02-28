import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.models import (
	Analysis,
	MarketData,
	Notification,
	Signal,
	Ticker,
	Watchlist,
	WatchlistItem,
)

pytestmark = pytest.mark.asyncio


async def test_ticker_create_and_read(session: AsyncSession):
	ticker = Ticker(
		symbol="SOLUSDT",
		asset_type="crypto",
		exchange="BINANCE",
		base_currency="SOL",
		quote_currency="USDT",
		is_active=True,
	)
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	assert ticker.id is not None
	assert isinstance(ticker.id, uuid.UUID)
	assert ticker.symbol == "SOLUSDT"
	assert ticker.created_at <= datetime.now(timezone.utc)


async def test_market_data_with_relation(session: AsyncSession):
	ticker = Ticker(symbol="ADAUSDT", asset_type="crypto")
	session.add(ticker)
	await session.flush()

	candle = MarketData(
		ticker_id=ticker.id,
		timeframe="15m",
		timestamp=datetime.now(timezone.utc),
		open=Decimal("1.234"),
		high=Decimal("1.289"),
		low=Decimal("1.210"),
		close=Decimal("1.267"),
		volume=Decimal("845712.6"),
	)
	session.add(candle)
	await session.commit()
	await session.refresh(candle)

	assert candle.ticker_id == ticker.id
	assert candle.close == Decimal("1.267")
	assert candle.timestamp is not None


async def test_analysis_and_signal_chain(session: AsyncSession):
	ticker = Ticker(symbol="LINKUSDT", asset_type="crypto")
	session.add(ticker)
	await session.flush()

	analysis = Analysis(
		ticker_id=ticker.id,
		timeframe="4h",
		model="llama3-70b",
		trend="bearish",
		confidence=0.87,
		summary="Ожидается продолжение снижения после пробоя поддержки",
		raw_llm_output={"reasoning": "...", "verdict": "sell"},
		indicators={"rsi": 68, "macd": {"hist": -0.45}},
	)
	session.add(analysis)
	await session.flush()

	signal = Signal(
		analysis_id=analysis.id,
		ticker_id=ticker.id,
		signal_type="sell",
		strength=0.82,
		entry_price=Decimal("18.45"),
		stop_loss=Decimal("19.80"),
		take_profit=Decimal("15.20"),
		status="new",
		reason="Пробой структуры + дивергенция RSI",
	)
	session.add(signal)
	await session.commit()
	await session.refresh(signal)

	assert signal.analysis_id == analysis.id
	assert signal.entry_price == Decimal("18.45")
	assert signal.status == "new"


async def test_notification_creation(session: AsyncSession):
	ticker = Ticker(symbol="BNBUSDT", asset_type="crypto")
	session.add(ticker)
	await session.flush()

	analysis = Analysis(ticker_id=ticker.id, model="test", trend="neutral")
	session.add(analysis)
	await session.flush()

	signal = Signal(
		analysis_id=analysis.id,
		ticker_id=ticker.id,
		signal_type="buy",
		status="pending",
	)
	session.add(signal)
	await session.flush()

	notif = Notification(
		signal_id=signal.id,
		channel="telegram",
		sent_to="@ swingtrader_group",
		status="sent",
	)
	session.add(notif)
	await session.commit()
	await session.refresh(notif)

	assert notif.signal_id == signal.id
	assert notif.channel == "telegram"
	assert notif.status == "sent"


async def test_watchlist_and_items(session: AsyncSession):
	ticker1 = Ticker(symbol="ETHUSDT", asset_type="crypto")
	ticker2 = Ticker(symbol="BTCUSDT", asset_type="crypto")
	session.add_all([ticker1, ticker2])
	await session.flush()

	watchlist = Watchlist(name="Top Alts 2026", owner_id=uuid.uuid4())
	session.add(watchlist)
	await session.flush()

	item1 = WatchlistItem(watchlist_id=watchlist.id, ticker_id=ticker1.id)
	item2 = WatchlistItem(watchlist_id=watchlist.id, ticker_id=ticker2.id)
	session.add_all([item1, item2])
	await session.commit()

	# проверяем через запрос
	result = await session.execute(
		select(WatchlistItem)
		.where(WatchlistItem.watchlist_id == watchlist.id)
		.order_by(WatchlistItem.ticker_id)
	)
	items = result.scalars().all()

	assert len(items) == 2
	assert {it.ticker_id for it in items} == {ticker1.id, ticker2.id}


async def test_created_at_automatic(session: AsyncSession):
	ticker = Ticker(symbol="TESTUSDT", asset_type="test")
	session.add(ticker)
	await session.commit()
	await session.refresh(ticker)

	delta = datetime.now(timezone.utc) - ticker.created_at
	assert delta.total_seconds() < 5
