from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.api.services.watchlist_service import WatchlistService
from swingtraderai.core.tenant import get_current_tenant_id
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.watchlist import (
	WatchlistDataItem,
	WatchlistItemCreate,
	WatchlistItemOut,
	WatchlistItemUpdate,
)

router = APIRouter(prefix="/users/me/watchlist", tags=["watchlist"])


def get_watchlist_service(db: AsyncSession = Depends(get_db)) -> WatchlistService:
	return WatchlistService(db)


@router.post("/items", response_model=WatchlistItemOut, status_code=201)
async def add_to_watchlist(
	item_in: WatchlistItemCreate,
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	watchlist_service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistItemOut:
	"""
	Добавление тикера в список наблюдения текущего пользователя.
	Проверяет:
	- Существование тикера
	- Отсутствие тикера в текущем watchlist
	При необходимости создает новый watchlist для пользователя.
	"""
	item = await watchlist_service.add_item(
		tenant_id=tenant_id,
		user_id=current_user.id,
		item_in=item_in,
	)
	return WatchlistItemOut.model_validate(item)


@router.get("/items", response_model=list[WatchlistItemOut])
async def get_my_watchlist(
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	watchlist_service: WatchlistService = Depends(get_watchlist_service),
) -> list[WatchlistItemOut]:
	"""
	Получение списка всех тикеров в watchlist текущего пользователя.
	Возвращает базовую информацию без ценовых данных.
	"""
	items = await watchlist_service.get_user_items(tenant_id, current_user.id)
	return [WatchlistItemOut.model_validate(i) for i in items]


@router.patch("/items/{item_id}", response_model=WatchlistItemOut)
async def update_watchlist_item(
	item_id: UUID,
	update_data: WatchlistItemUpdate,
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	watchlist_service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistItemOut:
	"""
	Частичное обновление элемента в списке наблюдения.
	Доступно только владельцу списка.
	Сейчас поддерживается только обновление заметок (notes).
	"""
	item = await watchlist_service.update_item(
		tenant_id=tenant_id,
		user_id=current_user.id,
		item_id=item_id,
		update_data=update_data,
	)
	return WatchlistItemOut.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
	item_id: UUID,
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	watchlist_service: WatchlistService = Depends(get_watchlist_service),
) -> None:
	"""
	Удаление тикера из списка наблюдения.
	Проверяет права доступа и существование элемента.
	"""
	await watchlist_service.remove_item(
		tenant_id=tenant_id,
		user_id=current_user.id,
		item_id=item_id,
	)


@router.get("/data", response_model=List[WatchlistDataItem])
async def get_watchlist_with_prices(
	limit: int = Query(50, ge=1, le=200, description="Максимум элементов"),
	sort_by: str = Query(
		"change_percent",
		description="Сортировка: symbol, change_percent, volume, price",
	),
	order: str = Query("desc", description="Порядок: asc / desc"),
	current_user: User = Depends(get_current_user),
	tenant_id: UUID = Depends(get_current_tenant_id),
	watchlist_service: WatchlistService = Depends(get_watchlist_service),
) -> List[WatchlistDataItem]:
	"""
	Возвращает watchlist текущего пользователя с актуальными ценами,
	изменением за день и объёмом.
	Это основной экран для просмотра портфеля/наблюдения.
	"""
	return await watchlist_service.get_watchlist_with_prices(
		tenant_id=tenant_id,
		user_id=current_user.id,
		limit=limit,
		sort_by=sort_by,
		order=order,
	)
