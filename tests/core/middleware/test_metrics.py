from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from swingtraderai.core.middleware.metrics import APIMetricsMiddleware


class TestAPIMetricsMiddleware:
	"""Тесты для APIMetricsMiddleware"""

	@pytest.fixture
	def app_with_middleware(self, mock_async_redis):
		"""Создает тестовое приложение с middleware"""
		app = FastAPI()

		@app.get("/api/v1/test/endpoint")
		async def test_endpoint():
			return {"status": "ok"}

		@app.get("/api/v1/admin/ml/predict/123")
		async def predict_endpoint():
			return {"prediction": 0.85}

		@app.get("/api/v1/admin/ml/train/")
		async def train_endpoint():
			return {"status": "training"}

		@app.get("/error-endpoint")
		async def error_endpoint():
			raise ValueError("Test error")

		@app.get("/rate-limit-endpoint")
		async def rate_limit_endpoint():
			return JSONResponse(status_code=429, content={"error": "Rate limit"})

		app.add_middleware(APIMetricsMiddleware, redis_client=mock_async_redis)
		return app

	@pytest.fixture
	def client(self, app_with_middleware):
		"""Создает тестовый клиент"""
		return TestClient(app_with_middleware)

	@pytest.mark.asyncio
	async def test_middleware_records_metrics_for_successful_request(
		self, client, mock_async_redis
	):
		"""Проверяет, что middleware записывает метрики для успешного запроса"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/test/endpoint")

		assert response.status_code == 200
		assert response.json() == {"status": "ok"}

		assert "X-Process-Time" in response.headers
		assert float(response.headers["X-Process-Time"]) >= 0

		mock_async_redis.pipeline.assert_called_once()

		assert mock_pipeline.incr.call_count == 2
		mock_pipeline.incr.assert_any_call("metrics:api:total_requests")
		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/api/v1/test/endpoint:requests"
		)

		assert "errors" not in str(mock_pipeline.incr.call_args_list)

		mock_pipeline.execute.assert_called_once()

	@pytest.mark.asyncio
	async def test_middleware_normalizes_predict_endpoint(
		self, client, mock_async_redis
	):
		"""Проверяет, что эндпоинт /predict нормализуется правильно"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/admin/ml/predict/123")

		assert response.status_code == 200

		mock_pipeline.incr.assert_any_call("metrics:api:endpoint:/predict:requests")
		assert "api/v1/admin/ml/predict/123" not in str(
			mock_pipeline.incr.call_args_list
		)

	@pytest.mark.asyncio
	async def test_middleware_normalizes_train_endpoint(self, client, mock_async_redis):
		"""Проверяет, что эндпоинт /train нормализуется правильно"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/admin/ml/train/")

		assert response.status_code == 200

		mock_pipeline.incr.assert_any_call("metrics:api:endpoint:/train:requests")

	@pytest.mark.asyncio
	async def test_middleware_normalizes_trailing_slash(self, client, mock_async_redis):
		"""Проверяет, что удаляется trailing slash"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		@client.app.get("/api/v1/test/with-slash/")
		async def slash_endpoint():
			return {"status": "ok"}

		response = client.get("/api/v1/test/with-slash/")

		assert response.status_code == 200

		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/api/v1/test/with-slash:requests"
		)

	@pytest.mark.asyncio
	async def test_middleware_records_errors_for_4xx_responses(
		self, client, mock_async_redis
	):
		"""Проверяет, что middleware записывает ошибки для 4xx ответов"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/nonexistent-endpoint")

		assert response.status_code == 404

		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/nonexistent-endpoint:errors"
		)
		mock_pipeline.incr.assert_any_call("metrics:api:total_requests")
		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/nonexistent-endpoint:requests"
		)

	@pytest.mark.asyncio
	async def test_middleware_records_rate_limit_hits(self, client, mock_async_redis):
		"""Проверяет, что middleware записывает rate limit hits"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/rate-limit-endpoint")

		assert response.status_code == 429

		mock_pipeline.incr.assert_any_call("metrics:api:rate_limit_hits")
		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/rate-limit-endpoint:errors"
		)

	@pytest.mark.asyncio
	async def test_middleware_handles_exception_during_request(
		self, app_with_middleware, mock_async_redis
	):
		"""Проверяет, что middleware обрабатывает исключения в обработчике"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		client = TestClient(app_with_middleware)

		with pytest.raises(ValueError, match="Test error"):
			client.get("/error-endpoint")

		mock_async_redis.pipeline.assert_called_once()
		mock_pipeline.incr.assert_any_call("metrics:api:total_requests")
		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/error-endpoint:requests"
		)
		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/error-endpoint:errors"
		)

	@pytest.mark.asyncio
	async def test_middleware_handles_redis_error_gracefully(
		self, client, mock_async_redis
	):
		"""Проверяет, что middleware не падает при ошибке Redis"""
		mock_pipeline = AsyncMock()
		mock_pipeline.execute.side_effect = Exception("Redis connection error")
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/test/endpoint")

		assert response.status_code == 200
		mock_async_redis.pipeline.assert_called_once()
		mock_pipeline.execute.assert_called_once()

	@pytest.mark.asyncio
	async def test_middleware_logs_redis_error(self, client, mock_async_redis, caplog):
		"""Проверяет, что ошибка Redis логируется"""
		mock_pipeline = AsyncMock()
		mock_pipeline.execute.side_effect = Exception("Redis connection error")
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/test/endpoint")

		assert response.status_code == 200

	@pytest.mark.asyncio
	async def test_middleware_adds_process_time_header(self, client):
		"""Проверяет, что добавляется заголовок X-Process-Time"""
		response = client.get("/api/v1/test/endpoint")

		assert "X-Process-Time" in response.headers
		process_time = float(response.headers["X-Process-Time"])
		assert process_time >= 0
		assert process_time < 1000

	@pytest.mark.asyncio
	async def test_process_time_format_is_correct(self, client):
		"""Проверяет формат времени выполнения"""
		response = client.get("/api/v1/test/endpoint")

		process_time = response.headers["X-Process-Time"]
		assert (
			process_time.replace(".", "").isdigit()
			or process_time.replace("-", "").replace(".", "").isdigit()
		)
		assert len(process_time.split(".")[-1]) <= 2

	@pytest.mark.asyncio
	async def test_middleware_handles_empty_path(self, client, mock_async_redis):
		"""Проверяет обработку пустого пути"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/")

		assert response.status_code == 404

		mock_pipeline.incr.assert_any_call("metrics:api:endpoint::requests")

	@pytest.mark.asyncio
	async def test_middleware_handles_path_with_query_params(
		self, client, mock_async_redis
	):
		"""Проверяет, что query params не влияют на имя эндпоинта"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/test/endpoint?param1=value1&param2=value2")

		assert response.status_code == 200

		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/api/v1/test/endpoint:requests"
		)

	@pytest.mark.asyncio
	async def test_middleware_handles_multiple_requests_concurrently(
		self, client, mock_async_redis
	):
		"""Проверяет обработку нескольких запросов"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		for _ in range(3):
			response = client.get("/api/v1/test/endpoint")
			assert response.status_code == 200

		assert mock_async_redis.pipeline.call_count == 3

	@pytest.mark.asyncio
	async def test_middleware_does_not_affect_response_body(self, client):
		"""Проверяет, что middleware не изменяет тело ответа"""
		response = client.get("/api/v1/test/endpoint")

		assert response.json() == {"status": "ok"}

	@pytest.mark.asyncio
	async def test_middleware_works_with_different_http_methods(
		self, client, mock_async_redis
	):
		"""Проверяет работу с разными HTTP методами"""
		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.post("/api/v1/test/endpoint")
		assert response.status_code == 405

		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/api/v1/test/endpoint:requests"
		)

	@pytest.mark.asyncio
	async def test_middleware_initialization(self, mock_async_redis):
		"""Проверяет инициализацию middleware"""
		app = FastAPI()

		middleware = APIMetricsMiddleware(app, redis_client=mock_async_redis)

		assert middleware.app == app
		assert middleware.redis == mock_async_redis


class TestAPIMetricsMiddlewareEdgeCases:
	"""Тесты edge cases для middleware"""

	@pytest.mark.asyncio
	async def test_middleware_with_special_characters_in_path(self, mock_async_redis):
		"""Проверяет обработку путей со спецсимволами"""
		app = FastAPI()

		@app.get("/api/v1/test/endpoint@special")
		async def special_endpoint():
			return {"status": "ok"}

		app.add_middleware(APIMetricsMiddleware, redis_client=mock_async_redis)
		client = TestClient(app)

		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/test/endpoint@special")

		assert response.status_code == 200
		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/api/v1/test/endpoint@special:requests"
		)

	@pytest.mark.asyncio
	async def test_middleware_with_unicode_in_path(self, mock_async_redis):
		"""Проверяет обработку путей с Unicode символами"""
		app = FastAPI()

		@app.get("/api/v1/test/привет")
		async def unicode_endpoint():
			return {"status": "ok"}

		app.add_middleware(APIMetricsMiddleware, redis_client=mock_async_redis)
		client = TestClient(app)

		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get("/api/v1/test/привет")

		assert response.status_code == 200
		mock_pipeline.incr.assert_called()

	@pytest.mark.asyncio
	async def test_middleware_with_very_long_path(self, mock_async_redis):
		"""Проверяет обработку очень длинного пути"""
		app = FastAPI()

		long_path = "/" + "/".join(["segment"] * 100)

		@app.get(long_path)
		async def long_endpoint():
			return {"status": "ok"}

		app.add_middleware(APIMetricsMiddleware, redis_client=mock_async_redis)
		client = TestClient(app)

		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		response = client.get(long_path)

		assert response.status_code == 200
		mock_pipeline.incr.assert_called()


class TestAPIMetricsMiddlewareMetricsNaming:
	"""Тесты корректности именования метрик"""

	@pytest.mark.asyncio
	async def test_total_requests_counter(self, mock_async_redis):
		"""Проверяет счетчик total_requests"""
		app = FastAPI()

		@app.get("/test")
		async def test():
			return {"ok": True}

		app.add_middleware(APIMetricsMiddleware, redis_client=mock_async_redis)
		client = TestClient(app)

		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		client.get("/test")

		mock_pipeline.incr.assert_any_call("metrics:api:total_requests")

	@pytest.mark.asyncio
	async def test_endpoint_specific_counter(self, mock_async_redis):
		"""Проверяет счетчики для конкретных эндпоинтов"""
		app = FastAPI()

		@app.get("/api/v1/users/123")
		async def get_user():
			return {"user": "test"}

		app.add_middleware(APIMetricsMiddleware, redis_client=mock_async_redis)
		client = TestClient(app)

		mock_pipeline = AsyncMock()
		mock_pipeline.incr = MagicMock(return_value=mock_pipeline)
		mock_async_redis.pipeline.return_value = mock_pipeline

		client.get("/api/v1/users/123")

		mock_pipeline.incr.assert_any_call(
			"metrics:api:endpoint:/api/v1/users/123:requests"
		)
