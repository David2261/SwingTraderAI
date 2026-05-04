from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.api.services.portfolio_service import PortfolioService
from swingtraderai.api.services.position_service import PositionService
from swingtraderai.api.services.user_service import UserService
from swingtraderai.core.tenant import get_current_tenant_id
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.auth import UserOut
from swingtraderai.schemas.user import (
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


def get_portfolio_service(db: AsyncSession = Depends(get_db)) -> PortfolioService:
	return PortfolioService(db)


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
	portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioSummary:
	"""
	Сводка по портфелю пользователя:
	- суммарная стоимость
	- P&L за день (% и абсолютное)
	- распределение по типам активов
	"""
	return await portfolio_service.get_portfolio_summary(
		tenant_id=tenant_id, user_id=current_user.id
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
