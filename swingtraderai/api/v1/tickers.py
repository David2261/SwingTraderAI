from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.api.services.ticker_service import TickerService
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.ticker import (
	OHLCVDataOut,
	TickerCreate,
	TickerOut,
	TickerSearchOut,
)

router = APIRouter(prefix="/tickers", tags=["tickers"])


def get_ticker_service(db: AsyncSession = Depends(get_db)) -> TickerService:
	return TickerService(db)


@router.post("/", response_model=TickerOut, status_code=201)
async def create_ticker(
	ticker_in: TickerCreate,
	ticker_service: TickerService = Depends(get_ticker_service),
	current_user: User = Depends(get_current_user),
) -> TickerOut:
	"""
	Создание нового тикера.
	Доступно только авторизованным пользователям.
	Проверяет уникальность символа тикера.
	"""
	ticker = await ticker_service.create(ticker_in)
	return TickerOut.model_validate(ticker)


@router.get("/", response_model=List[TickerOut])
async def list_tickers(
	skip: int = 0,
	limit: int = 100,
	ticker_service: TickerService = Depends(get_ticker_service),
) -> List[TickerOut]:
	"""
	Получение списка всех тикеров с пагинацией.
	Возвращает тикеры, отсортированные по символу.
	"""
	tickers = await ticker_service.get_all(skip, limit)
	return [TickerOut.model_validate(t) for t in tickers]


@router.get("/{ticker_id}", response_model=TickerOut)
async def get_ticker(
	ticker_id: UUID, ticker_service: TickerService = Depends(get_ticker_service)
) -> TickerOut:
	"""
	Получение информации о конкретном тикере по его ID.
	Возвращает 404, если тикер не найден.
	"""
	ticker = await ticker_service.get_by_id(ticker_id)
	return TickerOut.model_validate(ticker)


@router.get("/search", response_model=List[TickerSearchOut])
async def search_tickers(
	q: str = Query(..., min_length=1),
	limit: int = Query(20, ge=1, le=100),
	ticker_service: TickerService = Depends(get_ticker_service),
) -> List[TickerSearchOut]:
	"""
	Удобный поиск тикеров для добавления в watchlist.
	Ищет по символу, названию, бирже (LIKE %q%).
	Параметры:
	- q: поисковый запрос (минимальная длина 1 символ)
	- limit: максимальное количество результатов (от 1 до 100)
	"""
	tickers = await ticker_service.search(q, limit)
	return [TickerSearchOut.model_validate(t) for t in tickers]


@router.get("/{ticker_id}/data", response_model=list[OHLCVDataOut])
async def get_ticker_historical_data(
	ticker_id: UUID,
	timeframe: str = Query("1d", description="Таймфрейм: 1m, 5m, 15m, 1h, 1d, 1w..."),
	limit: int = Query(500, ge=1, le=5000, description="Максимум свечей"),
	start_date: Optional[datetime] = Query(None, description="Начальная дата (ISO)"),
	end_date: Optional[datetime] = Query(None, description="Конечная дата (ISO)"),
	ticker_service: TickerService = Depends(get_ticker_service),
) -> List[OHLCVDataOut]:
	"""
	Возвращает исторические OHLCV данные для тикера.
	Идеально для построения графика или таблицы цен.
	Параметры:
	- ticker_id: ID тикера
	- timeframe: таймфрейм свечей (1m, 5m, 1h, 1d и т.д.)
	- limit: максимальное количество свечей (по умолчанию 500)
	- start_date: фильтр по начальной дате
	- end_date: фильтр по конечной дате
	"""
	return await ticker_service.get_historical_data(
		ticker_id=ticker_id,
		timeframe=timeframe,
		limit=limit,
		start_date=start_date,
		end_date=end_date,
	)


@router.post("/bulk", response_model=List[TickerOut], status_code=201)
async def bulk_create_tickers(
	tickers_in: List[TickerCreate],
	ticker_service: TickerService = Depends(get_ticker_service),
	current_user: User = Depends(get_current_user),
) -> List[TickerOut]:
	tickers = await ticker_service.bulk_create(tickers_in)
	return [TickerOut.model_validate(t) for t in tickers]


@router.get("/{ticker_id}/indicators")
async def get_technical_indicators(
	ticker_id: UUID,
	period: str = Query("1h", description="Таймфрейм: 1m, 5m, 15m, 1h, 1d, 1w..."),
	indicators: str = Query(
		..., description="Список индикаторов через запятую: rsi,macd,sma20"
	),
	ticker_service: TickerService = Depends(get_ticker_service),
) -> Dict[str, Any]:
	"""
	Технические индикаторы (SMA, RSI, MACD, Bollinger и т.д.)
	"""
	return await ticker_service.get_technical_indicators(
		ticker_id=ticker_id,
		period=period,
		indicators=indicators,
	)


@router.get("/{ticker_id}/signals")
async def get_trading_signals(
	ticker_id: UUID,
	period: str = Query("1h", description="Таймфрейм для анализа"),
	ticker_service: TickerService = Depends(get_ticker_service),
) -> Dict[str, Any]:
	"""
	Торговые сигналы от ML/AI модели
	"""
	return await ticker_service.get_trading_signals(
		ticker_id=ticker_id,
		period=period,
	)
