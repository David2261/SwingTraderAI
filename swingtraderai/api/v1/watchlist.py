from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from swingtraderai.api.deps import get_current_user
from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.system import Watchlist, WatchlistItem
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.watchlist import (
	WatchlistDataItem,
	WatchlistItemCreate,
	WatchlistItemOut,
)

router = APIRouter(prefix="/users/me/watchlist", tags=["watchlist"])


@router.post("/items", response_model=WatchlistItemOut, status_code=201)
async def add_to_watchlist(
	item_in: WatchlistItemCreate,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> WatchlistItemOut:
	ticker = await db.get(Ticker, item_in.ticker_id)
	if not ticker:
		raise HTTPException(status_code=404, detail="Ticker not found")

	existing = await db.execute(
		select(WatchlistItem)
		.join(Watchlist)
		.where(
			Watchlist.owner_id == current_user.id,
			WatchlistItem.ticker_id == item_in.ticker_id,
		)
	)
	if existing.scalar_one_or_none():
		raise HTTPException(status_code=400, detail="Ticker already in watchlist")

	result = await db.execute(
		select(Watchlist).where(Watchlist.owner_id == current_user.id)
	)
	watchlist = result.scalar_one_or_none()
	if not watchlist:
		watchlist = Watchlist(
			owner_id=current_user.id, name=f"{current_user.id}-watchlist"
		)
		db.add(watchlist)
		await db.commit()
		await db.refresh(watchlist)

	item = WatchlistItem(
		watchlist_id=watchlist.id,
		ticker_id=item_in.ticker_id,
	)
	db.add(item)
	await db.commit()
	await db.refresh(item)
	return WatchlistItemOut.from_orm(item)


@router.get("/items", response_model=list[WatchlistItemOut])
async def get_my_watchlist(
	current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[WatchlistItemOut]:
	result = await db.execute(
		select(WatchlistItem)
		.join(Watchlist)
		.where(Watchlist.owner_id == current_user.id)
		.options(joinedload(WatchlistItem.ticker))
		.order_by(WatchlistItem.created_at.desc())
	)
	items = result.scalars().all()
	return [WatchlistItemOut.model_validate(i) for i in items]


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
	item_id: int,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> None:
	stmt = select(WatchlistItem).where(WatchlistItem.id == item_id)
	result = await db.execute(stmt)
	item = result.scalar_one_or_none()
	if not item:
		raise HTTPException(404, "Item not found")

	stmt_owner = select(Watchlist.owner_id).where(Watchlist.id == item.watchlist_id)
	owner_result = await db.execute(stmt_owner)
	owner_id = owner_result.scalar()

	if owner_id != current_user.id:
		raise HTTPException(403, "Not your watchlist item")

	await db.delete(item)
	await db.commit()
	return None


@router.get("/data", response_model=List[WatchlistDataItem])
async def get_watchlist_with_prices(
	limit: int = Query(50, ge=1, le=200, description="Максимум элементов"),
	sort_by: str = Query(
		"change_percent",
		description="Сортировка: symbol, change_percent, volume, price",
	),
	order: str = Query("desc", description="Порядок: asc / desc"),
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> List[WatchlistDataItem]:
	"""
	Возвращает watchlist текущего пользователя с актуальными ценами,
	изменением за день и объёмом.

	Это основной экран для просмотра портфеля/наблюдения.
	"""
	# Базовый запрос: все items watchlist + последний MarketData по каждому тикеру
	subq = (
		select(
			MarketData.ticker_id,
			MarketData.close.label("last_price"),
			MarketData.volume.label("last_volume"),
			MarketData.timestamp,
			func.lag(MarketData.close)
			.over(partition_by=MarketData.ticker_id, order_by=MarketData.timestamp)
			.label("prev_price"),
		).order_by(MarketData.ticker_id, MarketData.timestamp.desc())
	).subquery()

	last_prices = (
		select(subq)
		.distinct(subq.c.ticker_id)
		.order_by(subq.c.ticker_id, subq.c.timestamp.desc())
	).subquery()

	stmt = (
		select(
			WatchlistItem,
			Ticker.symbol,
			Ticker.asset_type,
			last_prices.c.last_price,
			last_prices.c.last_volume,
			last_prices.c.prev_price,
		)
		.join(Watchlist, WatchlistItem.watchlist_id == Watchlist.id)
		.join(Ticker, WatchlistItem.ticker_id == Ticker.id)
		.join(last_prices, last_prices.c.ticker_id == Ticker.id)
		.where(Watchlist.owner_id == current_user.id)
	)

	sort_field: Any = None

	if sort_by == "price":
		sort_field = last_prices.c.last_price
	elif sort_by == "volume":
		sort_field = last_prices.c.last_volume
	elif sort_by == "change_percent":
		sort_field = (
			last_prices.c.last_price - last_prices.c.prev_price
		) / func.nullif(last_prices.c.prev_price, 0)
	else:
		sort_field = Ticker.symbol

	if order.lower() == "asc":
		stmt = stmt.order_by(sort_field.asc())
	else:
		stmt = stmt.order_by(sort_field.desc())

	result = await db.execute(stmt.limit(limit))
	rows = result.all()

	items = []
	for row in rows:
		wi, symbol, a_type, lp, lv, pp = row

		change_abs = float(lp - pp) if lp and pp else 0.0
		change_pct = float((lp - pp) / pp * 100) if lp and pp and pp != 0 else 0.0

		items.append(
			WatchlistDataItem(
				item_id=wi.id,
				ticker_id=wi.ticker_id,
				symbol=symbol,
				asset_type=a_type,
				last_price=float(lp) if lp else None,
				change_percent=change_pct,
				change_abs=change_abs,
				volume=float(lv) if lv else None,
				added_at=wi.created_at,
			)
		)

	return items
