import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.watchlist_repository import (
	WatchlistItemRepository,
	WatchlistRepository,
)
from swingtraderai.db.models.system import Watchlist, WatchlistItem


@pytest.fixture
def watchlist_repo(session: AsyncSession):
	return WatchlistRepository(session)


@pytest.fixture
def watchlist_item_repo(session: AsyncSession):
	return WatchlistItemRepository(session)


async def test_get_by_owner_success(watchlist_repo, user, session):
	watchlist = Watchlist(
		tenant_id=user.tenant_id, owner_id=user.id, name="My Main Watchlist"
	)
	session.add(watchlist)
	await session.commit()

	result = await watchlist_repo.get_by_owner(user.tenant_id, user.id)
	assert result is not None
	assert result.id == watchlist.id
	assert result.name == "My Main Watchlist"


async def test_get_by_owner_not_found(watchlist_repo, user):
	result = await watchlist_repo.get_by_owner(user.tenant_id, user.id)
	assert result is None


async def test_get_or_create_default_creates_new(watchlist_repo, user):
	result = await watchlist_repo.get_or_create_default(
		tenant_id=user.tenant_id, user_id=user.id, name="Custom Watchlist"
	)

	assert result is not None
	assert result.owner_id == user.id
	assert result.tenant_id == user.tenant_id
	assert result.name == "Custom Watchlist"


async def test_get_or_create_default_returns_existing(watchlist_repo, user, session):
	existing = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Existing WL")
	session.add(existing)
	await session.commit()

	result = await watchlist_repo.get_or_create_default(user.tenant_id, user.id)

	assert result.id == existing.id
	assert result.name == "Existing WL"


async def test_get_user_watchlist_items(
	watchlist_item_repo, user, sample_ticker, session
):
	# Создаём watchlist и item
	wl = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Test WL")
	session.add(wl)
	await session.flush()

	item = WatchlistItem(
		tenant_id=user.tenant_id,
		watchlist_id=wl.id,
		ticker_id=sample_ticker.id,
		notes="Test note",
	)
	session.add(item)
	await session.commit()

	items = await watchlist_item_repo.get_user_watchlist_items(user.tenant_id, user.id)

	assert len(items) == 1
	assert items[0].ticker_id == sample_ticker.id
	assert items[0].notes == "Test note"
	assert items[0].ticker is not None  # joinedload сработал


async def test_get_by_ticker_found(watchlist_item_repo, user, sample_ticker, session):
	wl = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Test WL")
	session.add(wl)
	await session.flush()

	item = WatchlistItem(
		tenant_id=user.tenant_id, watchlist_id=wl.id, ticker_id=sample_ticker.id
	)
	session.add(item)
	await session.commit()

	found = await watchlist_item_repo.get_by_ticker(
		user.tenant_id, user.id, sample_ticker.id
	)

	assert found is not None
	assert found.ticker_id == sample_ticker.id


async def test_get_by_ticker_not_found(watchlist_item_repo, user, sample_ticker):
	result = await watchlist_item_repo.get_by_ticker(
		user.tenant_id, user.id, sample_ticker.id
	)
	assert result is None


async def test_get_by_watchlist(watchlist_item_repo, user, sample_ticker, session):
	wl = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Test WL")
	session.add(wl)
	await session.flush()

	for i in range(3):
		item = WatchlistItem(
			tenant_id=user.tenant_id,
			watchlist_id=wl.id,
			ticker_id=sample_ticker.id,
			notes=f"Item {i}",
		)
		session.add(item)

	await session.commit()

	items = await watchlist_item_repo.get_by_watchlist(user.tenant_id, wl.id)
	assert len(items) == 3


async def test_create_watchlist_item_success(
	watchlist_item_repo, user, sample_ticker, session
):
	wl = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Test WL")
	session.add(wl)
	await session.commit()

	item = await watchlist_item_repo.create_watchlist_item(
		tenant_id=user.tenant_id,
		watchlist_id=wl.id,
		ticker_id=sample_ticker.id,
		notes="Great setup",
		target_price=150.5,
		stop_loss=130.0,
	)

	assert item.watchlist_id == wl.id
	assert item.ticker_id == sample_ticker.id
	assert item.notes == "Great setup"
	assert item.target_price == 150.5


async def test_create_watchlist_item_duplicate_raises_error(
	watchlist_item_repo, user, sample_ticker, session
):
	wl = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Test WL")
	session.add(wl)
	await session.commit()

	await watchlist_item_repo.create_watchlist_item(
		user.tenant_id, wl.id, sample_ticker.id
	)

	with pytest.raises(ValueError) as exc:
		await watchlist_item_repo.create_watchlist_item(
			user.tenant_id, wl.id, sample_ticker.id
		)
	assert "already in watchlist" in str(exc.value)


async def test_create_watchlist_if_not_exists_creates_new(watchlist_item_repo, user):
	watchlist = await watchlist_item_repo.create_watchlist_if_not_exists(
		user.tenant_id, user.id, name="My Custom WL"
	)

	assert watchlist.owner_id == user.id
	assert watchlist.name == "My Custom WL"


async def test_create_watchlist_if_not_exists_returns_existing(
	watchlist_item_repo, user, session
):
	existing = Watchlist(tenant_id=user.tenant_id, owner_id=user.id, name="Old WL")
	session.add(existing)
	await session.commit()

	result = await watchlist_item_repo.create_watchlist_if_not_exists(
		user.tenant_id, user.id
	)

	assert result.id == existing.id
