from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.user import Position
from swingtraderai.schemas.user import PortfolioAsset, PortfolioSummary


class PortfolioService:
	"""Сервис для получения сводки по портфелю пользователя"""

	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_portfolio_summary(
		self, tenant_id: UUID, user_id: UUID
	) -> PortfolioSummary:
		"""
		Сводка по портфелю пользователя:
		- суммарная стоимость
		- P&L за день (% и абсолютное)
		- распределение по типам активов
		"""

		# Последняя цена по каждому тикеру
		latest_price_cte = select(
			MarketData.ticker_id,
			MarketData.close.label("current_price"),
			func.row_number()
			.over(
				partition_by=MarketData.ticker_id,
				order_by=MarketData.timestamp.desc(),
			)
			.label("rn"),
		).cte("latest_prices")

		curr_price = aliased(latest_price_cte)

		# Основной запрос
		stmt = (
			select(
				Position,
				Ticker.asset_type,
				curr_price.c.current_price,
			)
			.join(Ticker, Position.ticker_id == Ticker.id)
			.outerjoin(
				curr_price,
				and_(
					curr_price.c.ticker_id == Position.ticker_id,
					curr_price.c.rn == 1,
				),
			)
			.where(
				Position.tenant_id == tenant_id,
				Position.user_id == user_id,
				Position.closed_at.is_(None),
			)
		)

		result = await self.session.execute(stmt)
		rows = result.all()

		if not rows:
			return PortfolioSummary(
				total_value=0.0,
				total_change_percent=0.0,
				total_change_abs=0.0,
				assets=[],
			)

		total_value = Decimal("0")
		total_unrealized_pnl = Decimal("0")
		assets_dict: dict[str, dict[str, Decimal]] = {}

		for position, asset_type, current_price in rows:
			if current_price is None:
				position_value = Decimal("0")
				unrealized_pnl = Decimal("0")
			else:
				current_price = Decimal(str(current_price or 0))
				qty = Decimal(str(position.quantity))
				avg_price = Decimal(str(position.average_buy_price))

				if position.position_type == "long":
					position_value = qty * current_price
					unrealized_pnl = (current_price - avg_price) * qty
				else:
					position_value = qty * current_price
					unrealized_pnl = (avg_price - current_price) * qty

				total_value += position_value
				total_unrealized_pnl += unrealized_pnl

				if asset_type not in assets_dict:
					assets_dict[asset_type] = {
						"value": Decimal("0"),
						"pnl": Decimal("0"),
					}

				assets_dict[asset_type]["value"] += position_value
				assets_dict[asset_type]["pnl"] += unrealized_pnl

		assets: List[PortfolioAsset] = []
		for asset_type, data in assets_dict.items():
			value = float(data["value"])
			pnl = float(data["pnl"])

			assets.append(
				PortfolioAsset(
					asset_type=asset_type,
					value=value,
					percent=(
						(value / float(total_value) * 100) if total_value > 0 else 0.0
					),
					change_percent=0.0,
					change_abs=pnl,
				)
			)

		total_change_abs = float(total_unrealized_pnl)
		total_change_pct = (
			(total_change_abs / float(total_value) * 100) if total_value > 0 else 0.0
		)

		return PortfolioSummary(
			total_value=float(total_value),
			total_change_percent=total_change_pct,
			total_change_abs=total_change_abs,
			assets=assets,
		)
