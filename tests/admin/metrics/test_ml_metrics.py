import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from swingtraderai.admin.metrics.ml import (
	get_failed_predictions_rate,
	get_last_training_dates,
	get_latest_prediction_timestamps,
	get_model_performance_metrics,
	get_prediction_volume,
	get_tickers_under_management,
	get_trained_models_count,
	get_training_statuses,
)


@pytest.fixture
def mock_engine(mocker):
	engine = mocker.Mock()

	conn = mocker.AsyncMock()

	connect_cm = mocker.AsyncMock()
	connect_cm.__aenter__.return_value = conn
	connect_cm.__aexit__.return_value = None

	engine.connect.return_value = connect_cm

	return engine, conn


@pytest.mark.asyncio
async def test_get_tickers_under_management_ok(mock_engine):
	engine, conn = mock_engine

	row = (10, 7, ["AAPL", "BTCUSDT"])
	result_mock = MagicMock()
	result_mock.fetchone.return_value = row

	conn.execute.return_value = result_mock

	result = await get_tickers_under_management(engine)

	assert result["total_tickers"] == 10
	assert result["active_tickers"] == 7
	assert result["tickers_list"] == ["AAPL", "BTCUSDT"]


@pytest.mark.asyncio
async def test_get_tickers_under_management_empty(mock_engine):
	engine, conn = mock_engine

	result_mock = MagicMock()
	result_mock.fetchone.return_value = None
	conn.execute.return_value = result_mock

	result = await get_tickers_under_management(engine)

	assert result["total_tickers"] == 0
	assert result["tickers_list"] == []


@pytest.mark.asyncio
async def test_get_tickers_under_management_exception(mock_engine):
	engine, conn = mock_engine

	conn.execute.side_effect = Exception("DB down")

	result = await get_tickers_under_management(engine)

	assert result["total_tickers"] == 0
	assert "error" in result


@pytest.mark.asyncio
async def test_get_trained_models_count_ok(mock_engine):
	engine, conn = mock_engine

	row = (5, 2, 1, 1)
	result_mock = MagicMock()
	result_mock.fetchone.return_value = row
	conn.execute.return_value = result_mock

	result = await get_trained_models_count(engine)

	assert result["active"] == 5
	assert result["in_training"] == 2
	assert result["failed"] == 1
	assert result["deprecated"] == 1
	assert result["total_models"] == 9


@pytest.mark.asyncio
async def test_get_last_training_dates(mock_engine):
	engine, conn = mock_engine

	now = datetime.now(timezone.utc)

	rows = [
		("AAPL", now),
		("BTCUSDT", None),
	]

	result_mock = MagicMock()
	result_mock.fetchall.return_value = rows
	conn.execute.return_value = result_mock

	result = await get_last_training_dates(engine)

	assert result["AAPL"] == now.isoformat()
	assert result["BTCUSDT"] is None


@pytest.mark.asyncio
async def test_get_training_statuses(mock_engine):
	engine, conn = mock_engine

	now = datetime.now(timezone.utc)

	rows = [
		("AAPL", "success", "v1", now, 120, 3600),
	]

	result_mock = MagicMock()
	result_mock.fetchall.return_value = rows
	conn.execute.return_value = result_mock

	result = await get_training_statuses(engine)

	assert result["AAPL"]["status"] == "success"
	assert result["AAPL"]["training_duration_minutes"] == 2.0
	assert result["AAPL"]["minutes_since_last_train"] == 60.0


@pytest.mark.asyncio
async def test_get_prediction_volume(mock_async_redis):
	mock_async_redis.get = AsyncMock(side_effect=["10", "70"])

	result = await get_prediction_volume(mock_async_redis)

	assert result["daily_total"] == 10
	assert result["weekly_total"] == 70
	assert "collected_at" in result


@pytest.mark.asyncio
async def test_get_latest_prediction_timestamps(mock_engine):
	engine, conn = mock_engine

	now = datetime.now(timezone.utc)

	rows = [
		("AAPL", now),
		("BTCUSDT", None),
	]

	result_mock = MagicMock()
	result_mock.fetchall.return_value = rows
	conn.execute.return_value = result_mock

	result = await get_latest_prediction_timestamps(engine)

	assert result["AAPL"] == now.isoformat()
	assert result["BTCUSDT"] is None


@pytest.mark.asyncio
async def test_get_model_performance_metrics(mock_engine):
	engine, conn = mock_engine

	fi = json.dumps({"f1": 0.9, "f2": 0.8, "f3": 0.7, "f4": 0.6, "f5": 0.5, "f6": 0.4})

	rows = [
		(
			"AAPL",
			"v1",
			0.91,
			0.92,
			0.93,
			0.94,
			1.5,
			1.2,
			-0.1,
			0.6,
			1.8,
			0.95,
			0.96,
			fi,
		)
	]

	result_mock = MagicMock()
	result_mock.fetchall.return_value = rows
	conn.execute.return_value = result_mock

	result = await get_model_performance_metrics(engine)

	perf = result["AAPL"]

	assert perf["classification"]["accuracy"] == 0.91
	assert perf["trading"]["win_rate_percent"] == 60.0
	assert len(perf["top5_features"]) == 5


@pytest.mark.asyncio
async def test_get_failed_predictions_rate(mock_async_redis):
	mock_async_redis.get = AsyncMock(side_effect=["2", "10", "5", "20"])

	result = await get_failed_predictions_rate(mock_async_redis)

	assert result["daily_error_rate_percent"] == 20.0
	assert result["weekly_error_rate_percent"] == 25.0
