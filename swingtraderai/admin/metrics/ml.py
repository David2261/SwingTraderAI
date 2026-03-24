import json
from datetime import datetime
from typing import Any, Dict, Optional

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncEngine


async def get_tickers_under_management(db_engine: AsyncEngine) -> Dict[str, Any]:
	"""
	Tickers / Symbols under management
	Возвращает:
	- total_tickers
	- active_tickers (есть успешная модель)
	- list_of_tickers
	"""
	try:
		query = text(
			"""
			SELECT
				COUNT(DISTINCT ticker) AS total,
				COUNT(DISTINCT CASE WHEN status = 'success' THEN ticker END) AS active,
				ARRAY_AGG(DISTINCT ticker ORDER BY ticker) AS tickers
			FROM models
			WHERE deprecated = FALSE;
		"""
		)

		async with db_engine.connect() as conn:
			result = await conn.execute(query)
			row: Optional[Row[Any]] = result.fetchone()

			if row is None:
				return {
					"total_tickers": 0,
					"active_tickers": 0,
					"tickers_list": [],
				}

			return {
				"total_tickers": row[0] or 0,
				"active_tickers": row[1] or 0,
				"tickers_list": row[2] or [],
			}

	except Exception as e:
		return {
			"total_tickers": 0,
			"active_tickers": 0,
			"tickers_list": [],
			"error": str(e),
		}


async def get_trained_models_count(db_engine: AsyncEngine) -> Dict[str, int]:
	"""
	Trained Models count (активные / в обучении / failed / deprecated)
	"""
	query = text(
		"""
		SELECT
			COUNT(CASE WHEN status = 'success' THEN 1 END) AS active,
			COUNT(CASE WHEN status IN ('queued', 'running') THEN 1 END) AS training,
			COUNT(CASE WHEN status = 'error' THEN 1 END) AS failed,
			COUNT(CASE WHEN deprecated = TRUE THEN 1 END) AS deprecated
		FROM models;
	"""
	)

	async with db_engine.connect() as conn:
		result = await conn.execute(query)
		row: Optional[Row[Any]] = result.fetchone()

		if row is None:
			return {
				"active": 0,
				"in_training": 0,
				"failed": 0,
				"deprecated": 0,
				"total_models": 0,
			}

		active = row[0] or 0
		training = row[1] or 0
		failed = row[2] or 0
		deprecated = row[3] or 0

		return {
			"active": active,
			"in_training": training,
			"failed": failed,
			"deprecated": deprecated,
			"total_models": active + training + failed + deprecated,
		}


async def get_last_training_dates(db_engine: AsyncEngine) -> Dict[str, Optional[str]]:
	"""
	Last Training Date по каждому тикеру (только успешные модели)
	"""
	query = text(
		"""
		SELECT ticker, MAX(trained_at) AS last_trained
		FROM models
		WHERE status = 'success'
		GROUP BY ticker
		ORDER BY ticker;
	"""
	)

	async with db_engine.connect() as conn:
		result = await conn.execute(query)
		rows = result.fetchall()

		result_dict: Dict[str, Optional[str]] = {}
		for row in rows:
			ticker: str = row[0]
			trained_at: Optional[datetime] = row[1]
			result_dict[ticker] = trained_at.isoformat() if trained_at else None

		return result_dict


async def get_training_statuses(db_engine: AsyncEngine) -> Dict[str, Dict[str, Any]]:
	"""
	Training Status + duration по всем тикерам
	"""
	query = text(
		"""
		SELECT DISTINCT ON (ticker)
			ticker,
			status,
			version,
			trained_at,
			training_duration_seconds,
			EXTRACT(EPOCH FROM (NOW() - trained_at))::int AS seconds_since_last_train
		FROM models
		WHERE deprecated = FALSE
		ORDER BY ticker, trained_at DESC;
	"""
	)

	async with db_engine.connect() as conn:
		result = await conn.execute(query)
		rows = result.fetchall()

		statuses: Dict[str, Dict[str, Any]] = {}

		for row in rows:
			ticker: str = row[0]
			status: str = row[1]
			version: Optional[str] = row[2]
			trained_at: Optional[datetime] = row[3]
			training_duration_seconds: Optional[int] = row[4]
			seconds_since_last_train: Optional[int] = row[5]

			statuses[ticker] = {
				"status": status,
				"version": version,
				"last_trained": trained_at.isoformat() if trained_at else None,
				"training_duration_minutes": (
					round((training_duration_seconds or 0) / 60, 1)
					if training_duration_seconds
					else None
				),
				"minutes_since_last_train": round(
					(seconds_since_last_train or 0) / 60, 1
				),
			}
		return statuses


async def get_prediction_volume(
	redis_client: redis.Redis[Any], hours: int = 168
) -> Dict[str, Any]:
	"""
	Prediction Request Volume (за сутки / неделю)
	Предполагается, что в middleware / worker ты делаешь:
	redis.incr("ai:predictions:total")
	redis.incr(f"ai:predictions:ticker:{ticker}")
	"""
	now = datetime.now()

	total_day = int(await redis_client.get("ai:predictions:total:day") or 0)
	total_week = int(await redis_client.get("ai:predictions:total:week") or 0)

	return {
		"daily_total": total_day,
		"weekly_total": total_week,
		"period_hours": hours,
		"collected_at": now.isoformat(),
	}


async def get_latest_prediction_timestamps(
	db_engine: AsyncEngine,
) -> Dict[str, Optional[str]]:
	"""
	Latest Prediction Timestamp по каждому тикеру
	"""
	query = text(
		"""
		SELECT ticker, MAX(created_at) AS last_prediction
		FROM predictions
		GROUP BY ticker
		ORDER BY ticker;
	"""
	)

	async with db_engine.connect() as conn:
		result = await conn.execute(query)
		rows = result.fetchall()
		timestamps: Dict[str, Optional[str]] = {}
		for row in rows:
			ticker: str = row[0]
			last_prediction: Optional[datetime] = row[1]
			timestamps[ticker] = (
				last_prediction.isoformat() if last_prediction else None
			)

		return timestamps


async def get_model_performance_metrics(
	db_engine: AsyncEngine,
) -> Dict[str, Dict[str, Any]]:
	"""
	Model Performance Metrics (Accuracy, Sharpe, Win Rate и т.д.)
	Предполагается таблица model_performance с колонками:
	ticker, version, accuracy, precision, recall, f1, sharpe_ratio,
	sortino_ratio, max_drawdown, win_rate, profit_factor,
	roc_auc, pr_auc, feature_importance_json, date
	"""
	query = text(
		"""
		SELECT
			ticker,
			version,
			accuracy,
			precision,
			recall,
			f1,
			sharpe_ratio,
			sortino_ratio,
			max_drawdown,
			win_rate,
			profit_factor,
			roc_auc,
			pr_auc,
			feature_importance_json
		FROM model_performance
		WHERE date = (
			SELECT MAX(date)
			FROM model_performance mp2
			WHERE mp2.ticker = model_performance.ticker
		)
		ORDER BY ticker;
	"""
	)

	async with db_engine.connect() as conn:
		result = await conn.execute(query)
		rows = result.fetchall()

		perf: Dict[str, Dict[str, Any]] = {}

		for row in rows:
			ticker: str = row[0]
			version: Optional[str] = row[1]
			accuracy: Optional[float] = row[2]
			precision: Optional[float] = row[3]
			recall: Optional[float] = row[4]
			f1: Optional[float] = row[5]
			sharpe_ratio: Optional[float] = row[6]
			sortino_ratio: Optional[float] = row[7]
			max_drawdown: Optional[float] = row[8]
			win_rate: Optional[float] = row[9]
			profit_factor: Optional[float] = row[10]
			roc_auc: Optional[float] = row[11]
			pr_auc: Optional[float] = row[12]
			feature_importance_json: Optional[str] = row[13]

			fi = json.loads(feature_importance_json) if feature_importance_json else {}

			top5_features: Dict[str, float] = {}

			if isinstance(fi, dict):
				sorted_features = sorted(fi.items(), key=lambda x: x[1], reverse=True)[
					:5
				]
				top5_features = dict(sorted_features)

			perf[ticker] = {
				"version": version,
				"classification": {
					"accuracy": round(accuracy or 0, 4),
					"precision": round(precision or 0, 4),
					"recall": round(recall or 0, 4),
					"f1": round(f1 or 0, 4),
					"roc_auc": round(roc_auc or 0, 4),
					"pr_auc": round(pr_auc or 0, 4),
				},
				"trading": {
					"sharpe_ratio": round(sharpe_ratio or 0, 3),
					"sortino_ratio": round(sortino_ratio or 0, 3),
					"max_drawdown_percent": round((max_drawdown or 0) * 100, 2),
					"win_rate_percent": round((win_rate or 0) * 100, 2),
					"profit_factor": round(profit_factor or 0, 2),
				},
				"top5_features": top5_features,
			}

		return perf


async def get_failed_predictions_rate(
	redis_client: redis.Redis[Any], days: int = 7
) -> Dict[str, float]:
	"""
	Failed Predictions / Errors rate (за сутки / неделю)
	"""
	failed_day = int(await redis_client.get("ai:predictions:failed:day") or 0)
	total_day = int(await redis_client.get("ai:predictions:total:day") or 1)

	failed_week = int(await redis_client.get("ai:predictions:failed:week") or 0)
	total_week = int(await redis_client.get("ai:predictions:total:week") or 1)

	return {
		"daily_error_rate_percent": round((failed_day / total_day) * 100, 3),
		"weekly_error_rate_percent": round((failed_week / total_week) * 100, 3),
		"failed_day": failed_day,
		"failed_week": failed_week,
	}


async def get_all_ai_metrics(
	db_engine: AsyncEngine, redis_client: redis.Redis[Any]
) -> Dict[str, Any]:
	"""
	Одна функция, которая возвращает ВСЁ по ИИ-моделям сразу.
	Вызывай из API /metrics/ai
	"""
	return {
		"tickers": await get_tickers_under_management(db_engine),
		"models_count": await get_trained_models_count(db_engine),
		"last_training_dates": await get_last_training_dates(db_engine),
		"training_statuses": await get_training_statuses(db_engine),
		"prediction_volume": await get_prediction_volume(redis_client),
		"latest_predictions": await get_latest_prediction_timestamps(db_engine),
		"performance": await get_model_performance_metrics(db_engine),
		"error_rates": await get_failed_predictions_rate(redis_client),
		"collected_at": datetime.now().isoformat(),
	}
