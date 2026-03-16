from datetime import datetime
from pathlib import Path
from typing import Any, Dict, TypeGuard
from uuid import UUID

import joblib

from swingtraderai.schemas.prediction import ModelDataSchema, ModelMetadata


def is_model_data(obj: Any) -> TypeGuard[Dict[str, Any]]:
	"""Проверяет, является ли объект словарем."""
	return isinstance(obj, dict)


def load_latest_model(ticker_id: UUID, timeframe: str = "1h") -> ModelDataSchema:
	"""
	Загружает последнюю версию модели и сопутствующие данные.
	"""
	model_dir = Path(f"models/xgboost/{ticker_id}")

	if not model_dir.exists():
		raise FileNotFoundError(f"Директория для тикера {ticker_id} не найдена!")

	files = list(model_dir.glob(f"{ticker_id}_{timeframe}_*.joblib"))

	if not files:
		raise FileNotFoundError(
			f"Модель для {ticker_id} с таймфреймом {timeframe} ещё не обучена!"
		)

	latest_file = max(files, key=lambda x: x.stat().st_mtime)

	data = joblib.load(latest_file)

	if not is_model_data(data):
		raise TypeError(
			f"Загруженные данные должны быть словарем, получен {type(data)}"
		)

	metadata = ModelMetadata(
		ticker_id=ticker_id,
		timeframe=timeframe,
		model_path=str(latest_file),
		created_at=datetime.fromtimestamp(latest_file.stat().st_mtime),
		features=data.get("features", []),
	)

	return ModelDataSchema(
		model=data["model"],
		scaler=data["scaler"],
		features=data["features"],
		metadata=metadata,
	)
