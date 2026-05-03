from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.repositories.position_repository import PositionRepository
from swingtraderai.db.models.user import Position
from swingtraderai.schemas.user import PositionCreate, PositionUpdate


class PositionService:
	def __init__(self, session: AsyncSession):
		self.repo = PositionRepository(session)

	async def add_position(
		self, tenant_id: UUID, user_id: UUID, position_in: PositionCreate
	) -> Position:
		"""Добавление новой позиции с проверками"""

		from swingtraderai.db.models.market import Ticker

		ticker = await self.repo.session.get(Ticker, position_in.ticker_id)
		if not ticker:
			raise HTTPException(status_code=404, detail="Ticker not found")

		existing = await self.repo.get_active_by_ticker(
			tenant_id, user_id, position_in.ticker_id, position_in.position_type
		)
		if existing:
			raise HTTPException(
				status_code=400,
				detail=f"Active {position_in.position_type} \
                    position for this ticker already exists",
			)

		# Расчёт total_cost
		total_cost = position_in.quantity * position_in.average_entry_price
		if position_in.position_type == "short":
			total_cost = -total_cost

		position_data = {
			"user_id": user_id,
			"ticker_id": position_in.ticker_id,
			"position_type": position_in.position_type,
			"quantity": position_in.quantity,
			"average_buy_price": position_in.average_entry_price,
			"total_cost": total_cost,
			"notes": position_in.notes,
		}

		position = await self.repo.create(tenant_id, position_data)
		return position

	async def get_user_positions(
		self, tenant_id: UUID, user_id: UUID, closed: bool | None = False
	) -> Sequence[Position]:
		return await self.repo.get_all_by_user(tenant_id, user_id, closed=closed)

	async def get_active_by_ticker(
		self, tenant_id: UUID, user_id: UUID, ticker_id: UUID, position_type: str
	) -> Position | None:
		"""Получить активную позицию по тикеру и типу"""
		positions = await self.repo.get_all(
			tenant_id,
			user_id=user_id,
			ticker_id=ticker_id,
			position_type=position_type,
			closed_at=None,
		)
		return positions[0] if positions else None

	async def update_position(
		self,
		tenant_id: UUID,
		user_id: UUID,
		position_id: UUID,
		position_update: PositionUpdate,
	) -> Position:
		position = await self.repo.get_by_id(tenant_id, position_id)
		if not position:
			raise HTTPException(status_code=404, detail="Position not found")

		if position.user_id != user_id:
			raise HTTPException(status_code=403, detail="Not your position")

		if position.closed_at:
			raise HTTPException(status_code=400, detail="Position already closed")

		update_data = position_update.model_dump(exclude_unset=True)

		# Пересчёт total_cost при изменении количества или цены
		if "quantity" in update_data or "average_entry_price" in update_data:
			new_quantity = update_data.get("quantity", position.quantity)
			new_price = update_data.get(
				"average_entry_price", position.average_buy_price
			)
			total_cost = new_quantity * new_price
			if position.position_type == "short":
				total_cost = -total_cost
			update_data["total_cost"] = total_cost

			if "average_entry_price" in update_data:
				update_data["average_buy_price"] = update_data.pop(
					"average_entry_price"
				)

		for key, value in update_data.items():
			setattr(position, key, value)

		await self.repo.session.commit()
		await self.repo.session.refresh(position)
		return position

	async def delete_position(
		self, tenant_id: UUID, user_id: UUID, position_id: UUID
	) -> bool:
		position = await self.repo.get_by_id(tenant_id, position_id)
		if not position:
			raise HTTPException(status_code=404, detail="Position not found")

		if position.user_id != user_id:
			raise HTTPException(status_code=403, detail="Not your position")

		return await self.repo.delete(tenant_id, position_id)
