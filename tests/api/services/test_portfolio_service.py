from datetime import datetime, timezone
from decimal import Decimal

import pytest

from swingtraderai.api.services.portfolio_service import PortfolioService
from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.user import Position
from swingtraderai.schemas.user import PortfolioSummary


@pytest.fixture
async def portfolio_service(session):
	return PortfolioService(session)


@pytest.fixture
async def ticker_aapl(session):
	"""Тикер AAPL"""
	ticker = Ticker(
		symbol="AAPL",
		asset_type="stock",
		exchange_id=None,
		base_currency="USD",
		quote_currency="USD",
		is_active=True,
	)
	session.add(ticker)
	await session.flush()
	await session.refresh(ticker)
	return ticker


@pytest.fixture
async def ticker_btc(session):
	"""Тикер BTC (крипта)"""
	ticker = Ticker(
		symbol="BTCUSDT",
		asset_type="crypto",
		exchange_id=None,
		base_currency="BTC",
		quote_currency="USD",
		is_active=True,
	)
	session.add(ticker)
	await session.flush()
	await session.refresh(ticker)
	return ticker


@pytest.fixture
async def market_data(session, ticker_aapl, ticker_btc):
	"""Последние цены для тикеров"""
	data = [
		MarketData(
			ticker_id=ticker_aapl.id,
			close=Decimal("225.50"),
			timestamp=datetime(2025, 5, 5, 10, 0, 0),
		),
		MarketData(
			ticker_id=ticker_btc.id,
			close=Decimal("63500.00"),
			timestamp=datetime(2025, 5, 5, 10, 0, 0),
		),
	]
	session.add_all(data)
	await session.flush()
	return data


async def test_empty_portfolio(portfolio_service, user):
	"""Портфель пустой — должны вернуть нули"""
	result: PortfolioSummary = await portfolio_service.get_portfolio_summary(
		tenant_id=user.tenant_id, user_id=user.id
	)

	assert result.total_value == 0.0
	assert result.total_change_percent == 0.0
	assert result.total_change_abs == 0.0
	assert result.assets == []


async def test_long_position(portfolio_service, user, ticker_aapl, market_data):
	"""Тест длинной позиции"""
	quantity = Decimal("10")
	avg_price = Decimal("210.00")
	total_cost = quantity * avg_price

	position = Position(
		tenant_id=user.tenant_id,
		user_id=user.id,
		ticker_id=ticker_aapl.id,
		position_type="long",
		quantity=quantity,
		average_buy_price=avg_price,
		total_cost=total_cost,
		opened_at=datetime(2025, 5, 1),
	)
	session = portfolio_service.session
	session.add(position)
	await session.commit()

	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)

	expected_value = 10 * 225.50
	expected_change_abs = expected_value - float(total_cost)
	expected_change_percent = (expected_change_abs / expected_value) * 100

	assert result.total_value == pytest.approx(expected_value, rel=1e-5)
	assert result.total_change_abs == pytest.approx(expected_change_abs, rel=1e-5)
	assert result.total_change_percent == pytest.approx(
		expected_change_percent, rel=1e-5
	)

	assert len(result.assets) == 1
	asset = result.assets[0]
	assert asset.asset_type == "stock"
	assert asset.value == pytest.approx(expected_value)
	assert asset.change_abs == pytest.approx(expected_change_abs)
	assert asset.percent == pytest.approx(100.0)


async def test_short_position(portfolio_service, user, ticker_aapl, market_data):
	"""Тест короткой позиции"""
	quantity = Decimal("5")
	avg_price = Decimal("240.00")
	total_cost = quantity * avg_price  # 1200

	position = Position(
		tenant_id=user.tenant_id,
		user_id=user.id,
		ticker_id=ticker_aapl.id,
		position_type="short",
		quantity=quantity,
		average_buy_price=avg_price,
		total_cost=total_cost,
		opened_at=datetime(2025, 5, 1),
	)
	session = portfolio_service.session
	session.add(position)
	await session.commit()

	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)

	current_price = 225.50
	expected_value = quantity * Decimal(str(current_price))
	expected_change_abs = float((avg_price - Decimal(str(current_price))) * quantity)
	expected_change_percent = (expected_change_abs / float(expected_value)) * 100

	assert result.total_value == pytest.approx(float(expected_value), rel=1e-5)
	assert result.total_change_abs == pytest.approx(expected_change_abs, rel=1e-5)
	assert result.total_change_percent == pytest.approx(
		expected_change_percent, rel=1e-4
	)

	assert len(result.assets) == 1
	asset = result.assets[0]
	assert asset.asset_type == "stock"
	assert asset.value == pytest.approx(float(expected_value))
	assert asset.change_abs == pytest.approx(expected_change_abs)
	assert asset.percent == pytest.approx(100.0)


async def test_mixed_positions(
	portfolio_service, user, ticker_aapl, ticker_btc, market_data
):
	"""Смесь long + short + разные asset_type"""
	aapl_quantity = Decimal("20")
	aapl_avg_price = Decimal("200.0")
	aapl_total_cost = aapl_quantity * aapl_avg_price
	aapl_current_value = aapl_quantity * Decimal("225.50")
	aapl_pnl = aapl_current_value - aapl_total_cost

	btc_quantity = Decimal("0.5")
	btc_avg_price = Decimal("65000.0")
	btc_total_cost = btc_quantity * btc_avg_price
	btc_current_value = btc_quantity * Decimal("63500.00")
	btc_pnl = btc_total_cost - btc_current_value

	positions = [
		Position(
			tenant_id=user.tenant_id,
			user_id=user.id,
			ticker_id=ticker_aapl.id,
			position_type="long",
			quantity=aapl_quantity,
			average_buy_price=aapl_avg_price,
			total_cost=aapl_total_cost,
		),
		Position(
			tenant_id=user.tenant_id,
			user_id=user.id,
			ticker_id=ticker_btc.id,
			position_type="short",
			quantity=btc_quantity,
			average_buy_price=btc_avg_price,
			total_cost=btc_total_cost,
		),
	]

	session = portfolio_service.session
	session.add_all(positions)
	await session.commit()

	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)

	assert len(result.assets) == 2

	stock_asset = next(a for a in result.assets if a.asset_type == "stock")
	crypto_asset = next(a for a in result.assets if a.asset_type == "crypto")

	assert stock_asset.value == pytest.approx(4510.0)
	assert crypto_asset.value == pytest.approx(31750.0)

	total_value = 4510.0 + 31750.0
	total_pnl = aapl_pnl + btc_pnl
	total_change_percent = (float(total_pnl) / float(total_value)) * 100

	assert result.total_value == pytest.approx(total_value, rel=1e-5)
	assert result.total_change_abs == pytest.approx(float(total_pnl), rel=1e-5)
	assert result.total_change_percent == pytest.approx(total_change_percent, rel=1e-5)


async def test_position_without_current_price(portfolio_service, user, ticker_aapl):
	"""Позиция без текущей цены в MarketData"""
	quantity = Decimal("10")
	avg_price = Decimal("210.0")
	total_cost = quantity * avg_price

	position = Position(
		tenant_id=user.tenant_id,
		user_id=user.id,
		ticker_id=ticker_aapl.id,
		position_type="long",
		quantity=quantity,
		average_buy_price=avg_price,
		total_cost=total_cost,
	)
	session = portfolio_service.session
	session.add(position)
	await session.commit()

	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)

	assert result.total_value == 0.0
	assert result.total_change_abs == 0.0
	assert len(result.assets) == 0


async def test_zero_quantity_position(portfolio_service, user, ticker_aapl):
	"""Позиция с нулевым количеством (не должна ломать)"""
	quantity = Decimal("10")
	avg_price = Decimal("210.0")
	total_cost = quantity * avg_price
	position = Position(
		tenant_id=user.tenant_id,
		user_id=user.id,
		ticker_id=ticker_aapl.id,
		position_type="long",
		quantity=quantity,
		average_buy_price=avg_price,
		total_cost=total_cost,
	)
	session = portfolio_service.session
	session.add(position)
	await session.commit()

	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)
	assert result.total_value == 0.0


async def test_total_value_zero_division_avoided(portfolio_service, user):
	"""Защита от деления на ноль при total_value = 0"""
	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)
	assert result.total_change_percent == 0.0


async def test_multiple_tickers_same_type(portfolio_service, user, ticker_aapl):
	"""Несколько позиций по одному типу актива"""
	pos1_quantity = Decimal("10")
	pos1_avg_price = Decimal("200")
	pos1_total_cost = pos1_quantity * pos1_avg_price
	position1 = Position(
		tenant_id=user.tenant_id,
		user_id=user.id,
		ticker_id=ticker_aapl.id,
		position_type="long",
		quantity=pos1_quantity,
		average_buy_price=pos1_avg_price,
		total_cost=pos1_total_cost,
		closed_at=datetime(2025, 5, 4, tzinfo=timezone.utc),
		opened_at=datetime(2025, 5, 1, tzinfo=timezone.utc),
	)

	pos2_quantity = Decimal("5")
	pos2_avg_price = Decimal("220")
	pos2_total_cost = pos2_quantity * pos2_avg_price

	position2 = Position(
		tenant_id=user.tenant_id,
		user_id=user.id,
		ticker_id=ticker_aapl.id,
		position_type="long",
		quantity=pos2_quantity,
		average_buy_price=pos2_avg_price,
		total_cost=pos2_total_cost,
		opened_at=datetime(2025, 5, 5, tzinfo=timezone.utc),
	)

	session = portfolio_service.session
	session.add_all([position1, position2])
	await session.commit()

	current_price = Decimal("230")
	md = MarketData(
		ticker_id=ticker_aapl.id,
		close=current_price,
		timestamp=datetime(2025, 5, 5, 10, 0, 0, tzinfo=timezone.utc),
	)
	session.add(md)
	await session.commit()

	result = await portfolio_service.get_portfolio_summary(user.tenant_id, user.id)

	assert len(result.assets) == 1
	assert result.assets[0].asset_type == "stock"
	assert result.assets[0].value == 1150.0
	assert result.total_value == 1150.0
	assert result.total_change_abs == 50.0
