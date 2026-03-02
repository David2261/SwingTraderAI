from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from swingtraderai.api.deps import get_current_user
from swingtraderai.db.models.ticker import Ticker, Watchlist, WatchlistItem
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.watchlist import WatchlistItemCreate, WatchlistItemOut

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


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
	)
	items = result.scalars().all()
	return [WatchlistItemOut.from_orm(i) for i in items]


@router.delete("/items/{item_id}")
async def remove_from_watchlist(
	item_id: int,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
	item = await db.get(WatchlistItem, item_id)
	if not item or item.watchlist.owner_id != current_user.id:
		raise HTTPException(
			status_code=404, detail="Watchlist item not found or not owned"
		)

	await db.delete(item)
	await db.commit()
	return {"message": "Removed from watchlist"}
