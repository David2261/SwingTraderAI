from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.api.services.indicator_service import IndicatorService
from swingtraderai.api.services.ticker_service import TickerService
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.indicators.registry import registry
from swingtraderai.schemas.indicators import (
	IndicatorRequest,
	SignalOut,
	TechnicalIndicatorsOut,
)

router = APIRouter(prefix="/indicators", tags=["indicators"])


def get_ticker_service(db: AsyncSession = Depends(get_db)) -> TickerService:
	return TickerService(db)


def get_indicator_service(
	ticker_service: TickerService = Depends(get_ticker_service),
) -> IndicatorService:
	return IndicatorService(ticker_service)


# Опционально: все доступные индикаторы
@router.get("/available")
async def list_available_indicators(
	current_user: User = Depends(get_current_user),
) -> Dict[str, List[str]]:
	"""Возвращает список всех доступных индикаторов и их категорий"""
	return {
		"categories": registry.list_categories(),
		"indicators": sorted(registry.list_all()),
	}


@router.get("/{ticker_id}", response_model=TechnicalIndicatorsOut)
async def get_ticker_indicators(
	ticker_id: UUID,
	request: IndicatorRequest = Depends(),
	indicator_service: IndicatorService = Depends(get_indicator_service),
	current_user: User = Depends(get_current_user),
) -> TechnicalIndicatorsOut:
	"""
	Получение технических индикаторов для тикера.

	Примеры запроса:
	- /indicators/{ticker_id}?indicators=ema20,ema50,rsi,macd,bbands,atr
	- /indicators/{ticker_id}?indicators=ema20,rsi&timeframe=15m&limit=300
	"""
	return await indicator_service.get_indicators(
		ticker_id=ticker_id,
		indicators=request.indicators,
		timeframe=request.timeframe,
		limit=request.limit,
	)


@router.get("/{ticker_id}/signals", response_model=List[SignalOut])
async def get_ticker_signals(
	ticker_id: UUID,
	period: str = Query("1h", description="Таймфрейм анализа"),
	indicator_service: IndicatorService = Depends(get_indicator_service),
	current_user: User = Depends(get_current_user),
) -> List[SignalOut]:
	"""
	Получение торговых сигналов (композитных) для тикера.
	"""
	return await indicator_service.get_signals(
		ticker_id=ticker_id,
		period=period,
	)
