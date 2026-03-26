from datetime import datetime
from uuid import UUID

import pytest
from uuid6 import uuid7

from swingtraderai.schemas.prediction import (
	ModelDataSchema,
	ModelMetadata,
	PredictionRequest,
	PredictionResult,
)


def test_prediction_request_valid():
	ticker_id = uuid7()
	request = PredictionRequest(ticker_id=ticker_id, timeframe="15m")

	assert request.ticker_id == ticker_id
	assert request.timeframe == "15m"


def test_prediction_request_default_timeframe():
	request = PredictionRequest(ticker_id=uuid7())
	assert request.timeframe == "1h"


def test_prediction_request_invalid_ticker_id():
	with pytest.raises(ValueError):
		PredictionRequest(ticker_id="not-a-uuid", timeframe="1h")


def test_prediction_result_valid():
	ticker_id = uuid7()
	result = PredictionResult(
		ticker_id=ticker_id,
		timeframe="4h",
		probability=0.73,
		prediction="long",
		confidence=0.73,
		data_points=1250,
		features_used=["rsi", "macd", "bb_upper"],
	)

	assert result.probability == 0.73
	assert result.prediction == "long"
	assert result.confidence == 0.73
	assert result.data_points == 1250


def test_prediction_result_short_prediction():
	result = PredictionResult(
		ticker_id=uuid7(),
		timeframe="1h",
		probability=0.32,
		prediction="short",
		confidence=0.68,
	)
	assert result.prediction == "short"


def test_prediction_result_flat_prediction():
	result = PredictionResult(
		ticker_id=uuid7(),
		timeframe="1h",
		probability=0.51,
		prediction="flat",
		confidence=0.51,
	)
	assert result.prediction == "flat"


def test_prediction_result_confidence_validation_error():
	"""Тест валидатора: confidence должен примерно соответствовать probability"""
	ticker_id = uuid7()

	with pytest.raises(ValueError, match="Confidence .* не соответствует probability"):
		PredictionResult(
			ticker_id=ticker_id,
			timeframe="1h",
			probability=0.85,
			prediction="long",
			confidence=0.60,
		)


def test_prediction_result_invalid_prediction_value():
	with pytest.raises(ValueError):
		PredictionResult(
			ticker_id=uuid7(),
			timeframe="1h",
			probability=0.6,
			prediction="buy",
			confidence=0.6,
		)


def test_prediction_result_probability_out_of_range():
	with pytest.raises(ValueError):
		PredictionResult(
			ticker_id=uuid7(),
			timeframe="1h",
			probability=1.1,
			prediction="long",
			confidence=1.0,
		)


def test_model_metadata_valid():
	metadata = ModelMetadata(
		ticker_id=uuid7(),
		timeframe="1h",
		model_path="/models/xgb_aapl_1h.pkl",
		features=["rsi_14", "macd", "volume"],
		accuracy=0.672,
		created_at=datetime(2025, 3, 1, 12, 0),
	)

	assert metadata.accuracy == 0.672
	assert isinstance(metadata.ticker_id, UUID)


def test_model_metadata_optional_fields():
	metadata = ModelMetadata(
		ticker_id=uuid7(),
		timeframe="5m",
		model_path="model.joblib",
		features=["close", "rsi"],
	)
	assert metadata.accuracy is None
	assert metadata.created_at is None


def test_model_data_schema_valid():
	fake_model = object()
	fake_scaler = object()

	schema = ModelDataSchema(
		model=fake_model,
		scaler=fake_scaler,
		features=["rsi", "macd", "bb"],
		metadata=ModelMetadata(
			ticker_id=uuid7(),
			timeframe="1h",
			model_path="test.model",
			features=["rsi", "macd", "bb"],
		),
	)

	assert schema.model is fake_model
	assert schema.scaler is fake_scaler
	assert len(schema.features) == 3
	assert schema.metadata is not None


def test_model_data_schema_without_metadata():
	schema = ModelDataSchema(model=object(), scaler=object(), features=["close"])
	assert schema.metadata is None


def test_prediction_result_with_timestamp_types():
	"""Проверяем, что timestamp принимает разные типы"""
	now = datetime.now()

	for ts in [now, now.isoformat(), 1742820000, 1742820000.5]:
		result = PredictionResult(
			ticker_id=uuid7(),
			timeframe="1h",
			probability=0.65,
			prediction="long",
			confidence=0.65,
			timestamp=ts,
		)
		assert result.timestamp is not None


def test_empty_features_list_allowed():
	result = PredictionResult(
		ticker_id=uuid7(),
		timeframe="1h",
		probability=0.5,
		prediction="flat",
		confidence=0.5,
		features_used=[],
	)
	assert result.features_used == []
