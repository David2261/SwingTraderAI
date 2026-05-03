from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from swingtraderai.api.deps import get_current_user
from swingtraderai.api.services.position_service import PositionService
from swingtraderai.api.services.user_service import UserService
from swingtraderai.core.tenant import get_current_tenant_id
from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.system import Watchlist, WatchlistItem
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.auth import UserOut
from swingtraderai.schemas.user import (
	PortfolioAsset,
	PortfolioSummary,
	PositionCreate,
	PositionOut,
	PositionUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
	return UserService(db)


def get_position_service(db: AsyncSession = Depends(get_db)) -> PositionService:
	return PositionService(db)


@router.get("/me", response_model=UserOut)
async def read_users_me(
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	user_service: UserService = Depends(get_user_service),
) -> UserOut:
	"""
	Получение информации о текущем авторизованном пользователе.
	"""
	return UserOut.model_validate(current_user)


@router.get("/{user_id}", response_model=UserOut)
async def read_user(
	user_id: UUID,
	tenant_id: UUID = Depends(get_current_tenant_id),
	user_service: UserService = Depends(get_user_service),
	current_user: User = Depends(get_current_user),
) -> UserOut:
	"""
	Получение информации о пользователе по его ID.
	Доступно только авторизованным пользователям.
	"""
	user = await user_service.get_user_by_id(tenant_id, user_id)
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return UserOut.model_validate(user)


@router.get("/me/portfolio", response_model=PortfolioSummary)
async def get_my_portfolio_summary(
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	# Пока оставляем прямой запрос (сложный CTE), позже вынесем в PortfolioService
	db: AsyncSession = Depends(get_db),
) -> PortfolioSummary:
	"""
	Сводка по портфелю пользователя:
	- суммарная стоимость
	- P&L за день (% и абсолютное)
	- распределение по типам активов
	"""
	user_id = current_user.id
	latest_prices_cte = (
		select(
			MarketData.ticker_id,
			MarketData.close,
			func.row_number()
			.over(
				partition_by=MarketData.ticker_id, order_by=MarketData.timestamp.desc()
			)
			.label("rn"),
		)
		.join(WatchlistItem, WatchlistItem.ticker_id == MarketData.ticker_id)
		.join(Watchlist, WatchlistItem.watchlist_id == Watchlist.id)
		.where(Watchlist.owner_id == user_id)
		.cte("latest_prices")
	)

	curr_price = aliased(latest_prices_cte)
	prev_price = aliased(latest_prices_cte)

	stmt = (
		select(
			Ticker.asset_type,
			func.sum(curr_price.c.close).label("total_value"),
			func.sum(prev_price.c.close).label("prev_value"),
		)
		.join(WatchlistItem, WatchlistItem.ticker_id == Ticker.id)
		.join(Watchlist, WatchlistItem.watchlist_id == Watchlist.id)
		.join(
			curr_price, and_(curr_price.c.ticker_id == Ticker.id, curr_price.c.rn == 1)
		)
		.outerjoin(
			prev_price, and_(prev_price.c.ticker_id == Ticker.id, prev_price.c.rn == 2)
		)
		.where(Watchlist.owner_id == user_id)
		.group_by(Ticker.asset_type)
	)

	result = await db.execute(stmt)
	rows = result.all()

	if not rows:
		return PortfolioSummary(
			total_value=0.0,
			total_change_percent=0.0,
			total_change_abs=0.0,
			assets=[],
		)

	total_value = 0.0
	total_prev_value = 0.0
	assets: List[PortfolioAsset] = []

	for row in rows:
		asset_type, current_sum, prev_sum = row

		asset_value = float(current_sum or 0.0)
		asset_prev = float(prev_sum or 0.0)

		total_value += asset_value
		total_prev_value += asset_prev

		asset_change = asset_value - asset_prev
		asset_change_pct = (asset_change / asset_prev * 100) if asset_prev != 0 else 0.0

		assets.append(
			PortfolioAsset(
				asset_type=asset_type,
				value=asset_value,
				percent=(asset_value / total_value * 100) if total_value != 0 else 0.0,
				change_percent=asset_change_pct,
				change_abs=asset_change,
			)
		)

	total_change_abs = total_value - total_prev_value
	total_change_pct = (
		(total_change_abs / total_prev_value * 100) if total_prev_value != 0 else 0.0
	)

	return PortfolioSummary(
		total_value=total_value,
		total_change_percent=total_change_pct,
		total_change_abs=total_change_abs,
		assets=assets,
	)


@router.post(
	"/me/portfolio/positions",
	response_model=PositionOut,
	status_code=status.HTTP_201_CREATED,
)
async def add_position(
	position_data: PositionCreate,
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	position_service: PositionService = Depends(get_position_service),
) -> PositionOut:
	"""
	Добавление новой позиции в портфель пользователя.
	Проверяет:
	- Существование тикера
	- Отсутствие активной позиции по тому же тикеру и типу
	Рассчитывает общую стоимость позиции с учетом типа (long/short).
	"""
	position = await position_service.add_position(
		tenant_id=tenant_id,
		user_id=current_user.id,
		position_in=position_data,
	)
	return PositionOut.model_validate(position)


@router.put("/me/portfolio/positions/{position_id}", response_model=PositionOut)
async def update_position(
	position_id: UUID,
	position_update: PositionUpdate,
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	position_service: PositionService = Depends(get_position_service),
) -> PositionOut:
	"""Обновление позиции"""
	position = await position_service.update_position(
		tenant_id=tenant_id,
		user_id=current_user.id,
		position_id=position_id,
		position_update=position_update,
	)
	return PositionOut.model_validate(position)


@router.delete(
	"/me/portfolio/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_position(
	position_id: UUID,
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	position_service: PositionService = Depends(get_position_service),
) -> None:
	"""
	Удаление (закрытие) позиции.
	Физически удаляет позицию из БД.
	Проверяет права доступа и существование позиции.
	"""
	success = await position_service.delete_position(
		tenant_id=tenant_id,
		user_id=current_user.id,
		position_id=position_id,
	)
	if not success:
		raise HTTPException(status_code=404, detail="Position not found")
