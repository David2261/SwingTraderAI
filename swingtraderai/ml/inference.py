from uuid import UUID

import pandas as pd

from swingtraderai.indicators.matrix import add_all_indicators
from swingtraderai.ml.loader import load_latest_model
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA
from swingtraderai.schemas.prediction import (
	ModelDataSchema,
	PredictionRequest,
	PredictionResult,
)


async def predict(
	ticker_id: UUID, current_df: pd.DataFrame, timeframe: str = "1h"
) -> PredictionResult:
	"""
	Генерация прогноза для последнего бара.
	"""
	model_data: ModelDataSchema = load_latest_model(ticker_id, timeframe)

	model = model_data.model
	scaler = model_data.scaler
	feature_cols = model_data.features or MARKET_DATA_SCHEMA.MODEL_FEATURE_COLUMNS

	processed_df = add_all_indicators(current_df)

	if processed_df.empty:
		return PredictionResult(
			ticker_id=ticker_id,
			timeframe=timeframe,
			probability=0.0,
			prediction="flat",
			confidence=0.0,
			error="Недостаточно данных для расчета индикаторов",
			features_used=model_data.features,
			data_points=0,
		)

	missing_features = [
		col for col in model_data.features if col not in processed_df.columns
	]
	if missing_features:
		return PredictionResult(
			ticker_id=ticker_id,
			timeframe=timeframe,
			probability=0.0,
			prediction="flat",
			confidence=0.0,
			error=f"Отсутствуют фичи: {missing_features}",
			features_used=model_data.features,
			data_points=len(processed_df),
		)

	X_raw = processed_df[feature_cols].iloc[-1:]
	X_scaled = scaler.transform(X_raw)
	prob = model.predict_proba(X_scaled)[0][1]

	# Логика определения направления
	if prob > 0.65:
		prediction = "long"
	elif prob < 0.35:
		prediction = "short"
	else:
		prediction = "flat"
	timestamp = None
	return PredictionResult(
		ticker_id=ticker_id,
		timeframe=timeframe,
		probability=float(prob),
		prediction=prediction,
		confidence=float(prob if prob > 0.5 else 1 - prob),
		timestamp=timestamp,
		features_used=model_data.features,
		data_points=len(processed_df),
	)


async def predict_with_request(
	request: PredictionRequest, current_df: pd.DataFrame
) -> PredictionResult:
	"""Версия функции, принимающая Pydantic модель запроса."""
	required_cols = set(MARKET_DATA_SCHEMA.BASE_COLUMNS)
	missing = required_cols - set(current_df.columns)

	if missing:
		raise ValueError(f"Отсутствуют базовые колонки: {missing}")
	return await predict(request.ticker_id, current_df, request.timeframe)
