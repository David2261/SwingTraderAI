import inspect
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Union, cast

from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

RedisClient = Union[SyncRedis[Any], AsyncRedis[Any]]
RedisValue = Optional[Union[bytes, str, int, float]]

T = TypeVar("T")


def get_service_uptime(start_time: datetime) -> Dict[str, float]:
	"""
	Возвращает uptime основного сервиса в секундах и часах.
	start_time — время запуска приложения (app.state.start_time или global)
	"""
	uptime_sec = (datetime.now() - start_time).total_seconds()
	return {
		"uptime_seconds": round(uptime_sec, 2),
		"uptime_hours": round(uptime_sec / 3600, 2),
		"uptime_days": round(uptime_sec / 86400, 2),
	}


async def get_services_health(
	redis_client: SyncRedis[Any],
	db_engine: AsyncEngine,
	celery_app: Optional[Any] = None,
) -> Dict[str, str]:
	"""
	Простая проверка здоровья ключевых сервисов.
	Возвращает статус: ok / degraded / down
	"""
	health: Dict[str, str] = {"main_api": "ok"}

	try:
		redis_client.ping()
		health["redis"] = "ok"
	except Exception:
		health["redis"] = "down"

	try:
		async with db_engine.connect() as conn:
			await conn.execute(text("SELECT 1"))
		health["database"] = "ok"
	except Exception:
		health["database"] = "down"

	if celery_app is not None:
		try:
			inspector = celery_app.control.inspect()
			ping_result = inspector.ping()
			if ping_result:
				health["celery_workers"] = "ok"
			else:
				health["celery_workers"] = "degraded"
		except Exception:
			health["celery_workers"] = "down"
	else:
		health["celery_workers"] = "not_configured"

	return health


def get_disk_usage(path: str = "/") -> Dict[str, float]:
	"""
	Использование диска (в байтах и %). Работает на любом сервере без psutil.
	"""
	usage = shutil.disk_usage(path)
	return {
		"total_bytes": usage.total,
		"used_bytes": usage.used,
		"free_bytes": usage.free,
		"used_percent": round((usage.used / usage.total) * 100, 2),
	}


async def get_database_size(
	db_engine: AsyncEngine, database_name: Optional[str] = None
) -> Dict[str, int]:
	"""
	Размер PostgreSQL базы (в байтах и МБ).
	Если database_name=None — берёт текущую БД из connection.
	"""
	async with db_engine.connect() as conn:
		if database_name:
			query = text("SELECT pg_database_size(:dbname) AS size")
			result = await conn.execute(query, {"dbname": database_name})
		else:
			query = text("SELECT pg_database_size(current_database()) AS size")
			result = await conn.execute(query)

		size_bytes = result.scalar_one()

	return {
		"size_bytes": size_bytes,
		"size_mb": round(size_bytes / (1024 * 1024), 2),
		"size_gb": round(size_bytes / (1024 * 1024 * 1024), 2),
	}


async def get_table_sizes(db_engine: AsyncEngine) -> Dict[str, Dict[str, float]]:
	"""
	Размер всех таблиц (особенно полезно для OHLCV + индикаторы).
	Возвращает {table_name: {"bytes": , "mb": , "gb": }}
	"""
	query = text(
		"""
		SELECT
			table_name,
			COALESCE(pg_total_relation_size(table_name), 0) AS total_size
		FROM information_schema.tables
		WHERE table_schema = 'public'
		ORDER BY total_size DESC;
	"""
	)

	sizes: Dict[str, Dict[str, float]] = {}

	async with db_engine.connect() as conn:
		result = await conn.execute(query)

		for row in result.mappings():
			table_name = row["table_name"]
			bytes_size = row["total_size"]

			sizes[table_name] = {
				"bytes": int(bytes_size),
				"mb": round(bytes_size / (1024 * 1024), 2),
				"gb": round(bytes_size / (1024 * 1024 * 1024), 2),
			}
	return sizes


async def get_celery_queue_length(
	redis_client: Union[SyncRedis[Any], AsyncRedis[Any]], queue_name: str = "celery"
) -> Dict[str, int]:
	"""
	Длина очередей Celery (основная + любые custom).
	Работает через прямой доступ к Redis.
	"""
	if inspect.iscoroutinefunction(redis_client.llen):
		queue_length = await redis_client.llen(f"{queue_name}")
		retry_length = await redis_client.llen("celery_retry")
		failed_length = await redis_client.llen("celery_failed")
	else:
		queue_length = redis_client.llen(f"{queue_name}")
		retry_length = redis_client.llen("celery_retry")
		failed_length = redis_client.llen("celery_failed")

	queues: Dict[str, int] = {
		queue_name: queue_length if queue_length is not None else 0,
		"celery_retry": retry_length if retry_length is not None else 0,
		"celery_failed": failed_length if failed_length is not None else 0,
	}
	return queues


async def get_api_metrics(
	redis_client: Union[SyncRedis[Any], AsyncRedis[Any]], hours: int = 24
) -> Dict[str, Any]:
	"""
	Агрегированные метрики API за последние N часов.
	Поддерживает как синхронный, так и асинхронный redis-клиент.
	"""
	endpoint_keys_bytes = await _get_keys(
		redis_client, "metrics:api:endpoint:*:requests"
	)
	endpoint_keys: List[bytes] = endpoint_keys_bytes if endpoint_keys_bytes else []

	endpoint_stats: Dict[str, Dict[str, Union[int, float]]] = {}
	total_errors = 0

	total_requests_bytes = await _get(redis_client, "metrics:api:total_requests")
	total_requests = int(total_requests_bytes) if total_requests_bytes else 0

	for key in endpoint_keys:
		key_str = key.decode("utf-8")
		ep = key_str.split(":")[3]

		requests_bytes = await _get(redis_client, key_str)
		requests = int(requests_bytes) if requests_bytes else 0

		errors_key = key_str.replace("requests", "errors")
		errors_bytes = await _get(redis_client, errors_key)
		errors = int(errors_bytes) if errors_bytes else 0

		endpoint_stats[ep] = {
			"requests": requests,
			"errors": errors,
			"error_rate_percent": (
				round(errors / requests * 100, 2) if requests > 0 else 0.0
			),
		}
		total_errors += errors

	return {
		"total_requests": total_requests,
		"error_rate_overall_percent": (
			round(total_errors / total_requests * 100, 2) if total_requests > 0 else 0.0
		),
		"endpoints": endpoint_stats,
		"period_hours": hours,
		"collected_at": datetime.now().isoformat(),
	}


async def _get(client: RedisClient, key: str) -> RedisValue:
	"""
	Асинхронно получает значение из Redis, поддерживая как синхронный,
	так и асинхронный клиенты.
	"""
	if inspect.iscoroutinefunction(client.get):
		value: Any = await client.get(key)
		if value is None:
			return None
		return cast(Union[bytes, str, int, float], value)
	else:
		sync_value: Any = client.get(key)
		if sync_value is None:
			return None
		return cast(Union[bytes, str, int, float], sync_value)


async def _get_keys(client: RedisClient, pattern: str) -> List[bytes]:
	"""
	Асинхронно получает список ключей по паттерну, поддерживая
	как синхронный, так и асинхронный клиенты.
	"""
	if inspect.iscoroutinefunction(client.keys):
		keys_result: Any = await client.keys(pattern)
		if keys_result is None:
			return []
		if not isinstance(keys_result, list):
			return []
		return [cast(bytes, item) for item in keys_result]
	else:
		sync_keys_result: Any = client.keys(pattern)
		if sync_keys_result is None:
			return []
		if not isinstance(sync_keys_result, list):
			return []
		return [cast(bytes, item) for item in sync_keys_result]


def increment_api_counter(
	redis_client: SyncRedis[Any],
	endpoint: str,
	is_error: bool = False,
	is_rate_limit: bool = False,
) -> None:
	"""
	Вспомогательная функция — вызывайте в FastAPI middleware.
	"""
	pipe = redis_client.pipeline()
	pipe.incr("metrics:api:total_requests")

	pipe.incr(f"metrics:api:endpoint:{endpoint}:requests")
	if is_error:
		pipe.incr(f"metrics:api:endpoint:{endpoint}:errors")
	if is_rate_limit:
		pipe.incr("metrics:api:rate_limit_hits")

	pipe.execute()
