from typing import Dict
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.db.session import get_db
from swingtraderai.ml.inference import predict
from swingtraderai.ml.trainer import train_model
from swingtraderai.schemas.prediction import PredictionResult

router = APIRouter(prefix="/ml", tags=["machine-learning"])


@router.post("/train/{ticker_id}")
async def start_training(
	ticker_id: UUID, background_tasks: BackgroundTasks, timeframe: str = "1h"
) -> Dict[str, str]:
	"""
	Запуск обучения модели в фоновом режиме.
	"""
	background_tasks.add_task(train_model, ticker_id=ticker_id, timeframe=timeframe)

	return {"message": f"Обучение для {ticker_id} запущено в фоновом режиме."}


@router.get("/predict/{ticker_id}")
async def get_prediction(
	ticker_id: UUID, timeframe: str = "1h", db: AsyncSession = Depends(get_db)
) -> PredictionResult:
	"""
	Получение прогноза по последним данным из базы.
	"""
	query = text(
		"""
		SELECT time, open, high, low, close, volume
		FROM market_data
		WHERE ticker_id = :ticker_id AND timeframe = :tf
		ORDER BY time DESC LIMIT 150
	"""
	)
	result = await db.execute(query, {"ticker_id": ticker_id, "tf": timeframe})
	rows = result.fetchall()

	if not rows:
		raise HTTPException(status_code=404, detail="Данные для прогноза не найдены")

	df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
	df = df.sort_values("time")

	try:
		prediction_result = await predict(ticker_id, df, timeframe)
		return prediction_result
	except FileNotFoundError as exc:
		raise HTTPException(
			status_code=400, detail="Модель для этого тикера еще не обучена"
		) from exc
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Ошибка инференса: {str(e)}"
		) from e
