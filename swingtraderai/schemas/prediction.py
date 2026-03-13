from datetime import datetime
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class PredictionRequest(BaseModel):
	"""Схема для запроса на предсказание."""

	ticker_id: UUID = Field(..., description="Идентификатор тикера")
	timeframe: str = Field("1h", description="Таймфрейм")

	model_config = ConfigDict(arbitrary_types_allowed=True)


class PredictionResult(BaseModel):
	"""Схема для результата предсказания."""

	ticker_id: UUID
	timeframe: str
	probability: float = Field(ge=0.0, le=1.0, description="Вероятность long позиции")
	prediction: str = Field(
		..., pattern="^(long|short|flat)$", description="Направление"
	)
	confidence: float = Field(ge=0.0, le=1.0, description="Уверенность предсказания")
	timestamp: Optional[Union[datetime, str, int, float]] = None
	error: Optional[str] = None
	features_used: Optional[List[str]] = None
	data_points: Optional[int] = Field(None, ge=0)

	@field_validator("confidence")
	@classmethod
	def validate_confidence(cls, v: float, info: ValidationInfo) -> float:
		probability = info.data.get("probability")

		if probability is not None:
			expected = probability if probability > 0.5 else 1 - probability
			if abs(v - expected) > 0.01:
				raise ValueError(
					f"Confidence {v} не соответствует probability {probability} "
					f"(ожидаемое отклонение ≤ 0.01)"
				)

		return v


class ModelMetadata(BaseModel):
	"""Метаданные модели."""

	ticker_id: UUID
	timeframe: str
	model_path: str
	features: List[str]
	created_at: Optional[datetime] = None
	accuracy: Optional[float] = None

	model_config = ConfigDict(arbitrary_types_allowed=True)


class ModelDataSchema(BaseModel):
	"""Схема для данных загруженной модели."""

	model: Any  # XGBoost модель
	scaler: Any  # Scaler
	features: List[str]
	metadata: Optional[ModelMetadata] = None

	model_config = ConfigDict(arbitrary_types_allowed=True)
