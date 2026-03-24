import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
import redis
from sqlalchemy.ext.asyncio import AsyncEngine

from swingtraderai.admin.metrics.performance import (
	get_api_metrics,
	get_celery_queue_length,
	get_database_size,
	get_disk_usage,
	get_service_uptime,
	get_services_health,
	get_table_sizes,
	increment_api_counter,
)


@pytest.fixture
def start_time():
	return datetime(2025, 1, 1, 10, 0, 0)


@pytest.fixture
def mock_db_engine(mocker):
	engine = mocker.AsyncMock(spec=AsyncEngine)

	conn = mocker.AsyncMock()

	health_result = mocker.Mock()
	health_result.scalar_one.return_value = 1

	size_result = mocker.Mock()
	size_result.scalar_one.return_value = 1_234_567_890

	table_result = mocker.Mock()
	table_result.fetchall.return_value = [
		("users", 12_345_678),
		("ohlcv_1m", 1_073_741_824),
	]

	conn.execute.return_value = health_result

	engine.connect.return_value.__aenter__.return_value = conn

	engine._health_result = health_result
	engine._size_result = size_result
	engine._table_result = table_result

	return engine


def test_get_service_uptime(start_time):
	uptime = get_service_uptime(start_time)

	assert isinstance(uptime, dict)
	assert "uptime_seconds" in uptime
	assert "uptime_hours" in uptime
	assert "uptime_days" in uptime

	assert uptime["uptime_seconds"] > 0
	assert uptime["uptime_hours"] > 0
	assert isinstance(uptime["uptime_seconds"], float)


def test_get_disk_usage():
	usage = get_disk_usage("/")

	assert isinstance(usage, dict)
	assert all(
		k in usage for k in ["total_bytes", "used_bytes", "free_bytes", "used_percent"]
	)
	assert usage["total_bytes"] > 0
	assert 0 <= usage["used_percent"] <= 100
	assert isinstance(usage["used_percent"], float)


@pytest.mark.asyncio
async def test_get_services_health_all_ok(
	mocker, mock_redis, mock_db_engine, mock_celery
):
	conn = mocker.AsyncMock()
	conn.execute = AsyncMock()

	conn.execute.return_value = mocker.Mock()
	conn.execute.return_value.scalar_one = mocker.Mock(return_value=1)

	mock_db_engine.connect.return_value.__aenter__.return_value = conn
	health = await get_services_health(
		redis_client=mock_redis, db_engine=mock_db_engine, celery_app=mock_celery
	)

	assert health["main_api"] == "ok"
	assert health["redis"] == "ok"
	assert health["database"] == "ok"
	assert health["celery_workers"] == "ok"


@pytest.mark.asyncio
async def test_get_services_health_with_failures(mock_redis, mock_db_engine):
	mock_redis.ping.side_effect = Exception("Redis down")

	health = await get_services_health(
		redis_client=mock_redis, db_engine=mock_db_engine, celery_app=None
	)

	assert health["redis"] == "down"
	assert health["celery_workers"] == "not_configured"


@pytest.mark.asyncio
async def test_get_database_size(mock_db_engine):
	expected_size = 1_234_567_890

	conn = mock_db_engine.connect.return_value.__aenter__.return_value
	conn.execute.return_value.scalar_one.return_value = expected_size

	size_info = await get_database_size(mock_db_engine)

	assert size_info == {
		"size_bytes": expected_size,
		"size_mb": 1177.38,
		"size_gb": 1.15,
	}


@pytest.mark.asyncio
async def test_get_table_sizes(mock_db_engine):
	conn = mock_db_engine.connect.return_value.__aenter__.return_value

	mock_result = MagicMock()
	mock_result.mappings.return_value = [
		{"table_name": "ohlcv_1m", "total_size": 1073741824},
		{"table_name": "users", "total_size": 10485760},
		{"table_name": "tickers", "total_size": 0},
	]
	conn.execute.return_value = mock_result

	sizes = await get_table_sizes(mock_db_engine)

	assert isinstance(sizes, dict)
	assert "ohlcv_1m" in sizes
	assert "users" in sizes

	assert sizes["ohlcv_1m"]["bytes"] == 1073741824
	assert sizes["ohlcv_1m"]["gb"] == 1.0
	assert sizes["users"]["mb"] == 10.0
	assert sizes["tickers"]["bytes"] == 0


@pytest.mark.asyncio
async def test_get_celery_queue_length_sync_redis(mock_redis):
	queues = await get_celery_queue_length(mock_redis, queue_name="celery")

	assert queues["celery"] == 42
	assert queues["celery_retry"] == 42
	assert queues["celery_failed"] == 42


@pytest.mark.asyncio
async def test_get_celery_queue_length_async_redis():
	async_redis = AsyncMock(spec=redis.asyncio.Redis)
	async_redis.llen = AsyncMock(return_value=7)

	queues = await get_celery_queue_length(async_redis)

	assert queues["celery"] == 7


def test_get_api_metrics_empty(mock_redis):
	mock_redis.get.return_value = None
	mock_redis.keys = AsyncMock(return_value=[])

	metrics = asyncio.run(get_api_metrics(mock_redis, hours=24))

	assert metrics["total_requests"] == 0
	assert metrics["error_rate_overall_percent"] == 0.0
	assert metrics["endpoints"] == {}
	assert metrics["period_hours"] == 24


@pytest.mark.asyncio
async def test_get_api_metrics_with_data(mock_async_redis):
	async def mock_get(key):
		"""Асинхронная функция для мокинга redis.get"""
		key_str = key if isinstance(key, str) else key.decode()

		values = {
			"metrics:api:total_requests": b"1500",
			"metrics:api:endpoint:/predict:requests": b"800",
			"metrics:api:endpoint:/predict:errors": b"24",
			"metrics:api:endpoint:/health:requests": b"300",
			"metrics:api:endpoint:/health:errors": b"0",
		}

		result = values.get(key_str)
		return result if result is not None else None

	mock_async_redis.get = AsyncMock(side_effect=mock_get)

	mock_async_redis.keys = AsyncMock(
		return_value=[
			b"metrics:api:endpoint:/predict:requests",
			b"metrics:api:endpoint:/health:requests",
		]
	)

	metrics = await get_api_metrics(mock_async_redis, hours=6)

	assert metrics["total_requests"] == 1500
	assert metrics["error_rate_overall_percent"] == pytest.approx(1.6, rel=0.1)
	assert "/predict" in metrics["endpoints"]
	assert "/health" in metrics["endpoints"]
	assert metrics["endpoints"]["/predict"]["requests"] == 800
	assert metrics["endpoints"]["/predict"]["errors"] == 24
	assert metrics["endpoints"]["/predict"]["error_rate_percent"] == pytest.approx(
		3.0, rel=0.1
	)


def test_increment_api_counter(mock_redis):
	increment_api_counter(
		redis_client=mock_redis, endpoint="/predict", is_error=True, is_rate_limit=False
	)

	mock_redis.pipeline.assert_called_once()
	pipe = mock_redis.pipeline.return_value
	pipe.incr.assert_any_call("metrics:api:total_requests")
	pipe.incr.assert_any_call("metrics:api:endpoint:/predict:requests")
	pipe.incr.assert_any_call("metrics:api:endpoint:/predict:errors")
	pipe.execute.assert_called_once()


def test_get_service_uptime_very_old_start():
	old_start = datetime.now() - timedelta(days=365)
	uptime = get_service_uptime(old_start)
	assert uptime["uptime_days"] > 300


def test_get_disk_usage_custom_path():
	usage = get_disk_usage("/tmp")
	assert usage["total_bytes"] > 0
