from typing import List
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from swingtraderai.db.models.market import MarketData, Ticker
from swingtraderai.db.models.system import Watchlist, WatchlistItem
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
		latest_prices_cte = (
			select(
				MarketData.ticker_id,
				MarketData.close,
				func.row_number()
				.over(
					partition_by=MarketData.ticker_id,
					order_by=MarketData.timestamp.desc(),
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
				curr_price,
				and_(curr_price.c.ticker_id == Ticker.id, curr_price.c.rn == 1),
			)
			.outerjoin(
				prev_price,
				and_(prev_price.c.ticker_id == Ticker.id, prev_price.c.rn == 2),
			)
			.where(Watchlist.owner_id == user_id)
			.group_by(Ticker.asset_type)
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
			asset_change_pct = (
				(asset_change / asset_prev * 100) if asset_prev != 0 else 0.0
			)

			assets.append(
				PortfolioAsset(
					asset_type=asset_type,
					value=asset_value,
					percent=(
						(asset_value / total_value * 100) if total_value != 0 else 0.0
					),
					change_percent=asset_change_pct,
					change_abs=asset_change,
				)
			)

		total_change_abs = total_value - total_prev_value
		total_change_pct = (
			(total_change_abs / total_prev_value * 100)
			if total_prev_value != 0
			else 0.0
		)

		return PortfolioSummary(
			total_value=total_value,
			total_change_percent=total_change_pct,
			total_change_abs=total_change_abs,
			assets=assets,
		)
